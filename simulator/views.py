from rest_framework.decorators import api_view
from rest_framework.response import Response
import numpy as np
import time
import joblib
import os

# Load the trained model once when the server starts
MODEL_PATH = os.path.join(os.path.dirname(__file__), "slippage_model.pkl")
slippage_model = joblib.load(MODEL_PATH)

# Almgren-Chriss expected market impact function
def calculate_almgren_chriss_impact(quantity, time_horizon, price, eta=0.01, gamma=0.005):
    trading_rate = quantity / time_horizon
    temporary_impact = eta * trading_rate
    permanent_impact = gamma * quantity
    expected_impact_cost = (temporary_impact + permanent_impact) * price
    return round(expected_impact_cost, 6)

@api_view(['POST'])
def calculate_metrics(request):
    data = request.data
    try:
        quantity = float(data.get('quantity'))
        fee_tier = float(data.get('fee_tier', 0.001))  # 0.1% default
        volatility = float(data.get('volatility', 0.02))
        side = data.get('side', 'buy')  # 'buy' or 'sell'
        orderbook = data.get('orderbook', [])
        time_horizon = float(data.get('time_horizon', 60))  # in seconds

        start_time = time.time()

        if not orderbook or not isinstance(orderbook, list):
            return Response({'error': 'Invalid orderbook data'}, status=400)

        # Sort based on side
        sorted_book = sorted(orderbook, key=lambda x: float(x[0]), reverse=(side == 'sell'))

        total_qty = 0
        total_cost = 0
        price_start = float(sorted_book[0][0])

        for price_str, qty_str in sorted_book:
            price = float(price_str)
            level_qty = float(qty_str)

            if total_qty + level_qty >= quantity:
                fill_qty = quantity - total_qty
                total_cost += fill_qty * price
                break
            else:
                total_cost += level_qty * price
                total_qty += level_qty

        avg_fill_price = total_cost / quantity if quantity else 0

        # Use trained model to predict slippage
        side_encoded = 1 if side == "buy" else 0
        slippage_input = [[quantity, volatility, side_encoded, time_horizon]]
        predicted_slippage = float(slippage_model.predict(slippage_input)[0])

        # Market impact (AC model)
        ac_market_impact = calculate_almgren_chriss_impact(quantity, time_horizon, price_start)

        # Fee (based on execution value)
        fee = fee_tier * total_cost

        # Net cost = predicted_slippage * quantity + fee + market_impact
        net_cost = predicted_slippage * quantity + fee + ac_market_impact

        # Maker/taker proportion via sigmoid on volatility
        maker_taker_ratio = 1 / (1 + np.exp(-volatility * 10))

        end_time = time.time()
        internal_latency = end_time - start_time

        return Response({
            "slippage": round(predicted_slippage, 6),
            "fee": round(fee, 6),
            "market_impact": ac_market_impact,
            "net_cost": round(net_cost, 6),
            "avg_fill_price": round(avg_fill_price, 2),
            "maker_taker_proportion": round(maker_taker_ratio, 4),
            "internal_latency": round(internal_latency, 6)
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)
