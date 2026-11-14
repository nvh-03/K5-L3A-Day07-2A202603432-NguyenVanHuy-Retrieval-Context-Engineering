import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'starter'))
from agent_metrics import aggregate

class AgentMetricTests(unittest.TestCase):
    def test_counts_and_errors_are_separate(self):
        cases = [
            {'id':'a','answerable':True,'gold':[{'source_id':'doc','page':1,'evidence':'gold phrase'}]},
            {'id':'b','answerable':False},
            {'id':'c','answerable':True},
        ]
        traces = [{'query_id':'a','status':'answered','events':[{
                      'event':'search','context':'[c1 | docs/a.pdf | page 1]\ngold phrase',
                      'context_ids':['c1'],'results':[{'id':'c1','source_id':'doc','source':'docs/a.pdf',
                                                       'page':1,'text':'gold phrase'}],
                  }],'citations':['c1','c2']},
                  {'query_id':'b','status':'abstain','events':[{'event':'search'}],'citations':[]},
                  {'query_id':'c','status':'error','events':[],'citations':[]}]
        reviews = [{'query_id':'a','answer_grade':1,'citation_support':[True,False]},
                   {'query_id':'b','citation_support':[],'abstention_correct':True}]
        result = aggregate(cases, traces, reviews)
        self.assertEqual(result['provider_errors'], 1)
        self.assertEqual(result['tool_use'], {'n':2,'N':2})
        self.assertEqual(result['context_evidence'], {
            'n':1,'N':1,'rate':1.0,'missed_query_ids':[],
        })
        self.assertEqual(result['citation_validity'], {'n':1,'N':2})
        self.assertEqual(result['abstention'], {'n':1,'N':1})
        self.assertEqual(result['grounded_answer']['mean'], 1)

    def test_unanswerable_requires_human_confirmation(self):
        cases = [{'id':'a','answerable':False}]
        traces = [{'query_id':'a','status':'abstain','events':[],'citations':[]}]
        with self.assertRaises(ValueError): aggregate(cases, traces, [{'query_id':'a','citation_support':[]}])
        result = aggregate(cases, traces, [{'query_id':'a','citation_support':[], 'abstention_correct':False}])
        self.assertEqual(result['abstention'], {'n':0, 'N':1})

    def test_rejects_missing_review_and_false_abstention_grade(self):
        cases = [{'id':'a','answerable':True,'gold':[{'source_id':'doc','page':1,'evidence':'evidence'}]}]
        traces = [{'query_id':'a','status':'abstain','events':[],'citations':[]}]
        with self.assertRaises(ValueError): aggregate(cases,traces,[])
        with self.assertRaises(ValueError): aggregate(cases,traces,[{'query_id':'a','answer_grade':2,'citation_support':[]}])

    def test_context_evidence_uses_final_context_and_matches_source_and_page(self):
        cases = [
            {'id':'a','answerable':True,'gold':[{'source_id':'doc','page':1,'evidence':'required evidence'}]},
            {'id':'b','answerable':True,'gold':[{'source_id':'doc','page':1,'evidence':'required evidence'}]},
        ]
        traces = [
            {'query_id':'a','status':'answered','citations':[],'events':[
                {'event':'search','context':'[old | docs/a.pdf | page 1]\nrequired evidence',
                 'context_ids':['old'],'results':[{'id':'old','source_id':'doc','source':'docs/a.pdf',
                                                   'page':1,'text':'required evidence'}]},
                {'event':'search','context':'[wrong-page | docs/a.pdf | page 2]\nrequired evidence',
                 'context_ids':['wrong-page'],'results':[{'id':'wrong-page','source_id':'doc',
                                                          'source':'docs/a.pdf','page':2,
                                                          'text':'required evidence'}]},
            ]},
            {'query_id':'b','status':'answered','citations':[],'events':[
                {'event':'search','context':'[right | docs/a.pdf | page 1]\nrequired evidence',
                 'context_ids':['right'],'results':[{'id':'right','source_id':'doc','source':'docs/a.pdf',
                                                     'page':1,'text':'required evidence'}]},
            ]},
        ]
        reviews = [
            {'query_id':'a','answer_grade':2,'citation_support':[]},
            {'query_id':'b','answer_grade':2,'citation_support':[]},
        ]
        result = aggregate(cases,traces,reviews)
        self.assertEqual(result['context_evidence'], {
            'n':1,'N':2,'rate':0.5,'missed_query_ids':['a'],
        })

if __name__ == '__main__': unittest.main()
