import React from 'react';

export interface CaseInfo {
  case_id: string;
  name?: string;
  price_usd: string | number;
}

export interface CaseCardProps {
  caseInfo: CaseInfo;
  onClick: () => void;
}

export const CaseCard: React.FC<CaseCardProps> = ({ caseInfo, onClick }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full max-w-sm bg-white rounded-lg shadow p-6 flex flex-col items-center justify-center transform hover:scale-105 transition"
    >
      <div className="text-xl font-semibold mb-2">{caseInfo.name || caseInfo.case_id}</div>
      <div className="text-2xl font-bold mb-1">
        ${Number(caseInfo.price_usd).toFixed(2)}
      </div>
      <div className="text-sm text-gray-500">Відкрити кейс</div>
    </button>
  );
};

export default CaseCard;
