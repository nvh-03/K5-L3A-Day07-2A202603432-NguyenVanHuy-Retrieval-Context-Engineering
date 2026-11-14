"""Offline behavioral checks only; fake adapters do not measure model quality."""
import json
import sys
import unittest
from pathlib import Path
import os
import tempfile
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'starter'))
from agentic import OpenAICompatibleController, pack_context_chunks, run_agent
from run_agent import load_env_file

CHUNK = {'id': 'c1', 'text': 'Hoàn tiền trong 7 ngày.', 'source_id': 'doc',
         'source': 'doc.pdf', 'page': 1, 'score': 0.8, 'metadata': {}}

class Controller:
    def __init__(self, actions): self.actions = iter(actions)
    def decide(self, question, history): return next(self.actions)

class Retriever:
    def __init__(self, results): self.results = results; self.calls = []
    def search(self, query, *, filters, top_k):
        self.calls.append((query, filters, top_k)); return self.results

class AgentTests(unittest.TestCase):
    def test_agent_searches_and_cites_actual_context(self):
        c = Controller([{'action': 'search', 'query': 'hoàn tiền'},
                        {'action': 'answer', 'answer': '7 ngày [c1]', 'citations': ['c1']}])
        r = Retriever([CHUNK]); result = run_agent('Hoàn tiền?', c, r, filters={'year': 2025})
        self.assertEqual(result['status'], 'answered')
        self.assertEqual(result['citations'], ['c1'])
        self.assertEqual(r.calls, [('hoàn tiền', {'year': 2025}, 3)])
        self.assertEqual(result['events'][0]['context_ids'], ['c1'])

    def test_agent_adds_declared_context_citation_when_answer_omits_inline_marker(self):
        c = Controller([{'action': 'search', 'query': 'refund'},
                        {'action': 'answer', 'answer': 'Hoàn tiền trong 7 ngày.', 'citations': ['c1']}])
        result = run_agent('Hoàn tiền?', c, Retriever([CHUNK]))
        self.assertEqual(result['status'], 'answered')
        self.assertEqual(result['answer'], 'Hoàn tiền trong 7 ngày. [c1]')
        self.assertEqual(result['citations'], ['c1'])

    def test_invalid_citation_and_empty_context_abstain(self):
        for rows, cid in (([CHUNK], 'not-present'), ([], 'c1')):
            c = Controller([{'action':'search','query':'q'}, {'action':'answer','answer':f'7 ngày [{cid}]','citations':[cid]}])
            self.assertEqual(run_agent('q', c, Retriever(rows))['status'], 'abstain')

    def test_search_limit_is_enforced(self):
        c = Controller([{'action':'search','query':'one'}, {'action':'search','query':'two'}, {'action':'search','query':'three'}])
        r = Retriever([CHUNK]); result = run_agent('q', c, r, max_searches=2)
        self.assertEqual(result['status'], 'abstain'); self.assertEqual(len(r.calls), 2)

    def test_context_budget_across_multiple_searches(self):
        other = {**CHUNK, 'id': 'c2', 'text': 'Một đoạn bằng chứng khác.'}
        class SequentialRetriever:
            def __init__(self): self.i = 0
            def search(self, query, *, filters, top_k):
                self.i += 1
                return [CHUNK] if self.i == 1 else [other]
        class InspectController:
            def __init__(self): self.i = 0
            def decide(self, question, history):
                self.i += 1
                if history:
                    assert len(history) == 1 and len(history[0]['context']) <= 90
                if self.i <= 2: return {'action': 'search', 'query': str(self.i)}
                return {'action': 'answer', 'answer': '7 ngày [c1]', 'citations': ['c1']}
        result = run_agent('q', InspectController(), SequentialRetriever(), budget=90)
        self.assertEqual(result['status'], 'answered')
        self.assertTrue(all(len(e['context']) <= 90 for e in result['events'] if e['event'] == 'search'))

    def test_configurable_retrieval_allows_more_than_two_calls(self):
        c = Controller([{'action': 'search', 'query': str(i)} for i in range(3)] +
                       [{'action': 'answer', 'answer': '7 ngày [c1]', 'citations': ['c1']}])
        r = Retriever([CHUNK])
        result = run_agent('q', c, r, max_searches=3, top_k=7, budget=1200)
        self.assertEqual(result['status'], 'answered')
        self.assertEqual(len(r.calls), 3)
        self.assertTrue(all(call[2] == 7 for call in r.calls))

    def test_tool_errors_are_not_hidden(self):
        class Broken:
            def search(self, query, *, filters, top_k): raise ConnectionError('database unavailable')
        with self.assertRaises(ConnectionError):
            run_agent('q', Controller([{'action':'search','query':'q'}]), Broken())

    def test_openai_compatible_controller_uses_search_and_answer_tools(self):
        class FakeController(OpenAICompatibleController):
            def __init__(self):
                super().__init__(model='test-model')
                self.responses = [
                    {'tool_calls': [{'function': {'name': 'search_chunks', 'arguments': '{"query":"refund policy"}'}}]},
                    {'tool_calls': [{'function': {'name': 'submit_answer', 'arguments': '{"answer":"7 days [c1]","citations":["c1"]}'}}]},
                    {'tool_calls': [{'function': {'name': 'abstain', 'arguments': '{"reason":"No supporting evidence."}'}}]},
                ]
                self.calls = []
            def _chat(self, messages, *, tools=None):
                self.calls.append((messages, tools))
                return self.responses.pop(0)

        controller = FakeController()
        self.assertEqual(controller.decide('How long?', []), {'action': 'search', 'query': 'refund policy'})
        self.assertEqual(controller.decide('How long?', [{'context': '[c1] ...', 'context_ids': ['c1'], 'queries': ['refund policy']}]),
                         {'action': 'answer', 'answer': '7 days [c1]', 'citations': ['c1']})
        self.assertEqual(controller.decide('No answer?', []),
                         {'action': 'abstain', 'reason': 'No supporting evidence.'})
        self.assertEqual([tool['function']['name'] for tool in controller.calls[0][1]],
                         ['search_chunks', 'submit_answer', 'abstain'])
        self.assertIn('[c1] ...', controller.calls[1][0][-1]['content'])

    def test_controller_requires_a_tool_call_when_tools_are_provided(self):
        response = MagicMock()
        response.read.return_value = b'{"choices":[{"message":{"tool_calls":[]}}]}'
        with patch('urllib.request.urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value = response
            controller = OpenAICompatibleController(model='test-model')
            controller._chat([{'role': 'user', 'content': 'Question'}], tools=[])
        request = urlopen.call_args[0][0]
        body = json.loads(request.data)
        self.assertEqual(body['tool_choice'], 'required')

    def test_controller_uses_auto_tool_choice_for_gemini_endpoint(self):
        response = MagicMock()
        response.read.return_value = b'{"choices":[{"message":{"tool_calls":[]}}]}'
        with patch('urllib.request.urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value = response
            controller = OpenAICompatibleController(
                model='gemini-3.5-flash',
                base_url='https://generativelanguage.googleapis.com/v1beta/openai/',
            )
            controller._chat([{'role': 'user', 'content': 'Question'}], tools=[])
        request = urlopen.call_args[0][0]
        body = json.loads(request.data)
        self.assertEqual(body['tool_choice'], 'auto')

    def test_gemini_retries_when_auto_choice_returns_no_tool_call(self):
        controller = OpenAICompatibleController(
            model='gemini-3.5-flash',
            base_url='https://generativelanguage.googleapis.com/v1beta/openai/',
        )
        controller._chat = MagicMock(side_effect=[
            {'content': 'I can answer that.'},
            {'tool_calls': [{'function': {
                'name': 'search_chunks',
                'arguments': '{"query":"policy"}',
            }}]},
        ])
        self.assertEqual(
            controller.decide('What is the policy?', []),
            {'action': 'search', 'query': 'policy'},
        )
        self.assertEqual(controller._chat.call_count, 2)
        retry_messages = controller._chat.call_args_list[1].args[0]
        self.assertIn('must call exactly one available tool', retry_messages[-1]['content'])

    def test_verifier_requires_support_for_every_citation(self):
        class FakeController(OpenAICompatibleController):
            def __init__(self, content):
                super().__init__(model='test-model')
                self.content = content
            def _chat(self, messages, *, tools=None):
                return {'content': self.content}

        chunks = [{'id': 'c1', 'source': 'policy.pdf', 'page': 1, 'text': 'Refunds take 7 days.'}]
        supported = FakeController('{"supported":true,"citation_support":[{"id":"c1","supported":true}]}')
        unsupported = FakeController('{"supported":false,"citation_support":[{"id":"c1","supported":false}]}')
        self.assertTrue(supported.verify('How long?', '7 days [c1]', chunks))
        self.assertFalse(unsupported.verify('How long?', '8 days [c1]', chunks))

    def test_verifier_accepts_json_fenced_in_markdown(self):
        class FakeController(OpenAICompatibleController):
            def __init__(self):
                super().__init__(model='test-model')
            def _chat(self, messages, *, tools=None):
                return {'content': '```json\n{"supported":true,"citation_support":[{"id":"c1","supported":true}]}\n```'}

        chunks = [{'id': 'c1', 'source': 'policy.pdf', 'page': 1, 'text': 'Refunds take 7 days.'}]
        controller = FakeController()
        self.assertTrue(controller.verify('How long?', '7 days [c1]', chunks))

    def test_agent_abstains_when_verifier_rejects_answer(self):
        class VerifierController(Controller):
            def verify(self, question, answer, cited_chunks):
                self.cited_chunks = cited_chunks
                return False

        controller = VerifierController([{'action': 'search', 'query': 'refund'},
                                         {'action': 'answer', 'answer': '7 days [c1]', 'citations': ['c1']}])
        result = run_agent('How long?', controller, Retriever([CHUNK]))
        self.assertEqual(result['status'], 'abstain')
        self.assertEqual(result['events'][-1], {'event': 'citation_verification', 'citations': ['c1'], 'supported': False})
        self.assertEqual(controller.cited_chunks[0]['text'], CHUNK['text'])

    def test_context_is_truncated_to_budget_and_preserves_cited_excerpt(self):
        context, selected = pack_context_chunks([CHUNK], budget=45)
        self.assertLessEqual(len(context), 45)
        self.assertEqual(selected[0]['id'], 'c1')
        self.assertTrue(selected[0]['text'].endswith('...'))

    def test_verifier_only_sees_the_context_excerpt_sent_to_model(self):
        class ExcerptVerifier(Controller):
            def verify(self, question, answer, cited_chunks):
                return '7 ngày' in cited_chunks[0]['text']

        controller = ExcerptVerifier([{'action': 'search', 'query': 'refund'},
                                      {'action': 'answer', 'answer': '7 ngày [c1]', 'citations': ['c1']}])
        result = run_agent('How long?', controller, Retriever([CHUNK]), budget=45)
        self.assertEqual(result['status'], 'abstain')
        self.assertFalse(result['events'][-1]['supported'])

    def test_from_env_uses_deepseek_key_for_deepseek_endpoint(self):
        names = ('OPENAI_MODEL', 'OPENAI_API_KEY', 'OPENAI_BASE_URL', 'DEEPSEEK_MODEL',
                 'DEEPSEEK_API_KEY', 'OPENROUTER_MODEL', 'OPENROUTER_API_KEY')
        previous = {name: os.environ.get(name) for name in names}
        try:
            os.environ['OPENAI_MODEL'] = 'deepseek-chat'
            os.environ['OPENAI_BASE_URL'] = 'https://api.deepseek.com'
            os.environ['DEEPSEEK_API_KEY'] = 'test-secret'
            os.environ.pop('OPENAI_API_KEY', None)
            controller = OpenAICompatibleController.from_env()
            self.assertEqual(controller.model, 'deepseek-chat')
            self.assertEqual(controller.base_url, 'https://api.deepseek.com')
            self.assertEqual(controller.api_key, 'test-secret')
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_from_env_uses_openrouter_key_and_model_for_openrouter_endpoint(self):
        names = ('OPENAI_MODEL', 'OPENAI_API_KEY', 'OPENAI_BASE_URL', 'DEEPSEEK_MODEL',
                 'DEEPSEEK_API_KEY', 'OPENROUTER_MODEL', 'OPENROUTER_API_KEY')
        previous = {name: os.environ.get(name) for name in names}
        try:
            os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'
            os.environ['OPENROUTER_MODEL'] = 'openai/gpt-4o-mini'
            os.environ['OPENROUTER_API_KEY'] = 'openrouter-test-key'
            os.environ['OPENAI_MODEL'] = ''
            os.environ['OPENAI_API_KEY'] = 'unrelated-key'
            controller = OpenAICompatibleController.from_env()
            self.assertEqual(controller.model, 'openai/gpt-4o-mini')
            self.assertEqual(controller.base_url, 'https://openrouter.ai/api/v1')
            self.assertEqual(controller.api_key, 'openrouter-test-key')
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_from_env_uses_gemini_key_and_model_for_gemini_endpoint(self):
        names = ('OPENAI_MODEL', 'OPENAI_API_KEY', 'OPENAI_BASE_URL',
                 'GEMINI_MODEL', 'GEMINI_API_KEY', 'MODEL')
        previous = {name: os.environ.get(name) for name in names}
        try:
            os.environ['OPENAI_BASE_URL'] = 'https://generativelanguage.googleapis.com/v1beta/openai/'
            os.environ['GEMINI_MODEL'] = 'gemini-3.5-flash'
            os.environ['GEMINI_API_KEY'] = 'gemini-test-key'
            os.environ['OPENAI_MODEL'] = ''
            os.environ['OPENAI_API_KEY'] = 'unrelated-key'
            controller = OpenAICompatibleController.from_env()
            self.assertEqual(controller.model, 'gemini-3.5-flash')
            self.assertEqual(controller.base_url, 'https://generativelanguage.googleapis.com/v1beta/openai')
            self.assertEqual(controller.api_key, 'gemini-test-key')
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_agent_rejects_uncited_bracket_ids(self):
        controller = Controller([{'action': 'search', 'query': 'refund'},
                                 {'action': 'answer', 'answer': '7 days [c1] [fake]', 'citations': ['c1']}])
        result = run_agent('How long?', controller, Retriever([CHUNK]))
        self.assertEqual(result['status'], 'abstain')
        self.assertEqual(result['events'][-1]['event'], 'invalid_or_missing_citations')
        self.assertEqual(result['events'][-1]['proposed_citations'], ['c1'])
        self.assertEqual(result['events'][-1]['answer_citation_ids'], ['c1', 'fake'])

    def test_agent_records_explicit_model_abstention(self):
        retriever = Retriever([CHUNK])
        controller = Controller([{'action': 'abstain', 'reason': 'No matching evidence.'}])
        result = run_agent('What is the aircraft color?', controller, retriever)
        self.assertEqual(result['status'], 'abstain')
        self.assertEqual(result['events'], [{'event': 'model_abstention', 'reason': 'No matching evidence.'}])
        self.assertEqual(retriever.calls, [])

    def test_env_file_loads_values_without_overriding_process_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text(
                'TEST_AGENT_MODEL="example-model"\nTEST_AGENT_EXISTING=file-value\n',
                encoding='utf-8',
            )
            previous_model = os.environ.get('TEST_AGENT_MODEL')
            previous_existing = os.environ.get('TEST_AGENT_EXISTING')
            try:
                os.environ.pop('TEST_AGENT_MODEL', None)
                os.environ['TEST_AGENT_EXISTING'] = 'process-value'
                load_env_file(path)
                self.assertEqual(os.environ['TEST_AGENT_MODEL'], 'example-model')
                self.assertEqual(os.environ['TEST_AGENT_EXISTING'], 'process-value')
            finally:
                if previous_model is None:
                    os.environ.pop('TEST_AGENT_MODEL', None)
                else:
                    os.environ['TEST_AGENT_MODEL'] = previous_model
                if previous_existing is None:
                    os.environ.pop('TEST_AGENT_EXISTING', None)
                else:
                    os.environ['TEST_AGENT_EXISTING'] = previous_existing

if __name__ == '__main__': unittest.main()
