import os
import logging
from typing import List
from app.config import Config, logger
from app.metrics import rag_queries, system_errors

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

class RAGPipeline:
    """Retrieval-Augmented Generation for financial documents"""
    def __init__(self, vector_db_path: str, documents_path: str ="documents"):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_db_path = vector_db_path
        self.documents_path = documents_path
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._initialize_vector_store()
        self._load_documents_from_folder()

    def _initialize_vector_store(self):
        try:
            if os.path.exists(self.vector_db_path) and os.listdir(self.vector_db_path):
                # try loading existing
                try:
                    self.vector_store = FAISS.load_local(self.vector_db_path, self.embeddings)
                    logger.info(f"Loaded existing vector store from {self.vector_db_path}")
                except Exception as e:
                    logger.warning(f"Failed to load existing vector store, will create new one: {e}")
                    self._create_new_store()
            else:
                self._create_new_store()
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            system_errors.labels(component="rag_pipeline").inc()

    def _create_new_store(self):
        texts = ["Initial document for vector store initialization"]
        self.vector_store = FAISS.from_texts(texts, self.embeddings)
        os.makedirs(self.vector_db_path, exist_ok=True)
        try:
            self.vector_store.save_local(self.vector_db_path)
            logger.info(f"Created new vector store at {self.vector_db_path}")
        except Exception as e:
            logger.error(f"Error saving new vector store: {e}")
            system_errors.labels(component="rag_pipeline_save").inc()

    def _load_documents_from_folder(self):
        """Automatically load all the PDF documents from the doc folder"""
        if not os.path.exists(self.documents_path):
            logger.warning(f"Documents folder not found: {self.documents_path}")
            return
        pdf_files = [
            os.path.join(self.documents_path, f) for f in os.listdir(self.documents_path) if f.endswith('.pdf')]
        if pdf_files:
            logger.info(f"Foiund {len(pdf_files)} PDF files to load")
            self.add_documents(pdf_files)
        else:
            logger.warning(f"No pdf files found in {self.documents_path}")

            
    def add_documents(self, file_paths: List[str]):
        all_documents = []
        for file_path in file_paths:
            try:
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                split_docs = self.text_splitter.split_documents(documents)
                all_documents.extend(split_docs)
                logger.info(f"Loaded {len(split_docs)} chunks from {file_path}")
            except Exception as e:
                logger.error(f"Error loading document {file_path}: {e}")
                system_errors.labels(component="document_loader").inc()

        if all_documents:
            try:
                self.vector_store.add_documents(all_documents)
                self.vector_store.save_local(self.vector_db_path)
                logger.info(f"Added {len(all_documents)} documents to vector store")
            except Exception as e:
                logger.error(f"Error saving documents to vector store: {e}")
                system_errors.labels(component="rag_pipeline_save").inc()

    def query(self, query: str, k: int = 5) -> str:
        rag_queries.inc()
        try:
            results = self.vector_store.similarity_search(query, k=k)
            context = "\n\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            system_errors.labels(component="rag_query").inc()
            return ""
