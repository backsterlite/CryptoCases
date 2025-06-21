// в Header.jsx
import React from 'react';
import { useSelector, useDispatch } from 'react-redux';


import Spinner from './Spinner';
import UserAvatar from './UserAvatar'

export default function Header() {
  const { amount, loading, error } = useSelector(state => state.balance);
  if (loading) return <div>Loading…</div>;
  if (error)   return <div>Error: {error}</div>;
  return (
    <div className="w-full flex items-center justify-between px-4 py-2 bg-white shadow">
      <img src="/logo.svg" alt="Logo" className="h-8" />
      <div style={{color: 'black'}}>${amount}</div>
      <UserAvatar />
    </div>
  );
}
