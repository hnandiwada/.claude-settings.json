import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

from utils.boto import get_scheduler_row

live_lacking = [
    "af485479642742f7a916e56a863e9d82",
    "e6878da42cf84f16b2fd114d7824b308",
    "2f87f7df9b424a28bdda4ee7d3cbfddf",
    "b9df8fe520184a2eaf5e5fd2d70aeb24",
]
populated = ["2becd083b84d4641a62940382d6be569", "9083572a4725476d91c2fcb4957b660e"]

row = get_scheduler_row(live_lacking[0], "get_products")
print("scheduler row keys:", sorted(row.keys()), flush=True)
print(flush=True)

for cid in live_lacking + populated:
    r = get_scheduler_row(cid, "get_products")
    interesting = {}
    for k in sorted(r.keys()):
        if k in ("connection_id", "function_name"):
            continue
        v = r[k]
        if isinstance(v, (str, int, bool, float)) or v is None:
            interesting[k] = str(v)[:40]
    print(cid, interesting, flush=True)
