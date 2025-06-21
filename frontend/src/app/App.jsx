import React, { useEffect } from 'react';
import { loginWithTelegram, fetchCurrentUser, refreshAccessToken } from '../features/auth/authSlice';
import { fetchBalance } from '../features/balance/balanceSlice';
import SessionExpiredModal from '../common/components/SessionExpiredModal';
import Spinner from '../common/components/Spinner';
import AppRoutes from '../routes/AppRoutes';
import { useAppDispatch, useAppSelector } from './hooks';

const App = () => {
  const dispatch = useAppDispatch();
  const { accessToken, refreshToken, user, status, error } = useAppSelector((state) => state.auth);
  const { sessionExpiredModalVisible } = useAppSelector((state) => state.ui);
  useEffect(() => {
    const handleAuth = async () => {
      if (!accessToken && refreshToken) {
        await dispatch(refreshAccessToken());
      } else if (!accessToken && !refreshToken) {
        await dispatch(loginWithTelegram());
      } else if (accessToken && !user) {
        await dispatch(fetchCurrentUser());
        await dispatch(fetchBalance());
      }
    };

    handleAuth();
  }, [dispatch, accessToken, refreshToken, user, error]);

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
