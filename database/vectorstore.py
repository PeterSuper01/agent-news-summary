import hashlib
import logging
import time
from datetime import datetime, timedelta

from app.config import settings
from huggingface_hub.utils import disable_progress_bars
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from news.allowed_sections import AllowedSectionInput
import transformers.utils.logging

logger = logging.getLogger(__name__)

# Suppress output when loading the embedding model
transformers.utils.logging.set_verbosity_error()
transformers.utils.logging.disable_progress_bar()


class NewsVectorstore:
    def __init__(self, persist_dir: str):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            cache_folder=settings.EMBEDDING_MODEL_CACHE_FOLDER,
            model_kwargs={"token": settings.HF_TOKEN},
        )
        self.chunk_store = Chroma(
            collection_name=settings.CHROMA_DB_CHUNKS_COLLECTION,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_configuration={
                "hnsw": {"space": settings.CHROMA_DB_COLLECTION_DISTANCE_METRIC}
            },
        )
        self.article_store = Chroma(
            collection_name=settings.CHROMA_DB_ARTICLES_COLLECTION,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_configuration={
                "hnsw": {"space": settings.CHROMA_DB_COLLECTION_DISTANCE_METRIC}
            },
        )
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.VECTORSTORE_CHUNK_SIZE,
            chunk_overlap=settings.VECTORSTORE_CHUNK_OVERLAP,
        )

    def add_documents(self, documents: list[Document]):
        chunk_ids = []
        chunks = []
        article_ids = []
        articles = []

        skipped_expired = 0
        skipped_no_url = 0
        for doc in documents:
            if (
                time.time() - doc.metadata.get("public_date")
                < timedelta(days=7).total_seconds()
            ):
                url = doc.metadata.get("article_url")
                if url:
                    url_hash = hashlib.md5(url.encode()).hexdigest()

                    article_ids.append(url_hash)
                    articles.append(doc)

                    for i, chunk in enumerate(self._splitter.split_documents([doc])):
                        chunk_ids.append(f"{url_hash}_{i}")
                        chunks.append(chunk)
                else:
                    skipped_no_url += 1
                    logger.warning("Skipping document with no article URL: %s", doc.metadata)
            else:
                skipped_expired += 1

        if skipped_expired:
            logger.info("Skipped %d expired articles (> 7 days old)", skipped_expired)
        if skipped_no_url:
            logger.info("Skipped %d articles with no URL", skipped_no_url)

        if articles:
            self.article_store.add_documents(documents=articles, ids=article_ids)
            self.chunk_store.add_documents(documents=chunks, ids=chunk_ids)
            logger.info("Stored %d articles as %d chunks", len(articles), len(chunks))

    def search(
        self, query: str, section_input: AllowedSectionInput = None, k: int = 5
    ) -> list[Document]:
        search_filter = {}
        if section_input:
            search_filter["section"] = section_input.value

        matched_chunks = self.chunk_store.similarity_search(
            query, k=k, filter=search_filter if search_filter else None
        )

        seen_urls = []
        for chunk in matched_chunks:
            url = chunk.metadata.get("article_url")
            if url and url not in seen_urls:
                seen_urls.append(url)

        if not seen_urls:
            return []

        article_ids = [hashlib.md5(url.encode()).hexdigest() for url in seen_urls]
        result = self.article_store._collection.get(
            ids=article_ids, include=["documents", "metadatas"]
        )
        return [
            Document(page_content=content, metadata=meta)
            for content, meta in zip(result["documents"], result["metadatas"])
        ]

    def clear_expired_news(self, days: int = 7):
        cutoff_date = time.mktime((datetime.now() - timedelta(days=days)).timetuple())
        where = {"public_date": {"$lt": cutoff_date}}
        self.chunk_store._collection.delete(where=where)
        self.article_store._collection.delete(where=where)
