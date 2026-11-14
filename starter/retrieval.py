"""Dense, lexical, and reciprocal-rank-fusion retrievers for Day 7."""
from typing import Any, Protocol

from baseline import TfidfIndex


class VectorStore(Protocol):
    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        ...


class QueryEmbedder(Protocol):
    def embed_query(self, question: str) -> list[float]:
        ...


def _validate_search(query: str, top_k: int, filters: dict[str, Any] | None) -> None:
    if not isinstance(query, str) or not query.strip():
        raise ValueError('query phải là chuỗi không rỗng')
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError('top_k phải là số nguyên dương')
    if filters is not None and not isinstance(filters, dict):
        raise ValueError('filters phải là object hoặc None')


def _normalize_dense_result(row: dict[str, Any]) -> dict[str, Any]:
    required = ('chunk_id', 'document_id', 'source', 'page', 'text', 'score', 'metadata')
    missing = [key for key in required if key not in row]
    if missing:
        raise ValueError(f'Day 6 vector store thiếu trường: {missing}')
    return {
        'id': row['chunk_id'],
        'source_id': row['document_id'],
        'source': row['source'],
        'page': row['page'],
        'text': row['text'],
        'metadata': row['metadata'],
        'score': float(row['score']),
        'method': 'dense',
    }


class DenseRetriever:
    """Adapt Day 6 PgVectorStore and query embedder to the Day 7 retriever contract."""

    def __init__(self, store: VectorStore, embedder: QueryEmbedder, *, strategy: str = 'B') -> None:
        if not strategy:
            raise ValueError('strategy phải là chuỗi không rỗng')
        self.store = store
        self.embedder = embedder
        self.strategy = strategy
        self.config = {'strategy': strategy, 'similarity': 'cosine'}

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        _validate_search(query, top_k, filters)
        vector = self.embedder.embed_query(query)
        rows = self.store.search(self.strategy, vector, top_k=top_k, filters=filters)
        results = [_normalize_dense_result(row) for row in rows]
        if len(results) > top_k or len({row['id'] for row in results}) != len(results):
            raise ValueError('Day 6 vector store phải trả tối đa top_k chunk ID duy nhất')
        return [
            {**row, 'rank': rank}
            for rank, row in enumerate(results, start=1)
        ]


class LexicalRetriever:
    """TF-IDF lexical retrieval over the exported Day 6 chunks."""

    def __init__(self, chunks: list[dict[str, Any]]) -> None:
        self.index = TfidfIndex(chunks)
        self.config = {'algorithm': 'tfidf'}

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        _validate_search(query, top_k, filters)
        rows = self.index.search(query, top_k=top_k, filters=filters)
        return [
            {**row, 'method': 'lexical', 'rank': rank}
            for rank, row in enumerate(rows, start=1)
        ]


class HybridRetriever:
    """Fuse dense and lexical candidate rankings with reciprocal rank fusion."""

    def __init__(
        self,
        dense: DenseRetriever,
        lexical: LexicalRetriever,
        *,
        candidate_k: int = 20,
        rrf_k: int = 60,
    ) -> None:
        if candidate_k <= 0 or rrf_k <= 0:
            raise ValueError('candidate_k và rrf_k phải dương')
        self.dense = dense
        self.lexical = lexical
        self.candidate_k = candidate_k
        self.rrf_k = rrf_k
        self.config = {'fusion': 'reciprocal_rank_fusion', 'candidate_k': candidate_k, 'rrf_k': rrf_k}

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        _validate_search(query, top_k, filters)
        dense_rows = self.dense.search(query, filters=filters, top_k=self.candidate_k)
        lexical_rows = self.lexical.search(query, filters=filters, top_k=self.candidate_k)
        fused: dict[str, dict[str, Any]] = {}
        for rows, rank_key in ((dense_rows, 'dense_rank'), (lexical_rows, 'lexical_rank')):
            for row in rows:
                item = fused.setdefault(row['id'], {
                    key: row[key]
                    for key in ('id', 'source_id', 'source', 'page', 'text', 'metadata')
                })
                item[rank_key] = row['rank']
                item[f'{rank_key.removesuffix("_rank")}_score'] = row['score']
                item['score'] = item.get('score', 0.0) + 1.0 / (self.rrf_k + row['rank'])
        ordered = sorted(fused.values(), key=lambda row: (-row['score'], row['id']))[:top_k]
        return [
            {**row, 'method': 'hybrid_rrf', 'rank': rank}
            for rank, row in enumerate(ordered, start=1)
        ]
