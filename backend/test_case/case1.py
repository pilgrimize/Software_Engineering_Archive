import requests
import json
import utils

'''
6:0:0(A,301_01_V1,T,40)
6:0:0(A,301_01_V5,T,35)
6:5:0(A,301_01_V2,F,120)
6:10:0(A,301_01_V2,O,0)
8:0:0(B,T1,O,0)
8:20:0(A,301_01_V2,T,14)
8:30:0(B,F2,O,0)
8:35:0(A,301_01_V3,F,30)
8:40:0(A,301_01_V1,F,22.5)
8:50:0(B,F2,O,1)
9:0:0(B,T1,O,1)
9:10:0(A,301_01_V4,F,10)
9:15:0(C,301_01_V4,T,7)
9:35:0(A,301_01_V4,T,30)
10:15
10:20
11:00
'''

time1 = utils.Time()

# base = "http://127.0.0.1:8123"
base = "http://10.28.193.35:8123"

events = [
    {"ty": "apply", "id": "301_01_V1", "slow": True, "amount": 40, "time": "6:00"},
    {"ty": "apply", "id": "301_01_V5", "slow": True, "amount": 35, "time": "6:00"},
    {"ty": "apply", "id": "301_01_V2", "slow": False, "amount": 120, "time": "6:05"},
    {"ty": "end", "id": "301_01_V2", "time": "6:10"},
    {"ty": "breakdown", "pile_id": 2, "time": "8:00"},
    {"ty": "apply", "id": "301_01_V2", "slow": True, "amount": 14, "time": "8:20"},
    {"ty": "breakdown", "pile_id": 1, "time": "8:30"},
    {"ty": "apply", "id": "301_01_V3", "slow": False, "amount": 30, "time": "8:35"},
    {"ty": "end", "id": "301_01_V1", "time": "8:39"},
    {"ty": "apply", "id": "301_01_V1", "slow": False, "amount": 22.5, "time": "8:40"},
    {"ty": "restart", "pile_id": 1, "time": "8:50"},
    {"ty": "restart", "pile_id": 2, "time": "9:00"},
    {"ty": "apply", "id": "301_01_V4", "slow": False, "amount": 10, "time": "9:10"},
    {"ty": "modify", "id": "301_01_V4", "slow": True, "amount": 7, "time": "9:15"},
    {"ty": "apply", "id": "301_01_V4", "slow": True, "amount": 30, "time": "9:35"},
    {"ty": "set_time", "time": "10:15"},
    {"ty": "set_time", "time": "10:20"},
    {"ty": "set_time", "time": "11:00"},
]


for ev in events:
    print("time:", time1.get_time_stamp(ev["time"]))
    requests.get(base + "/time/set/", params={
        "set_time_sec": time1.get_time_stamp(ev["time"])
    })
    if ev["ty"] == "apply":
        requests.post(base + "/request", json={
            "id": ev["id"],
            "charge_volume": ev["amount"],
            "fast_charge": not ev["slow"]
        })
    elif ev["ty"] == "breakdown":
        requests.post(base + "/pile/shutdown/", json={
            "pile_id": ev["pile_id"]
        })
    elif ev["ty"] == "end":
        requests.post(base + "/request/end/", json={
            "id": ev["id"]
        })
    elif ev["ty"] == "restart":
        requests.post(base + "/pile/startup/", json={
            "pile_id": ev["pile_id"]
        })
    elif ev["ty"] == "modify":
        requests.post(base + "/request/modify/", json={
            "id": ev["id"],
            "charge_volume": ev["amount"],
            "type_choice": 'slow' if ev["slow"] else 'fast'
        })
    requests.post(base + "/stat/")