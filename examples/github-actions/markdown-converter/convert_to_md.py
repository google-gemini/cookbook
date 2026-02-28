# -*- coding: utf-8 -*-
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

import os
from google import genai


def convert_to_markdown(text_content,api_key):

   
    client = genai.Client(api_key = api_key)

    

    MODEL_ID = "gemini-2.5-flash" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"] {"allow-input":true, isTemplate: true}

    
    prompt = f"""
        Convert the following text into well-structured Markdown format suitable for GitHub documentation.
        Use appropriate headings (#, ##, ###), lists, code blocks, and bold/italic formatting.
        Ensure the output is clean and directly usable in a .md code don't include (```Markdown ````).

        Text to convert:
        {text_content}
    """
    
    try:
    
        response = client.models.generate_content(
            model = MODEL_ID,
            contents = prompt
        )
        
      
        return response.text
    except Exception as e:
        print(f"An error occurred during content generation: {e}")
        return ""

def main():

  
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        exit(1)

    input_file = "source.txt"  # You can change this to your input file
    output_file = "README.md"  # You can change this to your desired output file


    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        exit(1)

    with open(input_file, "r") as f:
        text_content = f.read()

    markdown_content = convert_to_markdown(text_content, api_key)

    if markdown_content:
       
        with open(output_file, "w") as f:
            f.write(markdown_content)
        print(f"Successfully converted '{input_file}' to '{output_file}'.")
    else:
        print("Markdown conversion failed.")

if __name__ == "__main__":
    main()