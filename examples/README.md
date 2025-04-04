# Gemini API Examples

This folder contains a collection of examples for the Gemini API. These are advanced examples and might be quite complex as they often use one of more Gemini capabilities.

For introductions to those features it is recommended to start with the [Quickstarts](../quickstarts/) guides, and the [Get started](../quickstarts/Get_started.ipynb) one in particular.
<br><br>

## Table of contents

This is a collection of fun and helpful examples for the Gemini API.

| Cookbook | Description | Features | Open |
| -------- | ----------- | -------- | ---- |
| [Browser as a tool](./Browser_as_a_tool.ipynb) | Demonstrates 3 ways to use a web browser as a tool with the Gemini API | Tools, Live API | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Browser_as_a_tool.ipynb) |
| [Illustrate a book](./Book_illustration.ipynb) | Use Gemini and Imagen to create illustration for an open-source book | Imagen, structured output | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb) |
| [Animated Story Generation](./Animated_Story_Video_Generation_gemini.ipynb) | Create animated videos by combining story generation, images, and audio | Imagen, Live API, structured output | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Animated_Story_Video_Generation_gemini.ipynb) |
| [Plotting and mapping Live](./LiveAPI_plotting_and_mapping.ipynb) | Ask Gemini for complex graphs live | Live API, Code execution | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/LiveAPI_plotting_and_mapping.ipynb) |
| [Search grounding for research report](./Search_grounding_for_research_report.ipynb) | Use grounding to improve the quality of your research report | Grounding | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Search_grounding_for_research_report.ipynb) |
| [Market a Jet Backpack](./Market_a_Jet_Backpack.ipynb) | Create a marketing campaign from a product sketch | Multimodal | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Market_a_Jet_Backpack.ipynb) |
| [3D Spatial understanding](./Spatial_understanding_3d.ipynb) | Use Gemini 3D spatial abilities to understand 3D scenes and answer questions about them | Multimodal, Spatial understanding | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Spatial_understanding_3d.ipynb) |
| [Video Analysis - Classification](./Analyze_a_Video_Classification.ipynb) | Use Gemini's multimodal capabilities to classify animal species in videos | Video, Multimodal | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Analyze_a_Video_Classification.ipynb) |
| [Video Analysis - Summarization](./Analyze_a_Video_Summarization.ipynb) | Generate summaries of video content using Gemini | Video, Multimodal | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Analyze_a_Video_Summarization.ipynb) |
| [Video Analysis - Event Recognition](./Analyze_a_Video_Historic_Event_Recognition.ipynb) | Identify when historical events occurred in video footage | Video, Multimodal | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Analyze_a_Video_Historic_Event_Recognition.ipynb) |
| [Gradio and live API](./gradio_audio.py) | Use gradio to deploy your own instance of the Live API | Live API | [Python Code](./gradio_audio.py) |
| [Apollo 11 - long context example](./Apollo_11.ipynb) | Search a 400 page transcript from Apollo 11. | File API | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Apollo_11.ipynb) |
| [Anomaly Detection](./Anomaly_detection_with_embeddings.ipynb) | Use embeddings to detect anomalies in your datasets | Embeddings | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Anomaly_detection_with_embeddings.ipynb) |
| [Invoice and Form Data Extraction](./Pdf_structured_outputs_on_invoices_and_forms.ipynb) | Use the Gemini API to extract information from PDFs | File API, Structured Outputs | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb) |
| [Opossum search](./Opossum_search.ipynb) | Code generation with the Gemini API. Just for fun, you'll prompt the model to create a web app called "Opossum Search" that searches Google with "opossum" appended to the query. | Code generation | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Opossum_search.ipynb) |
| [Virtual Try-on](./Virtual_Try_On.ipynb) | A Virtual Try-On application that utilizes Gemini 2.5 to create segmentation masks for identifying outfits in images, and Imagen 3 for generating and inpainting new outfits. | Spatial Understanding | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Virtual_Try_On.ipynb) |
| [Talk to documents](./Talk_to_documents_with_embeddings.ipynb) | Use embeddings to search through a custom database. | Embeddings | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Talk_to_documents_with_embeddings.ipynb) |
| [Entity extraction](./Entity_Extraction.ipynb) | Use Gemini API to speed up some of your tasks, such as searching through text to extract needed information. Entity extraction with a Gemini model is a simple query, and you can ask it to retrieve its answer in the form that you prefer. | Embeddings | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Entity_Extraction.ipynb) |

---
<br>
Some old examples are still using the legacy SDK, they should still work and are still worth checking to get ideas:

* [Agents and Automatic Function Calling](./Agents_Function_Calling_Barista_Bot.ipynb): Create an agent (Barrista-bot) to take your coffee order.
* [Classify text with emeddings](./Classify_text_with_embeddings.ipynb): Use embeddings from the Gemini API with Keras.
* [Guess the shape](./Guess_the_shape.ipynb): A simple example of using images in prompts.
* [Object detection](./Object_detection.ipynb): Extensive examples with object detection, including with multiple classes, OCR, visual question answering, and even an interactive demo.
* [Search Wikipedia with ReAct](./Search_Wikipedia_using_ReAct.ipynb): Use ReAct prompting with Gemini Flash to search Wikipedia interactively.
* [Search Re-ranking with Embeddings](./Search_reranking_using_embeddings.ipynb): Use embeddings to re-rank search results.
* [Story writing with prompt chaining.ipynb](./Story_Writing_with_Prompt_Chaining.ipynb): Write a story using two powerful tools: prompt chaining and iterative generation.
* [Tag and Caption images](./Tag_and_caption_images.ipynb): Use the Gemini model's vision capabilities and the embedding model to add tags and captions to images of pieces of clothing.
* [Talk to documents](./Talk_to_documents_with_embeddings.ipynb): This is a basic intro to Retrieval Augmented Generation (RAG). Use embeddings to search through a custom database.
* [Voice Memos](./Voice_memos.ipynb): You'll use the Gemini API to help you generate ideas for your next blog post, based on voice memos you recorded on your phone, and previous articles you've written.
* [Translate a public domain](./Translate_a_Public_Domain_Book.ipynb): In this notebook, you will explore Gemini model as a translation tool, demonstrating how to prepare data, create effective prompts, and save results into a `.txt` file.
* [Working with Charts, Graphs, and Slide Decks](./Working_with_Charts_Graphs_and_Slide_Decks.ipynb): Gemini models are powerful multimodal LLMs that can process both text and image inputs. This notebook shows how Gemini Flash model is capable of extracting data from various images.
* [Entity extraction](./Entity_Extraction.ipynb): Use Gemini API to speed up some of your tasks, such as searching through text to extract needed information. Entity extraction with a Gemini model is a simple query, and you can ask it to retrieve its answer in the form that you prefer.
<br><br>

### Integrations

* [Personalized Product Descriptions with Weaviate](../examples/weaviate/personalized_description_with_weaviate_and_gemini_api.ipynb): Load data into a Weaviate vector DB, build a semantic search system using embeddings from the Gemini API, create a knowledge graph and generate unique product descriptions for personas using the Gemini API and Weaviate.
* [Similarity Search using Qdrant](../examples/qdrant/Qdrant_similarity_search.ipynb): Load website data, build a semantic search system using embeddings from the Gemini API, store the embeddings in a Qdrant vector DB and perform similarity search using the Gemini API and Qdrant.
<br><br>

### Folders

* [Prompting examples](./prompting/): A directory with examples of various prompting techniques. 
* [JSON Capabilities](./json_capabilities/): A directory with guides containing different types of tasks you can do with JSON schemas.
* [Automate Google Workspace tasks with the Gemini API](./Apps_script_and_Workspace_codelab/): This codelabs shows you how to connect to the Gemini API using Apps Script, and uses the function calling, vision and text capabilities to automate Google Workspace tasks - summarizing a document, analyzing a chart, sending an email and generating some slides directly. All of this is done from a free text input.
* [Langchain examples](./langchain/): A directory with multiple examples using Gemini with Langchain.
