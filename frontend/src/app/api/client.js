// src/app/api/client.js
import axios from 'axios';
import { store } from '../store'; // імпортуй тут свій Redux store
import { showSessionExpiredModal } from '../../common/slices/uiSlice';
import { logout, refreshAccessToken } from '../../features/auth/authSlice';



const client = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

client.interceptors.request.use(config => {
  const { accessToken } = store.getState().auth;
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// response interceptor
client.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    const status = error.response?.status;

    if (status === 401 && !originalRequest._retry) {
      // якщо вже пробували оновити, не запускаємо вдруге
      originalRequest._retry = true;

      if (isRefreshing) {
        // якщо вже є запит на refresh у процесі, ставимо цей запит у чергу
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return client(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      isRefreshing = true;
      try {
        // Диспатчимо наш Thunk refreshAccessToken
        const resultAction = await store.dispatch(refreshAccessToken());
        if (refreshAccessToken.fulfilled.match(resultAction)) {
          // якщо успішно, беремо новий токен
          const newToken = resultAction.payload.access_token;
          // ставим у заголовок за замовчуванням
          client.defaults.headers.common.Authorization = `Bearer ${newToken}`;
          // обробляємо чергу – кожен попередній запит отримає новий токен
          processQueue(null, newToken);
          // оновлюємо originalRequest і повторюємо його
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        } else {
          // Якщо refreshToken не дійсний — диспатчити logout і показати помилку
          processQueue(resultAction.error || 'SessionExpired', null);
          store.dispatch(logout());
          store.dispatch(showSessionExpiredModal());
          return Promise.reject(resultAction.error);
        }
      } catch (err) {
        processQueue(err, null);
        store.dispatch(logout());
        store.dispatch(showSessionExpiredModal());
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    // Якщо не 401 або вже retry, просто прокидаємо помилку далі
    return Promise.reject(error);
  }
);

export default client;
