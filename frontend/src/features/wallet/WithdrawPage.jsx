import React from 'react';
import { WithdrawalForm } from '../withdrawals';
import { useParams } from 'react-router-dom';

export default function WithdrawPage() {
  const { network, token } = useParams();

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-4">Вивід {token?.toUpperCase()}</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <WithdrawalForm network={network} token={token} />
      </div>
    </div>
  );
}