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
    def test_code_execution_basic(self):
        # [START code_execution_basic]
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools="code_execution")
        response = model.generate_content(
            (
                "What is the sum of the first 50 prime numbers? "
                "Generate and run code for the calculation, and make sure you get all 50."
            )
        )

        # Each `part` either contains `text`, `executable_code` or an `execution_result`
        for part in response.candidates[0].content.parts:
            print(part, "\n")

        print("-" * 80)
        # The `.text` accessor joins the parts into a markdown compatible text representation.
        print("\n\n", response.text)
        # [END code_execution_basic]

        # [START code_execution_basic_return]
        import google.generativeai as genai

        # text: "I can help with that! To calculate the sum of the first 50 prime numbers, we\'ll need to first identify all the prime numbers up to the 50th prime number. \n\nHere is the code to find and sum the first 50 prime numbers:\n\n"
        #
        # executable_code {
        #   language: PYTHON
        #   code: "\ndef is_prime(n):\n    \"\"\"\n    Checks if a number is prime.\n    \"\"\"\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprime_count = 0\nnumber = 2\nprimes = []\nwhile prime_count < 50:\n    if is_prime(number):\n        primes.append(number)\n        prime_count += 1\n    number += 1\n\nprint(f\'The sum of the first 50 prime numbers is: {sum(primes)}\')\n"
        # }
        #
        # code_execution_result {
        #   outcome: OUTCOME_OK
        #   output: "The sum of the first 50 prime numbers is: 5117\n"
        # }
        #
        # text: "I ran the code and it calculated that the sum of the first 50 prime numbers is 5117. \n"
        #
        #
        # --------------------------------------------------------------------------------
        # I can help with that! To calculate the sum of the first 50 prime numbers, we'll need to first identify all the prime numbers up to the 50th prime number.
        #
        # Here is the code to find and sum the first 50 prime numbers:
        #
        #
        # ``` python
        # def is_prime(n):
        #     """
        #     Checks if a number is prime.
        #     """
        #     if n <= 1:
        #         return False
        #     for i in range(2, int(n**0.5) + 1):
        #         if n % i == 0:
        #             return False
        #     return True
        #
        # prime_count = 0
        # number = 2
        # primes = []
        # while prime_count < 50:
        #     if is_prime(number):
        #         primes.append(number)
        #         prime_count += 1
        #     number += 1
        #
        # print(f'The sum of the first 50 prime numbers is: {sum(primes)}')
        #
        # ```
        # ```
        # The sum of the first 50 prime numbers is: 5117
        #
        # ```
        # I ran the code and it calculated that the sum of the first 50 prime numbers is 5117.
        # [END code_execution_basic_return]

    def test_code_execution_request_override(self):
        # [START code_execution_request_override]
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(
            (
                "What is the sum of the first 50 prime numbers? "
                "Generate and run code for the calculation, and make sure you get all 50."
            ),
            tools="code_execution",
        )
        print(response.text)
        # [END code_execution_request_override]
        # [START code_execution_request_override_return]
        import google.generativeai as genai

        # ``` python
        # def is_prime(n):
        #     """
        #     Checks if a number is prime.
        #     """
        #     if n <= 1:
        #         return False
        #     for i in range(2, int(n**0.5) + 1):
        #         if n % i == 0:
        #             return False
        #     return True
        #
        # primes = []
        # num = 2
        # count = 0
        # while count < 50:
        #     if is_prime(num):
        #         primes.append(num)
        #         count += 1
        #     num += 1
        #
        # print(f'The first 50 prime numbers are: {primes}')
        # print(f'The sum of the first 50 prime numbers is: {sum(primes)}')
        #
        # ```
        # ```
        # The first 50 prime numbers are: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]
        # The sum of the first 50 prime numbers is: 5117
        #
        # ```
        # The code generated a list of the first 50 prime numbers, then sums the list to find the answer.
        #
        # The sum of the first 50 prime numbers is **5117**.
        # [END code_execution_request_override_return]

    def test_code_execution_chat(self):
        # [START code_execution_chat]
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools="code_execution")
        chat = model.start_chat()
        response = chat.send_message('Can you print "Hello world!"?')
        response = chat.send_message(
            (
                "What is the sum of the first 50 prime numbers? "
                "Generate and run code for the calculation, and make sure you get all 50."
            )
        )
        print(response.text)
        # [END code_execution_chat]
        # [START code_execution_chat_return]
        import google.generativeai as genai

        # ``` python
        # def is_prime(n):
        #     """
        #     Checks if a number is prime.
        #     """
        #     if n <= 1:
        #         return False
        #     for i in range(2, int(n**0.5) + 1):
        #         if n % i == 0:
        #             return False
        #     return True
        #
        # primes = []
        # num = 2
        # count = 0
        # while count < 50:
        #     if is_prime(num):
        #         primes.append(num)
        #         count += 1
        #     num += 1
        #
        # print(f'The first 50 prime numbers are: {primes}')
        # print(f'The sum of the first 50 prime numbers is: {sum(primes)}')
        #
        # ```
        # ```
        # The first 50 prime numbers are: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]
        # The sum of the first 50 prime numbers is: 5117
        #
        # ```
        # The code generated a list of the first 50 prime numbers, then sums the list to find the answer.
        #
        # The sum of the first 50 prime numbers is **5117**.
        # [END code_execution_chat_return]


if __name__ == "__main__":
    absltest.main()
