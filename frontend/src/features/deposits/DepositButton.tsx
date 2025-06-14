import React, { useState } from 'react';
import { TonConnectButton, useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';
import styles from './DepositButton.module.css';
import { useDeposit } from './useDeposit';

export interface DepositButtonProps {
  network: string;
}

export const DepositButton: React.FC<DepositButtonProps> = ({ network }) => {
  const wallet = useTonWallet();
  const [tonConnectUi] = useTonConnectUI();
  const { loading, error, address, getAddress, initiate } = useDeposit();
  const [amount, setAmount] = useState<number>(0);
  const [txHash, setTxHash] = useState<string>('');
  const [submitted, setSubmitted] = useState(false);

  const handleRequestAddress = async () => {
    if (!wallet?.account.address) return;
    await getAddress({ walletAddress: wallet.account.address, amount });
    setSubmitted(true);
  };

  const handleConfirm = async () => {
    if (!wallet) return;
    const transaction = {
      validUntil: Math.floor(Date.now() / 1000) + 60,
      messages: [
        {
          address: address!,
          amount: (amount * 1e9).toString(),
        },
      ],
    };
    const response = await tonConnectUi.sendTransaction(transaction);
    setTxHash(response.boc || '');
    await initiate({ walletAddress: wallet.account.address, amount, txHash: response.boc || '' });
  };

  return (
    <div className={styles.container}>
      {!wallet && <TonConnectButton />}
      {wallet && !submitted && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleRequestAddress();
          }}
        >
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            required
          />
          <button type="submit" disabled={loading}>Get Address</button>
        </form>
      )}
      {submitted && address && (
        <button onClick={handleConfirm} disabled={loading}>Confirm Deposit</button>
      )}
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
};

export default DepositButton;
