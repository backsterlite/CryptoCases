import React from 'react';

/**
 * Spin area with price and Play button
 */
export default function SpinArea({ price, onPlay, disabled }) {
  return (
    <div className="flex items-center space-x-4">
      <div className="text-xl">Price: ${price}</div>
      <button
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        onClick={onPlay}
        disabled={disabled}
      >
        Play
      </button>
    </div>
  );
}