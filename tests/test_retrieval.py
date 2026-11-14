import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'starter'))
from retrieval import DenseRetriever, HybridRetriever, LexicalRetriever
from retrieval_benchmark import evaluate_method, write_method_outputs


CHUNKS = [
    {'id': 'c1', 'source_id': 'doc', 'source': 'doc.pdf', 'page': 1,
     'text': 'Refund requests are processed within seven business days.',
     'metadata': {'section': 'refunds'}},
    {'id': 'c2', 'source_id': 'doc', 'source': 'doc.pdf', 'page': 2,
     'text': 'Flight changes cost fifty dollars after the first day.',
     'metadata': {'section': 'changes'}},
]


class FakeEmbedder:
    def __init__(self):
        self.queries = []

    def embed_query(self, query):
        self.queries.append(query)
        return [0.1, 0.2]


class FakeStore:
    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    def search(self, strategy, query_vector, top_k=3, filters=None):
        self.calls.append((strategy, query_vector, top_k, filters))
        return self.rows[:top_k]


def dense_row(chunk, score):
    return {
        'chunk_id': chunk['id'], 'document_id': chunk['source_id'],
        'source': chunk['source'], 'page': chunk['page'], 'text': chunk['text'],
        'score': score, 'metadata': chunk['metadata'],
    }


class RetrievalTests(unittest.TestCase):
    def test_lexical_retrieval_applies_metadata_filter(self):
        retriever = LexicalRetriever(CHUNKS)
        results = retriever.search('refund processed days', filters={'section': 'refunds'}, top_k=2)
        self.assertEqual([row['id'] for row in results], ['c1'])
        self.assertEqual(results[0]['rank'], 1)
        self.assertGreater(results[0]['score'], 0)

    def test_dense_adapter_preserves_filter_rank_and_day6_fields(self):
        store = FakeStore([dense_row(CHUNKS[0], 0.87)])
        embedder = FakeEmbedder()
        retriever = DenseRetriever(store, embedder, strategy='B')
        results = retriever.search('refund timeline', filters={'section': 'refunds'}, top_k=3)
        self.assertEqual(store.calls, [('B', [0.1, 0.2], 3, {'section': 'refunds'})])
        self.assertEqual(embedder.queries, ['refund timeline'])
        self.assertEqual((results[0]['id'], results[0]['source_id'], results[0]['page']), ('c1', 'doc', 1))
        self.assertEqual((results[0]['score'], results[0]['rank']), (0.87, 1))

    def test_hybrid_fuses_rankings_and_keeps_component_scores(self):
        store = FakeStore([dense_row(CHUNKS[1], 0.9), dense_row(CHUNKS[0], 0.8)])
        dense = DenseRetriever(store, FakeEmbedder(), strategy='B')
        lexical = LexicalRetriever(CHUNKS)
        retriever = HybridRetriever(dense, lexical, candidate_k=2, rrf_k=10)
        results = retriever.search('refund processed seven days', top_k=2)
        self.assertEqual(results[0]['id'], 'c1')
        self.assertEqual(results[0]['rank'], 1)
        self.assertIn('dense_score', results[0])
        self.assertIn('lexical_score', results[0])
        self.assertEqual(results[0]['method'], 'hybrid_rrf')
        self.assertEqual(results[0]['source'], 'doc.pdf')
        self.assertEqual(results[0]['page'], 1)

    def test_evidence_metrics_exclude_unanswerable_questions(self):
        retriever = LexicalRetriever(CHUNKS)
        questions = [
            {'id': 'answerable', 'split': 'dev', 'question': 'Refund processing time?',
             'answerable': True, 'gold': [{'source_id': 'doc', 'page': 1,
                                            'evidence': 'processed within seven business days'}]},
            {'id': 'abstain', 'split': 'dev', 'question': 'Does the document state the aircraft color?',
             'answerable': False},
        ]
        traces, summary = evaluate_method('lexical', retriever, questions, top_k=3)
        self.assertTrue(traces[0]['results'][0]['evidence_hit'])
        self.assertEqual(summary['hit_at_1'], {'n': 1, 'N': 1, 'rate': 1.0})
        self.assertEqual(summary['evidence_hit_at_3'], {'n': 1, 'N': 1, 'rate': 1.0})
        self.assertEqual((summary['questions'], summary['unanswerable_questions']), (2, 1))
        self.assertFalse(any(row['evidence_hit'] for row in traces[1]['results']))

    def test_benchmark_can_use_english_query_without_replacing_original_question(self):
        question = {
            'id': 'translated',
            'split': 'dev',
            'question': 'Thời gian xử lý hoàn tiền là bao lâu?',
            'retrieval_query_en': 'How long are refund requests processed?',
            'answerable': True,
            'gold': [{'source_id': 'doc', 'page': 1, 'evidence': 'seven business days'}],
        }
        traces, summary = evaluate_method(
            'lexical', LexicalRetriever(CHUNKS), [question], query_field='retrieval_query_en'
        )
        self.assertEqual(traces[0]['question'], question['question'])
        self.assertEqual(traces[0]['query'], question['retrieval_query_en'])
        self.assertEqual(traces[0]['query_field'], 'retrieval_query_en')
        self.assertTrue(traces[0]['results'][0]['evidence_hit'])
        self.assertEqual(summary['query_field'], 'retrieval_query_en')

    def test_benchmark_rejects_missing_selected_query_field(self):
        question = {'id': 'missing', 'split': 'dev', 'question': 'Refund processing time?'}
        with self.assertRaisesRegex(ValueError, 'retrieval_query_en'):
            evaluate_method(
                'lexical', LexicalRetriever(CHUNKS), [question], query_field='retrieval_query_en'
            )

    def test_benchmark_output_filenames_include_method_and_split(self):
        traces = [{'query_id': 'q1', 'method': 'lexical'}]
        summary = {'method': 'lexical', 'questions': 1}
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            write_method_outputs(output, 'dev', traces, summary)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {'dev-lexical-traces.json', 'dev-lexical-summary.json'},
            )
            self.assertEqual(
                json.loads((output / 'dev-lexical-summary.json').read_text(encoding='utf-8')),
                summary,
            )
            self.assertEqual(
                json.loads((output / 'dev-lexical-traces.json').read_text(encoding='utf-8')),
                traces,
            )


if __name__ == '__main__':
    unittest.main()
