import React from 'react';

export default function CaseCard({ caseInfo, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="bg-white rounded-lg shadow p-6 flex flex-col items-center justify-center transform hover:scale-105 transition"
    >
      <div className="text-xl font-semibold mb-2">{caseInfo.name || caseInfo.case_id}</div>
      {/* Uncomment when image URL is available */}
      {/* <img src={caseInfo.imageUrl} alt={caseInfo.name} className="w-16 h-16 mb-4" /> */}
      <div className="text-2xl font-bold mb-1">${Number(caseInfo.price_usd).toFixed(2)}</div>
      <div className="text-sm text-gray-500">Відкрити кейс</div>
    </button>
  );
}
