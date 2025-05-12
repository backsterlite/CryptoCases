import React, { createContext, useState, useEffect } from 'react';
import { loginWithTelegram } from '../services/auth';
import SessionExpiredModal from '../components/SessionExpiredModal';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const authenticate = async () => {
    try {
      await loginWithTelegram();
      setIsAuthenticated(true);
    } catch (err) {
      console.error('Login failed', err);
    }
  };

  useEffect(() => {
    if(import.meta.env.DEV) {
        setIsAuthenticated(true);
        return;
    }
    const token = localStorage.getItem('jwt');
    if (token) {
      setIsAuthenticated(true);
    } else {
      authenticate();
    }

    const onSessionExpired = () => setShowModal(true);
    window.addEventListener('session_expired', onSessionExpired);
    return () => window.removeEventListener('session_expired', onSessionExpired);
  }, []);

  const handleRefresh = () => {
    setShowModal(false);
    authenticate();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated }}>
      {children}
      {showModal && <SessionExpiredModal onRefresh={handleRefresh} />}
    </AuthContext.Provider>
  );
}