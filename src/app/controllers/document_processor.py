import os
import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import CONFIG as Config
from langchain_community.document_loaders import TextLoader  # Correct loader for .md files

class MarkdownLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_and_split(self, splitter):
        loader = TextLoader(self.file_path)
        return splitter.split_documents(loader.load())  # Updated for .md files

class DocumentProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

    def process_directory(self, directory_path):
        """Process all Markdown files in a directory"""
        all_docs = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".md"):
                file_path = os.path.join(directory_path, filename)
                loader = MarkdownLoader(file_path)
                docs = loader.load_and_split(self.splitter)
                all_docs.extend(docs)
        return all_docs
