import React, { useEffect } from 'react';
import Header from '../components/Header';
import Carousel from '../components/Carousel';
import CaseGrid from '../components/CaseGrid';
import QuickActions from '../components/QuickActions';
import { useAuth } from '../hooks/useAuth';

export default function MainPage() {
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.expand();
    }
  }, []);

  if (!isAuthenticated) {
    return null; // or a loading spinner
  }

  return (
    <div className="bg-gradient-to-b from-gray-100 via-white to-gray-100 min-h-screen flex flex-col items-center p-4">
      <Header />

      <div className="w-full my-4">
        <Carousel />
      </div>

      <div className="w-full flex-1">
        <CaseGrid />
      </div>

      <QuickActions />
    </div>
  );
}