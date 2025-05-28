import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

export default function WalletLayout() {
  return (
    <div>
      <h2 className="text-xl mb-4">Гаманець</h2>
      <div className="flex space-x-4 mb-6">
        <NavLink
          to="connect"
          className={({ isActive }) =>
            `px-3 py-1 border rounded ${isActive ? 'bg-blue-100' : ''}`
          }
        >
          Підключити
        </NavLink>
        <NavLink
          to="deposit"
          className={({ isActive }) =>
            `px-3 py-1 border rounded ${isActive ? 'bg-blue-100' : ''}`
          }
        >
          Депозит
        </NavLink>
        <NavLink
          to="withdraw"
          className={({ isActive }) =>
            `px-3 py-1 border rounded ${isActive ? 'bg-blue-100' : ''}`
          }
        >
          Вивід
        </NavLink>
      </div>
      <Outlet />
    </div>
  );
}