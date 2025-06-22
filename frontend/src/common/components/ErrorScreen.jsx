// frontend/src/common/components/ErrorScreen.jsx
import React from 'react';
import './css/ErrorScreen.css';

const ErrorScreen = ({ 
  error, 
  onRetry, 
  onClear, 
  retryDisabled = false,
  retryMessage = "Try Again"
}) => {
  const getErrorMessage = (error) => {
    if (typeof error === 'string') {
      return error;
    }
    
    if (error?.message) {
      return error.message;
    }
    
    return 'An unexpected error occurred';
  };

  const getErrorType = (error) => {
    const message = getErrorMessage(error).toLowerCase();
    
    if (message.includes('network') || message.includes('timeout')) {
      return 'network';
    }
    
    if (message.includes('auth') || message.includes('token')) {
      return 'auth';
    }
    
    if (message.includes('telegram')) {
      return 'telegram';
    }
    
    return 'general';
  };

  const getErrorIcon = (type) => {
    switch (type) {
      case 'network':
        return '🌐';
      case 'auth':
        return '🔐';
      case 'telegram':
        return '📱';
      default:
        return '⚠️';
    }
  };

  const getErrorTitle = (type) => {
    switch (type) {
      case 'network':
        return 'Connection Error';
      case 'auth':
        return 'Authentication Error';
      case 'telegram':
        return 'Telegram Integration Error';
      default:
        return 'Something went wrong';
    }
  };

  const getSuggestions = (type) => {
    switch (type) {
      case 'network':
        return [
          'Check your internet connection',
          'Try refreshing the page',
          'Wait a moment and try again'
        ];
      case 'auth':
        return [
          'Try logging in again',
          'Clear your browser cache',
          'Make sure you opened this app from Telegram'
        ];
      case 'telegram':
        return [
          'Make sure you opened this app from Telegram',
          'Try closing and reopening the app',
          'Update your Telegram app'
        ];
      default:
        return [
          'Try refreshing the page',
          'Wait a moment and try again',
          'Contact support if the problem persists'
        ];
    }
  };

  const errorType = getErrorType(error);
  const errorMessage = getErrorMessage(error);
  const errorIcon = getErrorIcon(errorType);
  const errorTitle = getErrorTitle(errorType);
  const suggestions = getSuggestions(errorType);

  return (
    <div className="error-screen">
      <div className="error-container">
        <div className="error-icon">
          {errorIcon}
        </div>
        
        <h2 className="error-title">
          {errorTitle}
        </h2>
        
        <p className="error-message">
          {errorMessage}
        </p>
        
        <div className="error-suggestions">
          <h3>What you can try:</h3>
          <ul>
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
        
        <div className="error-actions">
          {onClear && (
            <button 
              className="btn btn-secondary" 
              onClick={onClear}
            >
              Dismiss
            </button>
          )}
          
          {onRetry && (
            <button 
              className={`btn btn-primary ${retryDisabled ? 'disabled' : ''}`}
              onClick={onRetry}
              disabled={retryDisabled}
            >
              {retryMessage}
            </button>
          )}
        </div>
        
        <div className="error-details">
          <details>
            <summary>Technical Details</summary>
            <pre>{JSON.stringify(error, null, 2)}</pre>
          </details>
        </div>
      </div>
    </div>
  );
};

export default ErrorScreen;