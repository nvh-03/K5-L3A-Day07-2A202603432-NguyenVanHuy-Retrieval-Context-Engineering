import unittest

from starter.bonus_metrics import aggregate


class BonusMetricTests(unittest.TestCase):
    def test_multi_hop_requires_every_gold_item_in_context_and_citations(self):
        question = {
            'id': 'multi',
            'category': 'Multi-hop',
            'answerable': True,
            'gold': [
                {'source_id': 'book', 'page': 1, 'evidence': 'first fact'},
                {'source_id': 'book', 'page': 2, 'evidence': 'second fact'},
            ],
        }
        chunks = [
            {'id': 'first', 'source_id': 'book', 'page': 1, 'text': 'first fact'},
            {'id': 'second', 'source_id': 'book', 'page': 2, 'text': 'second fact'},
        ]
        trace = {
            'query_id': 'multi',
            'status': 'answered',
            'citations': ['first'],
            'events': [{'event': 'search', 'context_ids': ['first']}],
        }
        review = {'query_id': 'multi', 'answer_grade': 2, 'citation_support': [True]}

        partial = aggregate([question], [trace], [review], chunks)
        self.assertFalse(partial['case_results'][0]['passed'])
        self.assertEqual(partial['context_evidence_rate'], {'n': 0, 'N': 1, 'rate': 0.0})

        trace['citations'] = ['first', 'second']
        trace['events'].append({'event': 'search', 'context_ids': ['first', 'second']})
        review['citation_support'] = [True, True]
        complete = aggregate([question], [trace], [review], chunks)
        self.assertTrue(complete['case_results'][0]['passed'])
        self.assertEqual(complete['context_evidence_rate'], {'n': 1, 'N': 1, 'rate': 1.0})

    def test_evidence_groups_allow_required_number_of_alternatives(self):
        question = {
            'id': 'alternatives',
            'category': 'Multi-hop',
            'answerable': True,
            'gold': [
                {'source_id': 'book', 'page': 1, 'evidence': 'base fact'},
                {'source_id': 'book', 'page': 2, 'evidence': 'country A'},
                {'source_id': 'book', 'page': 2, 'evidence': 'country B'},
                {'source_id': 'book', 'page': 2, 'evidence': 'country C'},
            ],
            'evidence_groups': [
                {'min_matches': 1, 'gold_indices': [0]},
                {'min_matches': 2, 'gold_indices': [1, 2, 3]},
            ],
        }
        chunks = [
            {'id': 'base', 'source_id': 'book', 'page': 1, 'text': 'base fact'},
            {'id': 'a', 'source_id': 'book', 'page': 2, 'text': 'country A'},
            {'id': 'b', 'source_id': 'book', 'page': 2, 'text': 'country B'},
        ]
        trace = {
            'query_id': 'alternatives',
            'status': 'answered',
            'citations': ['base', 'a', 'b'],
            'events': [{'event': 'search', 'context_ids': ['base', 'a', 'b']}],
        }
        review = {
            'query_id': 'alternatives',
            'answer_grade': 2,
            'citation_support': [True, True, True],
        }

        result = aggregate([question], [trace], [review], chunks)
        self.assertTrue(result['case_results'][0]['passed'])
        self.assertEqual(result['context_evidence_rate']['n'], 1)

    def test_errors_fail_and_remain_in_the_overall_denominator(self):
        question = {
            'id': 'error',
            'category': 'Text',
            'answerable': True,
            'gold': [{'source_id': 'book', 'page': 1, 'evidence': 'fact'}],
        }
        trace = {
            'query_id': 'error',
            'status': 'error',
            'error': 'timeout',
            'citations': [],
            'events': [],
            'elapsed_ms': 100,
        }
        review = {'query_id': 'error', 'answer_grade': 0, 'citation_support': []}

        result = aggregate([question], [trace], [review], [])
        self.assertEqual(result['errors'], 1)
        self.assertEqual(result['total_questions'], 1)
        self.assertEqual(result['passed_questions'], 0)
        self.assertIsNone(result['total_cost_usd'])

    def test_unanswerable_questions_require_reviewed_abstention(self):
        question = {
            'id': 'missing',
            'category': 'Thiếu bằng chứng',
            'answerable': False,
        }
        trace = {
            'query_id': 'missing',
            'status': 'abstain',
            'citations': [],
            'events': [],
        }
        review = {
            'query_id': 'missing',
            'abstention_correct': True,
            'citation_support': [],
        }

        result = aggregate([question], [trace], [review], [])
        self.assertTrue(result['case_results'][0]['passed'])
        review['abstention_correct'] = False
        result = aggregate([question], [trace], [review], [])
        self.assertFalse(result['case_results'][0]['passed'])


if __name__ == '__main__':
    unittest.main()
