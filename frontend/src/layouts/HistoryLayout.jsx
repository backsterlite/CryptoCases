import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

export default function HistoryLayout() {
  return (
    <div className="flex h-full">
      <nav className="w-1/4 p-4 border-r">
        <NavLink
          to="deposits"
          className={({ isActive }) =>
            `block py-2 ${isActive ? 'font-bold text-blue-600' : ''}`
          }
        >
          Поповнення
        </NavLink>
        <NavLink
          to="opens"
          className={({ isActive }) =>
            `block py-2 ${isActive ? 'font-bold text-blue-600' : ''}`
          }
        >
          Кейси
        </NavLink>
        <NavLink
          to="withdrawals"
          className={({ isActive }) =>
            `block py-2 ${isActive ? 'font-bold text-blue-600' : ''}`
          }
        >
          Вивід
        </NavLink>
      </nav>
      <div className="flex-1 p-4 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}