

import React, { useState } from 'react'
import { openCase } from '../services/api'

export default function CasePage() {
  const [caseId, setCaseId] = useState('standard')
  const [result, setResult] = useState(null)

  const handleOpen = async () => {
    try {
      const res = await openCase(caseId)
      setResult(res)
    } catch (e) {
      alert('Failed to open case')
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-3xl mb-4">Open Case</h1>
      <select
        className="border p-2 mb-4"
        value={caseId}
        onChange={e => setCaseId(e.target.value)}
      >
        <option value="standard">Standard ($1)</option>
        <option value="premium">Premium ($5)</option>
      </select>
      <button
        className="bg-green-500 px-4 py-2 text-white rounded"
        onClick={handleOpen}
      >Open Case</button>

      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-800 text-white">
          <p>🎉 You won: <strong>{result.amount}</strong> <em>{result.token}</em></p>
        </div>
      )}
    </div>
  )
}