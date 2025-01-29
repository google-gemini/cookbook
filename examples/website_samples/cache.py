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
    def test_cache_create(self):
        # [START cache_create]
        import google.generativeai as genai

        document = genai.upload_file(path=media / "a11.txt")
        model_name = "gemini-1.5-flash-001"
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction="You are an expert analyzing transcripts.",
            contents=[document],
        )
        print(cache)

        model = genai.GenerativeModel.from_cached_content(cache)
        response = model.generate_content("Please summarize this transcript")
        print(response.text)
        # [END cache_create]
        cache.delete()

    def test_cache_create_from_name(self):
        # [START cache_create_from_name]
        import google.generativeai as genai

        document = genai.upload_file(path=media / "a11.txt")
        model_name = "gemini-1.5-flash-001"
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction="You are an expert analyzing transcripts.",
            contents=[document],
        )
        cache_name = cache.name  # Save the name for later

        # Later
        cache = genai.caching.CachedContent.get(cache_name)
        apollo_model = genai.GenerativeModel.from_cached_content(cache)
        response = apollo_model.generate_content("Find a lighthearted moment from this transcript")
        print(response.text)
        # [END cache_create_from_name]
        cache.delete()

    def test_cache_create_from_chat(self):
        # [START cache_create_from_chat]
        import google.generativeai as genai

        model_name = "gemini-1.5-flash-001"
        system_instruction = "You are an expert analyzing transcripts."

        model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
        chat = model.start_chat()
        document = genai.upload_file(path=media / "a11.txt")
        response = chat.send_message(["Hi, could you summarize this transcript?", document])
        print("\n\nmodel:  ", response.text)
        response = chat.send_message(
            ["Okay, could you tell me more about the trans-lunar injection"]
        )
        print("\n\nmodel:  ", response.text)

        # To cache the conversation so far, pass the chat history as the list of "contents".
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction=system_instruction,
            contents=chat.history,
        )
        model = genai.GenerativeModel.from_cached_content(cached_content=cache)

        # Continue the chat where you left off.
        chat = model.start_chat()
        response = chat.send_message(
            "I didn't understand that last part, could you explain it in simpler language?"
        )
        print("\n\nmodel:  ", response.text)
        # [END cache_create_from_chat]
        cache.delete()

    def test_cache_delete(self):
        # [START cache_delete]
        import google.generativeai as genai

        document = genai.upload_file(path=media / "a11.txt")
        model_name = "gemini-1.5-flash-001"
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction="You are an expert analyzing transcripts.",
            contents=[document],
        )
        cache.delete()
        # [END cache_delete]

    def test_cache_get(self):
        # [START cache_get]
        import google.generativeai as genai

        document = genai.upload_file(path=media / "a11.txt")
        model_name = "gemini-1.5-flash-001"
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction="You are an expert analyzing transcripts.",
            contents=[document],
        )
        print(genai.caching.CachedContent.get(name=cache.name))
        # [END cache_get]
        cache.delete()

    def test_cache_list(self):
        # [START cache_list]
        import google.generativeai as genai

        document = genai.upload_file(path=media / "a11.txt")
        model_name = "gemini-1.5-flash-001"
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction="You are an expert analyzing transcripts.",
            contents=[document],
        )
        print("My caches:")
        for c in genai.caching.CachedContent.list():
            print("    ", c.name)
        # [END cache_list]
        cache.delete()

    def test_cache_update(self):
        # [START cache_update]
        import google.generativeai as genai

        import datetime

        document = genai.upload_file(path=media / "a11.txt")
        model_name = "gemini-1.5-flash-001"
        cache = genai.caching.CachedContent.create(
            model=model_name,
            system_instruction="You are an expert analyzing transcripts.",
            contents=[document],
        )

        # You can update the ttl
        cache.update(ttl=datetime.timedelta(hours=2))
        print(f"After update:\n {cache}")

        # Or you can update the expire_time
        cache.update(expire_time=datetime.datetime.now() + datetime.timedelta(minutes=15))
        # [END cache_update]
        cache.delete()


if __name__ == "__main__":
    absltest.main()
