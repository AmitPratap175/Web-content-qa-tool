from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langgraph.checkpoint.memory import MemorySaver
import uuid

class QAHandler:
    def __init__(self, llm):
        self.llm = llm

        # Directly embed the refined WhatsApp bot prompt
        custom_prompt = """
You are a helpful AI assistant for DriveYourWay, a driving school in the Netherlands.

Answer ONLY questions that relate to:
- Frequently Asked Questions (FAQs)
- Pricing, lesson packages, and services offered

Follow these rules carefully:
1. Use ONLY the information provided in the context. Do NOT make up answers.
2. If the answer is not in the context, respond with: "I'm sorry, I don't have that information at the moment."
3. Keep responses concise but informative. Use bullet points or lists for clarity when needed.
4. Format the response clearly, using proper line breaks and headings if needed.
5. If a topic from the context is mentioned, summarize what is known about it in detail.
6. Provide appropriate responses for Whatsapp message formats. If you have to highlight use italics instead of bold.


Context: {context}

Customer Question: {question}

Answer:
        """

        self.qa_prompt = PromptTemplate(
            template=custom_prompt.strip(),
            input_variables=["context", "question"]
        )

    def get_answer(self, query, retriever):
        """Execute QA chain"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.qa_prompt}
        )
        return qa_chain.invoke(query)


class BotState(TypedDict):
    user_input: str
    sentiment: Annotated[str, "negative|positive"]
    qa_answer: str
    needs_human: bool
    response: str

class CustomerSupportBot:
    def __init__(self,llm):
        self.llm = llm
        self.qa_handler = QAHandler(llm)
        self.workflow = StateGraph(BotState)
        self.retriever = None
        self.memory = MemorySaver()
        
        # Define nodes
        self.workflow.add_node("analyze_sentiment", self.analyze_sentiment)
        self.workflow.add_node("retrieve_answer", self.retrieve_answer)
        self.workflow.add_node("escalate_to_human", self.escalate_to_human)
        self.workflow.add_node("generate_response", self.generate_response)

        # Define edges
        self.workflow.set_entry_point("analyze_sentiment")
        self.workflow.add_edge("generate_response", END)
        
        # Conditional routing
        self.workflow.add_conditional_edges(
            "analyze_sentiment",
            self.decide_routing,
            {
                "escalate": "escalate_to_human",
                "answer": "retrieve_answer"
            }
        )
        self.workflow.add_edge("retrieve_answer", "generate_response")
        self.workflow.add_edge("escalate_to_human", "generate_response")

        # Compile the graph
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def sentiment_analyzer(self, text: str) -> str:
        """Analyze sentiment of the text"""
        prompt = ChatPromptTemplate.from_template(
            """
        You are a customer support chatbot. Analyze the sentiment of the following customer query. 
        Ignore any previous chat history. Focus solely on the current query.
        Consider the context of customer support interactions when determining the sentiment.

        Respond with one of the following exactly: 'positive', or 'negative'.

        Here are some guidelines:

        - 'positive': The customer expresses satisfaction, appreciation, or positive feelings.The customer's query is informational, factual, or lacks strong emotional expression, and the chatbot can potentially provide a resolution.
            If the customer uses inappropriate language, but the query can still be answered by the bot, respond with neutral.
        - 'negative': The customer explicitly requests to speak to a human, or the customer's query indicates that the chatbot is unable to provide a satisfactory answer and requires human intervention.

        Query: {query}
        """
        )
        chain = prompt | self.llm
        sentiment = chain.invoke({"query": text}).content
        return sentiment

    def analyze_sentiment(self, state: BotState) -> dict:
        """Analyze user input sentiment"""
        sentiment = self.sentiment_analyzer(state["user_input"])
        return {"sentiment": sentiment}

    def decide_routing(self, state: BotState) -> str:
        """Route based on sentiment"""
        if state["sentiment"] == "negative":
            return "escalate"
        return "answer"

    def retrieve_answer(self, state: BotState) -> dict:
        """Get answer from knowledge base"""
        answer = self.qa_handler.get_answer(state["user_input"], self.retriever)
        return {"qa_answer": answer}

    def escalate_to_human(self, state: BotState) -> dict:
        """Handle escalation"""
        return {"needs_human": True}

    def generate_response(self, state: BotState) -> dict:
        """Final response formatting"""
        if state.get("needs_human"):
            return {"response": "Let me connect you to a human representative..."}
        return {"response": state["qa_answer"]}

    def handle_query(self, user_input: str, retriever) -> str:
        """Execute the workflow"""
        self.retriever = retriever
        results = self.app.invoke({"user_input": user_input},config={"configurable":{"thread_id": str(uuid.uuid4())}})
        return results["response"]