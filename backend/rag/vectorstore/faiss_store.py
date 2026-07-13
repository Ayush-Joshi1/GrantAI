"""FAISS-backed VectorStore implementation."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import numpy as np

from backend.rag.interfaces import DocumentChunk, RetrievalResult, VectorStore
from backend.rag.vectorstore.exceptions import DocumentNotFoundError, VectorStoreError

logger = logging.getLogger("rag.vectorstore.faiss")


class FAISSVectorStore(VectorStore):
    """FAISS-backed vector store that persists an index and metadata mapping.

    The store keeps a separate JSON file with metadata and a FAISS index file.
    Document chunk identifiers are mapped to integer IDs used by FAISS.
    """

    def __init__(self, index_path: str, dim: int, metric: str = "IP"):
        self.index_path = Path(index_path)
        self.meta_path = self.index_path.with_suffix(self.index_path.suffix + ".meta.json")
        self.dim = dim
        self.metric = metric.upper()

        self._index: Optional[faiss.Index] = None
        # mapping from int id -> metadata dict including chunk_id, content, metadata
        self._id_to_meta: Dict[int, Dict] = {}
        # mapping from chunk_id -> int id
        self._chunkid_to_int: Dict[str, int] = {}
        self._next_id = 1

        if self.index_path.exists():
            try:
                self.load()
            except Exception:
                logger.exception("Failed to load existing FAISS index; creating new index.")
                self.create_index(self.dim)
        else:
            self.create_index(self.dim)

    def create_index(self, dim: int) -> None:
        """Create a new FAISS index with the configured metric."""
        logger.info("Creating FAISS index dim=%d metric=%s", dim, self.metric)
        if self.metric == "IP":
            index = faiss.IndexFlatIP(dim)
        else:
            index = faiss.IndexFlatL2(dim)

        # use ID map to allow custom integer ids and deletions
        self._index = faiss.IndexIDMap(index)
        self._id_to_meta = {}
        self._chunkid_to_int = {}
        self._next_id = 1

    def save_index(self) -> None:
        """Persist the FAISS index and metadata to disk."""
        if self._index is None:
            raise VectorStoreError("Index not initialized")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Saving FAISS index to %s", self.index_path)
        faiss.write_index(self._index, str(self.index_path))

        logger.info("Saving metadata to %s", self.meta_path)
        with open(self.meta_path, "w", encoding="utf-8") as fh:
            json.dump({
                "next_id": self._next_id,
                "id_to_meta": self._id_to_meta,
                "chunkid_to_int": self._chunkid_to_int,
            }, fh, ensure_ascii=False, indent=2)

    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks and their embeddings to the store.

        Chunks and embeddings must be aligned by index.
        """
        if self._index is None:
            raise VectorStoreError("Index not initialized")

        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunks and embeddings length mismatch")

        vecs = np.array(embeddings, dtype=np.float32)
        ids = []
        for chunk in chunks:
            if chunk.id in self._chunkid_to_int:
                # overwrite existing mapping by creating a new id then deleting old
                old_int = self._chunkid_to_int[chunk.id]
                try:
                    self._index.remove_ids(np.array([old_int], dtype=np.int64))
                except Exception:
                    logger.debug("Failed to remove old id %s during add_documents", old_int)

            int_id = self._next_id
            self._next_id += 1
            ids.append(int_id)

            self._chunkid_to_int[chunk.id] = int_id
            self._id_to_meta[int_id] = {
                "chunk_id": chunk.id,
                "content": chunk.content,
                "metadata": chunk.metadata,
            }

        ids_np = np.array(ids, dtype=np.int64)
        try:
            self._index.add_with_ids(vecs, ids_np)
        except Exception as exc:
            message = f"Failed to add vectors to FAISS index: {exc}"
            logger.exception(message)
            raise VectorStoreError(message) from exc

    def update_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Update documents by deleting existing entries and adding new vectors."""
        # reuse add_documents which will attempt to remove old ids
        self.add_documents(chunks, embeddings)

    def persist(self) -> None:
        """Persist the current index and metadata mapping to disk."""
        self.save_index()

    def load(self) -> None:
        """Reload the index and metadata mapping from disk."""
        if not self.index_path.exists():
            raise VectorStoreError(f"Index file not found: {self.index_path}")

        logger.info("Loading FAISS index from %s", self.index_path)
        self._index = faiss.read_index(str(self.index_path))

        if self.meta_path.exists():
            with open(self.meta_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                self._next_id = int(data.get("next_id", 1))
                self._id_to_meta = {int(k): v for k, v in data.get("id_to_meta", {}).items()}
                self._chunkid_to_int = {k: int(v) for k, v in data.get("chunkid_to_int", {}).items()}
        else:
            self._id_to_meta = {}
            self._chunkid_to_int = {}

    def delete_documents(self, chunk_ids: List[str]) -> None:
        """Delete documents by their chunk identifiers."""
        if self._index is None:
            raise VectorStoreError("Index not initialized")

        int_ids = []
        for cid in chunk_ids:
            int_id = self._chunkid_to_int.get(cid)
            if int_id is None:
                raise DocumentNotFoundError(f"Chunk id not found: {cid}")
            int_ids.append(int_id)

        try:
            self._index.remove_ids(np.array(int_ids, dtype=np.int64))
        except Exception as exc:
            message = f"Failed to remove ids from FAISS index: {exc}"
            logger.exception(message)
            raise VectorStoreError(message) from exc

        for int_id in int_ids:
            meta = self._id_to_meta.pop(int(int_id), None)
            if meta:
                self._chunkid_to_int.pop(meta.get("chunk_id"), None)

    def _apply_metadata_filter(self, candidates: List[int], metadata_filter: Optional[Dict]) -> List[int]:
        if not metadata_filter:
            return candidates

        filtered = []
        for int_id in candidates:
            meta = self._id_to_meta.get(int(int_id), {})
            md = meta.get("metadata", {})
            match = True
            for k, v in metadata_filter.items():
                if md.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(int_id)

        return filtered

    def search(self, query_embedding: List[float], top_k: int, metadata_filter: Dict[str, object] | None = None) -> List[RetrievalResult]:
        """Search for top-k similar chunks to the provided embedding.

        Metadata filtering is applied after nearest-neighbor search to prune results.
        """
        if self._index is None:
            raise VectorStoreError("Index not initialized")

        if not query_embedding:
            return []

        q = np.array([query_embedding], dtype=np.float32)
        try:
            distances, ids = self._index.search(q, top_k * 2)
        except Exception as exc:
            message = f"FAISS search failed: {exc}"
            logger.exception(message)
            raise VectorStoreError(message) from exc

        ids_list = [int(i) for i in ids[0] if i != -1]
        ids_list = self._apply_metadata_filter(ids_list, metadata_filter)

        # trim to requested top_k
        results: List[RetrievalResult] = []
        for rank, int_id in enumerate(ids_list[:top_k]):
            meta = self._id_to_meta.get(int(int_id))
            if not meta:
                continue

            score = float(distances[0][rank]) if distances.size > 0 else 0.0
            results.append(
                RetrievalResult(
                    chunk_id=str(meta.get("chunk_id")),
                    content=str(meta.get("content")),
                    metadata=dict(meta.get("metadata", {})),
                    score=score,
                )
            )

        return results
