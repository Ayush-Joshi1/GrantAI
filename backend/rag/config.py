from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    model_name: str = "text-embedding-3-small"
    embedding_model_name: str = "BAAI/bge-base-en-v1.5"
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 5
    similarity_threshold: float = 0.2
    embedding_batch_size: int = 32
    embedding_device: str = "cpu"
    data_folder: str = "data/rag"
    vector_store_path: str = "data/rag/faiss.index"
    index_file_name: str = "faiss.index"
    vector_metric: str = "IP"
    persist_directory: str = "data/rag"
    logging_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_rag_settings() -> RAGSettings:
    return RAGSettings()
