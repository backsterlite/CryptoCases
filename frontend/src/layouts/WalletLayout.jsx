import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

const tabs = [
  { label: 'Депозит', path: 'deposit' },
  { label: 'Вивід', path: 'withdraw' },
  { label: 'Гаманець', path: 'all' },
];

export default function WalletLayout() {
  return (
    <div>
      <div className="border-b mb-4">
        <nav className="flex space-x-4">
          {tabs.map(({ label, path }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `pb-2 border-b-2 ${
                  isActive
                    ? 'border-blue-600 text-blue-600 font-semibold'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
      <Outlet />
    </div>
  );
}
