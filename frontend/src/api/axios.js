import axios from 'axios';

const api = axios.create({
  withCredentials: true,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      window.dispatchEvent(new Event('session_expired'));
    }
    return Promise.reject(error);
  }
);

export default api;


/* File: src/services/auth.js */
