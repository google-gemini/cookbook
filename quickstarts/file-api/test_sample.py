import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

from sample import upload_file, get_file, generate_content, delete_file, main

class TestSample(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.mock_client = MagicMock()
        self.mock_file_response = MagicMock()
        self.mock_file_response.display_name = "Test File"
        self.mock_file_response.uri = "files/test-file-uri"
        self.mock_file_response.name = "files/test-file-name"

    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    def test_upload_file(self, mock_file_open):
        """Test the upload_file function."""
        self.mock_client.files.upload.return_value = self.mock_file_response

        file_path = "dummy_path/image.png"
        display_name = "Test File"

        response = upload_file(self.mock_client, file_path, display_name)

        mock_file_open.assert_called_once_with(file_path, "rb")
        self.mock_client.files.upload.assert_called_once()
        self.assertEqual(response, self.mock_file_response)

    def test_get_file(self):
        """Test the get_file function."""
        self.mock_client.files.get.return_value = self.mock_file_response

        file_name = "files/test-file-name"

        response = get_file(self.mock_client, file_name)

        self.mock_client.files.get.assert_called_once_with(name=file_name)
        self.assertEqual(response, self.mock_file_response)

    def test_generate_content(self):
        """Test the generate_content function."""
        mock_generate_content_response = MagicMock()
        mock_generate_content_response.text = "This is a creative description."
        self.mock_client.models.generate_content.return_value = mock_generate_content_response

        model_name = "gemini-2.0-flash"
        prompt = "Describe the image"

        response = generate_content(self.mock_client, model_name, prompt, self.mock_file_response)

        self.mock_client.models.generate_content.assert_called_once_with(
            model=model_name,
            contents=[prompt, self.mock_file_response]
        )
        self.assertEqual(response.text, "This is a creative description.")

    def test_delete_file(self):
        """Test the delete_file function."""
        file_name = "files/test-file-name"

        delete_file(self.mock_client, file_name)

        self.mock_client.files.delete.assert_called_once_with(name=file_name)

    @patch('sample.upload_file')
    @patch('sample.get_file')
    @patch('sample.generate_content')
    @patch('sample.delete_file')
    @patch('sample.genai.Client')
    @patch('sample.load_dotenv')
    @patch('os.path.exists', return_value=True)
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_api_key"})
    def test_main(self, mock_exists, mock_load_dotenv, mock_client_constructor, mock_delete, mock_generate, mock_get, mock_upload):
        """Test the main function."""
        mock_upload.return_value = self.mock_file_response
        mock_client = MagicMock()
        mock_client_constructor.return_value = mock_client

        main()

        mock_load_dotenv.assert_called_once()
        mock_client_constructor.assert_called_once_with(api_key="test_api_key")

        # Get the absolute path to the file that should be checked
        script_dir = os.path.dirname(os.path.abspath(__file__))
        expected_path = os.path.join(script_dir, "sample_data/gemini_logo.png")
        mock_exists.assert_called_once_with(expected_path)

        mock_upload.assert_called_once_with(mock_client, expected_path, "Gemini Logo")
        mock_get.assert_called_once_with(mock_client, self.mock_file_response.name)
        mock_generate.assert_called_once_with(mock_client, "gemini-2.0-flash", "Describe the image with a creative description", self.mock_file_response)
        mock_delete.assert_called_once_with(mock_client, self.mock_file_response.name)

if __name__ == '__main__':
    unittest.main()
