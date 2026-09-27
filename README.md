# Trump–Iran: Emotion & Rhetoric

**[Open the interactive timeline →](https://strokeofluck.github.io/trump-iran-two-perspectives/)**

Explore two model interpretations of the same Trump Truth Social posts using the original connected event timeline. The default view compares fresh BART emotion scores with DistilBERT emotion scores. A toggle returns to the original BART rhetoric and DistilBERT emotion view. The original project is preserved separately.

## What is being compared?

| Model | Task | Scores |
|---|---|---|
| `bhadresh-savani/distilbert-base-uncased-finetuned-emotion` | Emotion classification | Sadness, joy, love, anger, fear, surprise; softmax scores sum to one per post |
| `facebook/bart-large-mnli` | Zero-shot emotion classification | Sadness, joy, love, anger, fear, surprise; competing labels sum to one per post |
| `facebook/bart-large-mnli` | Zero-shot rhetorical framing | Threat, victory, diplomacy, ceasefire/ending, blame allies, media criticism; independently scored labels can all be high |

This is a comparison of perspectives, not an accuracy leaderboard. A threat can use celebratory language; a high emotion score does not establish the speaker's feelings. DistilBERT's emotion training domain differs from these political posts. Human reference labels would be needed to evaluate accuracy, precision, recall or F1 here. Cross-model score differences are not meaningful probability differences.

## Emotion comparison

Both models now score the same six emotions on the same 87 posts. **These posts have no human reference labels.** Agreement shows where the models give the same top emotion, not whether either model is correct. This is a fun exploratory comparison, not an accuracy test or a ranking.

BART was freshly run using Lab 1's selected formulation B: sadness or unhappiness, happiness or joy, love or affection, anger or frustration, fear or anxiety, and surprise or astonishment. It uses revision `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`, template `This text expresses {}.`, and `multi_label=False`. These settings were not tuned on the Trump posts. No posts were truncated at the 1,024-token text/hypothesis pair limit.

Existing DistilBERT emotion and BART rhetoric scores are preserved. Run metadata and all three score sets are saved in `data/scores.json`; the CSV includes the new `bart_emotion_` columns. The agreement count counts each unique post once.

## Timeline colors

Bubble color is the highest mean BART rhetoric score among the unique posts in that displayed event-day window. Size retains UCDP significance. Exact ties (within 1e-9 numerical tolerance) split evenly between tied category colors; no scored event-day posts produces a gray bubble. Split areas denote tied leaders, not percentages of rhetoric. Tooltips include the top two mean scores and post count. Colors remain rhetoric-based in both comparison modes.

## Data and provenance

- 87 unique posts, 129 displayed appearances, 26 curated event dates; this is not the full corpus.
- Timeline HTML adapted from [the original portfolio timeline](https://strokeofluck.github.io/sean-data-portfolio/projects/assets/political-text-analysis/trump-iran-connected-timeline.html). Its event descriptions and dates are inherited, not independently reverified for this comparison.
- Text and original BART rhetoric scores come from [StrokeOfLuck/trump-iran-rhetoric-analysis](https://github.com/StrokeOfLuck/trump-iran-rhetoric-analysis), commit `b6711ed995ec540a22ebc266bb0f809d0f663b36`, files `data/trump_iran_event_windows_unique_dates.csv` and `data/trump_iran_zero_shot_scores_26event_subset.csv`.
- DistilBERT revision: `11350faca8e85c4861766cec4c30dec55fd06bb9`, identical to Lab 1. Scores were calculated locally from the CSV text, with a 512-token limit and softmax over the six model labels. No included post exceeded the limit. Text hashes and token counts are in `data/scores.json`.
- The published timeline preserves the original project's BART rhetoric scores. A separate fresh local rerun reproduced them at the displayed precision (see **Independent BART rerun** below). The original notebook used `multi_label=True` and `This text expresses {}.` with frame descriptions; it did not record an immutable model revision. Exact historical BART rerun reproducibility is therefore limited.
- Repeated cards use the same post-level scores. The summaries first average posts within each displayed event/window, then average those means equally across nonempty windows: 20 day-before windows, 21 event-day windows, and 21 day-after windows. Empty windows are excluded rather than treated as zeros.
- These event windows lack a non-event counterfactual and do not establish prediction or causation.

## Independent BART rerun

On September 27, 2026 (UTC), BART was freshly rerun locally on all **87 unique posts × 6 frames = 522 scores**, using the original frame descriptions, `multi_label=True`, and the hypothesis template `This text expresses {}.`.

- **522/522 post-level scores match the originals at two decimal places.**
- **18/18 event-balanced summary values match at two decimal places.**
- **0/87 posts changed their highest-scoring frame.**
- Mean absolute score difference: **0.0000000931**.
- Maximum absolute score difference: **0.0000015795**.
- No posts were truncated.

The fresh run used `facebook/bart-large-mnli` revision `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`, Python 3.12.14, PyTorch 2.14.0+cpu, and Transformers 4.57.6, on CPU in float32. The tiny differences are consistent with numerical variation; the displayed results reproduce the original analysis. This is a reproducibility check, not an accuracy evaluation.

[Read the detailed rerun comparison, including all 18 summary values →](BART-RERUN-RESULTS.md)

The published timeline still uses the preserved original BART rhetoric scores. This documentation records the separate fresh run; it does not replace the live site's data. DistilBERT was not rerun in this check.

## Explore

Open `index.html` directly, or serve the folder:

```sh
python -m http.server 8874
```

Use Previous/Next event or the date selector. Post carousels and full-text expansion work as on the original page. The comparison selector switches between both models doing emotion and the original emotion plus rhetoric view. `data/post_scores.csv` is a downloadable flat table; `data/event_windows.json` records the displayed group membership and `data/summary.json` contains the unrounded summary values.

## Reproduce

```sh
python -m venv .venv
# Activate the virtual environment for your shell, then:
pip install -r requirements.txt
python scripts/score_emotions.py
python scripts/score_bart_emotions.py
python scripts/build.py
```

Scoring downloads the pinned public DistilBERT and BART checkpoints. Building uses only the saved scores and the original HTML under `source/`. The source posts are preserved as strings so long Truth Social IDs are never rounded. No API key, live inference server, or paid model service is required for visitors.

For GitHub Pages, publish the repository's `main` branch root. `.nojekyll` is included.

## Validation

Every displayed card joins to exactly one post-level score record. Both emotion score sets sum to one within floating-point tolerance; all eighteen scores per post are finite and within [0,1]. Event summaries are recalculated from displayed membership, with duplicate post IDs counted once within each event/window. See `scripts/validate.py` for repeatable checks.
