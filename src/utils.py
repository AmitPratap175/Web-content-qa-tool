"""
Author: Amit Pratap

Description:
This script does the following:
1. Loads all `.md` files from the `data/` folder.
2. Embeds them using Google Generative AI embedding model.
3. Stores embeddings in a ChromaDB vector store.
4. Uses Gemini-Pro LLM with Corrective RAG to refine answers.

Usage:
- Set your Google API key in a `.env` file.
- Run the script: `python corrective_rag.py`
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


# Load environment variables
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# Load and embed markdown files
def load_and_embed_markdown(folder_path="data"):
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith(".md"):
            loader = TextLoader(os.path.join(folder_path, file))
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    embedding = GoogleGenerativeAIEmbeddings()
    vectorstore = Chroma.from_documents(docs, embedding=embedding, persist_directory="chroma_db")
    return vectorstore


