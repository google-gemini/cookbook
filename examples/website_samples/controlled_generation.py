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
    def test_json_controlled_generation(self):
        # [START json_controlled_generation]
        import google.generativeai as genai

        import typing_extensions as typing

        class Recipe(typing.TypedDict):
            recipe_name: str
            ingredients: list[str]

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        result = model.generate_content(
            "List a few popular cookie recipes.",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=list[Recipe]
            ),
        )
        print(result)
        # [END json_controlled_generation]

    def test_json_no_schema(self):
        # [START json_no_schema]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = """List a few popular cookie recipes in JSON format.

        Use this JSON schema:

        Recipe = {'recipe_name': str, 'ingredients': list[str]}
        Return: list[Recipe]"""
        result = model.generate_content(prompt)
        print(result)
        # [END json_no_schema]

    def test_json_enum(self):
        # [START json_enum]
        import google.generativeai as genai

        import enum

        class Choice(enum.Enum):
            PERCUSSION = "Percussion"
            STRING = "String"
            WOODWIND = "Woodwind"
            BRASS = "Brass"
            KEYBOARD = "Keyboard"

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        organ = genai.upload_file(media / "organ.jpg")
        result = model.generate_content(
            ["What kind of instrument is this:", organ],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=Choice
            ),
        )
        print(result)  # "Keyboard"
        # [END json_enum]

    def test_enum_in_json(self):
        # [START enum_in_json]
        import google.generativeai as genai

        import enum
        from typing_extensions import TypedDict

        class Grade(enum.Enum):
            A_PLUS = "a+"
            A = "a"
            B = "b"
            C = "c"
            D = "d"
            F = "f"

        class Recipe(TypedDict):
            recipe_name: str
            grade: Grade

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        result = model.generate_content(
            "List about 10 cookie recipes, grade them based on popularity",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=list[Recipe]
            ),
        )
        print(result)  # [{"grade": "a+", "recipe_name": "Chocolate Chip Cookies"}, ...]
        # [END enum_in_json]

    def test_json_enum_raw(self):
        # [START json_enum_raw]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        organ = genai.upload_file(media / "organ.jpg")
        result = model.generate_content(
            ["What kind of instrument is this:", organ],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "STRING",
                    "enum": ["Percussion", "String", "Woodwind", "Brass", "Keyboard"],
                },
            ),
        )
        print(result)  # "Keyboard"
        # [END json_enum_raw]

    def test_x_enum(self):
        # [START x_enum]
        import google.generativeai as genai

        import enum

        class Choice(enum.Enum):
            PERCUSSION = "Percussion"
            STRING = "String"
            WOODWIND = "Woodwind"
            BRASS = "Brass"
            KEYBOARD = "Keyboard"

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        organ = genai.upload_file(media / "organ.jpg")
        result = model.generate_content(
            ["What kind of instrument is this:", organ],
            generation_config=genai.GenerationConfig(
                response_mime_type="text/x.enum", response_schema=Choice
            ),
        )
        print(result)  # Keyboard
        # [END x_enum]

    def test_x_enum_raw(self):
        # [START x_enum_raw]
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        organ = genai.upload_file(media / "organ.jpg")
        result = model.generate_content(
            ["What kind of instrument is this:", organ],
            generation_config=genai.GenerationConfig(
                response_mime_type="text/x.enum",
                response_schema={
                    "type": "STRING",
                    "enum": ["Percussion", "String", "Woodwind", "Brass", "Keyboard"],
                },
            ),
        )
        print(result)  # Keyboard
        # [END x_enum_raw]


if __name__ == "__main__":
    absltest.main()
