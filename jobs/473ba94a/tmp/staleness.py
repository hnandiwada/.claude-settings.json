import os
import sys
from collections import Counter

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

from utils.boto import get_all_resources

for cid in [
    "2f87f7df9b424a28bdda4ee7d3cbfddf",
    "b9df8fe520184a2eaf5e5fd2d70aeb24",
]:
    products = get_all_resources(cid, "products", "wms")
    lacking_days = Counter()
    having_days = Counter()
    for p in products:
        stamp = str(p.get("trackstar_updated_date"))[:10]
        af = p.get("additional_fields") or {}
        if "unit_cost" in af:
            having_days[stamp] += 1
        else:
            lacking_days[stamp] += 1
    print(f"=== {cid}", flush=True)
    print(f"  rows WITH unit_cost, by trackstar_updated_date: {having_days.most_common(5)}", flush=True)
    print(f"  rows WITHOUT unit_cost, by trackstar_updated_date: {lacking_days.most_common(8)}", flush=True)
    print(flush=True)
