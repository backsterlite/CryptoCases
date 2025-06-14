import { useState } from 'react';
import {
  fetchManualDepositAddress,
  initiateDeposit,
  requestDepositAddress,
  DepositAddressResponse,
  DepositInitiateRequest,
  DepositAddressRequest
} from './depositApi';

export interface UseDepositReturn {
  loading: boolean;
  error: string | null;
  address: string | null;
  getAddress: (req: DepositAddressRequest) => Promise<void>;
  initiate: (req: DepositInitiateRequest) => Promise<void>;
  fetchManualAddress: (network: string) => Promise<string | null>;
}

export const useDeposit = (): UseDepositReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [address, setAddress] = useState<string | null>(null);

  const getAddress = async (req: DepositAddressRequest) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await requestDepositAddress(req);
      setAddress(data.address);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const initiate = async (req: DepositInitiateRequest) => {
    setLoading(true);
    setError(null);
    try {
      await initiateDeposit(req);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchManualAddress = async (network: string) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchManualDepositAddress(network);
      return data.address;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, address, getAddress, initiate, fetchManualAddress };
};
