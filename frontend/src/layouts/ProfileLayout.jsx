import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

export default function ProfileLayout() {
  return (
    <div className="flex h-full">
      <nav className="w-1/4 p-4 border-r">
        <NavLink
          to="wallet"
          className={({ isActive }) =>
            `block py-2 ${isActive ? 'font-bold text-blue-600' : ''}`
          }
        >
          Гаманець
        </NavLink>
        <NavLink
          to="history"
          className={({ isActive }) =>
            `block py-2 ${isActive ? 'font-bold text-blue-600' : ''}`
          }
        >
          Історія
        </NavLink>
        <NavLink
          to="settings"
          className={({ isActive }) =>
            `block py-2 ${isActive ? 'font-bold text-blue-600' : ''}`
          }
        >
          Налаштування
        </NavLink>
      </nav>
      <div className="flex-1 p-4 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}
