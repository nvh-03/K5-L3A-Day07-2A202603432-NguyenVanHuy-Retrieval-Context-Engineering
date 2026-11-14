import json
from pathlib import Path
import sys
sys.path.append('starter')
from retrieval import LexicalRetriever
from retrieval_benchmark import evaluate_method, write_method_outputs

def main():
    chunks = json.load(open('data/bonus_chunks.json', encoding='utf-8'))
    questions = json.load(open('data/bonus_questions.json', encoding='utf-8'))
    
    dev_q = [q for q in questions if q['split'] == 'dev']
    test_q = [q for q in questions if q['split'] == 'test']
    
    retriever = LexicalRetriever(chunks)
    out_dir = Path('starter/results/bonus-retrieval')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Dev Baseline
    traces_dev_raw, summary_dev_raw = evaluate_method('lexical-raw', retriever, dev_q, top_k=3, query_field='question')
    write_method_outputs(out_dir, 'dev', traces_dev_raw, summary_dev_raw)
    print("=== DEV BASELINE (Vietnamese Query) ===")
    print(f"Hit@1: {summary_dev_raw['hit_at_1']['n']}/{summary_dev_raw['hit_at_1']['N']} ({summary_dev_raw['hit_at_1']['rate']:.1%})")
    print(f"Evidence Hit@3: {summary_dev_raw['evidence_hit_at_3']['n']}/{summary_dev_raw['evidence_hit_at_3']['N']} ({summary_dev_raw['evidence_hit_at_3']['rate']:.1%})")
    print(f"Median latency: {summary_dev_raw['median_ms']:.2f} ms")
    
    # Dev Improved
    traces_dev_en, summary_dev_en = evaluate_method('lexical-en', retriever, dev_q, top_k=3, query_field='retrieval_query_en')
    write_method_outputs(out_dir, 'dev', traces_dev_en, summary_dev_en)
    print("\n=== DEV IMPROVED (English Query) ===")
    print(f"Hit@1: {summary_dev_en['hit_at_1']['n']}/{summary_dev_en['hit_at_1']['N']} ({summary_dev_en['hit_at_1']['rate']:.1%})")
    print(f"Evidence Hit@3: {summary_dev_en['evidence_hit_at_3']['n']}/{summary_dev_en['evidence_hit_at_3']['N']} ({summary_dev_en['evidence_hit_at_3']['rate']:.1%})")
    print(f"Median latency: {summary_dev_en['median_ms']:.2f} ms")

    # Test Baseline
    traces_test_raw, summary_test_raw = evaluate_method('lexical-raw', retriever, test_q, top_k=3, query_field='question')
    write_method_outputs(out_dir, 'test', traces_test_raw, summary_test_raw)
    print("\n=== TEST BASELINE (Vietnamese Query) ===")
    print(f"Hit@1: {summary_test_raw['hit_at_1']['n']}/{summary_test_raw['hit_at_1']['N']} ({summary_test_raw['hit_at_1']['rate']:.1%})")
    print(f"Evidence Hit@3: {summary_test_raw['evidence_hit_at_3']['n']}/{summary_test_raw['evidence_hit_at_3']['N']} ({summary_test_raw['evidence_hit_at_3']['rate']:.1%})")
    print(f"Median latency: {summary_test_raw['median_ms']:.2f} ms")

    # Test Selected
    traces_test_en, summary_test_en = evaluate_method('lexical-en', retriever, test_q, top_k=3, query_field='retrieval_query_en')
    write_method_outputs(out_dir, 'test', traces_test_en, summary_test_en)
    print("\n=== TEST SELECTED (English Query) ===")
    print(f"Hit@1: {summary_test_en['hit_at_1']['n']}/{summary_test_en['hit_at_1']['N']} ({summary_test_en['hit_at_1']['rate']:.1%})")
    print(f"Evidence Hit@3: {summary_test_en['evidence_hit_at_3']['n']}/{summary_test_en['evidence_hit_at_3']['N']} ({summary_test_en['evidence_hit_at_3']['rate']:.1%})")
    print(f"Median latency: {summary_test_en['median_ms']:.2f} ms")

if __name__ == '__main__':
    main()

