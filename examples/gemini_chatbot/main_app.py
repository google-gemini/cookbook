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

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

class GeminiChatbot:
    def __init__(self):
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        load_dotenv()
        # Set up Gemini API
        genai.configure(api_key=self.API_KEY)

    def app(self):
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

        st.title("🤖 Gemini Chatbot")

        user_input = st.text_input("Ask me anything...")

        if user_input:
            with st.spinner("Thinking..."):
                response = model.generate_content(user_input)
                st.success(response.text)

if __name__ == "__main__":
    chatbot = GeminiChatbot()
    chatbot.app()
# streamlit run app.py --server.port 8501 --server.address