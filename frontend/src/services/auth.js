import WebAppPromise from '../mocks/WebAppTG';
import api from './api';



export async function loginWithTelegram() {
  const WebApp = await WebAppPromise;
  const init_data = WebApp.initData;
  const { data } = await api.auth.telegram(init_data);
  const { token, exp } = data;
  localStorage.setItem('jwt', token);
  localStorage.setItem('jwt_exp', exp.toString());
  return data;
}
