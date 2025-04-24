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