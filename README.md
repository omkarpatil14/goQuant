# Trade Slippage and Market Impact API

This API provides calculations for trade slippage, fees, market impact, and net cost based on input order book data, order parameters, and a trained machine learning model for slippage prediction. It combines statistical models with classical financial theories (Almgren-Chriss) to deliver comprehensive trade cost metrics.

---

## Table of Contents
- [Overview](#overview)
- [Model Selection and Parameters](#model-selection-and-parameters)
- [Regression Techniques Chosen](#regression-techniques-chosen)
- [Market Impact Calculation Methodology](#market-impact-calculation-methodology)
- [Performance Optimization Approaches](#performance-optimization-approaches)
- [Usage](#usage)

---

## Overview

This backend service is built using Django REST framework and exposes an endpoint `/calculate_metrics` where clients send order details and orderbook snapshots. It outputs:
- Predicted trade slippage (from ML model)
- Fees
- Market impact cost (Almgren-Chriss model)
- Net cost combining all components
- Average fill price
- Maker/taker proportion estimate based on volatility
- Internal processing latency

---

## Model Selection and Parameters

- The core predictive element is a **trained regression model** saved as `slippage_model.pkl`, built to estimate trade slippage.
- **Input features** to the model include:
  - `quantity` — number of units traded
  - `volatility` — market price volatility
  - `side` — encoded as `1` for buy orders, `0` for sell orders
  - `time_horizon` — duration over which the trade is executed (seconds)
- These features are selected to capture key determinants of slippage: trade size, market uncertainty, directionality, and execution speed.

---

## Regression Techniques Chosen

- The model is based on **supervised regression techniques** (e.g., Random Forest, Gradient Boosting, or XGBoost). The exact technique depends on the training pipeline but generally:
  - Handles **non-linear relationships** between inputs and slippage
  - Is robust to noisy and high-dimensional data common in orderbook snapshots
  - Can approximate complex market microstructure impacts without explicit feature engineering
- Hyperparameters were tuned via cross-validation to optimize predictive accuracy on out-of-sample data.
- The trained model is serialized with `joblib` for efficient loading and inference in the API.

---

## Market Impact Calculation Methodology

- The API calculates **market impact** cost using the **Almgren-Chriss model**, a well-established framework in quantitative finance:
  - Temporary impact: proportional to the trading rate (quantity divided by time horizon)
  - Permanent impact: proportional to total quantity traded
  - Impact costs are scaled by starting market price
- This model captures the intuition that executing large orders too quickly disturbs the market, causing price shifts that increase costs.
- The formula used is:
  \[
  \text{Impact Cost} = \left(\eta \times \frac{Q}{T} + \gamma \times Q\right) \times P_0
  \]
  where \(Q\) is quantity, \(T\) is time horizon, \(P_0\) is starting price, \(\eta\) and \(\gamma\) are temporary and permanent impact coefficients (default: 0.01 and 0.005 respectively).

---

## Performance Optimization Approaches

- **Model Loading:** The machine learning model is loaded once at server start, not per request, minimizing I/O overhead.
- **Efficient Sorting:** The orderbook is sorted efficiently based on the trade side (buy/sell) to simulate order execution.
- **Early Break:** Loop over orderbook levels breaks as soon as the requested quantity is fulfilled, avoiding unnecessary computation.
- **Vectorized Operations:** NumPy is used for numeric operations (e.g., sigmoid for maker/taker proportion) for speed.
- **Minimal Data Validation:** Basic validation on input formats to avoid heavy error handling.
- **Latency Measurement:** Internal processing time is measured and returned to help identify bottlenecks and optimize further.
- **Modular Design:** Separation of concerns allows easy replacement or tuning of components (e.g., swapping out the ML model or impact formula).

---

## Usage

### Endpoint: `POST /calculate_metrics`

**Request Body Example:**

```json
{
  "quantity": 1000,
  "fee_tier": 0.001,
  "volatility": 0.02,
  "side": "buy",
  "orderbook": [
    ["100.5", "200"],
    ["100.6", "500"],
    ["100.7", "800"]
  ],
  "time_horizon": 60
}
