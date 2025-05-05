import os
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import CONFIG as Config
# from tenacity import retry, stop_after_attempt, wait_exponential


def create_chroma_vector_store():
    # Specify paths
    folder_path = Config.DOCUMENTS_DIR
    persist_directory = Config.PERSIST_DIR

    # Embedder
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Check if Chroma vector store already exists
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print("Loading existing Chroma vector store...")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
    else:
        print("Creating new Chroma vector store and embedding documents...")

        # Load and split documents
        loader = DirectoryLoader(path=folder_path, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        # Initialize Chroma vector store with persistence
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_model,
            persist_directory=persist_directory
        )

    # Create retriever
    retriever = vectorstore.as_retriever()

    return retriever
