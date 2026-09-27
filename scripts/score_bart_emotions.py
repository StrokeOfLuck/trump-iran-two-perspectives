"""Score the same posts using Lab 1's selected emotion descriptions."""
import os,json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
os.environ.setdefault('HF_HOME',str(ROOT/'.cache/huggingface'))
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
import torch,transformers
from transformers import pipeline
MODEL='facebook/bart-large-mnli'
REVISION='d7645e127eaf1aefc7862fd59a17a5aa8558b8ce'
LABELS={'sadness':'sadness or unhappiness','joy':'happiness or joy','love':'love or affection','anger':'anger or frustration','fear':'fear or anxiety','surprise':'surprise or astonishment'}
TEMPLATE='This text expresses {}.'
def main():
 torch.set_num_threads(4)
 payload=json.loads((ROOT/'data/scores.json').read_text(encoding='utf-8'))
 classifier=pipeline('zero-shot-classification',model=MODEL,revision=REVISION,device=-1)
 start=time.monotonic()
 for i,p in enumerate(payload['posts'],1):
  assert hashlib.sha256(p['text'].encode()).hexdigest()==p['text_sha256']
  result=classifier(p['text'],candidate_labels=list(LABELS.values()),hypothesis_template=TEMPLATE,multi_label=False,batch_size=4)
  values=dict(zip(result['labels'],result['scores']))
  p['bart_emotion']={k:float(values[v]) for k,v in LABELS.items()}
  lengths=[len(classifier.tokenizer(p['text'],TEMPLATE.format(v),truncation=False)['input_ids']) for v in LABELS.values()]
  p['bart_emotion_max_pair_tokens']=max(lengths)
  p['bart_emotion_truncated']=max(lengths)>classifier.tokenizer.model_max_length
  print(f'BART emotion {i}/{len(payload["posts"])} ({time.monotonic()-start:.0f}s)',flush=True)
 payload['bart_emotion_run']={'model':MODEL,'revision':REVISION,'candidate_labels':LABELS,'hypothesis_template':TEMPLATE,'multi_label':False,'max_length':classifier.tokenizer.model_max_length,'truncation':'only_first','device':'cpu','torch':torch.__version__,'transformers':transformers.__version__,'utc':datetime.now(timezone.utc).isoformat(),'truncated_posts':sum(p['bart_emotion_truncated'] for p in payload['posts']),'reference_labels':None,'source_settings':'Lab 1 selected formulation B; no tuning on the Trump posts.'}
 (ROOT/'data/scores.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Saved BART emotion scores. Existing emotion and rhetoric values preserved.',flush=True)
if __name__=='__main__':main()
