import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [exchange, setExchange] = useState('OKX');
  const [spotAsset, setSpotAsset] = useState('BTC-USDT');
  const [orderType, setOrderType] = useState('market');
  const [quantity, setQuantity] = useState(100);
  const [volatility, setVolatility] = useState(0.02);
  const [feeTier, setFeeTier] = useState(0.001);
  const [side, setSide] = useState('buy');
  const [output, setOutput] = useState({});
  const [socketData, setSocketData] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(
      "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
    );
    ws.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      setSocketData(data);
    };
    return () => ws.close();
  }, []);

  const calculate = async () => {
    if (!socketData) {
      alert("Orderbook data not available yet!");
      return;
    }

    const orderbook = side === 'buy' ? socketData.asks : socketData.bids;

    try {
      const res = await axios.post("http://localhost:8000/api/calculate/", {
        quantity: parseFloat(quantity),
        fee_tier: parseFloat(feeTier),
        volatility: parseFloat(volatility),
        side,
        orderbook,
      });
      setOutput(res.data);
    } catch (err) {
      console.error(err);
      alert("Error in calculation");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="flex flex-row gap-8 max-w-7xl mx-auto">
        {/* Input Section */}
        <div className="flex-1 space-y-6 bg-gray-800 p-6 rounded-lg shadow-lg">
          <h3 className="text-2xl font-semibold border-b border-gray-700 pb-3">
            Input Parameters
          </h3>

          <div>
            <label className="block mb-1">Exchange</label>
            <input
              type="text"
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
              placeholder="e.g., OKX"
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block mb-1">Spot Asset</label>
            <input
              type="text"
              value={spotAsset}
              onChange={(e) => setSpotAsset(e.target.value)}
              placeholder="e.g., BTC-USDT"
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block mb-1">Order Type</label>
            <input
              type="text"
              value={orderType}
              onChange={(e) => setOrderType(e.target.value)}
              placeholder="e.g., market"
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block mb-1">Quantity (USD)</label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block mb-1">Volatility</label>
            <input
              type="number"
              value={volatility}
              onChange={(e) => setVolatility(e.target.value)}
              step="0.001"
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block mb-1">Fee Tier</label>
            <input
              type="number"
              value={feeTier}
              onChange={(e) => setFeeTier(e.target.value)}
              step="0.0001"
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block mb-1">Side</label>
            <select
              value={side}
              onChange={(e) => setSide(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>

          <button
            onClick={calculate}
            className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-md font-semibold transition duration-200"
          >
            Simulate
          </button>
        </div>

        {/* Output Section */}
        <div className="flex-1 space-y-6 bg-gray-800 p-6 rounded-lg shadow-lg">
          <h3 className="text-2xl font-semibold border-b border-gray-700 pb-3">
            Output Metrics
          </h3>
          <pre className="bg-gray-700 text-green-400 p-4 rounded overflow-x-auto">
            {JSON.stringify(output, null, 2)}
          </pre>

          <div>
            <h4 className="text-xl font-semibold mb-3">Live Order Book (Top Bid/Ask)</h4>
            {socketData ? (
              <>
                <p>
                  <span className="text-blue-400 font-medium">Best Bid:</span>{' '}
                  {socketData.bids[0][0]}{' '}
                  <span className="text-gray-400">({socketData.bids[0][1]})</span>
                </p>
                <p>
                  <span className="text-red-400 font-medium">Best Ask:</span>{' '}
                  {socketData.asks[0][0]}{' '}
                  <span className="text-gray-400">({socketData.asks[0][1]})</span>
                </p>
              </>
            ) : (
              <p className="text-gray-400">Waiting for order book data...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
