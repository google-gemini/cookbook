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
    def test_embed_content(self):
        # [START embed_content]
        import google.generativeai as genai

        text = "Hello World!"
        result = genai.embed_content(
            model="models/text-embedding-004", content=text, output_dimensionality=10
        )
        print(result["embedding"])
        # [END embed_content]

    def batch_embed_contents(self):
        # [START batch_embed_contents]
        import google.generativeai as genai

        texts = [
            "What is the meaning of life?",
            "How much wood would a woodchuck chuck?",
            "How does the brain work?",
        ]
        result = genai.embed_content(
            model="models/text-embedding-004", content=texts, output_dimensionality=10
        )
        print(result)
        # [END batch_embed_contents]


if __name__ == "__main__":
    absltest.main()
