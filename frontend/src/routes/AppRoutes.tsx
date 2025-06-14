import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from '../app/hooks';
import MainLayout from '../layouts/MainLayout';
import HomePage from '../features/home/HomePage';
import GamePage from '../features/cases/GamePage';
import CaseDetailPage from '../features/caseDetail/CaseDetailPage';
import ProfileLayout from '../layouts/ProfileLayout';
import WalletLayout from '../layouts/WalletLayout';
import HistoryLayout from '../layouts/HistoryLayout';
import WalletsPage from '../features/wallet/WalletsPage';
import DepositPage from '../features/wallet/DepositPage';
import WithdrawPage from '../features/wallet/WithdrawPage';
import DepositHistoryPage from '../features/history/DepositHistoryPage';
import CaseOpensHistoryPage from '../features/history/CaseOpensHistoryPage';
import WithdrawHistoryPage from '../features/history/WithdrawHistoryPage';
import SettingsPage from '../features/settings/SettingsPage';

const Protected: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { accessToken } = useAppSelector((state) => state.auth);
  return accessToken ? children : <Navigate to="/" replace />;
};

const AppRoutes: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Protected><MainLayout /></Protected>}>
        <Route index element={<HomePage />} />
        <Route path="play" element={<GamePage />} />
        <Route path="play/:caseId" element={<Protected><CaseDetailPage /></Protected>} />

        <Route path="profile" element={<Protected><ProfileLayout /></Protected>}>
          <Route index element={<Navigate to="wallet" replace />} />

          <Route path="wallet" element={<Protected><WalletLayout /></Protected>}>
            <Route index element={<WalletsPage />} />
            <Route path="all" element={<WalletsPage />} />
            <Route path="deposit" element={<DepositPage />} />
            <Route path="withdraw" element={<WithdrawPage />} />
          </Route>

          <Route path="history" element={<Protected><HistoryLayout /></Protected>}>
            <Route index element={<DepositHistoryPage />} />
            <Route path="deposits" element={<DepositHistoryPage />} />
            <Route path="opens" element={<CaseOpensHistoryPage />} />
            <Route path="withdrawals" element={<WithdrawHistoryPage />} />
          </Route>

          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Route>
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;
