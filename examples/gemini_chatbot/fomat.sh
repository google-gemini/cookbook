#!/bin/bash

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