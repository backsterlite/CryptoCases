import { useState } from 'react';
import {
  fetchBalance,
  getSavedAddresses,
  saveAddress,
  initiateWithdrawal,
  WithdrawalAddress,
  WithdrawalInitiateRequest,
} from './withdrawalApi';

export interface UseWithdrawalReturn {
  addresses: WithdrawalAddress[];
  balance: number | null;
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
  addAddress: (addr: string, network: string) => Promise<void>;
  initiate: (payload: WithdrawalInitiateRequest) => Promise<void>;
  loadBalance: (network: string, token: string) => Promise<void>;
}

export const useWithdrawal = (): UseWithdrawalReturn => {
  const [addresses, setAddresses] = useState<WithdrawalAddress[]>([]);
  const [balance, setBalance] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await getSavedAddresses();
      setAddresses(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addAddress = async (addr: string, network: string) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await saveAddress(addr, network);
      setAddresses(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadBalance = async (network: string, token: string) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchBalance(network, token);
      setBalance(data.amount);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const initiate = async (payload: WithdrawalInitiateRequest) => {
    setLoading(true);
    setError(null);
    try {
      await initiateWithdrawal(payload);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { addresses, balance, loading, error, load, addAddress, initiate, loadBalance };
};
