"""Compare lexical, Day 6 dense, and hybrid retrieval on one selected split."""
import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from baseline import hit, validate
from retrieval import DenseRetriever, HybridRetriever, LexicalRetriever


def evaluate_method(
    name: str,
    retriever: Any,
    questions: list[dict[str, Any]],
    *,
    top_k: int = 3,
    query_field: str = 'question',
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    traces = []
    for question in questions:
        query = question.get(query_field)
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"{question['id']}: thiếu truy vấn hợp lệ trong trường {query_field}")
        filters = question.get('filter')
        started = time.perf_counter()
        results = retriever.search(query, filters=filters, top_k=top_k)
        elapsed_ms = (time.perf_counter() - started) * 1000
        answerable = question.get('answerable', True)
        marked = [
            {
                **row,
                'evidence_hit': answerable and hit(row, question['gold']),
            }
            for row in results
        ]
        traces.append({
            'query_id': question['id'],
            'split': question['split'],
            'question': question['question'],
            'query': query,
            'query_field': query_field,
            'method': name,
            'filters': filters,
            'top_k': top_k,
            'answerable': answerable,
            'results': marked,
            'elapsed_ms': elapsed_ms,
        })

    answerable_traces = [trace for trace in traces if trace['answerable']]
    answerable_count = len(answerable_traces)
    hit1 = sum(bool(trace['results'] and trace['results'][0]['evidence_hit']) for trace in answerable_traces)
    hit3 = sum(any(row['evidence_hit'] for row in trace['results'][:3]) for trace in answerable_traces)
    summary = {
        'method': name,
        'query_field': query_field,
        'config': retriever.config,
        'questions': len(traces),
        'answerable_questions': answerable_count,
        'unanswerable_questions': len(traces) - answerable_count,
        'hit_at_1': {'n': hit1, 'N': answerable_count, 'rate': hit1 / answerable_count if answerable_count else None},
        'evidence_hit_at_3': {'n': hit3, 'N': answerable_count, 'rate': hit3 / answerable_count if answerable_count else None},
        'median_ms': statistics.median(trace['elapsed_ms'] for trace in traces) if traces else None,
    }
    return traces, summary


def write_method_outputs(output: Path, split: str, traces: list[dict[str, Any]],
                         summary: dict[str, Any]) -> None:
    method = summary['method']
    (output / f'{split}-{method}-traces.json').write_text(
        json.dumps(traces, ensure_ascii=True, indent=2) + '\n', encoding='utf-8'
    )
    (output / f'{split}-{method}-summary.json').write_text(
        json.dumps(summary, ensure_ascii=True, indent=2) + '\n', encoding='utf-8'
    )


def _load_day6_dense(
    day6_root: Path,
    *,
    strategy: str,
    database_url: str | None,
    model_name: str | None,
    model_revision: str | None,
) -> DenseRetriever:
    starter_dir = day6_root.resolve() / 'starter'
    if not (starter_dir / 'src' / 'store.py').is_file():
        raise FileNotFoundError(f'Day 6 starter source not found under {starter_dir}')
    sys.path.insert(0, str(starter_dir))
    try:
        from dotenv import load_dotenv
        from src.embeddings import SentenceTransformerEmbedder
        from src.run import DEFAULT_MODEL, DEFAULT_MODEL_REVISION
        from src.store import PgVectorStore
    except ImportError as exc:
        raise RuntimeError(
            'Cần cài dependencies trong starter/requirements.txt của repo Day 6 để chạy dense retrieval.'
        ) from exc

    load_dotenv(starter_dir / '.env')
    url = database_url or os.getenv('DATABASE_URL')
    if not url:
        raise ValueError('Thiếu DATABASE_URL: dùng --database-url hoặc cấu hình starter/.env của Day 6.')
    selected_model = model_name or DEFAULT_MODEL
    selected_revision = model_revision
    if selected_revision is None and selected_model == DEFAULT_MODEL:
        selected_revision = DEFAULT_MODEL_REVISION
    embedder = SentenceTransformerEmbedder(selected_model, revision=selected_revision)
    store = PgVectorStore(url, embedder.dimensions)
    return DenseRetriever(store, embedder, strategy=strategy)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chunks', required=True, type=Path)
    parser.add_argument('--questions', required=True, type=Path)
    parser.add_argument('--split', required=True, choices=('dev', 'test'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--methods', nargs='+', choices=('lexical', 'dense', 'hybrid'),
                        default=['lexical', 'dense', 'hybrid'])
    parser.add_argument('--day6-root', type=Path, help='Root folder của repo Day 6; cần cho dense/hybrid.')
    parser.add_argument('--database-url', help='PostgreSQL connection string; mặc định dùng DATABASE_URL của Day 6.')
    parser.add_argument('--strategy', default='B', help='Tên strategy đã được index trong Day 6 (mặc định B).')
    parser.add_argument('--embedding-model', help='Mặc định model đã cấu hình trong starter Day 6.')
    parser.add_argument('--embedding-revision', help='Mặc định revision đã cấu hình trong starter Day 6.')
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--candidate-k', type=int, default=20, help='Candidates lấy từ từng retriever cho hybrid.')
    parser.add_argument('--rrf-k', type=int, default=60, help='Hằng số làm mượt reciprocal-rank fusion.')
    parser.add_argument('--query-field', choices=('question', 'retrieval_query_en'), default='question',
                        help='Trường truy vấn; dùng retrieval_query_en cho thí nghiệm query tiếng Anh.')
    args = parser.parse_args()
    if args.top_k <= 0 or args.candidate_k <= 0 or args.rrf_k <= 0:
        parser.error('--top-k, --candidate-k và --rrf-k phải dương.')
    if any(method in args.methods for method in ('dense', 'hybrid')) and not args.day6_root:
        parser.error('--day6-root bắt buộc khi chạy dense hoặc hybrid.')

    chunks = json.loads(args.chunks.read_text(encoding='utf-8'))
    questions = json.loads(args.questions.read_text(encoding='utf-8'))
    selected = [question for question in questions if question.get('split') == args.split]
    validate(chunks, selected)
    if args.query_field != 'question':
        missing_queries = [
            question['id'] for question in selected
            if not isinstance(question.get(args.query_field), str) or not question[args.query_field].strip()
        ]
        if missing_queries:
            raise ValueError(f"Thiếu truy vấn {args.query_field} cho: {', '.join(missing_queries)}")

    lexical = LexicalRetriever(chunks) if any(method in args.methods for method in ('lexical', 'hybrid')) else None
    dense = _load_day6_dense(
        args.day6_root,
        strategy=args.strategy,
        database_url=args.database_url,
        model_name=args.embedding_model,
        model_revision=args.embedding_revision,
    ) if any(method in args.methods for method in ('dense', 'hybrid')) else None
    retrievers = {
        'lexical': lexical,
        'dense': dense,
        'hybrid': HybridRetriever(dense, lexical, candidate_k=args.candidate_k, rrf_k=args.rrf_k)
        if dense is not None and lexical is not None else None,
    }

    args.output.mkdir(parents=True, exist_ok=True)
    summaries = []
    for method in args.methods:
        method_traces, summary = evaluate_method(
            method, retrievers[method], selected, top_k=args.top_k, query_field=args.query_field
        )
        write_method_outputs(args.output, args.split, method_traces, summary)
        summaries.append(summary)

    print(json.dumps({'split': args.split, 'top_k': args.top_k, 'methods': summaries},
                     ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
