import hashlib
import time
from datetime import datetime, timedelta

from app.config import settings
from huggingface_hub.utils import disable_progress_bars
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from news.allowed_sections import AllowedSectionInput
import transformers.utils.logging

# Suppress output when loading the embedding model
transformers.utils.logging.set_verbosity_error()
transformers.utils.logging.disable_progress_bar()


class NewsVectorstore:
    def __init__(self, persist_dir: str, collection_name: str):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            cache_folder=settings.EMBEDDING_MODEL_CACHE_FOLDER,
            model_kwargs={"token": settings.HF_TOKEN},
        )
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_configuration={
                "hnsw": {"space": settings.CHROMA_DB_COLLECTION_DISTANCE_METRIC}
            },
        )

    def add_documents(self, documents: list[Document]):
        ids = []
        valid_docs = []
        for doc in documents:
            # only keep news within 7 days
            if (
                time.time() - doc.metadata.get("public_date")
                < timedelta(days=7).total_seconds()
            ):
                url = doc.metadata.get("article_url")
                if url:
                    content_hash = hashlib.md5(url.encode()).hexdigest()
                    ids.append(content_hash)
                    valid_docs.append(doc)
                else:
                    print(
                        f"Warning: Skipping document with no article URL: {doc.metadata}"
                    )
        if len(valid_docs) > 0:
            self.vector_store.add_documents(documents=valid_docs, ids=ids)

    def search(
        self, query: str, section_input: AllowedSectionInput = None, k: int = 5
    ) -> list[Document]:
        search_filter = {}
        if section_input:
            search_filter["section"] = section_input.value

        return self.vector_store.similarity_search(
            query, k=k, filter=search_filter if search_filter else None
        )

    def clear_expired_news(self, days: int = 7):
        cutoff_date = time.mktime((datetime.now() - timedelta(days=days)).timetuple())
        self.vector_store._collection.delete(
            where={"public_date": {"$lt": cutoff_date}}
        )
