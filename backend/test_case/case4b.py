import requests
import json

'''
(A,301_01_V1,T,20)
(A,301_01_V2,T,15)
(A,301_01_V3,F,40)
(A,301_01_V4,F,60)
(A,301_01_V2,O,0)
(A,301_01_V5,T,10)
(A,301_01_V6,T,10)
(A,301_01_V7,F,50)
(A,301_01_V8,T,10)
(A,301_01_V9,F,50)
(A,301_01_V10,T,5)
(A,301_01_V11,F,15)
'''

base = "http://10.28.193.35:8123"

events = [
    # example: { "ty": "apply", "id": "301_01_V1", "slow": True, "amount": 14 },
    { "ty": "apply", "id": "301_01_V1", "slow": True, "amount": 20 },
    { "ty": "apply", "id": "301_01_V2", "slow": True, "amount": 15 },
    { "ty": "apply", "id": "301_01_V3", "slow": False, "amount": 40 },
    { "ty": "apply", "id": "301_01_V4", "slow": False, "amount": 60 },
    { "ty": "apply", "id": "301_01_V2", "slow": False, "amount": 0 },
    { "ty": "apply", "id": "301_01_V5", "slow": True, "amount": 10 },
    { "ty": "apply", "id": "301_01_V6", "slow": True, "amount": 10 },
    { "ty": "apply", "id": "301_01_V7", "slow": False, "amount": 50 },
    { "ty": "apply", "id": "301_01_V8", "slow": True, "amount": 10 },
    { "ty": "apply", "id": "301_01_V9", "slow": False, "amount": 50 },
    { "ty": "apply", "id": "301_01_V10", "slow": True, "amount": 5 },
    { "ty": "apply", "id": "301_01_V11", "slow": False, "amount": 15 },
]

for ev in events:
    if ev["ty"] == "apply":
        if ev["amount"] > 0:
            requests.post(base + "/request", json={
                "id": ev["id"],
                "charge_volume": ev["amount"],
                "fast_charge": not ev["slow"],
            })
        else:
            requests.post(base + "/request/end", json={
                "id": ev["id"],
            })
