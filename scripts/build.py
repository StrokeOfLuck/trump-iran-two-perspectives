import sys,json,csv,shutil,statistics,html
from pathlib import Path
root=Path(__file__).resolve().parent.parent
from bs4 import BeautifulSoup
out=root
payload=json.loads((out/'data/scores.json').read_text(encoding='utf-8'))
assert payload.get('bart_emotion_run'), 'Run scripts/score_bart_emotions.py first.'
posts={p['truth_id']:p for p in payload['posts']}
soup=BeautifulSoup((root/'source/original-timeline.html').read_text(encoding='utf-8'),'html.parser')
def fragment(markup): return BeautifulSoup(markup,'html.parser')
def post_id(card): return card.select_one('a.truth-link')['href'].rstrip('/').split('/')[-1]
def bars(values,kind):
 return ''.join(f'<div class="dual-row"><span>{html.escape(label.title() if kind in ('emotion','bart_emotion') else label)}</span><span class="dual-track"><span class="dual-fill {kind}" style="width:{value*100:.3f}%"></span></span><strong>{value:.2f}</strong></div>' for label,value in values.items())
cards=soup.select('.truth-card')
assert {post_id(c) for c in cards}==set(posts)
for card in cards:
 p=posts[post_id(card)]
 card['data-truth-id']=p['truth_id']
 old=card.select_one('.score-area')
 assert old
 markup='<div class="dual-scores">'
 markup+='<div class="model-panel rhetoric-panel"><div class="model-title">BART · Rhetoric</div>'+bars(p['rhetoric'],'rhetoric')+'</div>'
 markup+='<div class="model-panel bart-emotion-panel"><div class="model-title">BART · Emotion</div>'+bars(p['bart_emotion'],'bart_emotion')+'</div>'
 markup+='<div class="model-panel emotion-panel"><div class="model-title">DistilBERT · Emotion</div>'+bars(p['emotion'],'emotion')+'</div></div>'
 old.replace_with(fragment(markup))
 badge=card.select_one('.dominant-badge')
 if badge:
  badge.string='Top rhetoric: '+max(p['rhetoric'],key=p['rhetoric'].get)
  top=max(p['emotion'],key=p['emotion'].get)
  badge.insert_after(fragment(f'<span class="emotion-badge">DistilBERT: {top.title()}</span>'))
 for badge in card.select('.emotion-badge'):
  bart_top=max(p['bart_emotion'],key=p['bart_emotion'].get)
  badge.insert_after(fragment(f'<span class="emotion-badge bart-emotion-badge">BART: {bart_top.title()}</span>'))
assert len(soup.select('.dual-scores'))==len(cards)
soup.title.string='Trump–Iran: Emotion & Rhetoric'
soup.select_one('h1').string='Trump–Iran: Emotion & Rhetoric'
soup.select_one('.lede-question').string='Two models, the same posts. Compare their emotion predictions, or explore emotion alongside rhetorical framing.'
h3=soup.select_one('h3')
if h3: h3.string='Explore the connected timeline'
for a in soup.select('a[href]'):
 if a['href'] in ('political-text-analysis.html','../../political-text-analysis.html'): a['href']='https://strokeofluck.github.io/sean-data-portfolio/projects/political-text-analysis.html'
 if a['href'].startswith('../../../'):
  a['href']='https://strokeofluck.github.io/sean-data-portfolio/'+a['href'][9:]
intro=fragment('''<section class="comparison-intro" aria-label="How to read the models">
<div><strong>DistilBERT asks: what emotion does the text convey?</strong><p>Six competing emotion classes. Scores sum to 1 within each post.</p></div>
<div class="rhetoric-description"><strong>BART · Rhetorical frames</strong><p>Six independently scored frames. Several can score highly together.</p></div><div class="emotion-description"><strong>BART · Emotion</strong><p>The same six emotions as DistilBERT, using Lab 1’s expanded descriptions. Scores sum to 1 within each post.</p></div>
<p class="comparison-note">These posts have no human reference labels. This is an exploratory comparison of agreement and disagreement, not an accuracy test or a ranking of which model is better. Scores are model interpretations, not measurements of the author’s feelings or comparable probabilities of correctness. Timeline bubble colors always represent BART rhetoric, including in emotion comparison mode.</p>
<div class="comparison-controls"><label for="scoreView">Comparison mode</label><select id="scoreView"><option value="emotions">Emotion comparison · both models</option><option value="both">Emotion + rhetoric · original view</option></select><a href="data/post_scores.csv" download>Download scores (CSV)</a><a href="https://github.com/StrokeOfLuck/trump-iran-two-perspectives">Repository & methods ↗</a></div>
<details class="method-note"><summary>Scope and methods</summary><p>87 unique posts appear in 129 cards across 26 curated event windows. Repeated appearances share the same scores. This is the original timeline subset, not the full Iran-post corpus. Existing BART rhetoric and DistilBERT emotion scores are retained. BART emotion scores are freshly computed with the pinned Lab 1 checkpoint, selected formulation B, and multi_label=False. DistilBERT uses a 512-token limit; BART uses a 1,024-token text/hypothesis pair limit. None of these posts exceeded that limit. There are no human reference labels here, so accuracy and F1 are unavailable.</p><p>Event descriptions and dates are inherited from the original project and have not been independently reverified for this comparison. These before/after windows do not establish prediction or causation. <a href="https://strokeofluck.github.io/sean-data-portfolio/projects/assets/political-text-analysis/trump-iran-connected-timeline.html">Original timeline ↗</a></p></details>
</section>''')
soup.select_one('.lede-question').insert_after(intro)
soup.body['data-score-view']='emotions'
agreement=sum(max(p['emotion'],key=p['emotion'].get)==max(p['bart_emotion'],key=p['bart_emotion'].get) for p in posts.values())
agreement_note=soup.new_tag('p',attrs={'class':'comparison-note emotion-description','id':'emotion-agreement'})
agreement_note.string=f'Top emotion agrees on {agreement} of {len(posts)} unique posts ({agreement/len(posts):.1%}). Agreement is not accuracy. Each post is counted once, even when it appears around multiple events.'
soup.select_one('.comparison-intro').append(agreement_note)
events=[]
options=soup.select('#eventSelect option')
for i,event in enumerate(soup.select('.event-view')):
 row={'index':i,'date_label':options[i].get_text(' ',strip=True),'windows':{}}
 for label,selector in [('Day before','.before-posts'),('Event day','.eventday-posts'),('Day after','.after-posts')]:
  row['windows'][label]=list(dict.fromkeys(post_id(c) for c in event.select(selector+' .truth-card')))
 events.append(row)
summary={}
for kind in ('rhetoric','emotion','bart_emotion'):
 summary[kind]={}
 for window in ('Day before','Event day','Day after'):
  groups=[e['windows'][window] for e in events if e['windows'][window]]
  values={label:statistics.mean(statistics.mean(posts[id][kind][label] for id in group) for group in groups) for label in next(iter(posts.values()))[kind]}
  summary[kind][window]={'event_count':len(groups),'post_appearances':sum(map(len,groups)),'values':values}
old_summary=soup.select_one('.summary-table').find_parent(class_='panel-body')
summary_html='<h2>Event-balanced model summaries</h2><p>Average posts within each event/window, then average those event means with equal weight. Empty windows are excluded. These summaries cover the displayed 26-event subset; a post may appear around multiple events.</p><div class="summary-pair">'
for kind,title in [('rhetoric','BART · Rhetorical frames'),('bart_emotion','BART · Emotions'),('emotion','DistilBERT · Emotions')]:
 summary_html+=f'<section class="summary-{kind}"><h3>{title}</h3><div class="summary-scroll"><table class="dual-summary"><thead><tr><th>Category</th>'
 for w,d in summary[kind].items(): summary_html+=f'<th>{w}<small>{d["event_count"]} event windows</small></th>'
 summary_html+='</tr></thead><tbody>'
 for label in next(iter(posts.values()))[kind]:
  summary_html+='<tr><th>'+html.escape(label.title() if kind in ('emotion','bart_emotion') else label)+'</th>'
  for w,d in summary[kind].items():
   val=d['values'][label]
   summary_html+=f'<td><span class="summary-number">{val:.2f}</span><span class="dual-track"><span class="dual-fill {kind}" style="width:{val*100:.3f}%"></span></span></td>'
  summary_html+='</tr>'
 summary_html+='</tbody></table></div></section>'
summary_html+='</div>'
old_summary.clear();old_summary.append(fragment(summary_html))
style=soup.new_tag('style');style.string='''
.comparison-intro{margin:18px 0 28px;padding:20px 24px;background:#f5f5f1;border:1px solid #d8ddd9;border-radius:12px;display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;color:#273b3a}
.comparison-intro p{margin:5px 0;font-size:14px;line-height:1.5}.comparison-note,.comparison-controls,.method-note{grid-column:1/-1}.comparison-note{border-top:1px solid #d6ddda;padding-top:12px}.comparison-controls{display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:14px}.comparison-controls select{padding:8px;border:1px solid #a6b5ae;border-radius:5px;background:white}.comparison-controls a{color:#245751;text-decoration:underline}.method-note{font-size:13px}.method-note summary{cursor:pointer;font-weight:600}.dual-scores{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0 12px;text-align:left}.model-panel{min-width:0;border:1px solid #dbe2df;border-radius:8px;padding:10px;background:#fff}.model-title{font-size:12px;font-weight:750;letter-spacing:.02em;padding-bottom:9px;color:#254d46}.emotion-panel .model-title{color:#6e5084}.dual-row{display:grid;grid-template-columns:minmax(75px,1fr) minmax(24px,.7fr) 28px;gap:5px;align-items:center;font-size:11px;line-height:1.2;min-height:25px}.dual-row strong{font-variant-numeric:tabular-nums;font-size:11px}.dual-track{display:block;position:relative;height:6px;border-radius:4px;background:#e9eceb;overflow:hidden}.dual-fill{display:block;height:100%;border-radius:4px}.dual-fill.emotion{background:#88639d}.dual-fill.rhetoric{background:#497d71}.emotion-badge{display:inline-block;margin:5px 0 3px 6px;border-radius:6px;padding:5px 8px;background:#f0e8f6;color:#654479;font-size:11px;font-weight:700}.dominant-badge{font-size:11px!important}.summary-pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}.summary-pair h3{font-size:16px;margin:10px 0}.dual-summary{width:100%;border-collapse:collapse;font-size:12px}.dual-summary th,.dual-summary td{padding:9px 7px;border-bottom:1px solid #e2e7e3;text-align:left;vertical-align:middle}.dual-summary small{display:block;font-weight:400;font-size:10px;color:#68776f}.dual-summary .summary-number{display:block;margin-bottom:4px;font-variant-numeric:tabular-nums}.dual-summary td{min-width:66px}.dual-summary .dual-track{height:4px}body[data-score-view="emotion"] .rhetoric-panel,body[data-score-view="rhetoric"] .emotion-panel{display:none}body[data-score-view="emotion"] .dual-scores,body[data-score-view="rhetoric"] .dual-scores{grid-template-columns:1fr}
@media(max-width:700px){.comparison-intro,.summary-pair{grid-template-columns:1fr}.comparison-intro{padding:16px}.dual-scores{grid-template-columns:1fr}.dual-row{grid-template-columns:105px 1fr 32px;font-size:12px}.summary-pair{gap:20px}}
'''
style.string+='''
.dual-fill.bart_emotion{background:#3e79a0}.bart-emotion-panel .model-title{color:#326889}.bart-emotion-badge{background:#e7f0f7;color:#326889}
body[data-score-view="emotions"] .rhetoric-panel,body[data-score-view="emotions"] .summary-rhetoric,body[data-score-view="emotions"] .dominant-badge,body[data-score-view="emotions"] .rhetoric-description{display:none!important}
body:not([data-score-view="emotions"]) .bart-emotion-panel,body:not([data-score-view="emotions"]) .summary-bart_emotion,body:not([data-score-view="emotions"]) .bart-emotion-badge,body:not([data-score-view="emotions"]) .emotion-description{display:none!important}
.summary-scroll{overflow-x:auto}.comparison-controls select{max-width:100%}
'''
soup.head.append(style)
script=soup.new_tag('script');script.string='''document.addEventListener('DOMContentLoaded',function(){document.getElementById('scoreView').addEventListener('change',function(){document.body.dataset.scoreView=this.value;window.dispatchEvent(new Event('resize'));});});'''
soup.body.append(script)
for text in soup.find_all(string=True):
 if 'SVG rail rebuilt for clarity' in text: text.replace_with(str(text).replace('; SVG rail rebuilt for clarity',''))
from color_timeline import color_timeline
color_rows=color_timeline(soup, posts)
(out/'data/timeline_colors.json').write_text(json.dumps(color_rows,indent=2)+'\n',encoding='utf-8')
(out/'index.html').write_text(str(soup),encoding='utf-8')
(out/'data/event_windows.json').write_text(json.dumps(events,indent=2)+'\n',encoding='utf-8')
(out/'data/summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
with (out/'data/post_scores.csv').open('w',encoding='utf-8',newline='') as f:
 rows=[{'truth_id':p['truth_id'],'text':p['text'],'truth_url':p['truth_url'],**{'emotion_'+k:v for k,v in p['emotion'].items()},**{'rhetoric_'+k:v for k,v in p['rhetoric'].items()},**{'bart_emotion_'+k:v for k,v in p['bart_emotion'].items()}} for p in posts.values()]
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('Built',len(events),'events;',len(cards),'cards;',len(posts),'unique posts.')
