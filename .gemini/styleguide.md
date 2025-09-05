# Gemini Cookbook Python notebooks Style Guide

# Introduction
This style guide outlines the coding conventions for Python notebooks developped by the Gemini team.
It's based on PEP 8, but with some modifications to address specific needs and
preferences within our organization.

This guide is mostly about the python content and the notebook, but don't forget to also review the markdown files. In particular, any new notebook should be referenced in the corresponding readmes (at folder level at least, and potentially the one on higer levels).

# Key Principles
* **Readability:** Code should be easy to understand for all developers. Since they are notebooks and aimed at teaching
  how to use Gemini and its API/SDK, the focus should be on writting didactic and easy-to-read code while limiting the
  back and forth with the documentation or within the notebook.
* **Maintainability:** Code should be easy to modify and extend. In particular it must be easy to switch the models used.
* **Consistency:** Adhering to a consistent style across all projects improves
  collaboration and reduces errors. Similar codes (like getting the api key from the secret, initializing the client or
  selecting a model) should always be the same so it's easier for the reader to go directly to the specific content.
* **Performance:** While readability is paramount, code should be efficient
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: GEMINI_API_KEY' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'

