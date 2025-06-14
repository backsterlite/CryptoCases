import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import { store } from '../store';
import { showSessionExpiredModal } from '../../common/slices/uiSlice';
import { logout, refreshAccessToken } from '../../features/auth/authSlice';

const client = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token?: string) => void; reject: (err: unknown) => void }> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token ?? undefined);
    }
  });
  failedQueue = [];
};

client.interceptors.request.use((config) => {
  const { accessToken } = store.getState().auth;
  if (accessToken) {
    (config.headers = config.headers ?? {}).Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            (originalRequest.headers = originalRequest.headers ?? {}).Authorization = `Bearer ${token}`;
            return client(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      try {
        const resultAction = await store.dispatch(refreshAccessToken());
        if (refreshAccessToken.fulfilled.match(resultAction)) {
          const newToken = resultAction.payload.access_token;
          client.defaults.headers.common.Authorization = `Bearer ${newToken}`;
          processQueue(null, newToken);
          (originalRequest.headers = originalRequest.headers ?? {}).Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        }
        processQueue(resultAction.error || 'SessionExpired', null);
        store.dispatch(logout());
        store.dispatch(showSessionExpiredModal());
        return Promise.reject(resultAction.error);
      } catch (err) {
        processQueue(err, null);
        store.dispatch(logout());
        store.dispatch(showSessionExpiredModal());
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default client;
