// frontend/src/app/App.jsx
import React, { useEffect, useCallback, useState } from 'react';
import { 
  safeLoginWithTelegram,  // Використовуємо безпечну версію
  fetchCurrentUser, 
  refreshAccessToken, 
  retryLogin,
  clearError,
  forceResetFlags 
} from '../features/auth/authSlice';
import { fetchBalance } from '../features/balance/balanceSlice';
import SessionExpiredModal from '../common/components/SessionExpiredModal';
import Spinner from '../common/components/Spinner';
import ErrorScreen from '../common/components/ErrorScreen';
import AppRoutes from '../routes/AppRoutes';
import { useAppDispatch, useAppSelector } from './hooks';

const App = () => {
  const dispatch = useAppDispatch();
  const { 
    accessToken, 
    refreshToken, 
    user, 
    status, 
    error, 
    isRefreshingUI,
    isLoggingInUI,
    canRetryLogin,
    lastLoginAttempt 
  } = useAppSelector((state) => state.auth);
  const { sessionExpiredModalVisible } = useAppSelector((state) => state.ui);
  
  // Локальний стан для запобігання повторних викликів
  const [hasInitialized, setHasInitialized] = useState(false);
  const [initializationAttempted, setInitializationAttempted] = useState(false);

  // Функція для ініціалізації авторизації
  const initializeAuth = useCallback(async () => {
    // Запобігаємо повторним викликам
    if (initializationAttempted || isLoggingInUI || isRefreshingUI) {
      console.log('Skipping auth initialization - already in progress');
      return;
    }

    setInitializationAttempted(true);
    console.log('Starting auth initialization...');

    try {
      // Сценарій 1: Є refresh token, але немає access token
      if (refreshToken && !accessToken) {
        console.log('Attempting to refresh token...');
        const refreshResult = await dispatch(refreshAccessToken());
        
        if (refreshAccessToken.fulfilled.match(refreshResult)) {
          console.log('Token refreshed successfully');
          setHasInitialized(true);
          return;
        } else {
          console.log('Token refresh failed, attempting new login...');
          // Якщо refresh не вдався, спробуємо новий логін
          const loginResult = await dispatch(safeLoginWithTelegram());
          if (safeLoginWithTelegram.fulfilled.match(loginResult)) {
            console.log('New login successful');
          }
        }
      }
      // Сценарій 2: Немає жодних токенів
      else if (!accessToken && !refreshToken) {
        console.log('No tokens found, attempting safe login...');
        await dispatch(safeLoginWithTelegram());
      }
      // Сценарій 3: Є access token, але немає даних користувача
      else if (accessToken && !user) {
        console.log('Access token found, fetching user data...');
        await dispatch(fetchCurrentUser());
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
    } finally {
      setHasInitialized(true);
      // Дозволяємо повторну ініціалізацію через деякий час
      setTimeout(() => {
        setInitializationAttempted(false);
      }, 10000); // Збільшили до 10 секунд
    }
  }, [
    dispatch, 
    accessToken, 
    refreshToken, 
    user, 
    isLoggingInUI, 
    isRefreshingUI,
    initializationAttempted
  ]);

  // Ефект для ініціалізації при першому завантаженні
  useEffect(() => {
    if (!hasInitialized && !initializationAttempted) {
      // Додаємо невелику затримку для стабілізації стану
      const timer = setTimeout(() => {
        initializeAuth();
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [initializeAuth, hasInitialized, initializationAttempted]);

  // Ефект для завантаження балансу після успішної авторизації
  useEffect(() => {
    if (accessToken && user && status === 'succeeded') {
      console.log('Loading balance...');
      dispatch(fetchBalance());
    }
  }, [dispatch, accessToken, user, status]);

  // Ефект для аварійного скидання флагів (якщо щось пішло не так)
  useEffect(() => {
    const emergencyReset = setTimeout(() => {
      if ((isLoggingInUI || isRefreshingUI) && status !== 'loading') {
        console.warn('Emergency reset of UI flags');
        dispatch(forceResetFlags());
      }
    }, 30000); // Якщо операція триває більше 30 секунд

    return () => clearTimeout(emergencyReset);
  }, [isLoggingInUI, isRefreshingUI, status, dispatch]);

  // Функція для ручного повтору авторизації
  const handleRetryAuth = useCallback(async () => {
    if (!canRetryLogin) {
      console.warn('Retry not allowed at this time');
      return;
    }

    console.log('Manual retry auth triggered');
    dispatch(clearError());
    setHasInitialized(false);
    setInitializationAttempted(false);
    
    try {
      await dispatch(retryLogin());
    } catch (error) {
      console.error('Manual retry failed:', error);
    }
  }, [dispatch, canRetryLogin]);

  // Функція для очищення помилок
  const handleClearError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  // Функція для аварійного перезапуску
  const handleEmergencyRestart = useCallback(() => {
    console.log('Emergency restart triggered');
    dispatch(forceResetFlags());
    dispatch(clearError());
    setHasInitialized(false);
    setInitializationAttempted(false);
    
    // Перезапускаємо ініціалізацію через секунду
    setTimeout(() => {
      initializeAuth();
    }, 1000);
  }, [dispatch, initializeAuth]);

  // Рендеринг залежно від стану
  const renderContent = () => {
    // Показуємо спінер під час завантаження
    if (status === 'loading' || isLoggingInUI || isRefreshingUI || !hasInitialized) {
      const message = isLoggingInUI ? 'Logging in...' : 
                     isRefreshingUI ? 'Refreshing session...' : 
                     'Initializing...';
      return <Spinner message={message} />;
    }

    // Показуємо екран помилки при невдачі авторизації
    if (status === 'failed' && error) {
      const canRetry = canRetryLogin && 
        (!lastLoginAttempt || Date.now() - lastLoginAttempt > 5000);

      return (
        <ErrorScreen
          error={error}
          onRetry={canRetry ? handleRetryAuth : undefined}
          onClear={handleClearError}
          retryDisabled={!canRetry}
          retryMessage={
            !canRetry 
              ? "Please wait before trying again..." 
              : "Retry Authorization"
          }
          additionalActions={
            <button 
              className="btn btn-ghost"
              onClick={handleEmergencyRestart}
              style={{ marginTop: '10px' }}
            >
              Emergency Restart
            </button>
          }
        />
      );
    }

    // Показуємо основний додаток при успішній авторизації
    if (status === 'succeeded' && accessToken && user) {
      return <AppRoutes />;
    }

    // Fallback - показуємо спінер з додатковими діями
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <Spinner message="Please wait..." />
        <button 
          onClick={handleEmergencyRestart}
          style={{ 
            marginTop: '20px', 
            padding: '10px 20px',
            background: '#f0f0f0',
            border: '1px solid #ccc',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Force Restart
        </button>
      </div>
    );
  };

  return (
    <>
      {sessionExpiredModalVisible && (
        <SessionExpiredModal onRetry={handleRetryAuth} />
      )}
      {renderContent()}
    </>
  );
};

export default App;