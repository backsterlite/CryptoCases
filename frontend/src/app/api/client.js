// src/app/api/client.js
import axios from 'axios';
import { store } from '../store'; // імпортуй тут свій Redux store
import { showSessionExpiredModal } from '../../common/slices/uiSlice';
import { logout } from '../../features/auth/authSlice';


const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Тепер читаємо token із state.auth.token, який redux-persist уже витягнув із localStorage
client.interceptors.request.use(config => {
  const token = store.getState().auth.token;  // ← замість localStorage.getItem('jwt')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      store.dispatch(logout())
      store.dispatch(showSessionExpiredModal())
    }
    return Promise.reject(error);
  }
);

export default client;
