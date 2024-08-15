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
model_name = "models/gemini-1.5-pro-latest"
model = genai.GenerativeModel(model_name=model_name)
response = model.generate_content([prompt, file_response])
print(response)

# Delete the sample file
genai.delete_file(name=file_response.name)
print(f"Deleted file {file_response.display_name}")
