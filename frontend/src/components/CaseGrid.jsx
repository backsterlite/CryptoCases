import React from 'react';

const cases = [5, 10, 20];

export default function CaseGrid() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {cases.map((value) => (
        <button
          key={value}
          className="bg-white rounded-lg shadow p-6 flex flex-col items-center justify-center transform hover:scale-105 transition"
        >
          <div className="text-2xl font-bold mb-1">${value}</div>
          <div className="text-sm text-gray-500">Відкрити кейс</div>
        </button>
      ))}
    </div>
  );
}
