import os
import hashlib
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

def generate_persistent_directory(urls):
    hash_input = "".join(sorted(urls)).encode()
    hash_digest = hashlib.md5(hash_input).hexdigest()
    return f"./chroma_db/{hash_digest}"

def ingest_and_answer(urls, question):
    try:
        # Validate inputs
        if not urls or not all(url.startswith(('http://', 'https://')) for url in urls):
            return "Please enter valid URLs starting with http:// or https://"
            
        if not question.strip():
            return "Please enter a question"

        persistent_directory = generate_persistent_directory(urls)
        
        # Ingest content
        loader = WebBaseLoader(urls)
        documents = loader.load()
        
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        
        # Create or load vector store
        if not os.path.exists(persistent_directory):
            db = Chroma.from_documents(
                docs, 
                embeddings, 
                persist_directory=persistent_directory
            )
            db.persist()
        else:
            db = Chroma(
                persist_directory=persistent_directory,
                embedding_function=embeddings
            )
        
        # Create QA chain
        retriever = db.as_retriever(search_kwargs={"k": 5})
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a chat history and the latest user question, " +
             "rephrase the question to be a standalone question."),
            ("user", "{input}")
        ])
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer based on context:\n{context}\nIf unsure, say 'I don't know'."),
            ("user", "{input}")
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )
        document_chain = create_stuff_documents_chain(llm, qa_prompt)
        qa_chain = create_retrieval_chain(history_aware_retriever, document_chain)
        
        result = qa_chain.invoke({"input": question})
        return result["answer"]
    
    except Exception as e:
        return f"Error processing request: {str(e)}"