<<<<<<< HEAD
<<<<<<< HEAD
# Use the official Python 3.10-slim image as a base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the local directory to the container's working directory
=======
# Use the official Python image as a base image
=======
# Use the official Python 3.10-slim image as a base image
>>>>>>> ae5a9f8 (Set up new repository, add .gitignore, and update app files)
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

<<<<<<< HEAD
# Copy the app files to the container
>>>>>>> f656d72 (Initial commit)
=======
# Copy all files from the local directory to the container's working directory
>>>>>>> ae5a9f8 (Set up new repository, add .gitignore, and update app files)
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
<<<<<<< HEAD
# Create the /app/files directory with proper permissions
RUN mkdir -p /app/files && chmod 777 /app/files

# Expose the port that Flask will run on
EXPOSE 8083

# Define a build argument for the API key
ARG GEMINI_API
# Set the environment variable.
ENV GEMINI_API=${GEMINI_API}

# Command to run the app with Gunicorn for production use
CMD ["gunicorn", "--bind", "0.0.0.0:8083", "main:app"]
=======
# Expose the port Flask will run on
EXPOSE 8080

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
>>>>>>> f656d72 (Initial commit)
=======
# Create the /app/files directory with proper permissions
RUN mkdir -p /app/files && chmod 777 /app/files

# Expose the port that Flask will run on
EXPOSE 8083

# Define a build argument for the API key
ARG GEMINI_API
# Set the environment variable.
ENV GEMINI_API=${GEMINI_API}

# Command to run the app with Gunicorn for production use
CMD ["gunicorn", "--bind", "0.0.0.0:8083", "main:app"]
>>>>>>> ae5a9f8 (Set up new repository, add .gitignore, and update app files)
