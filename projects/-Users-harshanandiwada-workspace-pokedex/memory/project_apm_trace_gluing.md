---
name: apm-trace-gluing-investigation
description: Open investigation into APM traces on lambda-api-prod that glue many sequential customer invocations under one trace_id; suspect ThreadPoolExecutor + ddtrace + provisioned concurrency interaction.
metadata: 
  node_type: memory
  type: project
  originSessionId: 000ea2f4-4765-4f27-b1cf-fc771da549bc
---

User noticed traces on `lambda-api-prod` where one trace_id contains dozens of distinct Lambda invocations (different request_ids, same endpoint, e.g. 32x `GET /wms/inventory` under trace 6419210676144968466).

Confirmed signals from that trace:
- Customer client: `GuzzleHttp/7` (no DD instrumentation, not propagating headers)
- All invocations: `cold_start: false`, `init_type: provisioned-concurrency`
- Strictly sequential (zero overlap), ~1s per request, ~2s gap
- Same warm container across all 32

Actual cause (refined 2026-06-02): ThreadPoolExecutor was a red herring — the glued endpoints (e.g. `GET /wms/inventory`) don't hit any of the TPE call sites. Real culprit is **datadog-lambda's context reset failing on warm provisioned-concurrency containers** with `serverless_wsgi`. Each invocation's `aws.lambda` span inherits the previous invocation's trace_id from leftover contextvar state on the warm container.

**Attempt 1 (insufficient)**: `tracer.context_provider.activate(None)` at top of `handler()` in `lambda_handlers/api.py`. Reduced glued invocations per trace from ~32 to ~6 but didn't eliminate. Reason: datadog-lambda layer wraps handler externally and starts `aws.lambda` span BEFORE handler body runs, so context clear was too late.

**Attempt 2 (deployed 2026-06-03)**: set `DD_TRACE_PROPAGATION_STYLE_EXTRACT=none` env var on all Lambdas via `templates/lambda_services.py`. Tells dd-trace-py to never extract incoming trace context, so each invocation starts fresh regardless of warm-container state leakage. The `activate(None)` was reverted as redundant.

Crawler is unaffected — ddtrace's celery integration already creates one `celery.run` root per task properly (confirmed via trace 6a1f71f200000000a389502f2514f0f0: 139 spans, exactly 1 celery.run, one org/connection/function).

**Verification after deploy:** pull a few recent traces from `lambda-api-prod` and confirm each has exactly one `aws.lambda` / `flask.request` / `request_id`. Use `fetch_apm_spans('service:lambda-api-prod', hours=1, limit=200)` then group by trace_id and count distinct request_ids per group — should all be 1.

**Why this matters:** trace pollution makes APM unusable for debugging individual customer requests — clicking a trace yields a noise pile from a different invocation. Related: [[apm-tag-bleed]] which was fixed via _SafeTracer in utils/logutil.py.
