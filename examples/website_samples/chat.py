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
    def test_chat(self):
        # [START chat]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(
            history=[
                {"role": "user", "parts": "Hello"},
                {"role": "model", "parts": "Great to meet you. What would you like to know?"},
            ]
        )
        response = chat.send_message("I have 2 dogs in my house.")
        print(response.text)
        response = chat.send_message("How many paws are in my house?")
        print(response.text)
        # [END chat]

    def test_chat_streaming(self):
        # [START chat_streaming]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(
            history=[
                {"role": "user", "parts": "Hello"},
                {"role": "model", "parts": "Great to meet you. What would you like to know?"},
            ]
        )
        response = chat.send_message("I have 2 dogs in my house.", stream=True)
        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        response = chat.send_message("How many paws are in my house?", stream=True)
        for chunk in response:
            print(chunk.text)
            print("_" * 80)

        print(chat.history)
        # [END chat_streaming]

    def test_chat_streaming_with_images(self):
        # [START chat_streaming_with_images]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat()

        response = chat.send_message(
            "Hello, I'm interested in learning about musical instruments. Can I show you one?",
            stream=True,
        )
        for chunk in response:
            print(chunk.text)  # Yes.
            print("_" * 80)

        organ = genai.upload_file(media / "organ.jpg")
        response = chat.send_message(
            ["What family of intruments does this instrument belong to?", organ], stream=True
        )
        for chunk in response:
            print(chunk.text)
            print("_" * 80)
        # [END chat_streaming_with_images]


if __name__ == "__main__":
    absltest.main()
