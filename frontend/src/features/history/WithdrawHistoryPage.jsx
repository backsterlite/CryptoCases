import React from 'react';
import api from '../../services/api';

export default function WithdrawHistoryPage() {

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-4">Історія виведень</h1>
      <ul className="space-y-2">
        {data.map(tx => (
          <li key={tx.id}>{tx.amount} USD — {tx.address} — {new Date(tx.date).toLocaleString()}</li>
        ))}
      </ul>
    </div>
  );
}
