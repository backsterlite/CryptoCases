import WebAppPromise from '../mocks/WebAppTG';
import api from './api';

export interface TelegramLoginResponse {
  token: string;
  exp: number;
}

export async function loginWithTelegram(): Promise<TelegramLoginResponse> {
  const WebApp = await WebAppPromise;
  const init_data = WebApp.initData;
  const { data } = await api.auth.telegram(init_data);
  const { token, exp } = data as TelegramLoginResponse;
  localStorage.setItem('jwt', token);
  localStorage.setItem('jwt_exp', exp.toString());
  return data as TelegramLoginResponse;
}
