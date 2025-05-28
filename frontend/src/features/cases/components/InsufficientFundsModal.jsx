import React from 'react';

export default function InsufficientFundsModal({ onClose }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded shadow-lg w-80">
        <h2 className="text-xl text-black font-semibold mb-4">Недостатньо коштів</h2>
        <p className="mb-4 text-black">У вас недостатньо коштів для відкриття цього кейсу.</p>
        <button
          onClick={onClose}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Закрити
        </button>
      </div>
    </div>
  );
}
