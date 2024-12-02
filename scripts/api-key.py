import os

def update_ipynb_files(directory):
  """
  Updates all .ipynb files in the given directory and its subdirectories recursively, 
  replacing the specified text.

  Args:
    directory: The root directory to start the search.
  """
  for root, _, files in os.walk(directory):
    for filename in files:
      if filename.endswith(".ipynb"):
        filepath = os.path.join(root, filename)
        with open(filepath, 'r') as f:
          content = f.read()

        old1_text = "from google.colab import userdata"
        old2_text = "GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')"
        old3_text = r'userdata.get(\"GOOGLE_API_KEY\")'
        old4_text = "userdata.get('GOOGLE_API_KEY')"
        new1_text = "import os"
        new2_text = "GOOGLE_API_KEY=os.environ['GOOGLE_API_KEY']"
        new3_text = "os.environ['GOOGLE_API_KEY']"
        updated_content = content.replace(old1_text, new1_text)
        updated_content = updated_content.replace(old2_text, new2_text)
        updated_content = updated_content.replace(old3_text, new3_text)
        updated_content = updated_content.replace(old4_text, new3_text)

        with open(filepath, 'w') as f:
          f.write(updated_content)

if __name__ == "__main__":
  directory = "."
  update_ipynb_files(directory)