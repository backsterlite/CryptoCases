import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchWallets } from './walletSlice';
import './css/WalletsPage.css';
import SwapModal from './components/SwapModal';

const WalletsPage = () => {
  const dispatch = useDispatch();

  const wallets = useSelector(state => state.wallet.wallets);
  const isLoading = useSelector(state => state.wallet.walletsLoading);
  const error = useSelector(state => state.wallet.walletsError);

  const [isSwapOpen, setIsSwapOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchWallets());
  }, [dispatch]);

  if (isLoading) {
    return <div className="loading-wallets">Завантаження гаманців...</div>;
  }

  if (error) {
    return <div className="error-wallets">Помилка: {error}</div>;
  }

  const entries = wallets ? Object.entries(wallets) : [];

  // Функція для форматування мережі
  const formatNetwork = (network) => {
    if (network === 'None' || network === null) {
      return 'Default';
    }
    return network;
  };

  // Функція для форматування балансу
  const formatBalance = (balance) => {
    const num = parseFloat(balance);
    if (num === 0) return '0';
    if (num < 0.000001) return '<0.000001';
    if (num < 1) return num.toFixed(6);
    if (num < 1000) return num.toFixed(4);
    return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
  };

  return (
    <div className="wallets-page">
      <button className="swap-button" onClick={() => setIsSwapOpen(true)}>
        Swap Tokens
      </button>
      
      <h2>Ваші гаманці</h2>

      {entries.length === 0 ? (
        <div className="no-wallets">Гаманці відсутні</div>
      ) : (
        <table className="wallets-table">
          <thead>
            <tr>
              <th>Іконка</th>
              <th>Монета</th>
              <th>Мережа</th>
              <th>Баланс</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([coinKey, userTokenWallet]) => {
              const { coin, balance } = userTokenWallet;
              const iconUrl = coin.thumb;
              const displayName = coin.name;
              const symbol = coin.symbol.toUpperCase();

              const networkEntries = Object.entries(balance);

              return networkEntries.map(([network, amount]) => {
                const networkLabel = formatNetwork(network);
                const formattedAmount = formatBalance(amount);

                return (
                  <tr key={`${coinKey}-${network}`}>
                    <td className="wallets-table__icon">
                      <img
                        src={iconUrl}
                        alt={symbol}
                        className="wallets-table__img"
                        onError={(e) => {
                          e.target.src = '/placeholder-coin.png';
                        }}
                      />
                    </td>
                    <td>
                      <div>{displayName}</div>
                      <div style={{ fontSize: '12px', color: '#666' }}>{symbol}</div>
                    </td>
                    <td>{networkLabel}</td>
                    <td style={{ fontWeight: parseFloat(amount) > 0 ? '500' : 'normal' }}>
                      {formattedAmount}
                    </td>
                  </tr>
                );
              });
            })}
          </tbody>
        </table>
      )}

      <SwapModal isOpen={isSwapOpen} onClose={() => setIsSwapOpen(false)} />
    </div>
  );
};

export default WalletsPage;