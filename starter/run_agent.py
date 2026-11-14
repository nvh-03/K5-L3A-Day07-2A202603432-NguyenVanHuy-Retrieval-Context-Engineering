"""Run the real-model agent over one selected benchmark split."""
import argparse
import json
import os
import re
import statistics
import time
from pathlib import Path
from typing import Any

from agentic import OpenAICompatibleController, run_agent
from baseline import validate
from retrieval import HybridRetriever, LexicalRetriever
from retrieval_benchmark import _load_day6_dense


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line_number, raw_line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        name, separator, value = line.partition('=')
        name = name.strip()
        value = value.strip()
        if not separator or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name):
            raise ValueError(f'Invalid .env entry at line {line_number}.')
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        os.environ.setdefault(name, value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chunks', required=True, type=Path)
    parser.add_argument('--questions', required=True, type=Path)
    parser.add_argument('--split', required=True, choices=('dev', 'test'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--method', choices=('lexical', 'dense', 'hybrid'), default='lexical')
    parser.add_argument('--day6-root', type=Path, help='Day 6 repository root; required for dense/hybrid.')
    parser.add_argument('--database-url', help='PostgreSQL URL; defaults to Day 6 DATABASE_URL.')
    parser.add_argument('--strategy', default='B')
    parser.add_argument('--embedding-model')
    parser.add_argument('--embedding-revision')
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--candidate-k', type=int, default=20)
    parser.add_argument('--rrf-k', type=int, default=60)
    parser.add_argument('--max-searches', type=int, default=4)
    parser.add_argument('--budget', type=int, default=800, help='Maximum context characters sent to the model.')
    args = parser.parse_args()
    if min(args.top_k, args.candidate_k, args.rrf_k, args.max_searches, args.budget) <= 0:
        parser.error('top-k, candidate-k, rrf-k, max-searches, and budget must be positive.')
    if args.method in ('dense', 'hybrid') and not args.day6_root:
        parser.error('--day6-root is required for dense or hybrid retrieval.')

    load_env_file(Path(__file__).resolve().parents[1] / '.env')
    chunks = json.loads(args.chunks.read_text(encoding='utf-8'))
    questions = json.loads(args.questions.read_text(encoding='utf-8'))
    selected = [question for question in questions if question.get('split') == args.split]
    validate(chunks, selected)

    controller = OpenAICompatibleController.from_env()
    lexical = LexicalRetriever(chunks) if args.method in ('lexical', 'hybrid') else None
    dense = _load_day6_dense(
        args.day6_root,
        strategy=args.strategy,
        database_url=args.database_url,
        model_name=args.embedding_model,
        model_revision=args.embedding_revision,
    ) if args.method in ('dense', 'hybrid') else None
    if args.method == 'lexical':
        retriever = lexical
    elif args.method == 'dense':
        retriever = dense
    else:
        retriever = HybridRetriever(dense, lexical, candidate_k=args.candidate_k, rrf_k=args.rrf_k)
    if retriever is None:
        raise RuntimeError(f'Không khởi tạo được retriever cho method {args.method}.')
    traces: list[dict[str, Any]] = []
    for question in selected:
        started = time.perf_counter()
        result = run_agent(
            question['question'],
            controller,
            retriever,
            filters=question.get('filter'),
            max_searches=args.max_searches,
            top_k=args.top_k,
            budget=args.budget,
        )
        traces.append({
            'query_id': question['id'],
            'split': question['split'],
            'question': question['question'],
            'answerable': question.get('answerable', True),
            'method': args.method,
            'elapsed_ms': (time.perf_counter() - started) * 1000,
            **result,
        })

    args.output.mkdir(parents=True, exist_ok=True)
    summary = {
        'split': args.split,
        'method': args.method,
        'model': controller.model,
        'retriever_config': retriever.config,
        'questions': len(traces),
        'status_counts': {
            status: sum(trace['status'] == status for trace in traces)
            for status in ('answered', 'abstain')
        },
        'median_ms': statistics.median(trace['elapsed_ms'] for trace in traces) if traces else None,
        'service_cost_usd': None,
        'service_cost_note': 'Not reported by the configured model endpoint.',
    }
    (args.output / 'traces.json').write_text(
        json.dumps(traces, ensure_ascii=True, indent=2) + '\n', encoding='utf-8'
    )
    (args.output / 'summary.json').write_text(
        json.dumps(summary, ensure_ascii=True, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
