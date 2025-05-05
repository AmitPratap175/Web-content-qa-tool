import sys
import os
from dotenv import load_dotenv
import logging


class CONFIG:
    PERSIST_DIR = "/home/dspratap/Documents/suneater175/chat_url_bot/src/app/vector_db" # TODO: change this to environment variable
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    MODEL_NAME = "gemini-1.5-flash"
    EMBEDDING_MODEL = "models/embedding-001"
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DOCUMENTS_DIR = "/home/dspratap/Documents/suneater175/chat_url_bot/src/app/data/processed"
    SCRAPED_DIR = "/home/dspratap/Documents/suneater175/chat_url_bot/src/app/data/scraped"
    
    PROMPT_FILE = "./templates/qa_prompt.txt"

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
