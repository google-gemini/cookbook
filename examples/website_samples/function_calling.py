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


class UnitTests(absltest.TestCase):
    def test_function_calling(self):
        # [START function_calling]
        import google.generativeai as genai

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
            model_name="gemini-1.5-flash", tools=[add, subtract, multiply, divide]
        )
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(
            "I have 57 cats, each owns 44 mittens, how many mittens is that in total?"
        )
        print(response.text)
        # [END function_calling]


if __name__ == "__main__":
    absltest.main()
