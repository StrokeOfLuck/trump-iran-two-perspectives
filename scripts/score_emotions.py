import sys, os, json, csv, hashlib, time
from pathlib import Path
root=Path(__file__).resolve().parent.parent
os.environ['HF_HOME']=str(root/'.cache/huggingface')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
torch.set_num_threads(4)
model_id='bhadresh-savani/distilbert-base-uncased-finetuned-emotion'
revision='11350faca8e85c4861766cec4c30dec55fd06bb9'
scores=list(csv.DictReader((root/'source/original-bart-scores.csv').open(encoding='utf-8')))
texts={p['truth_id']:p for p in json.loads((root/'source/posts.json').read_text(encoding='utf-8'))}
tokenizer=AutoTokenizer.from_pretrained(model_id,revision=revision)
model=AutoModelForSequenceClassification.from_pretrained(model_id,revision=revision).eval()
result=[]
for start in range(0,len(scores),8):
    group=scores[start:start+8]
    batch=[texts[r['truth_id']]['text'] for r in group]
    inputs=tokenizer(batch,padding=True,truncation=True,max_length=512,return_tensors='pt')
    with torch.inference_mode():
        probs=model(**inputs).logits.softmax(dim=-1).tolist()
    for row,text,values in zip(group,batch,probs):
        tokens=len(tokenizer(text,add_special_tokens=True,truncation=False)['input_ids'])
        source=texts[row['truth_id']]
        result.append({'truth_id':row['truth_id'],'text':text,'truth_url':source['truth_url'],'archive_url':source['archive_url'],'created_at_et':source['created_at_et'],'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'emotion':{model.config.id2label[i].lower():p for i,p in enumerate(values)},'rhetoric':{k:float(v) for k,v in row.items() if k!='truth_id'},'emotion_input_tokens':tokens,'emotion_truncated':tokens>512})
    print(f'Scored {len(result)}/{len(scores)} posts',flush=True)
out=root/'data'
out.mkdir(parents=True,exist_ok=True)
payload={'emotion_model':model_id,'emotion_revision':revision,'emotion_max_tokens':512,'rhetoric_model':'facebook/bart-large-mnli','rhetoric_revision':None,'rhetoric_provenance':'Existing 26-event subset scores from StrokeOfLuck/trump-iran-rhetoric-analysis, main at b6711ed995ec540a22ebc266bb0f809d0f663b36. Original scoring did not pin a model revision.','posts':result}
(out/'scores.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved',len(result),'posts. Truncated:',sum(p['emotion_truncated'] for p in result),flush=True)
