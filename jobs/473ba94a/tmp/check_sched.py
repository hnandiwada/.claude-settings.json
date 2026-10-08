import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

from utils.boto import connections_table, scheduler_table

rows = connections_table.scan(
    FilterExpression="integration_name = :n",
    ExpressionAttributeValues={":n": "deposco"},
    ProjectionExpression="id, crawl_frequencies",
)["Items"]

for row in rows:
    cid = row["id"]
    freqs = row.get("crawl_frequencies") or {}
    products_freq = freqs.get("products", "<not set>")
    inventory_freq = freqs.get("inventory", "<not set>")
    sched = scheduler_table.get_item(
        Key={"connection_id": cid, "function_name": "get_products"}
    ).get("Item")
    if sched is None:
        state = "NO SCHEDULER ROW"
    else:
        state = f"latest_data={bool(sched.get('latest_data'))} paused={bool(sched.get('paused'))}"
    print(f"{cid} products_freq={products_freq} inventory_freq={inventory_freq} {state}", flush=True)
