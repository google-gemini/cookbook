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

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]

# Initialize Google API Client
genai.configure(api_key=api_key)

# Prepare file to upload to GenAI File API
file_path = "sample_data/gemini_logo.png"
display_name = "Gemini Logo"
file_response = genai.upload_file(path=file_path, display_name=display_name)
print(f"Uploaded file {file_response.display_name} as: {file_response.uri}")

# Verify the file is uploaded to the API
get_file = genai.get_file(name=file_response.name)
print(f"Retrieved file {get_file.display_name} as: {get_file.uri}")

# Make Gemini 1.5 API LLM call
prompt = "Describe the image with a creative description"
model_name = "models/gemini-2.0-flash"
model = genai.GenerativeModel(model_name=model_name)
response = model.generate_content([prompt, file_response])
print(response)

# Delete the sample file
genai.delete_file(name=file_response.name)
print(f"Deleted file {file_response.display_name}")
