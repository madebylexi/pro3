import os
import json
from flask import Flask, request, redirect, render_template
from google.cloud import storage
import google.generativeai as genai
import google.cloud.exceptions

app = Flask(__name__, template_folder='templates')

# Environment variables
bucket_name = os.environ.get("BUCKET_NAME", "pr1images-bucket")
background_color = os.environ.get("BACKGROUND_COLOR", "#FFFFFF")

# Initialize GCS client
storage_client = storage.Client()

# Configure Gemini
genai.configure(api_key=os.environ['GEMINI_API'])
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 512,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

PROMPT = """Analyze the image and provide a short, concise title followed by a detailed description.
Respond in JSON format:  
{
  "title": "<A meaningful, short title>",
  "description": "<A clear and accurate description>"
}"""

@app.route('/')
def home():
    html = f"""
    <html>
    <head>
        <title>Upload Image</title>
    </head>
    <body style="background-color:{background_color}; text-align:center;">
        <h1>Upload an Image</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="form_file" accept="image/*" required><br><br>
            <button>Upload</button>
        </form>
        <h2>Uploaded Files</h2>
        <ul>
    """
    try:
        all_files = get_list_of_files()
        if not all_files:
            html += "<li>No files found in the bucket.</li>"
        else:
            for blob_name in all_files:
                print("DEBUG: Processing blob_name:", repr(blob_name), "type:", type(blob_name))
                if not isinstance(blob_name, str):
                    print("ERROR: Skipping non-string blob:", blob_name)
                    continue
                if not blob_name.endswith('.json'):
                    html += f'<li><a href="/files/{blob_name}" target="_blank">{blob_name}</a></li>'
    except google.cloud.exceptions.NotFound as e:
        html += f"<li>Error: Bucket '{bucket_name}' not found: {str(e)}</li>"
        print("ERROR: Bucket not found:", str(e))
    except google.cloud.exceptions.Forbidden as e:
        html += f"<li>Error: Permission denied accessing bucket '{bucket_name}': {str(e)}</li>"
        print("ERROR: Permission denied:", str(e))
    except Exception as e:
        html += f"<li>Error fetching files: {str(e)}</li>"
        print("ERROR in home():", str(e))

    html += "</ul></body></html>"
    return html

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files.get('form_file')
    if not file:
        return "No file uploaded.", 400

    filename = file.filename
    try:
        local_file_path = upload_file(file)
        generate_description_and_caption(filename)
        return redirect("/")
    except Exception as e:
        print("Error during upload or AI processing:", e)
        return f"Error during upload or AI processing: {str(e)}", 500

@app.route('/files/<filename>')
def view_file(filename):
    json_filename = f"{filename.rsplit('.', 1)[0]}.json"
    try:
        ai_response = get_ai_response(json_filename)
    except Exception as e:
        return f"Error fetching AI response: {str(e)}", 500

    return render_template("view_image.html", filename=filename, ai_response=ai_response, bucket_name=bucket_name)

def get_list_of_files():
    file_list = []
    print("DEBUG: Listing blobs in bucket:", bucket_name)
    try:
        bucket = storage_client.bucket(bucket_name)
        blobs = list(bucket.list_blobs())
        print("DEBUG: Converted to list. Length:", len(blobs))

        for i, blob in enumerate(blobs):
            print(f"[DEBUG] Blob #{i} type: {type(blob)} name: {blob.name}")
            if hasattr(blob, 'name') and isinstance(blob.name, str):
                file_list.append(blob.name)
    except Exception as e:
        print("ERROR: Failed to list blobs in bucket:", str(e))
        raise
    return file_list

def upload_file(file):
    local_folder = os.path.join(".", "uploads")
    os.makedirs(local_folder, exist_ok=True)
    local_file_path = os.path.join(local_folder, file.filename)
    file.save(local_file_path)
    print("Saved file locally:", local_file_path)

    blob = storage_client.bucket(bucket_name).blob(file.filename)
    blob.upload_from_filename(local_file_path)
    print("Uploaded file to GCS:", file.filename)

    return local_file_path

def generate_description_and_caption(filename):
    local_file_path = os.path.join("./uploads", filename)
    try:
        with open(local_file_path, "rb") as f:
            image_data = f.read()

        response = model.generate_content([
            {"mime_type": "image/jpeg", "data": image_data},
            "\n\n",
            PROMPT
        ])

        print("DEBUG: Gemini raw response:", repr(response.text))

        title = "Untitled"
        description = "No description available."

        try:
            parsed = json.loads(response.text)
            if isinstance(parsed, dict) and "title" in parsed and "description" in parsed:
                title = parsed["title"]
                description = parsed["description"]
            else:
                print("ERROR: AI response is not a dictionary or missing keys. Fallback.")
                description = str(parsed)
        except json.JSONDecodeError as e:
            print("ERROR: Failed to parse Gemini JSON:", str(e))
            description = response.text.strip()

        json_data = {"title": title, "description": description}
        json_filename = f"{filename.rsplit('.', 1)[0]}.json"
        blob = storage_client.bucket(bucket_name).blob(json_filename)
        blob.upload_from_string(json.dumps(json_data), content_type='application/json')

        print("Generated JSON and uploaded:", json_filename)
    except Exception as e:
        print("Error generating description for", filename, ":", e)
        raise

def get_ai_response(json_filename):
    try:
        blob = storage_client.bucket(bucket_name).blob(json_filename)
        raw = blob.download_as_text()
        print("DEBUG: Raw JSON from GCS:", repr(raw))

        try:
            ai_data = json.loads(raw)
            if not isinstance(ai_data, dict):
                print("ERROR: AI response is not a dictionary. Using fallback.")
                return {"title": "Untitled", "description": raw.strip()}
        except json.JSONDecodeError:
            print("ERROR: Failed to parse AI response as JSON.")
            return {"title": "Untitled", "description": raw.strip()}

        return ai_data
    except Exception as e:
        print("ERROR: Fetching AI response from GCS:", e)
        return {"title": "Untitled", "description": "Error fetching AI response."}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
