import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

from utils.boto import get_all_resources, connections_table

rows = connections_table.scan(
    FilterExpression="integration_name = :n",
    ExpressionAttributeValues={":n": "deposco"},
    ProjectionExpression="id",
)["Items"]
print("deposco connections:", len(rows), flush=True)

for row in rows:
    cid = row["id"]
    try:
        products = get_all_resources(cid, "products", "wms")
    except Exception as e:
        print(cid, "ERROR", str(e)[:80], flush=True)
        continue
    no_af = 0
    no_cost = 0
    no_meas = 0
    kits_no_cost = 0
    kits = 0
    for p in products:
        if p["is_kit"]:
            kits += 1
        af = p.get("additional_fields")
        if af is None:
            no_af += 1
            if p["is_kit"]:
                kits_no_cost += 1
            continue
        if "unit_cost" not in af:
            no_cost += 1
            if p["is_kit"]:
                kits_no_cost += 1
        if "measurements" not in af:
            no_meas += 1
    print(
        f"{cid} products={len(products)} kits={kits} no_additional_fields={no_af} "
        f"no_unit_cost={no_cost} no_measurements={no_meas} kits_lacking={kits_no_cost}",
        flush=True,
    )
