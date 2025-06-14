import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  withCredentials: true
});

export interface DepositAddressRequest {
  walletAddress: string;
  amount: number;
}

export interface DepositAddressResponse {
  address: string;
}

export interface DepositInitiateRequest {
  walletAddress: string;
  amount: number;
  txHash: string;
}

export const requestDepositAddress = (data: DepositAddressRequest) =>
  apiClient.post<DepositAddressResponse>('/deposits/address', data);

export const initiateDeposit = (data: DepositInitiateRequest) =>
  apiClient.post('/deposits/initiate', data);

export const fetchManualDepositAddress = (network: string) =>
  apiClient.get<DepositAddressResponse>(`/deposits/address?network=${network}`);
