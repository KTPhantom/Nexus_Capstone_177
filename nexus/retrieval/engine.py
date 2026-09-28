"""
Comparative Retrieval Engine Orchestrator.
Hosts:
1. BM25 Lexical Baseline
2. Naive Raw Code Dense Embedding Baseline
3. Proposed Nexus Component Pipeline (AST + Noise Filter + Composite Representation + HNSW + MMR)
"""

from typing import List, Dict, Tuple, Optional
import numpy as np

from nexus.parser.models import ComponentMetadata
from nexus.indexing.embedder import DenseEmbedder
from nexus.indexing.hnsw_index import HNSWIndex
from nexus.indexing.mmr_reranker import APIRecMMRReranker
from nexus.indexing.vector_store import ComponentVectorStore, SearchResult
from .baseline_bm25 import BM25Retriever


class NaiveRawCodePipeline:
    """
    Baseline that embeds raw, unparsed TSX source code directly into dense vectors
    without AST analysis, Tailwind noise removal, or MMR diversity re-ranking.
    """

    def __init__(self, embedder: DenseEmbedder):
        self.embedder = embedder
        self.raw_documents: Dict[str, str] = {}
        self.embeddings: Dict[str, np.ndarray] = {}

    def index(self, raw_docs: Dict[str, str]):
        self.raw_documents = raw_docs
        doc_ids = list(raw_docs.keys())
        texts = [raw_docs[cid] for cid in doc_ids]
        vectors = self.embedder.embed_texts(texts)
        for cid, vec in zip(doc_ids, vectors):
            self.embeddings[cid] = vec

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if not self.embeddings:
            return []
        query_vec = self.embedder.embed_query(query)
        scores = []
        for cid, vec in self.embeddings.items():
            dot = float(np.dot(query_vec, vec))
            scores.append((cid, dot))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class RetrievalEngine:
    """
    Unified retrieval orchestrator supporting comparative benchmarking.
    """

    def __init__(self, embedder: Optional[DenseEmbedder] = None):
        self.embedder = embedder or DenseEmbedder()
        self.nexus_store = ComponentVectorStore(embedder=self.embedder)
        self.bm25 = BM25Retriever()
        self.naive_dense = NaiveRawCodePipeline(embedder=self.embedder)
        self.raw_sources: Dict[str, str] = {}

    def index_components(self, components: List[ComponentMetadata], raw_sources: Dict[str, str]):
        self.raw_sources = raw_sources

        # 1. Index Nexus Store
        for comp in components:
            self.nexus_store.add_component(comp)

        # 2. Index BM25
        self.bm25.index(raw_sources)

        # 3. Index Naive Dense
        self.naive_dense.index(raw_sources)

    def search_nexus(
        self,
        query: str,
        top_k: int = 5,
        use_mmr: bool = True,
        lambda_param: float = 0.75,
        domain_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        return self.nexus_store.search(
            query=query,
            top_k=top_k,
            use_mmr=use_mmr,
            lambda_param=lambda_param,
            domain_filter=domain_filter,
        )

    def search_bm25(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        return self.bm25.search(query, top_k=top_k)

    def search_naive_dense(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        return self.naive_dense.search(query, top_k=top_k)
