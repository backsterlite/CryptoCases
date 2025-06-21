import axios from 'axios';
import { store } from '../store';
import { showSessionExpiredModal } from '../../common/slices/uiSlice';
import { logout, refreshAccessToken, loginWithTelegram } from '../../features/auth/authSlice';

const client = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token ?? undefined);
    }
  });
  failedQueue = [];
};

// Функція для перевірки чи це запит авторизації
const isAuthRequest = (url) => {
  return url.includes('/auth/telegram') || url.includes('/auth/refresh');
};

client.interceptors.request.use((config) => {
  const { accessToken } = store.getState().auth;
  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const errorMessage = error.response?.data?.detail;

    // Перевіряємо чи це помилка авторизації і чи це не запит авторизації
    if (status === 401 && !isAuthRequest(originalRequest.url)) {
      // Якщо вже відбувається оновлення токена, додаємо запит в чергу
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers = originalRequest.headers || {};
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return client(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      try {
        // Спробуємо оновити токен
        const resultAction = await store.dispatch(refreshAccessToken());
        
        if (refreshAccessToken.fulfilled.match(resultAction)) {
          const newToken = resultAction.payload.access_token;
          client.defaults.headers.common.Authorization = `Bearer ${newToken}`;
          processQueue(null, newToken);
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        }

        // Якщо оновлення не вдалось
        processQueue(error, null);
        store.dispatch(logout());
        
        // Запускаємо нову авторизацію через Telegram
        await store.dispatch(loginWithTelegram());
        return Promise.reject(error);
      } catch (err) {
        processQueue(err, null);
        store.dispatch(logout());
        // При будь-якій помилці оновлення токена запускаємо нову авторизацію
        await store.dispatch(loginWithTelegram());
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default client;
