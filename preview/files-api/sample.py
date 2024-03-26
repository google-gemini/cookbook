import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import os
from dotenv import load_dotenv
import mimetypes

# Load environment variables from .env file
load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]
GENAI_DISCOVERY_URL = f"https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta&key={api_key}"

# Initialize Google API Client
discovery_docs = requests.get(GENAI_DISCOVERY_URL)
genai_service = googleapiclient.discovery.build_from_document(
    discovery_docs.content, developerKey=api_key)

# Prepare file to upload to GenAI File API
file_path = "sample_data/gemini_logo.png"
media = MediaFileUpload(file_path, mimetype=mimetypes.guess_type(file_path)[0])
body = {"file": {"displayName": "Gemini logo"}}

# Upload file
create_file_request = genai_service.media().upload(media_body=media, body=body)
create_file_response = create_file_request.execute()
file_uri = create_file_response["file"]["uri"]
file_mimetype = create_file_response["file"]["mimeType"]
print("Uploaded file: " + file_uri)

# Make Gemini 1.5 API LLM call
prompt = "Describe the image with a creative description"
model = "models/gemini-1.5-pro-latest"
contents = {"contents": [{ 
  "parts":[
    {"text": prompt},
    {"file_data": {"file_uri": file_uri, "mime_type": file_mimetype}}]
}]}
genai_request = genai_service.models().generateContent(
  model=model, body=contents)
print(genai_request.execute())
