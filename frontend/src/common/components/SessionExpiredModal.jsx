// frontend/src/common/components/SessionExpiredModal.jsx
import React, { useState } from 'react';
import { useAppDispatch } from '../../app/hooks';
import { hideSessionExpiredModal } from '../slices/uiSlice';
import { retryLogin, resetLoginAttempts } from '../../features/auth/authSlice';
import './css/SessionExpiredModal.css';

const SessionExpiredModal = ({ onRetry }) => {
  const dispatch = useAppDispatch();
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    if (isRetrying) return;
    
    setIsRetrying(true);
    
    try {
      // Використовуємо переданий onRetry або стандартний retryLogin
      if (onRetry) {
        await onRetry();
      } else {
        await dispatch(retryLogin()).unwrap();
      }
      
      // Якщо успішно, приховуємо модальне вікно
      dispatch(hideSessionExpiredModal());
    } catch (error) {
      console.error('Retry login failed:', error);
      // Модальне вікно залишається відкритим при помилці
    } finally {
      setIsRetrying(false);
    }
  };

  const handleClose = () => {
    dispatch(hideSessionExpiredModal());
    // Скидаємо лічильники спроб при закритті
    dispatch(resetLoginAttempts());
  };

  const handleReload = () => {
    // Повне перезавантаження сторінки як крайній варіант
    window.location.reload();
  };

  return (
    <div className="session-modal-overlay">
      <div className="session-modal">
        <div className="session-modal-header">
          <div className="session-modal-icon">🔐</div>
          <h2>Session Expired</h2>
        </div>
        
        <div className="session-modal-body">
          <p>
            Your session has expired or become invalid. 
            Please log in again to continue using the app.
          </p>
          
          <div className="session-modal-info">
            <h4>This might happen if:</h4>
            <ul>
              <li>You've been inactive for too long</li>
              <li>Your authentication token has expired</li>
              <li>There was a connection issue</li>
            </ul>
          </div>
        </div>
        
        <div className="session-modal-actions">
          <button 
            className="btn btn-secondary" 
            onClick={handleClose}
            disabled={isRetrying}
          >
            Close
          </button>
          
          <button 
            className={`btn btn-primary ${isRetrying ? 'loading' : ''}`}
            onClick={handleRetry}
            disabled={isRetrying}
          >
            {isRetrying ? (
              <>
                <span className="spinner"></span>
                Logging in...
              </>
            ) : (
              'Login Again'
            )}
          </button>
          
          <button 
            className="btn btn-ghost" 
            onClick={handleReload}
            disabled={isRetrying}
          >
            Reload Page
          </button>
        </div>
        
        <div className="session-modal-footer">
          <small>
            Make sure you're accessing this app through Telegram
          </small>
        </div>
      </div>
    </div>
  );
};

export default SessionExpiredModal;