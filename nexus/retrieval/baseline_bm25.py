"""
BM25 Lexical Retrieval Baseline.
Implements Okapi BM25 ranking function for code search benchmarking (Robertson & Zaragoza 2009).
"""

import math
import re
from typing import List, Dict, Tuple
from collections import Counter


class BM25Retriever:
    """
    Okapi BM25 Lexical Retriever operating on raw code documents.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lens: Dict[str, int] = {}
        self.doc_frequencies: Dict[str, int] = {}  # term -> num docs containing term
        self.doc_term_freqs: Dict[str, Counter] = {}  # doc_id -> Counter(terms)
        self.doc_ids: List[str] = []

    def _tokenize(self, text: str) -> List[str]:
        # Split on non-alphanumeric characters, CamelCase transitions, and underscores
        words = re.findall(r"[A-Za-z0-9]+", text)
        tokens = []
        for word in words:
            # Handle CamelCase (e.g. PomodoroTimer -> pomodoro, timer)
            splits = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", word)
            for s in splits:
                tokens.append(s.lower())
        return tokens

    def index(self, documents: Dict[str, str]):
        """
        documents: Dict[doc_id, raw_code_or_text]
        """
        self.corpus_size = len(documents)
        self.doc_ids = list(documents.keys())
        total_len = 0

        self.doc_frequencies.clear()
        self.doc_term_freqs.clear()
        self.doc_lens.clear()

        for doc_id, text in documents.items():
            tokens = self._tokenize(text)
            self.doc_lens[doc_id] = len(tokens)
            total_len += len(tokens)

            tf = Counter(tokens)
            self.doc_term_freqs[doc_id] = tf

            for term in set(tokens):
                self.doc_frequencies[term] = self.doc_frequencies.get(term, 0) + 1

        self.avg_doc_len = total_len / max(1, self.corpus_size)

    def _idf(self, term: str) -> float:
        n_q = self.doc_frequencies.get(term, 0)
        # Standard Lucene/Okapi smoothed IDF
        return math.log(1.0 + (self.corpus_size - n_q + 0.5) / (n_q + 0.5))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        query_tokens = self._tokenize(query)
        if not query_tokens or self.corpus_size == 0:
            return []

        scores: Dict[str, float] = {}

        for doc_id in self.doc_ids:
            score = 0.0
            doc_len = self.doc_lens[doc_id]
            tf = self.doc_term_freqs[doc_id]

            for term in query_tokens:
                if term not in self.doc_frequencies:
                    continue
                f_q = tf.get(term, 0)
                if f_q == 0:
                    continue

                idf = self._idf(term)
                denom = f_q + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1e-9, self.avg_doc_len)))
                term_score = idf * (f_q * (self.k1 + 1.0)) / max(1e-9, denom)
                score += term_score

            if score > 0:
                scores[doc_id] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
