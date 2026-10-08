import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

import config
from utils.boto import get_all_resources

for cid in sorted(config.DEPOSCO_ENTERPRISE_INVENTORY_CONNECTIONS):
    try:
        products = get_all_resources(cid, "products", "wms")
    except Exception as e:
        print(f"{cid} ERROR {str(e)[:50]}", flush=True)
        continue
    kits = 0
    kits_lacking = 0
    lacking = 0
    for p in products:
        af = p.get("additional_fields")
        missing = af is None or "unit_cost" not in af
        if missing:
            lacking += 1
        if p["is_kit"]:
            kits += 1
            if missing:
                kits_lacking += 1
    print(
        f"{cid} products={len(products)} kits={kits} lacking={lacking} kits_lacking={kits_lacking}",
        flush=True,
    )
