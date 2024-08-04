import os
from random import randint
from typing import Iterable
import google.generativeai as genai
from google.api_core import retry
import gradio as gr
import requests
from bs4 import BeautifulSoup

from google.colab import userdata
genai.configure(api_key=userdata.get('GOOGLE_API_KEY'))


# Replace these with your actual Google Custom Search API key and CX
GOOGLE_API_KEY = ''
GOOGLE_CX = ''


def google_search(query: str) -> str:
    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CX,
        'q': query
    }
    response = requests.get(url, params=params)
    search_results = response.json()
    
    # Check for error in response
    if 'error' in search_results:
        return f"Error: {search_results['error']['message']}"
    
    # Collect the top search results and their summaries
    top_results = []
    if 'items' in search_results:
        for item in search_results['items'][:1]:
            # Get the page content
            page_response = requests.get(item['link'])
            if page_response.status_code == 200:
                soup = BeautifulSoup(page_response.text, 'html.parser')
                # Extract text from the main body of the webpage or any other HTML elements as necessary
                page_text = soup.get_text()
                top_results.append(f"Title: {item['title']}\nLink: {item['link']}\npagetext: {page_text}\n")
            else:
                top_results.append(f"Title: {item['title']}\nLink: {item['link']}\npagetext: Could not retrieve the content.\n")
        return "\n".join(top_results)
    else:
        return "No results found."

GEMINI_PROMPT = """\You are the Gemini model from Google. Whenever the user requests anything that needs internet access please call google_search. 
Calling google_search will give you the latest results from the internet on the user query and you can use this information to respond to the user.
If confused always rely on google_search to get more accurate information.
"""
tools_to_call = [google_search]

# Toggle this to switch between Gemini 1.5 with a system instruction, or Gemini 1.0 Pro.
use_sys_inst = False

model_name = 'gemini-1.5-pro-latest' if use_sys_inst else 'gemini-1.0-pro-latest'

if use_sys_inst:
  model = genai.GenerativeModel(
      model_name, tools=tools_to_call, system_instruction=GEMINI_PROMPT)
  convo = model.start_chat(enable_automatic_function_calling=True)

else:
  model = genai.GenerativeModel(model_name, tools=google_search)
  convo = model.start_chat(
      history=[
          {'role': 'user', 'parts': [GEMINI_PROMPT]},
          {'role': 'model', 'parts': ['OK I understand. I will do my best!']}
        ],
      enable_automatic_function_calling=True)


@retry.Retry(initial=30)
def send_message(message):
  return convo.send_message(message)


# Assuming you have already defined the send_message function and placed_order
def gemini_with_internet(user_input):
    response = send_message(user_input)
    return response.text

# Create a Gradio interface
iface = gr.Interface(
    fn=gemini_with_internet,  # function to call
    inputs="text",  # input type
    outputs="text",  # output type
    title="Gemini with Internet Access",
    description="Interact with the Gemini model that has access to the internet."
)

# Launch the interface
iface.launch(share=True)
