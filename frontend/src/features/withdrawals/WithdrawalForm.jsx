import React, { useEffect, useState } from 'react';
import styles from './WithdrawalForm.module.css';
import { useWithdrawal } from './useWithdrawal';

export const WithdrawalForm = ({ network, token }) => {
  const { addresses, balance, loading, error, load, addAddress, initiate, loadBalance } = useWithdrawal();
  const [selected, setSelected] = useState('');
  const [newAddress, setNewAddress] = useState('');
  const [amount, setAmount] = useState(0);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    load();
    loadBalance(network, token);
  }, [network, token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (amount > (balance || 0)) {
      alert('Amount exceeds balance');
      return;
    }
    await initiate({ addressId: selected, token, amount });
  };

  const handleAddAddress = async () => {
    await addAddress(newAddress, network);
    setAdding(false);
  };

  return (
    <form role="form" className={styles.container} onSubmit={handleSubmit}>
      <select value={selected} onChange={(e) => setSelected(e.target.value)}>
        <option value="" disabled>Select address</option>
        {addresses.map((a) => (
          <option key={a.id} value={a.id}>{a.address}</option>
        ))}
      </select>
      <button type="button" onClick={() => setAdding(true)}>Add New Address</button>
      {adding && (
        <div>
          <input value={newAddress} onChange={(e) => setNewAddress(e.target.value)} />
          <button type="button" onClick={handleAddAddress}>Save</button>
        </div>
      )}
      <div>Balance: {balance ?? '...'}</div>
      <input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} />
      <button type="submit" disabled={loading}>Withdraw</button>
      {error && <span className={styles.error}>{error}</span>}
    </form>
  );
};

export default WithdrawalForm; 