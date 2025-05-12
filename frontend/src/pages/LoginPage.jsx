import React, { useState } from 'react';
import { loginDev } from '../services/api';

export default function LoginPage() {
  const [telegramId, setTelegramId] = useState('');
  const [botToken, setBotToken] = useState('');
  
  const handleLogin = async () => {
    try {
      const token = await loginDev(telegramId, botToken);
      localStorage.setItem('api_token', token);
      window.location.href = '/';
    } catch (e) {
      alert(`Login failed. ERROR: ${e}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <input
        className="border p-2 m-2"
        placeholder="Telegram ID"
        value={telegramId}
        onChange={e => setTelegramId(e.target.value)}
      />
      <input
        className="border p-2 m-2"
        placeholder="Dev Bot Token"
        value={botToken}
        onChange={e => setBotToken(e.target.value)}
      />
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        onClick={handleLogin}
      >
        Login
      </button>
    </div>
  );
}
