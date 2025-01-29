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
    def test_tokens_context_window(self):
        # [START tokens_context_window]
        import google.generativeai as genai

        model_info = genai.get_model("models/gemini-1.5-flash")

        # Returns the "context window" for the model,
        # which is the combined input and output token limits.
        print(f"{model_info.input_token_limit=}")
        print(f"{model_info.output_token_limit=}")
        # ( input_token_limit=30720, output_token_limit=2048 )
        # [END tokens_context_window]

    def test_tokens_text_only(self):
        # [START tokens_text_only]
        import google.generativeai as genai

        model = genai.GenerativeModel("models/gemini-1.5-flash")

        prompt = "The quick brown fox jumps over the lazy dog."

        # Call `count_tokens` to get the input token count (`total_tokens`).
        print("total_tokens: ", model.count_tokens(prompt))
        # ( total_tokens: 10 )

        response = model.generate_content(prompt)

        # On the response for `generate_content`, use `usage_metadata`
        # to get separate input and output token counts
        # (`prompt_token_count` and `candidates_token_count`, respectively),
        # as well as the combined token count (`total_token_count`).
        print(response.usage_metadata)
        # ( prompt_token_count: 11, candidates_token_count: 73, total_token_count: 84 )
        # [END tokens_text_only]

    def test_tokens_chat(self):
        # [START tokens_chat]
        import google.generativeai as genai

        model = genai.GenerativeModel("models/gemini-1.5-flash")

        chat = model.start_chat(
            history=[
                {"role": "user", "parts": "Hi my name is Bob"},
                {"role": "model", "parts": "Hi Bob!"},
            ]
        )
        # Call `count_tokens` to get the input token count (`total_tokens`).
        print(model.count_tokens(chat.history))
        # ( total_tokens: 10 )

        response = chat.send_message(
            "In one sentence, explain how a computer works to a young child."
        )

        # On the response for `send_message`, use `usage_metadata`
        # to get separate input and output token counts
        # (`prompt_token_count` and `candidates_token_count`, respectively),
        # as well as the combined token count (`total_token_count`).
        print(response.usage_metadata)
        # ( prompt_token_count: 25, candidates_token_count: 21, total_token_count: 46 )

        from google.generativeai.types.content_types import to_contents

        # You can call `count_tokens` on the combined history and content of the next turn.
        print(model.count_tokens(chat.history + to_contents("What is the meaning of life?")))
        # ( total_tokens: 56 )
        # [END tokens_chat]

    def test_tokens_multimodal_image_inline(self):
        # [START tokens_multimodal_image_inline]
        import google.generativeai as genai

        import PIL.Image

        model = genai.GenerativeModel("models/gemini-1.5-flash")

        prompt = "Tell me about this image"
        your_image_file = PIL.Image.open(media / "organ.jpg")

        # Call `count_tokens` to get the input token count
        # of the combined text and file (`total_tokens`).
        # An image's display or file size does not affect its token count.
        # Optionally, you can call `count_tokens` for the text and file separately.
        print(model.count_tokens([prompt, your_image_file]))
        # ( total_tokens: 263 )

        response = model.generate_content([prompt, your_image_file])

        # On the response for `generate_content`, use `usage_metadata`
        # to get separate input and output token counts
        # (`prompt_token_count` and `candidates_token_count`, respectively),
        # as well as the combined token count (`total_token_count`).
        print(response.usage_metadata)
        # ( prompt_token_count: 264, candidates_token_count: 80, total_token_count: 345 )
        # [END tokens_multimodal_image_inline]

    def test_tokens_multimodal_image_file_api(self):
        # [START tokens_multimodal_image_file_api]
        import google.generativeai as genai

        model = genai.GenerativeModel("models/gemini-1.5-flash")

        prompt = "Tell me about this image"
        your_image_file = genai.upload_file(path=media / "organ.jpg")

        # Call `count_tokens` to get the input token count
        # of the combined text and file (`total_tokens`).
        # An image's display or file size does not affect its token count.
        # Optionally, you can call `count_tokens` for the text and file separately.
        print(model.count_tokens([prompt, your_image_file]))
        # ( total_tokens: 263 )

        response = model.generate_content([prompt, your_image_file])
        response.text
        # On the response for `generate_content`, use `usage_metadata`
        # to get separate input and output token counts
        # (`prompt_token_count` and `candidates_token_count`, respectively),
        # as well as the combined token count (`total_token_count`).
        print(response.usage_metadata)
        # ( prompt_token_count: 264, candidates_token_count: 80, total_token_count: 345 )
        # [END tokens_multimodal_image_file_api]

    def test_tokens_multimodal_video_audio_file_api(self):
        # [START tokens_multimodal_video_audio_file_api]
        import google.generativeai as genai

        import time

        model = genai.GenerativeModel("models/gemini-1.5-flash")

        prompt = "Tell me about this video"
        your_file = genai.upload_file(path=media / "Big_Buck_Bunny.mp4")

        # Videos need to be processed before you can use them.
        while your_file.state.name == "PROCESSING":
            print("processing video...")
            time.sleep(5)
            your_file = genai.get_file(your_file.name)

        # Call `count_tokens` to get the input token count
        # of the combined text and video/audio file (`total_tokens`).
        # A video or audio file is converted to tokens at a fixed rate of tokens per second.
        # Optionally, you can call `count_tokens` for the text and file separately.
        print(model.count_tokens([prompt, your_file]))
        # ( total_tokens: 300 )

        response = model.generate_content([prompt, your_file])

        # On the response for `generate_content`, use `usage_metadata`
        # to get separate input and output token counts
        # (`prompt_token_count` and `candidates_token_count`, respectively),
        # as well as the combined token count (`total_token_count`).
        print(response.usage_metadata)
        # ( prompt_token_count: 301, candidates_token_count: 60, total_token_count: 361 )

        # [END tokens_multimodal_video_audio_file_api]

    def test_tokens_multimodal_pdf_file_api(self):
        # [START tokens_multimodal_pdf_file_api]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_pdf = genai.upload_file(media / "test.pdf")
        token_count = model.count_tokens(["Give me a summary of this document.", sample_pdf])
        print(f"{token_count=}")

        response = model.generate_content(["Give me a summary of this document.", sample_pdf])
        print(response.usage_metadata)
        # [END tokens_multimodal_pdf_file_api]

    def test_tokens_cached_content(self):
        # [START tokens_cached_content]
        import google.generativeai as genai

        import time

        model = genai.GenerativeModel("models/gemini-1.5-flash")

        your_file = genai.upload_file(path=media / "a11.txt")

        cache = genai.caching.CachedContent.create(
            model="models/gemini-1.5-flash-001",
            # You can set the system_instruction and tools
            system_instruction=None,
            tools=None,
            contents=["Here the Apollo 11 transcript:", your_file],
        )

        model = genai.GenerativeModel.from_cached_content(cache)

        prompt = "Please give a short summary of this file."

        # Call `count_tokens` to get input token count
        # of the combined text and file (`total_tokens`).
        # A video or audio file is converted to tokens at a fixed rate of tokens per second.
        # Optionally, you can call `count_tokens` for the text and file separately.
        print(model.count_tokens(prompt))
        # ( total_tokens: 9 )

        response = model.generate_content(prompt)

        # On the response for `generate_content`, use `usage_metadata`
        # to get separate input and output token counts
        # (`prompt_token_count` and `candidates_token_count`, respectively),
        # as well as the cached content token count and the combined total token count.
        print(response.usage_metadata)
        # ( prompt_token_count: 323393, cached_content_token_count: 323383, candidates_token_count: 64)
        # ( total_token_count: 323457 )

        cache.delete()
        # [END tokens_cached_content]

    def test_tokens_system_instruction(self):
        # [START tokens_system_instruction]
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        prompt = "The quick brown fox jumps over the lazy dog."

        print(model.count_tokens(prompt))
        # total_tokens: 10

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", system_instruction="You are a cat. Your name is Neko."
        )

        # The total token count includes everything sent to the `generate_content` request.
        # When you use system instructions, the total token count increases.
        print(model.count_tokens(prompt))
        # ( total_tokens: 21 )
        # [END tokens_system_instruction]

    def test_tokens_tools(self):
        # [START tokens_tools]
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        prompt = "I have 57 cats, each owns 44 mittens, how many mittens is that in total?"

        print(model.count_tokens(prompt))
        # ( total_tokens: 22 )

        def add(a: float, b: float):
            """returns a + b."""
            return a + b

        def subtract(a: float, b: float):
            """returns a - b."""
            return a - b

        def multiply(a: float, b: float):
            """returns a * b."""
            return a * b

        def divide(a: float, b: float):
            """returns a / b."""
            return a / b

        model = genai.GenerativeModel(
            "models/gemini-1.5-flash-001", tools=[add, subtract, multiply, divide]
        )

        # The total token count includes everything sent to the `generate_content` request.
        # When you use tools (like function calling), the total token count increases.
        print(model.count_tokens(prompt))
        # ( total_tokens: 206 )
        # [END tokens_tools]


if __name__ == "__main__":
    absltest.main()
