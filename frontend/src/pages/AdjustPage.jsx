import React, { useState } from 'react'
import { adjustWallet } from '../services/api'

export default function AdjustPage() {
  const [symbol, setSymbol] = useState('USDT')
  const [network, setNetwork] = useState('ERC20')
  const [delta, setDelta] = useState('0.1')
  const [balances, setBalances] = useState(null)

  const handleAdjust = async () => {
    try {
      const res = await adjustWallet(symbol, network, delta)
      setBalances(res.balances)
    } catch {
      alert('Adjust failed')
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-3xl mb-4">Adjust Wallet</h1>
      <input
        className="border p-2 mr-2"
        placeholder="Symbol"
        value={symbol}
        onChange={e=>setSymbol(e.target.value)}
      />
      <input
        className="border p-2 mr-2"
        placeholder="Network"
        value={network}
        onChange={e=>setNetwork(e.target.value)}
      />
      <input
        className="border p-2 mr-2"
        placeholder="Delta"
        value={delta}
        onChange={e=>setDelta(e.target.value)}
      />
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        onClick={handleAdjust}
      >Adjust</button>

      {balances && (
        <div className="mt-4">
          <h2 className="text-xl">Updated Balances:</h2>
          <pre>{JSON.stringify(balances, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}