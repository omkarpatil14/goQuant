# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, QuantileRegressor
from sklearn.metrics import mean_squared_error
import joblib

df = pd.read_csv("trade_log.csv")

# Encode side: buy=1, sell=0
df["side"] = df["side"].map({"buy": 1, "sell": 0})

X = df[["quantity", "volatility", "side", "time_horizon"]]
y = df["slippage"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()  
model.fit(X_train, y_train)

print("MSE:", mean_squared_error(y_test, model.predict(X_test)))

joblib.dump(model, "slippage_model.pkl")
