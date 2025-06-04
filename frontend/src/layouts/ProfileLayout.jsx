import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

const tabs = [
  { label: 'Гаманець', path: 'wallet' },
  { label: 'Історія', path: 'history' },
  { label: 'Налаштування', path: 'settings' },
];

export default function ProfileLayout() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-6">
          {tabs.map(({ label, path }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `pb-2 border-b-2 text-sm font-medium ${
                  isActive
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="bg-white p-6 rounded shadow">
        <Outlet />
      </div>
    </div>
  );
}