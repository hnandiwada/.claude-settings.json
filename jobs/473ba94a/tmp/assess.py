import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

from utils.boto import get_all_resources, get_connection_errors, get_scheduler_row

LIVE = {
    "3f8d0ef207504007a741e2d43b3e165d": "populated",
    "9083572a4725476d91c2fcb4957b660e": "populated",
    "0a453c4e2ed94679bd54bf0179441524": "populated",
    "2becd083b84d4641a62940382d6be569": "populated",
    "af485479642742f7a916e56a863e9d82": "all lacking",
    "2f87f7df9b424a28bdda4ee7d3cbfddf": "partial",
    "b9df8fe520184a2eaf5e5fd2d70aeb24": "partial",
    "e6878da42cf84f16b2fd114d7824b308": "all lacking (bad creds)",
}

first = True
for cid, label in LIVE.items():
    errors = get_connection_errors(cid)
    err_summary = []
    for e in errors:
        endpoints = []
        for ae in e.get("affected_endpoints", []):
            endpoints.append(f"{ae.get('endpoint')}(preventing={ae.get('preventing_sync')})")
        err_summary.append(
            f"{str(e.get('failed_url'))[:60]} | {e.get('error_type') or e.get('type') or '?'} | {','.join(endpoints)}"
        )

    products = get_all_resources(cid, "products", "wms")
    if first and products:
        print("product row keys:", sorted(products[0].keys()), flush=True)
        print(flush=True)
        first = False

    lacking_kits = 0
    lacking_products = []
    for p in products:
        af = p.get("additional_fields") or {}
        if "unit_cost" in af:
            continue
        if p["is_kit"]:
            lacking_kits += 1
        else:
            lacking_products.append(p)

    sched = get_scheduler_row(cid, "get_products")
    print(f"=== {cid} [{label}]", flush=True)
    print(
        f"    products={len(products)} lacking_non_kit={len(lacking_products)} lacking_kits={lacking_kits}",
        flush=True,
    )
    print(f"    products latest_data={sched.get('latest_data')}", flush=True)
    print(f"    connection_errors={len(errors)}", flush=True)
    for line in err_summary[:4]:
        print(f"      - {line}", flush=True)
    for p in lacking_products[:3]:
        print(f"      sample lacking: id={p['id']} active={p.get('active')} af={p.get('additional_fields')}", flush=True)
    print(flush=True)
