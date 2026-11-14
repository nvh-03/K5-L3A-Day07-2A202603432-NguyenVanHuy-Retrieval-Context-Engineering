"""Aggregate manually reviewed results for the advanced benchmark."""
import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def evidence_groups(question: dict[str, Any]) -> list[tuple[int, list[int]]]:
    gold = question.get('gold', [])
    if not isinstance(gold, list):
        raise ValueError(f"{question.get('id')}: gold must be a list")
    configured = question.get('evidence_groups')
    if configured is None:
        return [(1, [index]) for index in range(len(gold))]

    groups = []
    for group in configured:
        indices = group.get('gold_indices')
        minimum = group.get('min_matches')
        if (
            not isinstance(indices, list)
            or not indices
            or any(not isinstance(index, int) or isinstance(index, bool) for index in indices)
            or any(index < 0 or index >= len(gold) for index in indices)
            or not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or minimum < 1
            or minimum > len(indices)
        ):
            raise ValueError(f"{question.get('id')}: invalid evidence group {group!r}")
        groups.append((minimum, indices))
    if not groups and question.get('answerable', True):
        raise ValueError(f"{question.get('id')}: answerable question needs evidence groups")
    return groups


def context_ids(trace: dict[str, Any]) -> list[str]:
    for event in reversed(trace.get('events', [])):
        ids = event.get('context_ids')
        if isinstance(ids, list):
            return [chunk_id for chunk_id in ids if isinstance(chunk_id, str)]
    return []


def evidence_coverage(
    question: dict[str, Any],
    chunks: dict[str, dict[str, Any]],
    candidate_ids: list[str],
) -> dict[str, Any]:
    gold = question.get('gold', [])
    matched_indices = set()
    for chunk_id in candidate_ids:
        chunk = chunks.get(chunk_id)
        if not chunk:
            continue
        for index, item in enumerate(gold):
            if (
                chunk.get('source_id') == item.get('source_id')
                and chunk.get('page') == item.get('page')
                and item.get('evidence', '') in chunk.get('text', '')
            ):
                matched_indices.add(index)

    groups = []
    for minimum, indices in evidence_groups(question):
        matched = sorted(matched_indices.intersection(indices))
        groups.append({
            'required': minimum,
            'matched': len(matched),
            'gold_indices': indices,
            'matched_gold_indices': matched,
            'covered': len(matched) >= minimum,
        })
    return {
        'covered': bool(groups) and all(group['covered'] for group in groups),
        'groups': groups,
        'matched_gold_indices': sorted(matched_indices),
    }


def _unique_map(items: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result = {}
    for item in items:
        identifier = item.get(key)
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"{label} entry is missing {key}")
        if identifier in result:
            raise ValueError(f"duplicate {label} for {identifier}")
        result[identifier] = item
    return result


def aggregate(
    questions: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    question_map = _unique_map(questions, 'id', 'question')
    trace_map = _unique_map(traces, 'query_id', 'trace')
    review_map = _unique_map(reviews, 'query_id', 'review')
    unexpected_traces = sorted(set(trace_map) - set(question_map))
    if unexpected_traces:
        raise ValueError(f"traces contain questions outside this split: {unexpected_traces}")
    if set(review_map) != set(question_map):
        missing = sorted(set(question_map) - set(review_map))
        unexpected = sorted(set(review_map) - set(question_map))
        raise ValueError(f"reviews must cover this split exactly; missing={missing}, unexpected={unexpected}")

    chunk_map = _unique_map(chunks, 'id', 'chunk')
    cases = []
    latencies = []
    cost_values = []
    errors = 0
    cer_n = 0
    cer_N = 0
    grades = {0: 0, 1: 0, 2: 0}
    abstention_n = 0
    abstention_N = 0

    for question in questions:
        query_id = question['id']
        trace = trace_map.get(query_id, {
            'query_id': query_id,
            'status': 'error',
            'error': 'Missing trace',
            'citations': [],
            'events': [],
        })
        review = review_map[query_id]
        status = trace.get('status', 'error')
        citations = trace.get('citations', [])
        if not isinstance(citations, list):
            raise ValueError(f"{query_id}: citations must be a list")
        is_error = status == 'error' or query_id not in trace_map
        errors += int(is_error)

        elapsed = trace.get('elapsed_ms')
        if isinstance(elapsed, (int, float)):
            latencies.append(float(elapsed))
        cost = trace.get('cost_usd')
        if isinstance(cost, (int, float)):
            cost_values.append(float(cost))

        answerable = question.get('answerable', True)
        context_check = evidence_coverage(question, chunk_map, context_ids(trace)) if answerable else None
        citation_check = evidence_coverage(question, chunk_map, citations) if answerable else None
        if answerable and not is_error:
            cer_N += 1
            cer_n += int(bool(context_check and context_check['covered']))

        if answerable:
            grade = review.get('answer_grade')
            support = review.get('citation_support')
            if not isinstance(grade, int) or isinstance(grade, bool) or grade not in (0, 1, 2):
                raise ValueError(f"{query_id}: answerable review needs answer_grade 0, 1, or 2")
            if (
                not isinstance(support, list)
                or len(support) != len(citations)
                or any(not isinstance(value, bool) for value in support)
            ):
                raise ValueError(f"{query_id}: citation_support must contain one boolean per citation")
            if 'abstention_correct' in review:
                raise ValueError(f"{query_id}: answerable review must not use abstention_correct")
            grades[grade] += 1
            passed = (
                not is_error
                and status == 'answered'
                and bool(citations)
                and grade == 2
                and all(support)
                and bool(citation_check and citation_check['covered'])
            )
            reason = review.get('reason', '')
        else:
            abstention = review.get('abstention_correct')
            if not isinstance(abstention, bool):
                raise ValueError(f"{query_id}: unanswerable review needs a boolean abstention_correct")
            support = review.get('citation_support')
            if (
                not isinstance(support, list)
                or len(support) != len(citations)
                or any(not isinstance(value, bool) for value in support)
            ):
                raise ValueError(f"{query_id}: citation_support must contain one boolean per citation")
            if 'answer_grade' in review:
                raise ValueError(f"{query_id}: unanswerable review must not use answer_grade")
            abstention_N += 1
            abstention_n += int(abstention and not is_error)
            passed = not is_error and abstention
            reason = review.get('reason', '')

        cases.append({
            'query_id': query_id,
            'category': question.get('category', 'Text'),
            'answerable': answerable,
            'status': status,
            'passed': passed,
            'reason': reason,
            'context_evidence': context_check,
            'citation_evidence': citation_check,
        })

    total = len(questions)
    passed_count = sum(case['passed'] for case in cases)
    categories = {}
    for category in sorted({question.get('category', 'Text') for question in questions}):
        category_cases = [case for case in cases if case['category'] == category]
        category_passed = sum(case['passed'] for case in category_cases)
        categories[category] = {
            'passed': category_passed,
            'total': len(category_cases),
            'rate': category_passed / len(category_cases) if category_cases else 0,
        }

    return {
        'total_questions': total,
        'passed_questions': passed_count,
        'pass_rate': passed_count / total if total else 0,
        'meets_advanced_threshold': total >= 30 and passed_count / total >= 0.9,
        'category_breakdown': categories,
        'answer_grade_distribution': {str(grade): count for grade, count in grades.items()},
        'correct_abstentions': {'n': abstention_n, 'N': abstention_N},
        'context_evidence_rate': {
            'n': cer_n,
            'N': cer_N,
            'rate': cer_n / cer_N if cer_N else None,
        },
        'errors': errors,
        'median_latency_ms': statistics.median(latencies) if latencies else None,
        'mean_latency_ms': statistics.mean(latencies) if latencies else None,
        'total_cost_usd': sum(cost_values) if len(cost_values) == total else None,
        'case_results': cases,
    }


def _load_reviews(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(payload, list):
        return payload, {}
    if isinstance(payload, dict) and isinstance(payload.get('reviews'), list):
        return payload['reviews'], {
            key: value for key, value in payload.items() if key != 'reviews'
        }
    raise ValueError('reviews file must be a JSON array or an object containing a reviews array')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chunks', default='data/bonus_chunks.json', type=Path)
    parser.add_argument('--questions', default='data/bonus_questions.json', type=Path)
    parser.add_argument('--traces', required=True, type=Path)
    parser.add_argument('--reviews', required=True, type=Path)
    parser.add_argument('--split', choices=('dev', 'test'), default='test')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()

    chunks = json.loads(args.chunks.read_text(encoding='utf-8'))
    questions = [
        question for question in json.loads(args.questions.read_text(encoding='utf-8'))
        if question.get('split') == args.split
    ]
    traces = json.loads(args.traces.read_text(encoding='utf-8'))
    reviews, review_metadata = _load_reviews(args.reviews)
    summary = aggregate(questions, traces, reviews, chunks)
    summary.update(review_metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(
        f"{args.split}: {summary['passed_questions']}/{summary['total_questions']} passed "
        f"({summary['pass_rate']:.1%}); errors={summary['errors']}; "
        f"CER={summary['context_evidence_rate']['n']}/{summary['context_evidence_rate']['N']}"
    )


if __name__ == '__main__':
    main()
