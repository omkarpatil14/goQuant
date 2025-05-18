import random
import requests
import csv
import os

URL = "http://localhost:8000/api/calculate/"  # your backend endpoint

CSV_FILE = "trade_log.csv"

# Define CSV columns
fieldnames = [
    "quantity", "volatility", "side", "time_horizon",
    "slippage", "fee", "market_impact", "net_cost",
    "avg_fill_price", "maker_taker_proportion"
]

# Remove old file if it exists
if os.path.exists(CSV_FILE):
    os.remove(CSV_FILE)

# Open CSV and write header
with open(CSV_FILE, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(500):  # You can increase this
        payload = {
            "quantity": round(random.uniform(10, 5000), 2),
            "volatility": round(random.uniform(0.005, 0.1), 4),
            "fee_tier": 0.001,
            "side": random.choice(["buy", "sell"]),
            "orderbook": [[str(round(100 + random.uniform(-2, 2), 2)), str(round(random.uniform(1, 100), 2))] for _ in range(10)],
            "time_horizon": round(random.uniform(10, 120), 2)
        }

        try:
            res = requests.post(URL, json=payload)
            if res.status_code == 200:
                data = res.json()
                writer.writerow({
                    "quantity": payload["quantity"],
                    "volatility": payload["volatility"],
                    "side": payload["side"],
                    "time_horizon": payload["time_horizon"],
                    "slippage": data.get("slippage", 0),
                    "fee": data.get("fee", 0),
                    "market_impact": data.get("market_impact", 0),
                    "net_cost": data.get("net_cost", 0),
                    "avg_fill_price": data.get("avg_fill_price", 0),
                    "maker_taker_proportion": data.get("maker_taker_proportion", 0)
                })
                print(f"[{i+1}/500] Slippage: {data.get('slippage')}")
            else:
                print(f"[{i+1}/500] Error: {res.status_code}")
        except Exception as e:
            print(f"[{i+1}/500] Request error: {e}")

print("✅ Data generation complete. You can now train the model.")
