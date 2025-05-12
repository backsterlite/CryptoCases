import React, { useState } from 'react'
import { withdraw } from '../services/api'

export default function WithdrawPage() {
  const [symbol, setSymbol] = useState('USDT')
  const [network, setNetwork] = useState('ERC20')
  const [amount, setAmount] = useState('0.1')
  const [address, setAddress] = useState('')
  const [tx, setTx] = useState(null)

  const handleWithdraw = async () => {
    try {
      const res = await withdraw(symbol, network, amount, address)
      setTx(res)  // tx hash
    } catch {
      alert('Withdraw failed')
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-3xl mb-4">Withdraw</h1>
      <input
        className="border p-2 mr-2" placeholder="Symbol"
        value={symbol} onChange={e=>setSymbol(e.target.value)}
      />
      <input
        className="border p-2 mr-2" placeholder="Network"
        value={network} onChange={e=>setNetwork(e.target.value)}
      />
      <input
        className="border p-2 mr-2" placeholder="Amount"
        value={amount} onChange={e=>setAmount(e.target.value)}
      />
      <input
        className="border p-2 mr-2" placeholder="To Address"
        value={address} onChange={e=>setAddress(e.target.value)}
      />
      <button
        className="bg-red-500 text-white px-4 py-2 rounded"
        onClick={handleWithdraw}
      >Withdraw</button>

      {tx && (
        <div className="mt-4 text-green-400">
          Tx Hash: {tx}
        </div>
      )}
    </div>
  )
}