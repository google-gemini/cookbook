import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import importlib

# Add the root of the repo to the path to allow importing quickstarts.file_api.sample
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now we can import the module
from quickstarts.file_api import sample

class TestSample(unittest.TestCase):

    def setUp(self):
        # Create a dummy image file
        os.makedirs("quickstarts/file_api/sample_data", exist_ok=True)
        with open("quickstarts/file_api/sample_data/gemini_logo.png", "w") as f:
            f.write("dummy image data")

        # Create a dummy .env file.
        with open("quickstarts/file_api/.env", "w") as f:
            f.write("GOOGLE_API_KEY=test_api_key")

    def tearDown(self):
        # Remove the dummy files and directory
        os.remove("quickstarts/file_api/sample_data/gemini_logo.png")
        os.rmdir("quickstarts/file_api/sample_data")
        os.remove("quickstarts/file_api/.env")

    @patch('quickstarts.file_api.sample.genai.Client')
    @patch('quickstarts.file_api.sample.Part')
    def test_main(self, mock_part, mock_client):
        # Mock the API calls
        mock_part.from_uri.return_value = MagicMock()
        mock_client.return_value.models.generate_content.return_value = MagicMock(text="A creative description of the image.")

        # Change to the script's directory before running the main function
        original_cwd = os.getcwd()
        os.chdir('quickstarts/file_api')

        sample.main()

        os.chdir(original_cwd)

        # Assert that the Part.from_uri method was called
        mock_part.from_uri.assert_called_once_with(file_uri="sample_data/gemini_logo.png", mime_type="image/png")

        # Assert that the Client was instantiated
        mock_client.assert_called_once()

        # Assert that the generate_content method was called
        mock_client.return_value.models.generate_content.assert_called_once()


if __name__ == '__main__':
    unittest.main()
