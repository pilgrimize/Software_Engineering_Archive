import requests
import json

'''
(A,301_01_V1,T,14)
(A,301_01_V2,T,21)
(A,301_01_V3,F,30)
(A,301_01_V4,F,45)
(A,301_01_V5,T,7)
(A,301_01_V6,T,14)
(A,301_01_V7,F,30)
(A,301_01_V8,F,15)
(A,301_01_V9,T,10.5)
(A,301_01_V10,F,15)
(A,301_01_V11,T,3.5)
(A,301_01_V12,T,5.25)
(A,301_01_V13,T,1.75)
(A,301_01_V14,F,30)
(A,301_01_V15,T,7)
(A,301_01_V16,F,50)
(A,301_01_V17,F,60)
(A,301_01_V18,T,14)
(A,301_01_V19,T,10.5)
(A,301_01_V20,T,14)
(A,301_01_V21,F,60)
(A,301_01_V22,F,45)
(A,301_01_V23,T,14)
'''

base = "http://10.28.193.35:8123"

events = [
    { "ty": "apply", "id": "301_01_V1", "slow": True, "amount": 14 },
    { "ty": "apply", "id": "301_01_V2", "slow": True, "amount": 21 },
    { "ty": "apply", "id": "301_01_V3", "slow": False, "amount": 30 },
    { "ty": "apply", "id": "301_01_V4", "slow": False, "amount": 45 },
    { "ty": "apply", "id": "301_01_V5", "slow": True, "amount": 7 },
    { "ty": "apply", "id": "301_01_V6", "slow": True, "amount": 14 },
    { "ty": "apply", "id": "301_01_V7", "slow": False, "amount": 30 },
    { "ty": "apply", "id": "301_01_V8", "slow": False, "amount": 15 },
    { "ty": "apply", "id": "301_01_V9", "slow": True, "amount": 10.5 },
    { "ty": "apply", "id": "301_01_V10", "slow": False, "amount": 15 },
    { "ty": "apply", "id": "301_01_V11", "slow": True, "amount": 3.5 },
    { "ty": "apply", "id": "301_01_V12", "slow": True, "amount": 5.25 },
    { "ty": "apply", "id": "301_01_V13", "slow": True, "amount": 1.75 },
    { "ty": "apply", "id": "301_01_V14", "slow": False, "amount": 30 },
    { "ty": "apply", "id": "301_01_V15", "slow": True, "amount": 7 },
    { "ty": "apply", "id": "301_01_V16", "slow": False, "amount": 50 },
    { "ty": "apply", "id": "301_01_V17", "slow": False, "amount": 60 },
    { "ty": "apply", "id": "301_01_V18", "slow": True, "amount": 14 },
    { "ty": "apply", "id": "301_01_V19", "slow": True, "amount": 10.5 },
    { "ty": "apply", "id": "301_01_V20", "slow": True, "amount": 14 },
    { "ty": "apply", "id": "301_01_V21", "slow": False, "amount": 60 },
    { "ty": "apply", "id": "301_01_V22", "slow": False, "amount": 45 },
    { "ty": "apply", "id": "301_01_V23", "slow": True, "amount": 14 },
]

for ev in events:
    if ev["ty"] == "apply":
        requests.post(base + "/request", json={
            "id": ev["id"],
            "charge_volume": ev["amount"],
            "fast_charge": not ev["slow"],
        })
