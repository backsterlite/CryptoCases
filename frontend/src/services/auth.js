import api from '../api/axios';

export async function loginWithTelegram() {
  const initData = window.Telegram.WebApp.initData;
  const { data } = await api.post('/auth/telegram', { initData });
  const { token, exp } = data;
  localStorage.setItem('jwt', token);
  localStorage.setItem('jwt_exp', exp);
  return data;
}