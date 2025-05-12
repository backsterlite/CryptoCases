import React from 'react';

const sampleItems = [
  { amount: 5, nickname: 'alice' },
  { amount: 20, nickname: 'bob' },
  { amount: 10, nickname: 'charlie' },
];

export default function Carousel() {
  return (
    <div className="w-full overflow-x-auto flex space-x-3 py-2">
      {sampleItems.map((item, idx) => (
        <div
          key={idx}
          className="min-w-[120px] bg-white rounded-lg shadow flex flex-col items-center justify-center p-3"
          title={`$${item.amount} кейс від @${item.nickname}`}
        >
          <div className="text-xl font-semibold">+${item.amount}</div>
          <div className="text-sm text-gray-500">@{item.nickname}</div>
        </div>
      ))}
    </div>
  );
}