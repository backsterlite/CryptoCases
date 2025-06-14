import React, { useEffect } from 'react';
import { loginWithTelegram, fetchCurrentUser, refreshAccessToken } from '../features/auth/authSlice';
import { fetchBalance } from '../features/balance/balanceSlice';
import SessionExpiredModal from '../common/components/SessionExpiredModal';
import Spinner from '../common/components/Spinner';
import AppRoutes from '../routes/AppRoutes';
import { useAppDispatch, useAppSelector } from './hooks';

const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const { accessToken, refreshToken, user, status } = useAppSelector((state) => state.auth);
  const { sessionExpiredModalVisible } = useAppSelector((state) => state.ui);

  useEffect(() => {
    if (!accessToken && refreshToken) {
      dispatch(refreshAccessToken());
    } else if (!accessToken && !refreshToken) {
      dispatch(loginWithTelegram());
    } else if (accessToken && !user) {
      dispatch(fetchCurrentUser());
      dispatch(fetchBalance());
    }
  }, [dispatch, accessToken, refreshToken, user]);

  useEffect(() => {
    if (accessToken && user) {
      dispatch(fetchBalance());
    }
  }, [dispatch, accessToken, status, user]);

  return (
    <>
      {sessionExpiredModalVisible && <SessionExpiredModal />}
      {status === 'loading' && <Spinner />}
      {status === 'succeeded' && <AppRoutes />}
    </>
  );
};

export default App;
