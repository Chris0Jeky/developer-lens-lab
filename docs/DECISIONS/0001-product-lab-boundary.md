# ADR-0001: Product, lab, and artifact-store boundary

Status: accepted, 2026-08-06.

Developer Lens owns product contracts, deterministic behavior, runtime adapters, and promotion.
Developer Lens Lab owns invented research, experiments, evaluation, and rejection evidence. Large
or generated objects live under a confined ignored lab root and never in Git. Product schemas enter
as generated commit-pinned snapshots; bundles return only for review.

This avoids a Python dependency in the product, a forked user-facing product, submodule coupling,
and automatic promotion. Reversal requires an explicit owner/product architecture decision.
