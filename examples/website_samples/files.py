# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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
from absl.testing import absltest

import google
import pathlib

media = pathlib.Path(__file__).parents[1] / "third_party"


class UnitTests(absltest.TestCase):
    def test_files_create_text(self):
        # [START files_create_text]
        import google.generativeai as genai

        myfile = genai.upload_file(media / "poem.txt")
        print(f"{myfile=}")

        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [myfile, "\n\n", "Can you add a few more lines to this poem?"]
        )
        print(f"{result.text=}")
        # [END files_create_text]

    def test_files_create_image(self):
        # [START files_create_image]
        import google.generativeai as genai

        myfile = genai.upload_file(media / "Cajun_instruments.jpg")
        print(f"{myfile=}")

        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [myfile, "\n\n", "Can you tell me about the instruments in this photo?"]
        )
        print(f"{result.text=}")
        # [END files_create_image]

    def test_files_create_audio(self):
        # [START files_create_audio]
        import google.generativeai as genai

        myfile = genai.upload_file(media / "sample.mp3")
        print(f"{myfile=}")

        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content([myfile, "Describe this audio clip"])
        print(f"{result.text=}")
        # [END files_create_audio]

    def test_files_create_video(self):
        # [START files_create_video]
        import google.generativeai as genai

        import time

        # Video clip (CC BY 3.0) from https://peach.blender.org/download/
        myfile = genai.upload_file(media / "Big_Buck_Bunny.mp4")
        print(f"{myfile=}")

        # Videos need to be processed before you can use them.
        while myfile.state.name == "PROCESSING":
            print("processing video...")
            time.sleep(5)
            myfile = genai.get_file(myfile.name)

        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content([myfile, "Describe this video clip"])
        print(f"{result.text=}")
        # [END files_create_video]

    def test_files_create_pdf(self):
        # [START files_create_pdf]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_pdf = genai.upload_file(media / "test.pdf")
        response = model.generate_content(["Give me a summary of this pdf file.", sample_pdf])
        print(response.text)
        # [END files_create_pdf]

    def test_files_create_from_IO(self):
        # [START files_create_io]
        import google.generativeai as genai

        # You can pass a file-like object, instead of a path.
        # Useful for streaming.
        model = genai.GenerativeModel("gemini-1.5-flash")
        fpath = media / "test.pdf"
        with open(fpath, "rb") as f:
            sample_pdf = genai.upload_file(f, mime_type="application/pdf")
        response = model.generate_content(["Give me a summary of this pdf file.", sample_pdf])
        print(response.text)
        # [END files_create_io]

    def test_files_list(self):
        # [START files_list]
        import google.generativeai as genai

        print("My files:")
        for f in genai.list_files():
            print("  ", f.name)
        # [END files_list]

    def test_files_get(self):
        # [START files_get]
        import google.generativeai as genai

        myfile = genai.upload_file(media / "poem.txt")
        file_name = myfile.name
        print(file_name)  # "files/*"

        myfile = genai.get_file(file_name)
        print(myfile)
        # [END files_get]

    def test_files_delete(self):
        # [START files_delete]
        import google.generativeai as genai

        myfile = genai.upload_file(media / "poem.txt")

        myfile.delete()

        try:
            # Error.
            model = genai.GenerativeModel("gemini-1.5-flash")
            result = model.generate_content([myfile, "Describe this file."])
        except google.api_core.exceptions.PermissionDenied:
            pass
        # [END files_delete]


if __name__ == "__main__":
    absltest.main()
