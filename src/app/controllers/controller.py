import shutil
import os
from app.controllers.vector_db_manager import create_chroma_vector_store
from app.controllers.document_processor import DocumentProcessor
from app.controllers.qa_graph_handler import CustomerSupportBot
from app.config import CONFIG as Config
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, stop_after_attempt, wait_exponential

class DBController:
    def __init__(self, llm):
        self.retriever = create_chroma_vector_store()
        self.doc_processor = DocumentProcessor()
        self.qa_handler = CustomerSupportBot(llm)
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.db_created = True
        # self.create_new_database()

    def create_new_database(self, directory_path):
        if not os.path.exists(directory_path):
            raise ValueError("Invalid directory path provided.")

        if os.path.exists(Config.PERSIST_DIR) and os.listdir(Config.PERSIST_DIR):
            shutil.rmtree(Config.PERSIST_DIR)

        print("Creating new Chroma vector store and embedding documents...")

        # Load and split documents
        loader = DirectoryLoader(path=Config.DOCUMENTS_DIR, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        # Initialize Chroma vector store with persistence
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embedding_model,
            persist_directory=Config.PERSIST_DIR
        )

        return f"Database created!"
        

    def clear_database(self):
        if os.path.exists(Config.PERSIST_DIR):
            shutil.rmtree(Config.PERSIST_DIR)
            self.db_created = False
            return "Database cleared successfully!"
        else:
            return "No database found to clear."

    def use_existing_database(self):
        if os.path.exists(Config.PERSIST_DIR):
            self.db_created = True
            return "Using existing database."
        else:
            self.create_new_database(Config.DOCUMENTS_DIR)
            return "No existing database found. Creating a new one."

    def ask_question(self, query):
        if not self.db_created:
            return "Database not initialized. Please create or load a database first."
 
        response = self.qa_handler.handle_query(query, self.retriever)
        return response['result'] if isinstance(response, dict) and 'result' in response else response
