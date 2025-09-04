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

import google.genai as genai
from google.genai.types import Part
import os
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    # The client library automatically picks up the API key from the environment variable GOOGLE_API_KEY.

    client = genai.Client()

    # Create a Part object from the image file
    file_path = "sample_data/gemini_logo.png"
    sample_file = Part.from_uri(
        file_uri=file_path,
        mime_type="image/png"
    )

    # Generate content using the client.models API
    prompt = "Describe the image with a creative description"
    model_name = "gemini-1.5-flash"
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, sample_file]
    )
    print(response.text)

if __name__ == "__main__":
    main()
