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

import pathlib

media = pathlib.Path(__file__).parents[1] / "third_party"


class UnitTests(absltest.TestCase):
    def test_text_gen_text_only_prompt(self):
        # [START text_gen_text_only_prompt]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Write a story about a magic backpack.")
        print(response.text)
        # [END text_gen_text_only_prompt]

    def test_text_gen_text_only_prompt_streaming(self):
        # [START text_gen_text_only_prompt_streaming]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Write a story about a magic backpack.", stream=True)
        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END text_gen_text_only_prompt_streaming]

    def test_text_gen_multimodal_one_image_prompt(self):
        # [START text_gen_multimodal_one_image_prompt]
        import google.generativeai as genai

        import PIL.Image

        model = genai.GenerativeModel("gemini-1.5-flash")
        organ = PIL.Image.open(media / "organ.jpg")
        response = model.generate_content(["Tell me about this instrument", organ])
        print(response.text)
        # [END text_gen_multimodal_one_image_prompt]

    def test_text_gen_multimodal_one_image_prompt_streaming(self):
        # [START text_gen_multimodal_one_image_prompt_streaming]
        import google.generativeai as genai

        import PIL.Image

        model = genai.GenerativeModel("gemini-1.5-flash")
        organ = PIL.Image.open(media / "organ.jpg")
        response = model.generate_content(["Tell me about this instrument", organ], stream=True)
        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END text_gen_multimodal_one_image_prompt_streaming]

    def test_text_gen_multimodal_multi_image_prompt(self):
        # [START text_gen_multimodal_multi_image_prompt]
        import google.generativeai as genai

        import PIL.Image

        model = genai.GenerativeModel("gemini-1.5-flash")
        organ = PIL.Image.open(media / "organ.jpg")
        cajun_instrument = PIL.Image.open(media / "Cajun_instruments.jpg")
        response = model.generate_content(
            ["What is the difference between both of these instruments?", organ, cajun_instrument]
        )
        print(response.text)
        # [END text_gen_multimodal_multi_image_prompt]

    def test_text_gen_multimodal_multi_image_prompt_streaming(self):
        # [START text_gen_multimodal_multi_image_prompt_streaming]
        import google.generativeai as genai

        import PIL.Image

        model = genai.GenerativeModel("gemini-1.5-flash")
        organ = PIL.Image.open(media / "organ.jpg")
        cajun_instrument = PIL.Image.open(media / "Cajun_instruments.jpg")
        response = model.generate_content(
            ["What is the difference between both of these instruments?", organ, cajun_instrument],
            stream=True,
        )
        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END text_gen_multimodal_multi_image_prompt_streaming]

    def test_text_gen_multimodal_audio(self):
        # [START text_gen_multimodal_audio]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_audio = genai.upload_file(media / "sample.mp3")
        response = model.generate_content(["Give me a summary of this audio file.", sample_audio])
        print(response.text)
        # [END text_gen_multimodal_audio]

    def test_text_gen_multimodal_audio_streaming(self):
        # [START text_gen_multimodal_audio_streaming]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_audio = genai.upload_file(media / "sample.mp3")
        response = model.generate_content(["Give me a summary of this audio file.", sample_audio])

        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END text_gen_multimodal_audio_streaming]

    def test_text_gen_multimodal_video_prompt(self):
        # [START text_gen_multimodal_video_prompt]
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
        response = model.generate_content([myfile, "Describe this video clip"])
        print(f"{response.text=}")
        # [END text_gen_multimodal_video_prompt]

    def test_text_gen_multimodal_video_prompt_streaming(self):
        # [START text_gen_multimodal_video_prompt_streaming]
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

        response = model.generate_content([myfile, "Describe this video clip"])
        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END text_gen_multimodal_video_prompt_streaming]

    def test_text_gen_multimodal_pdf(self):
        # [START text_gen_multimodal_pdf]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_pdf = genai.upload_file(media / "test.pdf")
        response = model.generate_content(["Give me a summary of this document:", sample_pdf])
        print(f"{response.text=}")
        # [END text_gen_multimodal_pdf]

    def test_text_gen_multimodal_pdf_streaming(self):
        # [START text_gen_multimodal_pdf_streaming]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_pdf = genai.upload_file(media / "test.pdf")
        response = model.generate_content(["Give me a summary of this document:", sample_pdf])

        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END text_gen_multimodal_pdf_streaming]


if __name__ == "__main__":
    absltest.main()
