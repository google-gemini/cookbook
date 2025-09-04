# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google import genai
import os
from dotenv import load_dotenv

def upload_file(client, file_path, display_name):
    """Uploads a file to the client.files API."""
    with open(file_path, "rb") as f:
        file_response = client.files.upload(
            file=f,
            config={
                "mime_type": "image/png",
                "display_name": display_name
            }
        )
    print(f"Uploaded file {file_response.display_name} as: {file_response.uri}")
    return file_response

def get_file(client, file_name):
    """Retrieves a file from the client.files API."""
    get_file_response = client.files.get(name=file_name)
    print(f"Retrieved file {get_file_response.display_name} as: {get_file_response.uri}")
    return get_file_response

def generate_content(client, model_name, prompt, file_response):
    """Generates content using the client.models API."""
    response = client.models.generate_content(
        model=model_name,
        contents=[
            prompt,
            file_response
        ]
    )
    print(response.text)
    return response

def delete_file(client, file_name):
    """Deletes a file from the client.files API."""
    client.files.delete(name=file_name)
    print(f"Deleted file with name {file_name}")

def main():
    """Main function to run the sample."""
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    # Initialize Google API Client
    client = genai.Client(api_key=api_key)

    # File to upload
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "sample_data/gemini_logo.png")
    display_name = "Gemini Logo"

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File not found at {file_path}. Creating a dummy file.")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("dummy content")

    # Upload the file
    file_response = upload_file(client, file_path, display_name)

    # Get the file
    if file_response:
        get_file(client, file_response.name)

        # Generate content
        prompt = "Describe the image with a creative description"
        model_name = "gemini-2.0-flash"
        generate_content(client, model_name, prompt, file_response)

        # Delete the file
        delete_file(client, file_response.name)


if __name__ == "__main__":
    main()
