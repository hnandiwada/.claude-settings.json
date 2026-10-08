---
name: feedback-link-test-compensating-validation
description: "When a WMS/cart link test fails on page-overlap, resolve BOTH id sets of the link, not just one"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a32d29dd-19bb-4a1f-9dbf-31a6a97acbd0
---

When a link test fails purely because sampled pages don't overlap (fix-tests cause #2: window/page mismatch, class C/F — both sides correct, big catalog or snapshot endpoint, page 1 of each rarely overlaps), the fix is the cybership/warehouseos compensating-validation pattern: add the link key to `ignore_link_tests()` with a rationale, then re-validate the link by direct lookup in the test (no production code change).

**The rule I keep getting wrong: resolve BOTH id sets of the link through the authority endpoint — symmetrically — never just the side that doesn't obviously come from that endpoint.**

A link is `set_A & set_B` (e.g. `order_product_ids & product_ids`, or `product_inventory_ids & inventory_ids`). The compensating check must prove BOTH sets live in the same id space by resolving each through the same authority endpoint (for star, `product/pagelist` skuList). 

**Why:** asserting only one side and assuming the other is "trivially correct because it comes straight from that endpoint" is a reasoning shortcut. If a formatter bug or id transform ever made `product_ids` diverge from what the endpoint returns, the one-sided check wouldn't catch it. Symmetric resolution is assumption-free and uniform across every link. cybership_test.py does exactly this — its `test_get_products` resolves BOTH `product_inventory_ids` AND `inventory_ids` via the products endpoint.

I initially did only the order skus / only the inventory_ids side and called it done twice; the user had to point out the missing half both times. Default to symmetric from the start.

Use one helper: `any_sku_resolves_to_product(integration, skus)` — loop skus, `product/pagelist` with `skuList: [sku]`, return True on first match, `continue` past a failed call, return False if none resolve. Don't split it into per-sku + any-of wrappers.

Related: [[project-star-wms-link-tests]] for the concrete star implementation.
