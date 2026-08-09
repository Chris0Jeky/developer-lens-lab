<!--
See CONTRIBUTING.md. Open this pull request ready for review when the work is complete. Explain
what was proved and what was not; a research result may be rejected and is never automatic product
promotion.
-->

## What changed

<!-- One paragraph. Link the issue if there is one. -->

## Proof

Narrowest command that exercises this change:

```powershell

```

Result:

## Not verified

<!-- State what this change does NOT prove. -->

## Checklist

- [ ] Invented/public fixtures only — no real or private datasets, Parquet files, `.dllab` content,
      generated run outputs, credentials, provider IDs, repository allowlists, or private links.
- [ ] Missing, unavailable, censored, restricted, refused, and intentionally omitted evidence stay
      explicit; no missing value is converted to zero.
- [ ] Reproducibility and ResearchPack/EvaluationBundle compatibility remain intact, with a
      deterministic fallback when a model or service is absent.
- [ ] Nothing installs itself into or silently promotes through Developer Lens.
- [ ] The narrowest proving command above was actually run and exercises the changed paths.
- [ ] `uv run dllab context verify` and `git diff --check origin/main...HEAD` pass for docs/templates;
      the relevant focused or full gate was run for code/config changes.
- [ ] I am proposing this contribution under **AGPL-3.0-only** and have read the q-7 contribution
      policy note in `CONTRIBUTING.md`.
