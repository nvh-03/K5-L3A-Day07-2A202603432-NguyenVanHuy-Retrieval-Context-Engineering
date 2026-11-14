"""Aggregate agent traces with human labels; never infer grounding from citation IDs."""
import argparse
import json
from pathlib import Path


def aggregate(cases, traces, reviews):
    """Cases: id/answerable/gold; traces: query_id/status/events/citations.

    Reviews: query_id, answer_grade (0..2 for answerable), citation_support
    (one boolean per citation), and abstention_correct (boolean for unanswerable).
    Context evidence requires an exact gold quote in the final packed search context,
    matched to a retrieved chunk with the same source and page.
    Provider errors are excluded and reported.
    """
    if len({c['id'] for c in cases}) != len(cases):
        raise ValueError('case ID trùng')
    if len({r['query_id'] for r in traces}) != len(traces) or len({r['query_id'] for r in reviews}) != len(reviews):
        raise ValueError('trace/review ID trùng')
    trace_by_id = {r['query_id']: r for r in traces}
    review_by_id = {r['query_id']: r for r in reviews}
    out = {'cases': len(cases), 'provider_errors': 0, 'tool_use': {'n': 0, 'N': 0},
           'grounded_answer': {'0': 0, '1': 0, '2': 0, 'N': 0, 'mean': None},
           'context_evidence': {'n': 0, 'N': 0, 'rate': None, 'missed_query_ids': []},
           'citation_validity': {'n': 0, 'N': 0}, 'answer_citation_coverage': {'n': 0, 'N': 0},
           'abstention': {'n': 0, 'N': 0}, 'false_abstention': {'n': 0, 'N': 0}}
    for case in cases:
        cid = case['id']
        if not isinstance(case.get('answerable'), bool): raise ValueError(f'{cid}: thiếu answerable boolean')
        if cid not in trace_by_id: raise ValueError(f'{cid}: thiếu trace')
        t = trace_by_id[cid]
        if t.get('status') == 'error':
            out['provider_errors'] += 1
            continue
        if t.get('status') not in ('answered', 'abstain'): raise ValueError(f'{cid}: status không hợp lệ')
        if cid not in review_by_id: raise ValueError(f'{cid}: thiếu nhãn audit')
        r = review_by_id[cid]
        events = t.get('events')
        citations = t.get('citations')
        support = r.get('citation_support')
        if not isinstance(events, list) or not isinstance(citations, list): raise ValueError(f'{cid}: events/citations không hợp lệ')
        if not isinstance(support, list) or len(support) != len(citations) or any(type(v) is not bool for v in support):
            raise ValueError(f'{cid}: cần một nhãn boolean cho mỗi citation')
        if case['answerable']:
            gold = case.get('gold')
            if not isinstance(gold, list) or not gold:
                raise ValueError(f'{cid}: cần gold để tính context evidence')
            out['context_evidence']['N'] += 1
            if _final_context_supports_gold(t, gold):
                out['context_evidence']['n'] += 1
            else:
                out['context_evidence']['missed_query_ids'].append(cid)
        out['tool_use']['N'] += 1
        out['tool_use']['n'] += any(e.get('event') == 'search' for e in events)
        out['citation_validity']['n'] += sum(support)
        out['citation_validity']['N'] += len(citations)
        if t['status'] == 'answered':
            out['answer_citation_coverage']['N'] += 1
            out['answer_citation_coverage']['n'] += bool(citations)
        if case['answerable']:
            grade = r.get('answer_grade')
            if type(grade) is not int or grade not in (0, 1, 2): raise ValueError(f'{cid}: answer_grade phải là 0, 1 hoặc 2')
            if t['status'] == 'abstain' and grade != 0: raise ValueError(f'{cid}: abstain trên câu có đáp án phải được chấm 0')
            out['grounded_answer'][str(grade)] += 1
            out['grounded_answer']['N'] += 1
            out['false_abstention']['N'] += 1
            out['false_abstention']['n'] += t['status'] == 'abstain'
        else:
            correct = r.get('abstention_correct')
            if type(correct) is not bool:
                raise ValueError(f'{cid}: cần nhãn abstention_correct do người chấm xác nhận')
            if correct and t['status'] != 'abstain':
                raise ValueError(f'{cid}: nhãn từ chối đúng không khớp status')
            out['abstention']['N'] += 1
            out['abstention']['n'] += correct
    g = out['grounded_answer']
    if g['N']: g['mean'] = (g['1'] + 2*g['2']) / g['N']
    context_evidence = out['context_evidence']
    if context_evidence['N']:
        context_evidence['rate'] = context_evidence['n'] / context_evidence['N']
    return out


def _final_context_supports_gold(trace, gold):
    searches = [event for event in trace.get('events', []) if event.get('event') == 'search']
    if not searches:
        return False
    final_search = searches[-1]
    context = final_search.get('context')
    context_ids = final_search.get('context_ids')
    if not isinstance(context, str) or not isinstance(context_ids, list):
        return False
    results_by_id = {
        row.get('id'): row
        for event in searches
        for row in event.get('results', [])
        if isinstance(row, dict) and isinstance(row.get('id'), str)
    }
    for evidence in gold:
        for chunk_id in context_ids:
            row = results_by_id.get(chunk_id)
            if (
                not isinstance(row, dict)
                or row.get('source_id') != evidence.get('source_id')
                or row.get('page') != evidence.get('page')
                or not isinstance(row.get('source'), str)
            ):
                continue
            marker = f"[{chunk_id} | {row['source']} | page {row['page']}]\n"
            start = context.find(marker)
            if start < 0:
                continue
            body_start = start + len(marker)
            body_end = context.find('\n\n[', body_start)
            body = context[body_start:] if body_end < 0 else context[body_start:body_end]
            if isinstance(evidence.get('evidence'), str) and evidence['evidence'] in body:
                return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Tổng hợp trace agent và nhãn audit thủ công')
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--traces', type=Path, required=True)
    parser.add_argument('--reviews', type=Path, required=True)
    parser.add_argument('--split', choices=('dev', 'test'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    def load(path): return json.loads(path.read_text(encoding='utf-8'))
    cases = [c for c in load(args.cases) if c.get('split') == args.split]
    if not cases: raise ValueError('không có case trong split')
    report = {'split': args.split, **aggregate(cases, load(args.traces), load(args.reviews))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
