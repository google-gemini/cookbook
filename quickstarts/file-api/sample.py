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

# Load environment variables from .env file
load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]

# Initialize Google API Client
client=genai.Client(api_key=api_key)

# Upload a sample file to the client.files API
file_path = "/content/image.png"
display_name = "Gemini Logo"
file_response = client.files.upload(
    file=open(file_path, "rb"),
    config={
        "mime_type":"image/png",
        "display_name":display_name
    }
)
print(f"Uploaded file {file_response.display_name} as: {file_response.uri}")

# Retrieve the uploaded file from the client.files.get
get_file =client.files.get(name=file_response.name)
print(f"Retrieved file {get_file.display_name} as: {get_file.uri}")

# Generate content using the client.models API
prompt = "Describe the image with a creative description"
model_name = "gemini-2.0-flash"
response = client.models.generate_content(
    model=model_name,
    contents=[
      prompt,
      file_response
    ]
)
print(response.text)

# Delete the sample file
client.files.delete(name=file_response.name)
print(f"Deleted file {file_response.display_name}")
