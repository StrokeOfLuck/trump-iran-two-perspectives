# BART rerun results

Fresh inference completed for **87 unique posts × 6 frames = 522 scores**, on 2026-09-27T03:35:04.489994+00:00.

The original frame descriptions, hypothesis template, and independent multi-label scoring were retained. The current checkpoint is pinned; the historical run did not pin a revision, so its exact environment cannot be reconstructed.

- Mean absolute score difference: 0.0000000931
- Maximum absolute score difference: 0.0000015795
- Post-level scores different at two decimals: 0/522
- Posts with a different highest-scoring frame: 0/87
- Event-summary cells different at two decimals: 0/18
- Posts truncated: 0/87

| Window | Frame | Original | Rerun | Difference |
|---|---|---:|---:|---:|
| Day before | Threat | 0.54763393 | 0.54763389 | -0.0000000405 |
| Day before | Victory | 0.67296123 | 0.67296124 | +0.0000000107 |
| Day before | Diplomacy | 0.22273545 | 0.22273551 | +0.0000000600 |
| Day before | Ceasefire / Ending | 0.34289053 | 0.34289044 | -0.0000000911 |
| Day before | Blame Allies | 0.07084262 | 0.07084259 | -0.0000000213 |
| Day before | Media Criticism | 0.34286164 | 0.34286164 | +0.0000000000 |
| Event day | Threat | 0.52447802 | 0.52447799 | -0.0000000314 |
| Event day | Victory | 0.76111595 | 0.76111595 | +0.0000000053 |
| Event day | Diplomacy | 0.20924541 | 0.20924539 | -0.0000000168 |
| Event day | Ceasefire / Ending | 0.32792368 | 0.32792361 | -0.0000000681 |
| Event day | Blame Allies | 0.12468281 | 0.12468283 | +0.0000000199 |
| Event day | Media Criticism | 0.33287015 | 0.33287015 | +0.0000000000 |
| Day after | Threat | 0.48452707 | 0.48452707 | +0.0000000008 |
| Day after | Victory | 0.69967070 | 0.69967070 | +0.0000000031 |
| Day after | Diplomacy | 0.27170956 | 0.27170956 | +0.0000000007 |
| Day after | Ceasefire / Ending | 0.39100892 | 0.39100872 | -0.0000001974 |
| Day after | Blame Allies | 0.11238546 | 0.11238546 | +0.0000000036 |
| Day after | Media Criticism | 0.35114521 | 0.35114521 | +0.0000000000 |

## Reproducibility

Model: `facebook/bart-large-mnli`; revision: `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`.
Runtime: Python 3.12.14, PyTorch 2.14.0+cpu, Transformers 4.57.6; CPU, float32.

Source: https://github.com/StrokeOfLuck/trump-iran-rhetoric-analysis/tree/b6711ed995ec540a22ebc266bb0f809d0f663b36

This is a reproducibility comparison, not a model-accuracy test. DistilBERT predictions remain unchanged. The rerun does not add new posts, change the framing definitions, or validate the event descriptions.
