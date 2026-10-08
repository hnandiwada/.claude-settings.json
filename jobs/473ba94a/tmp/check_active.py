import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

from utils.boto import connections_table, scheduler_table, get_all_resources

rows = connections_table.scan(
    FilterExpression="integration_name = :n",
    ExpressionAttributeValues={":n": "deposco"},
)["Items"]

for row in rows:
    cid = row["id"]
    deleted = row.get("deleted", False)
    org = row.get("org_id", "?")
    sched = scheduler_table.query(
        KeyConditionExpression="connection_id = :c",
        ExpressionAttributeValues={":c": cid},
    )["Items"]
    prod_row = None
    inv_row = None
    for s in sched:
        if s["function_name"] == "get_products":
            prod_row = s
        if s["function_name"] == "get_inventory":
            inv_row = s

    def describe(s):
        if s is None:
            return "none"
        return (
            f"paused={bool(s.get('paused'))} latest_data={bool(s.get('latest_data'))} "
            f"last_run={str(s.get('last_successful_crawl') or s.get('updated_at') or '?')[:19]}"
        )

    try:
        products = get_all_resources(cid, "products", "wms")
    except Exception as e:
        print(f"{cid} deleted={deleted} PRODUCTS_ERROR {str(e)[:50]}", flush=True)
        continue
    lacking = 0
    kits_lacking = 0
    for p in products:
        af = p.get("additional_fields") or {}
        if "unit_cost" not in af:
            lacking += 1
            if p["is_kit"]:
                kits_lacking += 1
    print(
        f"{cid} org={org} deleted={deleted} products={len(products)} "
        f"lacking_unit_cost={lacking} (kits={kits_lacking})\n"
        f"    get_products:  {describe(prod_row)}\n"
        f"    get_inventory: {describe(inv_row)}",
        flush=True,
    )
