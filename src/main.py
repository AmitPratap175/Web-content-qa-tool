import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import List, Dict, TypedDict
from pydantic import BaseModel, Field
from app.controllers.controller import DBController
from app.controllers.crawler import crawl_recursive_batch
from app.controllers.markdown_cleaner import MarkdownCleaner
import asyncio

# Configuration
class AppConfig(BaseModel):
    google_api_key: str = Field(..., env="OPENAI_API_KEY")
    temperature: float = 0.5
    max_history_length: int = 10


# State for LangGraph
class ChatState(TypedDict):
    messages: List[Dict[str, str]]


# Chat History Manager
class ChatHistoryManager:
    def __init__(self, max_length: int = 10):
        self.max_length = max_length
        if "history" not in st.session_state:
            st.session_state.history = []

    def add_message(self, role: str, content: str):
        st.session_state.history.append({"role": role, "content": content, "feedback": None})
        if len(st.session_state.history) > self.max_length:
            st.session_state.history.pop(0)

    def get_history(self) -> List[Dict[str, str]]:
        return st.session_state.history

    def update_feedback(self, index: int, feedback: str):
        try:
            st.session_state.history[index]["feedback"] = feedback
        except IndexError:
            pass

    def clear_history(self):
        st.session_state.history = []


# LangGraph conversation service
class ConversationService:
    def __init__(self, llm: ChatGoogleGenerativeAI, history_manager: ChatHistoryManager, db_controller: DBController):
        self.llm = llm
        self.db_controller = db_controller#DBController(llm)

    def generate_response(self, state: ChatState) -> ChatState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        chain = prompt | self.llm
        response = self.db_controller.ask_question(state["messages"][-1]["content"])
        return {"messages": state["messages"] + [{"role": "assistant", "content": response.content}]}


# Streamlit UI
class ChatUI:
    @staticmethod
    def setup_sidebar() -> AppConfig:
        st.sidebar.title("Settings")
        return AppConfig(
            google_api_key=st.sidebar.text_input("Google API Key", type="password"),
            temperature=st.sidebar.slider("Temperature", 0.0, 1.0, 0.5),
            max_history_length=st.sidebar.number_input("Max Chat History Length", min_value=5, max_value=50, value=10)
        )

    @staticmethod
    def get_url_input() -> str:
        return st.text_input("Enter URL to scrape:")

    @staticmethod
    def display_chat(history_manager: ChatHistoryManager):
        history = history_manager.get_history()
        for index, message in enumerate(history):
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message["role"] == "assistant":
                    if not message.get("feedback"):
                        col1, col2 = st.columns(2)
                        if col1.button("👍", key=f"thumbsup_{index}"):
                            history_manager.update_feedback(index, "up")
                            st.success("Thanks for your feedback!")
                        if col2.button("👎", key=f"thumbsdown_{index}"):
                            history_manager.update_feedback(index, "down")
                            st.error("Thanks for your feedback!")
                    else:
                        st.info(f"Feedback recorded: {'👍' if message['feedback'] == 'up' else '👎'}")


# Main Application
class ChatApplication:
    def __init__(self):
        self.config = ChatUI.setup_sidebar()
        self.url = ChatUI.get_url_input()

        if "url_loaded" not in st.session_state:
            st.session_state.url_loaded = False

        self.history_manager = ChatHistoryManager(max_length=self.config.max_history_length)
        self.llm = None
        self.conversation_service = None
        self.db_initialized = False

    def _initialize_db_controller(self, llm):
        if not self.db_initialized:
            self.db_controller = DBController(llm)
            self.db_initialized = True

    def _initialize_model(self):
        if not self.config.google_api_key.startswith("A"):
            return None
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=self.config.temperature,
                max_tokens=None,
                timeout=None,
                google_api_key=self.config.google_api_key
            )
        except Exception as e:
            st.error(f"Model Error: {str(e)}")
            return None

    async def run(self):
        st.title("AI Chatbot with Memory & Feedback")

        # Require URL before proceeding
        if not self.url:
            st.info("Please enter a URL to begin scraping.")
            return

        if not st.session_state.url_loaded:
            st.info(f"Scraping data from: {self.url}")
            await crawl_recursive_batch([self.url], max_depth=2, max_concurrent=10)
            await MarkdownCleaner().process_files()
            st.session_state.url_loaded = True
            st.success("Scraping complete. You can now chat.")

        # Now initialize model
        if not self.llm:
            self.llm = self._initialize_model()
            if not self.llm:
                st.warning("Enter a valid Google API key.")
                return
            self._initialize_db_controller(self.llm)
            self.conversation_service = ConversationService(self.llm, self.history_manager, self.db_controller)

        ChatUI.display_chat(self.history_manager)

        if prompt := st.chat_input("Ask something"):
            self._process_user_input(prompt)
            self._generate_and_display_response(prompt)

    def _process_user_input(self, prompt: str):
        with st.chat_message("user"):
            st.write(prompt)
        self.history_manager.add_message("user", prompt)

    def _generate_and_display_response(self, prompt: str):
        with st.chat_message("assistant"):
            response_container = st.empty()
            response = self.conversation_service.db_controller.ask_question(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            response_container.markdown(content)
            self.history_manager.add_message("assistant", content)
            st.rerun()


# Entry Point
if __name__ == "__main__":
    app = ChatApplication()
    asyncio.run(app.run())
