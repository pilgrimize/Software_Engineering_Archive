import requests
import utils
import route
import json

'''
6:00(A,301_01_V1,T,7)
6:00(A,301_01_V2,F,30)
6:30(A,301_01_V3,T,28)
6:30(A,301_01_V4,F,120)
7:00(A,301_01_V5,T,24.5)
7:00(A,301_01_V6,F,45)
7:30
8:00(A,301_01_V7,F,75)
8:30
9:00(A,301_01_V8,T,14)
9:30
10:00
10:30
11:00
'''

time1 = utils.Time()

# base = "http://127.0.0.1:8123"
base = "http://10.28.193.35:8123"

events = [
    {"ty": "apply", "id": "301_01_V1", "slow": True, "amount": 7, "time": "6:00"},
    {"ty": "apply", "id": "301_01_V2", "slow": False, "amount": 30, "time": "6:00"},
    {"ty": "apply", "id": "301_01_V3", "slow": True, "amount": 28, "time": "6:30"},
    {"ty": "apply", "id": "301_01_V4", "slow": False, "amount": 120, "time": "6:30"},
    {"ty": "apply", "id": "301_01_V5", "slow": True, "amount": 24.5, "time": "7:00"},
    {"ty": "apply", "id": "301_01_V6", "slow": False, "amount": 45, "time": "7:00"},
    {"ty": "set_time", "time": "7:30"},
    {"ty": "apply", "id": "301_01_V7", "slow": False, "amount": 75, "time": "8:00"},
    {"ty": "set_time", "time": "8:30"},
    {"ty": "apply", "id": "301_01_V8", "slow": True, "amount": 14, "time": "9:00"},
    {"ty": "set_time", "time": "9:30"},
    {"ty": "set_time", "time": "10:00"},
    {"ty": "set_time", "time": "10:30"},
    {"ty": "set_time", "time": "11:00"},
]


for ev in events:
    print("time:",time1.get_time_stamp(ev["time"]))
    requests.get(base + "/time/set/", params={
        "set_time_sec": time1.get_time_stamp(ev["time"])
    })
    if ev["ty"] == "apply":
        requests.post(base + "/request", json={
            "id": ev["id"],
            "charge_volume": ev["amount"],
            "fast_charge": not ev["slow"],
        })
    requests.post(base + "/stat/")