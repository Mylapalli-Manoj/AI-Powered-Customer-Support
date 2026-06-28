"""
rag.py
------
Implements a simple RAG (Retrieval-Augmented Generation) pipeline.

Loads all documents from the knowledge_base folder, splits them into
chunks, converts them into embeddings, and allows searching for the
most relevant chunks given a customer query.

Task 6: Integrate a RAG pipeline using the provided company documents.
"""

import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

KNOWLEDGE_BASE_DIR = "knowledge_base"

_vectorstore = None


def build_vectorstore():
    """
    Loads all .txt files from the knowledge_base folder, splits them
    into smaller chunks, and builds a searchable FAISS vector store.
    """
    documents = []

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    return vectorstore


def get_vectorstore():
    """Returns the vectorstore, building it once and reusing it after that."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = build_vectorstore()
    return _vectorstore


def retrieve_context(query: str, k: int = 3) -> str:
    """
    Searches the knowledge base for the most relevant chunks
    to the given customer query, and returns them as a single string.
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return "No relevant company information found."

    context_pieces = [doc.page_content for doc in results]
    return "\n---\n".join(context_pieces)