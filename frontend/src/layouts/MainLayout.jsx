import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../common/components/Header'
import NavBar from '../common/components/NavBar';

/**
 * MainLayout wraps the entire app with fixed Header and NavBar,
 * and scrollable content in between.
 */
export default function MainLayout() {
  return (
    <div className="flex-1 mt-16 mb-16 overflow-auto px-4 w-full max-w-screen-md mx-auto">
      {/* Fixed header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white shadow z-10">
        <Header />
      </header>

      {/* Main content area with appropriate top/bottom margins */}
      <main className="flex-1 mt-16 mb-16 overflow-auto">
        <Outlet />
      </main>

      {/* Fixed bottom navigation */}
      <footer className="fixed bottom-0 left-0 right-0 h-16 bg-white shadow z-10">
        <NavBar />
      </footer>
    </div>
  );
}
