import json
import sys
sys.path.append('starter')
import build_bonus_questions as bq

chunks = json.load(open('data/bonus_chunks.json', encoding='utf-8'))
failed = 0
for q in bq.DEV_QUESTIONS + bq.TEST_QUESTIONS:
    if not q.get('answerable', True):
        continue
    for g in q['gold']:
        matched = False
        for c in chunks:
            if c['source_id'] == g['source_id'] and c['page'] == g['page'] and g['evidence'] in c['text']:
                matched = True
                break
        if not matched:
            print(f"FAIL: {q['id']} (Page {g['page']}) -> evidence not found: {g['evidence'][:60]}")
            failed += 1

print(f"Total check complete. Failures: {failed}")

