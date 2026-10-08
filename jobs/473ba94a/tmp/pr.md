Follow-up to #5465. `get_inventory` now builds its product and kit maps from the stored catalog instead of re-pulling the whole Deposco product catalog on every pass.

The pre-fetch existed only to read `purchaseCost` and pack measurements, which aren't in the canonical Product schema. #5465 persisted both on each product's `additional_fields`, so inventory can read them from what we already store, which drops a full `search/item` + `search/kitHeader` walk per pass (the dominant cost on large connections, TRA-2554).

What changed:
- `get_product_and_kit_maps` becomes `build_product_and_kit_maps`, backed by `Product(self).get_all_resources()` and gated on the product first crawl being complete.
- `format_inventory_item` and `format_enterprise_inventory` read `unit_cost` and `measurements` off `additional_fields` instead of re-deriving them from the raw packs.
- `format_product` drops the `is_internal` branch and the `additional_info` payload that only fed the pre-fetch.
- The "map did not finish building" zero-fill guard is gone: the dynamo build either completes or raises, so a partial map is no longer possible. The database-error and short-feed guards are unchanged, and an inventory item with no stored product still falls back to a synthetic one.

Two things to know: kits and products that haven't re-crawled since #5465 carry no stored cost or measurements yet, so they format as null cost and empty measurements until the catalog backfills. And the zero-fill's unseen set is now the stored catalog rather than a live pull, so stale rows count toward the share threshold, which fails safe by skipping the zero-fill rather than wiping stock.

Verified with `yarn test -k deposco --inventory --products`: `test_get_inventory`, `test_get_products`, and `test_create_product` passed, the two write tests skipped, ledger xfail. Also checked the dev catalog directly: stored `additional_fields` round-trip through dynamo with the same values the old inline derivation produced.

test override: `yarn test -k deposco`
