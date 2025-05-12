import React from 'react';
import  logo  from '../assets/react.svg'

export default function Header() {
  const user = window.Telegram.WebApp?.user || {};
  const balance = 123.45; // TODO: replace with real data

  return (
    <div className="w-full flex items-center justify-between bg-white py-2 px-3 rounded-lg shadow">
      <div className="text-lg font-medium text-gray-800">$ {balance.toFixed(2)}</div>
      <img
        src={user.photo_url || logo}
        alt={user.first_name}
        className="w-8 h-8 rounded-full"
      />
    </div>
  );
}