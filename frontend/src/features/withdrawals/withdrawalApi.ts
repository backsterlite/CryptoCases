import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  withCredentials: true
});

export interface WithdrawalAddress {
  id: string;
  address: string;
  network: string;
}

export const getSavedAddresses = () =>
  apiClient.get<WithdrawalAddress[]>('/withdrawals/addresses');

export const saveAddress = (address: string, network: string) =>
  apiClient.post<WithdrawalAddress[]>('/withdrawals/addresses', { address, network });

export interface BalanceResponse {
  amount: number;
}

export const fetchBalance = (network: string, token: string) =>
  apiClient.get<BalanceResponse>(`/balance?network=${network}&token=${token}`);

export interface WithdrawalInitiateRequest {
  addressId: string;
  token: string;
  amount: number;
}

export const initiateWithdrawal = (payload: WithdrawalInitiateRequest) =>
  apiClient.post('/withdrawals/initiate', payload);
