## Gemini API Qdrant Examples

### Table of Contents

This folder contains example notebooks demonstrating how to combine the **Gemini API** with the **Qdrant vector database** to enable semantic search and recommendation features using embeddings.

---

### Notebooks

* **[Similarity Search using Qdrant](./Qdrant_similarity_search.ipynb)**
  Load website data, build a semantic search system using embeddings from the Gemini API, store the embeddings in a Qdrant vector DB, and perform similarity search using Gemini-powered queries.

* **[Movie Recommendation using Qdrant](./Movie_Recommendation.ipynb)**
  Process and embed a large movie dataset with the Gemini API, index movie vectors in Qdrant, and build a semantic movie recommender that returns similar movies based on user input using vector similarity search.

* **[Hybrid Search & Reranking with Qdrant: Under the Hood of Legal AI](./Hybrid_Search_Legal.ipynb)**
  Embed and index a legal dataset with the Gemini API and Qdrant, combining dense (based on Matryoshka Representations of Gemini embeddings) and sparse (based on the Qdrant's custom keywords-based retriever miniCOIL) vectors for hybrid search to ensure high accuracy, citation-grounded legal domain question answering.
  

---

These examples show how to:

* Embed unstructured text data using Gemini's embedding model.
* Store and search high-dimensional vectors in Qdrant.
* Use Gemini queries to semantically match user input to relevant content.

You can use these templates as a foundation for building search, recommendation, or AI assistant systems using Gemini and Qdrant.