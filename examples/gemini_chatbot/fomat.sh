#!/bin/bash
# Copyright 2025 Google LLC.
#
# @title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Install the formatter and linter
pip install -U tensorflow-docs

# Format all notebooks in the folder
python -m tensorflow_docs.tools.nbfmt ./gemini_chatbot.ipynb

# Lint all notebooks in the folder
python -m tensorflow_docs.tools.nblint \
  --styles=google,tensorflow \
  --arg=repo:MaryamZahiri/cookbook \
  --arg=branch:add-gemini-chatbot-quickstart \
  --arg=base_url:https://ai.google.dev/ \
  --exclude_lint=tensorflow::button_colab \
  --exclude_lint=tensorflow::button_github \
  --exclude_lint=tensorflow::button_download \
  --exclude_lint=tensorflow::button_website \
  ./gemini_chatbot.ipynb

# chmod +x ./gemini_chatbot.ipynb
# ./format.sh