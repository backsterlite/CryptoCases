import React from 'react';
import { useDispatch } from 'react-redux';

import { hideSessionExpiredModal } from '../slices/uiSlice';
import { loginWithTelegram } from '../../features/auth/authSlice';

export default function SessionExpiredModal({ onRefresh }) {

  const dispatch = useDispatch()

  const handleRefresh = () => {
    dispatch(hideSessionExpiredModal())
    dispatch(loginWithTelegram())
  }
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Сесія закінчилась</h2>
        <p className="mb-6">Будь ласка, натисніть кнопку, щоб оновити сесію через Telegram.</p>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          onClick={handleRefresh}
        >
          Оновити
        </button>
      </div>
    </div>
  );
}