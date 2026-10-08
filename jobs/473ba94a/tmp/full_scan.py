import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

import config
from utils.boto import connections_table, get_all_resources, get_connection_errors

rows = []
kwargs = {
    "FilterExpression": "integration_name = :n",
    "ExpressionAttributeValues": {":n": "deposco"},
}
while True:
    resp = connections_table.scan(**kwargs)
    rows.extend(resp["Items"])
    if "LastEvaluatedKey" not in resp:
        break
    kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]

print(f"deposco connections (paginated): {len(rows)}", flush=True)
ent = config.DEPOSCO_ENTERPRISE_INVENTORY_CONNECTIONS

live_at_risk = []
totals = {"live": 0, "live_rows": 0, "live_lacking": 0}

for row in sorted(rows, key=lambda r: bool(r.get("deleted", False))):
    cid = row["id"]
    deleted = bool(row.get("deleted", False))
    if deleted:
        continue
    totals["live"] += 1
    path = "enterprise" if cid in ent else "standard"

    inventory_blocked = False
    for e in get_connection_errors(cid):
        for ae in e.get("affected_endpoints", []):
            if ae.get("endpoint") == "GET /wms/inventory" and ae.get("preventing_sync"):
                inventory_blocked = True

    try:
        products = get_all_resources(cid, "products", "wms")
    except Exception as exc:
        print(f"{cid} ERROR {str(exc)[:60]}", flush=True)
        continue

    no_af_key = 0
    no_cost = 0
    kits_lacking = 0
    for p in products:
        af = p.get("additional_fields")
        if af is None:
            no_af_key += 1
            if p["is_kit"]:
                kits_lacking += 1
            continue
        if "unit_cost" not in af:
            no_cost += 1
            if p["is_kit"]:
                kits_lacking += 1

    lacking = no_af_key + no_cost
    totals["live_rows"] += len(products)
    totals["live_lacking"] += lacking
    flag = ""
    if lacking and not inventory_blocked:
        flag = "  <-- WOULD RAISE on direct index"
        live_at_risk.append((cid, path, lacking, no_af_key, kits_lacking))
    print(
        f"{cid} path={path} inv_blocked={inventory_blocked} products={len(products)} "
        f"lacking={lacking} (no_af_key={no_af_key}, kits={kits_lacking}){flag}",
        flush=True,
    )

print(flush=True)
print(f"live connections={totals['live']} rows={totals['live_rows']} lacking={totals['live_lacking']}", flush=True)
print("at risk:", flush=True)
for entry in live_at_risk:
    print("   ", entry, flush=True)
