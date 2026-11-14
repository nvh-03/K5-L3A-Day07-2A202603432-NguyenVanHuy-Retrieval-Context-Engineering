import sys, json
from pathlib import Path
sys.path.append('starter')
from run_agent import load_env_file
from agentic import OpenAICompatibleController, run_agent
from retrieval import LexicalRetriever

load_env_file(Path('.env'))
chunks = json.load(open('data/bonus_chunks.json', encoding='utf-8'))
questions = json.load(open('data/bonus_questions.json', encoding='utf-8'))
retriever = LexicalRetriever(chunks)
controller = OpenAICompatibleController.from_env()

for qid in ('bonus-dev-03', 'bonus-dev-08', 'bonus-dev-10', 'bonus-dev-11', 'bonus-dev-12'):
    q = [x for x in questions if x['id'] == qid][0]
    print(f"Testing {qid} ({q['category']})...")
    res = run_agent(q['question'], controller, retriever, top_k=5, budget=3000, max_searches=4)
    print(f"  Status: {res['status']}, Citations: {res.get('citations')}")
    print(f"  Answer: {res.get('answer', '')[:120]}")

