import React from 'react';
import { DepositButton, ManualDepositAddress } from '../deposits';
import { useParams } from 'react-router-dom';

export default function DepositPage() {
  const { network, token } = useParams();

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-4">Депозит {token?.toUpperCase()}</h1>
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Автоматичний депозит</h2>
          <DepositButton network={network} />
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Ручний депозит</h2>
          <ManualDepositAddress network={network} />
        </div>
      </div>
    </div>
  );
}