import os
import sys

os.environ["STAGE"] = "prod"
sys.path.insert(0, "/Users/harshanandiwada/workspace/deposco-inventory-dynamo-products")

import config

live = {
    "3f8d0ef207504007a741e2d43b3e165d": "populated",
    "9083572a4725476d91c2fcb4957b660e": "populated",
    "0a453c4e2ed94679bd54bf0179441524": "populated",
    "2becd083b84d4641a62940382d6be569": "populated",
    "2f87f7df9b424a28bdda4ee7d3cbfddf": "165 stale rows (16 with no additional_fields key)",
    "b9df8fe520184a2eaf5e5fd2d70aeb24": "11 stale rows",
    "af485479642742f7a916e56a863e9d82": "bad creds, inventory blocked",
    "e6878da42cf84f16b2fd114d7824b308": "bad creds, inventory blocked",
}

ent = config.DEPOSCO_ENTERPRISE_INVENTORY_CONNECTIONS
print("enterprise inventory connections:", sorted(ent), flush=True)
print(flush=True)
for cid, note in live.items():
    path = "enterprise" if cid in ent else "standard (zero-fills)"
    print(f"{cid} path={path} :: {note}", flush=True)
