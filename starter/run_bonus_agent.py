"""Run and evaluate the agent over the bonus dataset (dev or test split)."""
import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

from agentic import OpenAICompatibleController, run_agent
from baseline import validate
from bonus_metrics import context_ids, evidence_coverage
from retrieval import LexicalRetriever
from run_agent import load_env_file


def evaluate_question(trace: dict[str, Any], question: dict[str, Any], chunks_map: dict[str, Any]) -> dict[str, Any]:
    answerable = question.get('answerable', True)
    status = trace['status']
    citations = trace.get('citations', [])
    answer = trace.get('answer', '')
    context_evidence = evidence_coverage(
        question, chunks_map, context_ids(trace)
    ) if answerable else None
    citation_evidence = evidence_coverage(
        question, chunks_map, citations
    ) if answerable else None

    return {
        'query_id': question['id'],
        'category': question.get('category', 'Text'),
        'answerable': answerable,
        'status': status,
        'context_evidence': context_evidence,
        'citation_evidence': citation_evidence,
        'candidate_abstention': status == 'abstain' if not answerable else None,
        'citations': citations,
        'answer': answer,
        'expected_answer': question.get('expected_answer', question.get('absence_reason', '')),
        'manual_review_required': True,
        'note': 'This is an evidence screen only; it does not grade answer correctness or abstention safety.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chunks', default='data/bonus_chunks.json', type=Path)
    parser.add_argument('--questions', default='data/bonus_questions.json', type=Path)
    parser.add_argument('--split', required=True, choices=('dev', 'test'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--budget', type=int, default=2000)
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--max-searches', type=int, default=4)
    args = parser.parse_args()

    load_env_file(Path(__file__).resolve().parents[1] / '.env')
    chunks = json.loads(args.chunks.read_text(encoding='utf-8'))
    questions = json.loads(args.questions.read_text(encoding='utf-8'))
    selected = [q for q in questions if q.get('split') == args.split]

    validate(chunks, selected)

    chunks_map = {c['id']: c for c in chunks}
    controller = OpenAICompatibleController.from_env()
    retriever = LexicalRetriever(chunks)

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    traces = []
    automatic_checks = []
    latencies = []

    print(f"Starting agent run on split '{args.split}' with {len(selected)} questions...")

    for i, question in enumerate(selected, start=1):
        started = time.perf_counter()
        print(f"[{i}/{len(selected)}] Processing {question['id']} ({question.get('category')}): {question['question'][:60]}...")
        
        try:
            result = run_agent(
                question['question'],
                controller,
                retriever,
                filters=question.get('filter'),
                max_searches=args.max_searches,
                top_k=args.top_k,
                budget=args.budget,
            )
            elapsed_ms = (time.perf_counter() - started) * 1000
            latencies.append(elapsed_ms)
            
            trace = {
                'query_id': question['id'],
                'split': question['split'],
                'category': question.get('category'),
                'question': question['question'],
                'answerable': question.get('answerable', True),
                'elapsed_ms': elapsed_ms,
                **result
            }
            traces.append(trace)
            
            check = evaluate_question(trace, question, chunks_map)
            automatic_checks.append(check)
            if not question.get('answerable', True):
                res_str = "ABSTENTION CANDIDATE" if check['candidate_abstention'] else "NEEDS REVIEW"
            else:
                evidence_ready = (
                    check['context_evidence']['covered']
                    and check['citation_evidence']['covered']
                )
                res_str = "EVIDENCE READY" if evidence_ready else "NEEDS REVIEW"
            print(f"    -> {res_str} | Status: {result['status']} | Time: {elapsed_ms:.1f}ms")

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            latencies.append(elapsed_ms)
            print(f"    -> ERROR: {exc}")
            trace = {
                'query_id': question['id'],
                'split': question['split'],
                'category': question.get('category'),
                'question': question['question'],
                'answerable': question.get('answerable', True),
                'elapsed_ms': elapsed_ms,
                'status': 'error',
                'error': str(exc),
                'citations': [],
                'answer': '',
                'events': []
            }
            traces.append(trace)
            automatic_checks.append({
                'query_id': question['id'],
                'category': question.get('category'),
                'answerable': question.get('answerable', True),
                'status': 'error',
                'context_evidence': None,
                'citation_evidence': None,
                'candidate_abstention': False,
                'citations': [],
                'answer': '',
                'manual_review_required': True,
                'note': f"Execution error; counted as a failure by the manual metrics step: {exc}",
            })

    total_q = len(selected)
    answerable_checks = [
        check for check in automatic_checks
        if check['answerable'] and check['status'] != 'error'
    ]
    cer_count = sum(
        1 for check in answerable_checks
        if check['context_evidence'] and check['context_evidence']['covered']
    )
    citation_count = sum(
        1 for check in answerable_checks
        if check['citation_evidence'] and check['citation_evidence']['covered']
    )

    summary = {
        'split': args.split,
        'model': controller.model,
        'base_url': controller.base_url,
        'run_config': {
            'top_k': args.top_k,
            'max_searches': args.max_searches,
            'context_budget': args.budget,
        },
        'total_questions': total_q,
        'answerable_questions': sum(1 for q in selected if q.get('answerable', True)),
        'manual_review_required': total_q,
        'context_evidence_rate': cer_count / len(answerable_checks) if answerable_checks else None,
        'cer_n': cer_count,
        'cer_N': len(answerable_checks),
        'citation_evidence_complete_n': citation_count,
        'citation_evidence_complete_N': len(answerable_checks),
        'median_latency_ms': statistics.median(latencies) if latencies else 0,
        'mean_latency_ms': statistics.mean(latencies) if latencies else 0,
        'errors': sum(1 for t in traces if t.get('status') == 'error'),
        'evaluation_note': (
            'Automated evidence checks only. Answer correctness, citation support, and safe abstention '
            'must be manually reviewed; no pass rate is computed here.'
        ),
    }

    (output_dir / 'traces.json').write_text(json.dumps(traces, indent=2, ensure_ascii=False), encoding='utf-8')
    (output_dir / 'automatic_checks.json').write_text(
        json.dumps(automatic_checks, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    (output_dir / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')

    print("\n" + "=" * 50)
    print(f"BENCHMARK {args.split.upper()} AUTOMATIC EVIDENCE SUMMARY")
    print(f"Manual reviews required: {total_q}")
    print(f"Complete context evidence: {cer_count}/{len(answerable_checks)}")
    print(f"Complete cited evidence: {citation_count}/{len(answerable_checks)}")
    print(f"Median Latency: {summary['median_latency_ms']:.1f} ms")
    print("=" * 50)

if __name__ == '__main__':
    main()

