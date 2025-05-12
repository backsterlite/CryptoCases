import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('api_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function loginDev(telegramId, devToken) {
  console.log(`API_URL: ${client.baseURL}`)

  const { data } = await client.get('/dev/gen_token', {
    params: { telegram_id: parseInt(telegramId), bot_token: devToken },
  });
  console.log(data.access_token)
  return data.access_token;
}

export async function fetchUsdBalance() {
  const { data } = await client.get('/balance/usd');
  return data;
}

export async function fetchWallets() {
  const { data } = await client.get('/users/me/wallets');
  return data;
}

export async function openCase(caseId) {
  const { data } = await client.post('/cases/open', { case_id: caseId });
  return data;
}

export async function adjustWallet(symbol, network, delta) {
  const { data } = await client.post('/wallets/adjust', { symbol, network, delta });
  return data;
}

export async function withdraw(symbol, network, amount, address) {
  const { data } = await client.post('/withdraw', { token: symbol, network, amount, to_address: address });
  return data;
}
