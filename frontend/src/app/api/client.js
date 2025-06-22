// frontend/src/app/api/client.js
import axios from 'axios';
import { store } from '../store';
import { showSessionExpiredModal } from '../../common/slices/uiSlice';
import { logout, refreshAccessToken, clearError } from '../../features/auth/authSlice';

const client = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  timeout: 10000, // 10 секунд таймаут
});

let isRefreshing = false;
let failedQueue = [];
let refreshAttempts = 0;
const MAX_REFRESH_ATTEMPTS = 2;

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Функція для перевірки чи це запит авторизації
const isAuthRequest = (url) => {
  return url.includes('/auth/telegram') || 
         url.includes('/auth/refresh') || 
         url.includes('/auth/logout');
};

// Функція для перевірки чи це критичний запит (не потребує авторизації)
const isCriticalRequest = (url) => {
  return url.includes('/health') || 
         url.includes('/status') || 
         url.includes('/public');
};

// Request interceptor
client.interceptors.request.use((config) => {
  const { accessToken } = store.getState().auth;
  
  // Додаємо токен тільки якщо він є і це не запит авторизації
  if (accessToken && !isAuthRequest(config.url)) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  
  // Додаємо унікальний ID для відстеження запитів
  config.metadata = { 
    requestId: Math.random().toString(36).substring(7),
    startTime: Date.now()
  };
  
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Response interceptor
client.interceptors.response.use(
  (response) => {
    // Логуємо успішні запити (опціонально)
    const duration = Date.now() - response.config.metadata?.startTime;
    if (duration > 3000) {
      console.warn(`Slow request: ${response.config.url} took ${duration}ms`);
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const errorMessage = error.response?.data?.detail;
    const requestUrl = originalRequest?.url || '';

    // Логуємо помилку для відладки
    console.error('API Error:', {
      url: requestUrl,
      status,
      message: errorMessage,
      requestId: originalRequest?.metadata?.requestId
    });

    // Обробляємо таймаут та мережеві помилки
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.error('Request timeout for:', requestUrl);
      return Promise.reject({
        ...error,
        message: 'Request timeout. Please check your connection.'
      });
    }

    // Обробляємо 401 помилки (тільки для НЕ-авторизаційних запитів)
    if (status === 401 && !isAuthRequest(requestUrl) && !isCriticalRequest(requestUrl)) {
      
      // Перевіряємо чи не досягли максимуму спроб оновлення
      if (refreshAttempts >= MAX_REFRESH_ATTEMPTS) {
        console.warn('Max refresh attempts reached, logging out');
        refreshAttempts = 0;
        store.dispatch(logout());
        store.dispatch(showSessionExpiredModal());
        return Promise.reject(error);
      }

      // Якщо вже відбувається оновлення, додаємо запит в чергу
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (token) {
              originalRequest.headers = originalRequest.headers || {};
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return client(originalRequest);
            }
            return Promise.reject(error);
          })
          .catch((err) => Promise.reject(err));
      }

      // Починаємо процес оновлення токена
      isRefreshing = true;
      refreshAttempts++;

      try {
        const { refreshToken } = store.getState().auth;
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        console.log(`Attempting token refresh (attempt ${refreshAttempts}/${MAX_REFRESH_ATTEMPTS})`);
        
        const refreshResult = await store.dispatch(refreshAccessToken());
        
        if (refreshAccessToken.fulfilled.match(refreshResult)) {
          const newToken = refreshResult.payload.access_token;
          
          // Оновлюємо заголовки для повторного запиту
          client.defaults.headers.common.Authorization = `Bearer ${newToken}`;
          processQueue(null, newToken);
          
          // Повторюємо оригінальний запит
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          
          // Скидаємо лічильник спроб при успіху
          refreshAttempts = 0;
          
          return client(originalRequest);
        } else {
          // Якщо оновлення не вдалось
          throw new Error(refreshResult.payload || 'Token refresh failed');
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        
        // Обробляємо помилки оновлення
        processQueue(refreshError, null);
        
        // Якщо досягли максимуму спроб або refresh token недійсний
        if (refreshAttempts >= MAX_REFRESH_ATTEMPTS || 
            refreshError.response?.status === 401) {
          
          refreshAttempts = 0;
          store.dispatch(logout());
          store.dispatch(showSessionExpiredModal());
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Обробляємо інші помилки
    if (status === 403) {
      console.warn('Access forbidden:', requestUrl);
    } else if (status === 404) {
      console.warn('Resource not found:', requestUrl);
    } else if (status >= 500) {
      console.error('Server error:', status, requestUrl);
    }

    // Для критичних запитів не показуємо модальне вікно
    if (isCriticalRequest(requestUrl)) {
      return Promise.reject(error);
    }

    // Додаємо додаткову інформацію до помилки
    const enhancedError = {
      ...error,
      requestId: originalRequest?.metadata?.requestId,
      timestamp: new Date().toISOString(),
      url: requestUrl
    };

    return Promise.reject(enhancedError);
  }
);

// Функція для скидання стану клієнта (корисно при логауті)
client.resetState = () => {
  isRefreshing = false;
  failedQueue = [];
  refreshAttempts = 0;
  delete client.defaults.headers.common.Authorization;
};

// Функція для встановлення токена
client.setAuthToken = (token) => {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete client.defaults.headers.common.Authorization;
  }
};

export default client;