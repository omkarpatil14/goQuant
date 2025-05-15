from rest_framework.decorators import api_view
from rest_framework.response import Response
import numpy as np
import time

@api_view(['POST'])
def calculate_metrics(request):
    data = request.data
    quantity = float(data.get('quantity'))
    fee_tier = float(data.get('fee_tier', 0.001))  # 0.1% default
    volatility = float(data.get('volatility', 0.02))
    side = data.get('side', 'buy')  # 'buy' or 'sell'
    orderbook = data.get('orderbook', [])

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
    slippage = abs(avg_fill_price - price_start)

    # Market Impact: simplified Almgren-Chriss proportional to variance and quantity
    market_impact = (volatility ** 2) * quantity * avg_fill_price * 0.0001  # tuned factor

    # Fee (based on execution value)
    fee = fee_tier * total_cost

    net_cost = slippage * quantity + fee + market_impact

    # Maker/taker proportion via sigmoid on volatility
    maker_taker_ratio = 1 / (1 + np.exp(-volatility * 10))

    end_time = time.time()
    internal_latency = end_time - start_time

    return Response({
        "slippage": round(slippage, 6),
        "fee": round(fee, 6),
        "market_impact": round(market_impact, 6),
        "net_cost": round(net_cost, 6),
        "avg_fill_price": round(avg_fill_price, 2),
        "maker_taker_proportion": round(maker_taker_ratio, 4),
        "internal_latency": round(internal_latency, 6)
    })
