import { useState } from 'react';
import api from '../../services/api';

export const useWithdrawal = () => {
  const [addresses, setAddresses] = useState([]);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.withdrawals.getAddresses();
      setAddresses(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addAddress = async (addr, network) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.withdrawals.saveAddress(addr, network);
      setAddresses(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadBalance = async (network, token) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.withdrawals.getBalance(network, token);
      setBalance(data.amount);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const initiate = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      await api.withdrawals.initiate(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { addresses, balance, loading, error, load, addAddress, initiate, loadBalance };
}; 