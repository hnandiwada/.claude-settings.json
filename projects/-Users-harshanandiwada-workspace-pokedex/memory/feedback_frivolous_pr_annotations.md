---
name: feedback-frivolous-pr-annotations
description: "fix-tests/iterate-integration PRs shouldn't add api-summary AMENDED sections or \"what we're doing\" comments for simple fixes"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de25cfb6-1812-4ee6-a778-323837ece03d
---

Don't add an "AMENDED" section to an integration's `api-summary.md`, and don't add an explanatory comment, for simple fixes — a missed enumerated value, a new key access, a straightforward deduplication. Both are noise the user has to read past.

**Why:** these annotations earn their place only when the underlying logic is genuinely complicated. For a one-line fix they're frivolous, and the user has been seeing this repeatedly out of `/fix-tests` (and by extension `/iterate-integration`) PRs. Comments explaining "this is what we're doing" are redundant with self-documenting code per the repo's code-style rule; api-summary AMENDED sections just log churn nobody needs.

A comment is still warranted when the fix touches something genuinely non-obvious — e.g. mapping an unintuitive vendor enum value (`UNDISP` → `order_shipment`) where a reader can't infer the reasoning from the code alone.

**How to apply:** when running `/fix-tests` or `/iterate-integration`, or reviewing their output before shipping — skip AMENDED-style api-summary additions and skip narrating comments for simple changes (missing enum case, new field access, dedup logic). Only add a comment if the mapping/logic is non-obvious on its own. The user believes the current `.claude/` skill/reference wording either doesn't state this clearly or isn't being followed — worth checking `.claude/skills/fix-tests/` and `.claude/references/integration-patterns.md` for where this should be tightened.
