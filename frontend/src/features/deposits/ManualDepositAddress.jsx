import React, { useEffect, useState } from 'react';
import styles from './DepositButton.module.css';
import { useDeposit } from './useDeposit';

export const ManualDepositAddress = ({ network }) => {
  const { fetchManualAddress, loading, error } = useDeposit();
  const [address, setAddress] = useState('');

  useEffect(() => {
    fetchManualAddress(network).then((addr) => {
      if (addr) setAddress(addr);
    });
  }, [network]);

  const copy = () => navigator.clipboard.writeText(address);

  if (loading && !address) return <div>Loading...</div>;
  return (
    <div className={styles.container}>
      <div>{address}</div>
      <button onClick={copy}>Copy</button>
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
};

export default ManualDepositAddress; 