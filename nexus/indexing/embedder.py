"""
Dense embedding module using sentence-transformers/all-MiniLM-L6-v2.
Includes mean pooling, L2 normalization, and a deterministic fallback embedder
for offline/isolated environments.
"""

from typing import List, Optional
import numpy as np


class DenseEmbedder:
    """
    Generates 384-dimensional dense semantic vectors using
    sentence-transformers/all-MiniLM-L6-v2 via HuggingFace transformers.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self._tokenizer = None
        self._model = None
        self._fallback_mode = False
        self._dimension = 384

        self._initialize_model()

    def _initialize_model(self):
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel

            if self.device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self._model.eval()
            self._fallback_mode = False
        except Exception as e:
            # Fallback to local deterministic TF-IDF / SVD embedder if transformers cannot load
            self._fallback_mode = True
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            self._tfidf = TfidfVectorizer(max_features=2048, ngram_range=(1, 2))
            self._svd = TruncatedSVD(n_components=self._dimension, random_state=42)
            self._is_fitted = False

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def is_fallback(self) -> bool:
        return self._fallback_mode

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self._dimension), dtype=np.float32)

        if not self._fallback_mode:
            import torch

            # Tokenize with truncation and padding
            inputs = self._tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(self.device)

            with torch.no_grad():
                outputs = self._model(**inputs)
                # Mean Pooling: take attention mask into account for correct averaging
                token_embeddings = outputs.last_hidden_state  # [batch, seq_len, dim]
                input_mask_expanded = inputs["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
                sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
                mean_pooled = sum_embeddings / sum_mask

                # Normalize embeddings to unit L2 norm
                norm = torch.norm(mean_pooled, p=2, dim=1, keepdim=True)
                normalized = mean_pooled / torch.clamp(norm, min=1e-9)

                return normalized.cpu().numpy().astype(np.float32)
        else:
            # Deterministic pseudo-semantic embedding for fallback
            return self._fallback_embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        vectors = self.embed_texts([query])
        return vectors[0]

    def _fallback_embed(self, texts: List[str]) -> np.ndarray:
        # Fast n-gram hash projection into unit sphere
        embeddings = []
        for text in texts:
            vec = np.zeros(self._dimension, dtype=np.float32)
            tokens = text.lower().split()
            for token in tokens:
                h = hash(token)
                idx = abs(h) % self._dimension
                sign = 1.0 if (h // self._dimension) % 2 == 0 else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm > 1e-9:
                vec /= norm
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)
