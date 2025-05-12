import React from 'react';

export default function QuickActions() {
  const actions = [
    { label: 'Історія', onClick: () => {} },
    { label: 'Баланс', onClick: () => {} },
    { label: 'Налаштування', onClick: () => {} },
  ];

  return (
    <div className="w-full mt-4 bg-white rounded-lg shadow">
      <div className="flex justify-around py-3">
        {actions.map((act) => (
          <button
            key={act.label}
            onClick={act.onClick}
            className="flex-1 text-center py-2 hover:bg-gray-100 rounded"
          >
            {act.label}
          </button>
        ))}
      </div>
    </div>
  );
}