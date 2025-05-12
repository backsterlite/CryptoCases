import React, { useEffect, useState } from 'react';
import { fetchUsdBalance, fetchWallets } from '../services/api';

export default function Dashboard() {
  const [usdBalance, setUsdBalance] = useState('...');
  const [wallets, setWallets] = useState({});

  useEffect(() => {
    fetchUsdBalance().then(setUsdBalance);
    fetchWallets().then(setWallets);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-4xl font-bold mb-6">Total: {usdBalance} $</h1>
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(wallets).map(([symbol, { balances }]) => (
          <div key={symbol} className="border p-4 rounded">
            <h2 className="text-2xl font-semibold">{symbol}</h2>
            <ul>
              {Object.entries(balances).map(([net, amt]) => (
                <li key={net}>{net}: {amt}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}