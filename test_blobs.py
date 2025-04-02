from google.cloud import storage

bucket_name = "pr1images-bucket"
storage_client = storage.Client()

def test_blobs():
    print("Testing blob list...")
    try:
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()

        for i, blob in enumerate(blobs):
            print(f"[{i}] type: {type(blob)} | content: {blob}")
            if hasattr(blob, 'name'):
                print(f"     name: {blob.name}")
            else:
                print("     NO name attribute!")
    except Exception as e:
        print("Error listing blobs:", e)

if __name__ == "__main__":
    test_blobs()
