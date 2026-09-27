# Trump–Iran: Emotion & Rhetoric

**[Open the interactive timeline →](https://strokeofluck.github.io/trump-iran-two-perspectives/)**

Explore two model interpretations of the same Trump Truth Social posts using the original connected event timeline. Each card pairs existing BART rhetorical-frame scores with newly computed DistilBERT emotion scores. The original project is preserved separately.

## What is being compared?

| Model | Task | Scores |
|---|---|---|
| `bhadresh-savani/distilbert-base-uncased-finetuned-emotion` | Emotion classification | Sadness, joy, love, anger, fear, surprise; softmax scores sum to one per post |
| `facebook/bart-large-mnli` | Zero-shot rhetorical framing | Threat, victory, diplomacy, ceasefire/ending, blame allies, media criticism; independently scored labels can all be high |

This is a comparison of perspectives, not an accuracy leaderboard. A threat can use celebratory language; a high emotion score does not establish the speaker's feelings. DistilBERT's emotion training domain differs from these political posts. Human reference labels would be needed to evaluate accuracy, precision, recall or F1 here. Cross-model score differences are not meaningful probability differences.

## Data and provenance

- 87 unique posts, 129 displayed appearances, 26 curated event dates; this is not the full corpus.
- Timeline HTML adapted from [the original portfolio timeline](https://strokeofluck.github.io/sean-data-portfolio/projects/assets/political-text-analysis/trump-iran-connected-timeline.html). Its event descriptions and dates are inherited, not independently reverified for this comparison.
- Text and BART scores come from [StrokeOfLuck/trump-iran-rhetoric-analysis](https://github.com/StrokeOfLuck/trump-iran-rhetoric-analysis), commit `b6711ed995ec540a22ebc266bb0f809d0f663b36`, files `data/trump_iran_event_windows_unique_dates.csv` and `data/trump_iran_zero_shot_scores_26event_subset.csv`.
- DistilBERT revision: `11350faca8e85c4861766cec4c30dec55fd06bb9`, identical to Lab 1. Scores were calculated locally from the CSV text, with a 512-token limit and softmax over the six model labels. No included post exceeded the limit. Text hashes and token counts are in `data/scores.json`.
- BART scores are preserved from the original project, not rerun. The original notebook used `multi_label=True` and `This text expresses {}.` with frame descriptions; it did not record an immutable model revision. Exact historical BART rerun reproducibility is therefore limited.
- Repeated cards use the same post-level scores. The summaries first average posts within each displayed event/window, then average those means equally across nonempty windows: 20 day-before windows, 21 event-day windows, and 21 day-after windows. Empty windows are excluded rather than treated as zeros.
- These event windows lack a non-event counterfactual and do not establish prediction or causation.

## Explore

Open `index.html` directly, or serve the folder:

```sh
python -m http.server 8874
```

Use Previous/Next event or the date selector. Post carousels and full-text expansion work as on the original page. The score selector switches between both models, emotion only, and rhetoric only. `data/post_scores.csv` is a downloadable flat table; `data/event_windows.json` records the displayed group membership and `data/summary.json` contains the unrounded summary values.

## Reproduce

```sh
python -m venv .venv
# Activate the virtual environment for your shell, then:
pip install -r requirements.txt
python scripts/score_emotions.py
python scripts/build.py
```

Scoring downloads the pinned public DistilBERT checkpoint. Building uses only the saved scores and the original HTML under `source/`. The source posts are preserved as strings so long Truth Social IDs are never rounded. No API key, live inference server, or paid model service is required for visitors.

For GitHub Pages, publish the repository's `main` branch root. `.nojekyll` is included.

## Validation

Every displayed card joins to exactly one post-level score record. Emotion scores sum to one within floating-point tolerance; all twelve scores per post are finite and within [0,1]. Event summaries are recalculated from displayed membership, with duplicate post IDs counted once within each event/window. See `scripts/validate.py` for repeatable checks.
