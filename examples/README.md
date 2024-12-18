# Gemini API Examples

## Table of contents

This is a collection of fun examples for the Gemini API. 

* [Agents and Automatic Function Calling](./Agents_Function_Calling_Barista_Bot.ipynb): Create an agent (Barrista-bot) to take your coffee order. 
* Video Analysis: Three notebooks using multimodal capabilities of the Gemini model to [classify the species of animals](./Analyze_a_Video_Classification.ipynb) for a video, [summarize one](./Analyze_a_Video_Summarization.ipynb) or [recognizing when it happened](./Analyze_a_Video_Historic_Event_Recognition.ipynb), 
* [Anomaly Detection](./Anomaly_detection_with_embeddings.ipynb): Use embeddings to detect anomalies in your datasets.
* [Analyze a Video with Summarization](./Analyze_a_Video_Summarization.ipynb): This notebook shows how you can use Gemini API's multimodal capabilities for video summarization.
* [Apollo 11 - long context example](./Apollo_11.ipynb): Search a 400 page transcript from Apollo 11.
* [Clasify text with emeddings](./Classify_text_with_embeddings.ipynb): Use embeddings from the Gemini API with Keras.
* [Guess the shape](./Guess_the_shape.ipynb): A simple example of using images in prompts.
* [Market a Jet Backpack](./Market_a_Jet_Backpack.ipynb): Create a marketing campaign from a product sketch.
* [Object detection](./Object_detection.ipynb): Extensive examples with object detection, including with multiple classes, OCR, visual question answering, and even an interactive demo.  
* [Opossum search](./Opossum_search.ipynb): Code generation with the Gemini API. Just for fun, you'll prompt the model to create a web app called "Opossum Search" that searches Google with "opossum" appended to the query.
* [Search Wikipedia with ReAct](./Search_Wikipedia_using_ReAct.ipynb): Use ReAct prompting with Gemini 1.5 Flash to search Wikipedia interactively.
* [Search Re-ranking with Embeddings](./Search_reranking_using_embeddings.ipynb): Use embeddings to re-rank search results.
* [Story writing with prompt chaining.ipynb](./Story_Writing_with_Prompt_Chaining.ipynb): Write a story using two powerful tools: prompt chaining and iterative generation.
* [Talk to documents](./Talk_to_documents_with_embeddings.ipynb): This is a basic intro to Retrieval Augmented Generation (RAG). Use embeddings to search through a custom database.
* [Upload files to Colab](./Upload_files_to_Colab.ipynb): This is a helper notebook that shows how to upload files from your local computer to Colab. Note: to upload files to the Gemini API (text, code, images, audio, video), check out the [Files quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/File_API.ipynb).
* [Voice Memos](./Voice_memos.ipynb): You'll use the Gemini API to help you generate ideas for your next blog post, based on voice memos you recorded on your phone, and previous articles you've written.
* [Translate a public domain](./Translate_a_Public_Domain_Book.ipynb): In this notebook, you will explore Gemini model as a translation tool, demonstrating how to prepare data, create effective prompts, and save results into a `.txt` file.
* [Working with Charts, Graphs, and Slide Decks](./Working_with_Charts_Graphs_and_Slide_Decks.ipynb): Gemini models are powerful multimodal LLMs that can process both text and image inputs. This notebook shows how Gemini 1.5 Flash model is capable of extracting data from various images.
* [Entity extraction](./Entity_Extraction.ipynb): Use Gemini API to speed up some of your tasks, such as searching through text to extract needed information. Entity extraction with a Gemini model is a simple query, and you can ask it to retrieve its answer in the form that you prefer.
* [Generate a company research report using search grounding](./search_grounding_for_research_report.ipynb): Use search grounding to write a company research report with Gemini 1.5 Flash.

### Integrations

* [Personalized Product Descriptions with Weaviate](weaviate/personalized_description_with_weaviate_and_gemini_api.ipynb): Load data into a Weaviate vector DB, build a semantic search system using embeddings from the Gemini API, create a knowledge graph and generate unique product descriptions for personas using the Gemini API and Weaviate.

### Folders

* [Prompting examples](./prompting): A directory with examples of various prompting techniques. 
* [JSON Capabilities](./json-capabilities): A directory with guides containing different types of tasks you can do with JSON schemas.
* [Automate Google Workspace tasks with the Gemini API](./Apps_script_and_Workspace_codelab): This codelabs shows you how to connect to the Gemini API using Apps Script, and uses the function calling, vision and text capabilities to automate Google Workspace tasks - summarizing a document, analyzing a chart, sending an email and generating some slides directly. All of this is done from a free text input.
* [Langchain examples](./langchain): A directory with multiple examples using Gemini with Langchain.

There are even more examples in the [quickstarts](../quickstarts) folder and in the [Awesome Gemini page](../Awesome_gemini.md).