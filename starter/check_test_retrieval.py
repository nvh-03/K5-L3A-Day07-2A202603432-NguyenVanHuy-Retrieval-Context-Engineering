import json, sys
sys.path.append('starter')
from retrieval import LexicalRetriever
from baseline import hit

chunks = json.load(open('data/bonus_chunks.json', encoding='utf-8'))
questions = json.load(open('data/bonus_questions.json', encoding='utf-8'))
test_q = [q for q in questions if q['split'] == 'test']
retriever = LexicalRetriever(chunks)

hits = 0
total = 0
for q in test_q:
    if not q.get('answerable', True):
        continue
    total += 1
    res = retriever.search(q['retrieval_query_en'], top_k=3)
    matched = any(hit(r, q['gold']) for r in res)
    if matched:
        hits += 1
    status = 'HIT' if matched else 'MISS'
    print(f"{q['id']} ({q.get('category')}): {status}")

print(f"Total test answerable retrieval hits: {hits}/{total} ({hits/total:.1%})")

