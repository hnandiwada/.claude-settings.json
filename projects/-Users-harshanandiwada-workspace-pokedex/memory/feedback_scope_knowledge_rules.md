---
name: feedback-scope-knowledge-rules
description: "rules added to .claude knowledge/patterns must be scoped to the vendors that hit the problem, not written as universal mandates"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 98a7d00b-5b6f-40ed-aa7e-b2e43cc6129c
  modified: 2026-10-05T21:19:48.926Z
---

When writing a rule into `.claude/references/integration-patterns.md` or `integration-gotchas.md` from a fix that touched some integrations, scope it to the situation that triggers it. Don't phrase it so every integration must adopt the mechanism.

**Why:** for TRA-2952 (WriteNotReturnedException), I first wrote the patterns rule and a reviewer checklist item that read as "every write must poll its read-back". The user pushed back: most vendors return the record on the first read, and a universal rule would push writers and reviewers to add speculative polls.

**How to apply:** lead with "only when X is observed", say what the default is when it isn't, and make sure reviewer `[BLOCK]` items can't fire on integrations that don't have the problem.
