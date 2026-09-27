import json, math, hashlib
from pathlib import Path
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parent.parent
payload=json.loads((root/'data/scores.json').read_text(encoding='utf-8'))
posts={p['truth_id']:p for p in payload['posts']}
assert len(posts)==len(payload['posts'])==87
for p in posts.values():
    assert p['text_sha256']==hashlib.sha256(p['text'].encode()).hexdigest()
    assert abs(sum(p['emotion'].values())-1)<1e-5
    for kind in ['emotion','rhetoric']:
        assert len(p[kind])==6
        assert all(math.isfinite(v) and 0<=v<=1 for v in p[kind].values())
page=BeautifulSoup((root/'index.html').read_text(encoding='utf-8'),'html.parser')
cards=page.select('.truth-card')
assert len(cards)==129 and len(page.select('.event-view'))==26
assert {c['data-truth-id'] for c in cards}==set(posts)
assert all(len(c.select('.dual-row'))==12 for c in cards)
events=json.loads((root/'data/event_windows.json').read_text(encoding='utf-8'))
summaries=json.loads((root/'data/summary.json').read_text(encoding='utf-8'))
for kind,windows in summaries.items():
    for name,summary in windows.items():
        groups=[e['windows'][name] for e in events if e['windows'][name]]
        assert len(groups)==summary['event_count']
        assert all(len(g)==len(set(g)) for g in groups)
        for label,value in summary['values'].items():
            expected=sum(sum(posts[id][kind][label] for id in g)/len(g) for g in groups)/len(groups)
            assert abs(value-expected)<1e-12
print('Passed: 87 posts, 129 cards, 26 events, valid scores and reconciled summaries.')
