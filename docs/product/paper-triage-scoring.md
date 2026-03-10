# Paper Triage and Scoring Design

This document defines the first public-safe paper triage system for Scivly's arXiv-first ingestion
pipeline. It is intentionally explainable, low-cost, and easy to tune in small steps.

The system is designed around one practical constraint: we should not download and parse every PDF
or source package before we know whether a paper is worth deeper work. Metadata must carry the
first-pass ranking.

## Scope

- Source scope: arXiv first
- Initial decision scope: metadata-first ranking before PDF download
- Optional deep processing: PDF parsing, figure extraction, structured summary, and source fetch
- Output scope: candidate queues for digest generation, library indexing, and follow-up QA

## External references we can actually inspect

We did not find public exact weight tables for products such as AlphaXiv, Semantic Scholar, or
Litmaps. The design below therefore borrows from public signal choices and published methods, not
from any claim of replicating a private ranking stack.

| Reference | Public takeaway | Scivly implication |
| --- | --- | --- |
| [arXiv API user manual](https://info.arxiv.org/help/api/user-manual.html) | The public API exposes title, abstract, authors, categories, comments, and optional affiliation, journal reference, and DOI fields. | First-pass scoring should rely on metadata that is already cheap to fetch. |
| [Modernizing arXiv's Classification Processes](https://info.arxiv.org/about/reports/2021_arXiv_annual_report.pdf) | arXiv reports that its replacement classifier works on title and abstract only. | Title plus abstract is enough for a practical coarse routing pass. |
| [Citeomatic](https://arxiv.org/abs/1801.08904) | Public abstract: recommendations combine titles, abstracts, authors, venues, keyphrases, and citation signals. | Hybrid ranking should mix text relevance and metadata priors instead of using prestige alone. |
| [arxiv-sanity-lite](https://github.com/karpathy/arxiv-sanity-lite) | The open implementation ranks papers from title and abstract features and learned user signal. | A lightweight metadata ranker is a valid baseline before expensive enrichment. |
| [CSRankings FAQ](https://csrankings.org/faq) | The project uses fractional credit to avoid over-rewarding very large author lists. | Prestige and affiliation boosts should be normalized by author count. |

## Design goals

1. Cheap first pass: score papers before PDF download whenever possible.
2. Explainable output: every non-trivial score must produce reasons.
3. Capped prestige: famous authors, labs, and schools can help, but cannot rescue an irrelevant paper.
4. Multi-stage escalation: only a small candidate pool reaches PDF parsing or source fetch.
5. User-tunable behavior: topic profiles and priors must be editable without code changes.

## Pipeline stages

### Stage 0: Ingest and deduplicate

- Pull new arXiv entries by category and announcement window.
- Canonicalize `arxiv_id`, version, title, and author strings.
- Merge cross-lists into a single paper record.
- Keep raw metadata even if a paper later fails ranking, so tuning can be replayed.

### Stage 1: Hard filters

Hard filters should remove obviously irrelevant or low-value items before scoring:

- allow only selected primary and secondary categories
- reject withdrawn, errata, or empty-metadata entries
- drop malformed records with missing title or missing abstract
- apply profile-specific negative rules for domains the user explicitly does not track

Hard filters must stay narrow. Global filters should block only clearly bad inputs. Most topic
decisions belong in scoring, not in brittle exclusion rules.

### Stage 2: Metadata score

The metadata score is the main decision point for whether a paper deserves PDF download.

Default point budget:

| Component | Max points | Notes |
| --- | --- | --- |
| Topical relevance | 45 | Title, abstract, category, and topic-profile similarity. |
| Prestige priors | 20 | Author, institution, and lab priors with a hard cap. |
| Actionability | 15 | Code, dataset, benchmark, accepted-to, and project-page signals. |
| Profile fit and freshness | 10 | Match to the user's saved themes and current monitoring windows. |
| Novelty and diversity | 10 | Avoid flooding the queue with near-duplicates of the same idea. |
| Penalties | -25 | Missing detail, suspicious mismatch, or obvious out-of-scope patterns. |

Recommended thresholds:

| Band | Action |
| --- | --- |
| `< 35` | Drop after logging reasons. |
| `35-54` | Keep metadata only for analytics and replay. |
| `55-64` | Download PDF and queue for deterministic parsing. |
| `65-74` | Also send to the small-model reranker. |
| `75-81` | Treat as digest candidate after PDF validation. |
| `>= 82` | Allow optional source fetch if downstream extraction would benefit. |

### Stage 3: Small-model rerank

After metadata scoring, a small model such as `gpt-4o-mini` can refine the shortlist. This model
should not act as the only judge. It should only adjust a candidate that already passed a metadata
bar.

Use the small model for:

- topic fit when the abstract is ambiguous but non-empty
- paper type classification, such as method, benchmark, survey, dataset, or opinion piece
- likely user value for a specific watchlist
- conflict resolution among several very similar papers on the same day

Guardrails:

- run only on the top candidate pool per profile per day
- limit the score delta to `+/- 12` points
- require structured output with reasons, not free-form ranking text
- log both the pre-LLM score and the post-LLM score

### Stage 4: PDF score

Only candidates that pass the metadata gate should reach PDF parsing. Full-text processing can then
extract stronger signals:

- concrete task and dataset mentions
- experiment density and ablation presence
- figure and table quality
- claims that appear to match the abstract
- citation patterns and overlap with tracked topics

This stage should refine delivery and indexing decisions. It should not replace the metadata gate.

### Stage 5: Optional source fetch

Source packages are the most expensive and least reliable input. They should be fetched only for
papers that benefit from deeper structural extraction, for example equation-heavy work, appendix
figures, or table reconstruction.

## Default metadata weighting

The public-safe default weighting is described in
[`config/reference/paper_triage_defaults.yaml`](../../config/reference/paper_triage_defaults.yaml).
The logic is designed around five signal families.

### Topical relevance

Topical relevance is the strongest component and should remain the strongest component.

Suggested sub-signals:

- embedding similarity between the topic profile and `title + abstract`
- keyword coverage for task, method, model family, and benchmark names
- category prior, with higher defaults for `cs.AI`, `cs.CL`, `cs.CV`, `cs.LG`, `cs.RO`, and
  `stat.ML`
- short recency boost when a topic has a known fast-moving burst

If the title and abstract are weak, no prestige signal should fully rescue the paper.

### Prestige priors

Prestige priors are useful but dangerous. They can improve early ranking, but they also amplify
bias. For that reason they should be soft boosts, not filters.

Recommended split inside the prestige bucket:

- author prior: 45 percent of prestige points
- institution prior: 30 percent of prestige points
- lab prior: 25 percent of prestige points

Recommended normalization:

```text
prestige_raw = 0.45 * author_prior
             + 0.30 * institution_prior
             + 0.25 * lab_prior

author_count_factor = clamp(0.55, 1.00, 2.2 / sqrt(author_count))

prestige_points = min(18, 20 * prestige_raw * author_count_factor)
```

Notes:

- `author_prior` should come from Scivly history, manual watchlists, and repeated positive feedback,
  not from a static celebrity table.
- `institution_prior` and `lab_prior` should use the seed dictionaries in
  [`config/reference/`](../../config/reference/README.md).
- If affiliation or lab resolution is inferred rather than explicit, apply a discount before
  scoring.
- The combined prestige contribution is capped below the full 20-point bucket so weak topical fit
  cannot be overruled by brand alone.

### Actionability

Actionability is a strong early signal for what belongs in a daily digest.

Useful metadata clues:

- code release or project page in comments
- benchmark or dataset terms in title and abstract
- accepted-to venue comments
- explicit evaluation language, such as ablation, robustness, or scaling study

### Profile fit and freshness

This component helps personalize the queue:

- direct match to a saved theme
- direct match to a tracked author or lab
- recent burst in a tracked subtopic
- workspace-specific exclusions or boosts

### Novelty and diversity

A daily digest should not be a duplicate list. Diversity scoring should reduce same-day crowding
from highly similar papers.

Useful strategies:

- cluster same-day abstracts and keep only the strongest representative near the top
- reduce score for repeated incremental variants from the same author set
- preserve diversity across tracked subtopics when several candidates tie

## Institution and lab dictionaries

Scivly should keep public-safe, versioned dictionaries for soft priors. They live in:

- [`config/reference/institution_priors.yaml`](../../config/reference/institution_priors.yaml)
- [`config/reference/lab_priors.yaml`](../../config/reference/lab_priors.yaml)

The dictionaries should follow four rules:

1. They are soft priors, not hard filters.
2. They are tiered, not pseudo-precise numeric rankings.
3. They must remain editable because research quality changes over time.
4. They should record aliases to make affiliation resolution robust.

## Handling author count, institution, and lab effects

Author count should matter, but not in a way that destroys legitimate multi-author papers.

Recommended behavior:

- normalize prestige by author count using an inverse-square-root rule
- if per-author affiliation is known, weight first author and last author more heavily
- if per-author affiliation is missing, use the strongest resolved affiliation with an uncertainty
  discount
- cap the total prestige uplift so it cannot overtake topic relevance

This is intentionally softer than full fractional credit. The goal is ranking for triage, not
credit assignment for a leaderboard.

## Explainability requirements

Every candidate that survives hard filters should persist:

- the score version
- the topic profile version
- the matched positive and negative rules
- the per-component subscores
- the final decision and stage

This allows later tuning without guessing why a paper was dropped or promoted.

## Tuning workflow

Start with one global default profile and adjust carefully.

1. Review false negatives from the dropped and metadata-only bands.
2. Review false positives from the PDF and digest bands.
3. Adjust one rule family at a time.
4. Bump the config version when thresholds or point budgets change.
5. Keep manual notes about why a change was made.

## Near-term implementation plan

1. Store the default scoring profile in
   [`config/reference/paper_triage_defaults.yaml`](../../config/reference/paper_triage_defaults.yaml).
2. Store institution and lab priors in versioned YAML dictionaries.
3. Add a deterministic metadata scorer in `workers/arxiv/`.
4. Add structured small-model reranking behind a threshold gate.
5. Persist score explanations for every candidate.

## References

- [arXiv API User's Manual](https://info.arxiv.org/help/api/user-manual.html)
- [Modernizing arXiv's Classification Processes](https://info.arxiv.org/about/reports/2021_arXiv_annual_report.pdf)
- [Citeomatic: A Research Paper Recommendation System with Citation Embeddings](https://arxiv.org/abs/1801.08904)
- [arxiv-sanity-lite](https://github.com/karpathy/arxiv-sanity-lite)
- [CSRankings FAQ](https://csrankings.org/faq)
