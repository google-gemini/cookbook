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
    def test_models_list(self):
        # [START models_list]
        import google.generativeai as genai

        print("List of models that support generateContent:\n")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)

        print("List of models that support embedContent:\n")
        for m in genai.list_models():
            if "embedContent" in m.supported_generation_methods:
                print(m.name)
        # [END models_list]

    def test_models_get(self):
        # [START models_get]
        import google.generativeai as genai

        model_info = genai.get_model("models/gemini-1.5-flash-latest")
        print(model_info)
        # [END models_get]


if __name__ == "__main__":
    absltest.main()
