import React from 'react';

import api from '../../services/api';

export default function CaseOpensHistoryPage() {

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-4">Історія відкриття кейсів</h1>
      <ul className="space-y-2">
        {data.map(tx => (
          <li key={tx.id}>Кейс {tx.caseId} — {tx.result} — {new Date(tx.date).toLocaleString()}</li>
        ))}
      </ul>
    </div>
  );
}