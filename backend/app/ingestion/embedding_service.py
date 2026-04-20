"""Local embedding boundary with deterministic offline fallback."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence
from typing import Protocol


class EmbeddingProvider(Protocol):
    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        ...


class HashingEmbeddingProvider:
    def __init__(self, *, dimensions: int = 384) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero.")
        self.dimensions = dimensions

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"\w+", text.casefold())
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
        return _normalize(vector)


class SentenceTransformerEmbeddingProvider:
    def __init__(self, *, model_name: str, local_files_only: bool = True) -> None:
        self.model_name = model_name
        self.local_files_only = local_files_only
        self._model: object | None = None

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._load_model()
        encoded = model.encode(  # type: ignore[attr-defined]
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [list(map(float, row)) for row in encoded]

    def _load_model(self) -> object:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_name,
                local_files_only=self.local_files_only,
            )
        return self._model


class EmbeddingService:
    def __init__(
        self,
        *,
        model_name: str = "BAAI/bge-m3",
        provider: EmbeddingProvider | None = None,
    ) -> None:
        self.model_name = model_name
        self.provider = provider or HashingEmbeddingProvider()

    @classmethod
    def using_local_sentence_transformer(
        cls,
        *,
        model_name: str = "BAAI/bge-m3",
    ) -> "EmbeddingService":
        return cls(
            model_name=model_name,
            provider=SentenceTransformerEmbeddingProvider(
                model_name=model_name,
                local_files_only=True,
            ),
        )

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.provider.encode(texts)


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
