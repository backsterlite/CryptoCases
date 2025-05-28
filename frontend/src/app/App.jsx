import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loginWithTelegram, fetchCurrentUser } from '../features/auth/authSlice';
import { fetchBalance } from '../features/balance/balanceSlice';
import SessionExpiredModal from '../common/components/SessionExpiredModal';
import Spinner from '../common/components/Spinner';
import AppRoutes from '../routes/AppRoutes';



function App() {

  const dispatch = useDispatch();
  const { token, user, status, error } = useSelector(state => state.auth);
  const {sessionExpiredModalVisible} = useSelector(state => state.ui)

// On mount or token change: login or fetch user
  useEffect(() => {
    if (!token) {
      dispatch(loginWithTelegram());
    } else if (!user) {
      dispatch(fetchCurrentUser());
    }
  }, [dispatch, token, user]);

  // After successful auth, fetch balance
  useEffect(() => {
    if (token && user) {
      dispatch(fetchBalance());
    }
  }, [dispatch, token, status]);

  // Handle session expiration modal
  console.log(sessionExpiredModalVisible)

  return (
    <>
      {sessionExpiredModalVisible && (
        <SessionExpiredModal />
      )}
      {status === 'loading' && <Spinner />}
      {status === 'succeeded' && <AppRoutes />}
    </>
  );
}

export default App;