import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

DRY = os.environ.get("STAMP_APPLY") != "1"

from config import PRODUCTS_TABLE
from utils.boto import connections_table, dynamodb, get_all_resources

products_table = dynamodb.Table(PRODUCTS_TABLE)

BLANK = {
    "length": None,
    "width": None,
    "height": None,
    "unit": None,
    "weight": None,
    "weight_unit": None,
}

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

live = [r["id"] for r in rows if not r.get("deleted", False)]
print(f"live deposco connections: {len(live)} (dry_run={DRY})", flush=True)

total_stamped = 0
total_kits_skipped = 0
for cid in live:
    try:
        products = get_all_resources(cid, "products", "wms")
    except Exception as e:
        print(f"{cid} ERROR {str(e)[:60]}", flush=True)
        continue
    to_stamp = []
    kits_skipped = 0
    for p in products:
        af = p.get("additional_fields")
        if af is not None and "unit_cost" in af and "measurements" in af:
            continue
        if p["is_kit"]:
            kits_skipped += 1
            continue
        merged = dict(af or {})
        if "unit_cost" not in merged:
            merged["unit_cost"] = None
        if "measurements" not in merged:
            merged["measurements"] = dict(BLANK)
        to_stamp.append((p["id"], merged))

    if to_stamp and not DRY:
        for item_id, merged in to_stamp:
            products_table.update_item(
                Key={"connection_id": cid, "id": item_id},
                UpdateExpression="SET additional_fields = :af",
                ExpressionAttributeValues={":af": merged},
            )
    total_stamped += len(to_stamp)
    total_kits_skipped += kits_skipped
    if to_stamp or kits_skipped:
        verb = "would stamp" if DRY else "stamped"
        print(f"{cid} {verb}={len(to_stamp)} kits_skipped={kits_skipped}", flush=True)

print(flush=True)
print(f"TOTAL {'would stamp' if DRY else 'stamped'}={total_stamped} kits_skipped={total_kits_skipped}", flush=True)
