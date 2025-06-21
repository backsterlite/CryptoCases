import { useState } from 'react';
import api from '../../services/api';

export const useDeposit = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [address, setAddress] = useState(null);

  const getAddress = async (req) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.deposits.requestAddress(req);
      setAddress(data.address);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const initiate = async (req) => {
    setLoading(true);
    setError(null);
    try {
      await api.deposits.initiate(req);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchManualAddress = async (network) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.deposits.getManualAddress(network);
      return data.address;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, address, getAddress, initiate, fetchManualAddress };
}; 