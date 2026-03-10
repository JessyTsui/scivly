# Reference Config

This directory stores public-safe reference data for Scivly's paper triage system.

It exists for values that should be versioned and reviewed like code, but should not live in
private prompts or ad hoc environment variables.

## Files

- `paper_triage_defaults.yaml`: default thresholds, score bands, category priors, and rerank gates
- `institution_priors.yaml`: editable institution tiers and aliases used for soft metadata boosts
- `lab_priors.yaml`: editable lab and research-org tiers and aliases used for soft metadata boosts

## Rules

- Keep these files public-safe and explanation-friendly.
- Use tiers and coarse points instead of fake precision.
- Treat dictionaries as soft priors, never as hard allowlists.
- Update aliases when affiliation strings drift.
- Prefer normalized exact matching or high-confidence prefix matching for aliases, not loose
  substring matching.
- Bump `version` when a change affects scoring behavior.

## Review workflow

1. Change the YAML.
2. Update the matching explanation in
   [`docs/product/paper-triage-scoring.md`](../../docs/product/paper-triage-scoring.md) if the logic
   changed.
3. Record the new version in worker logs and evaluation runs.
