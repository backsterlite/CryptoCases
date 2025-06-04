import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loginWithTelegram, fetchCurrentUser } from '../features/auth/authSlice';
import { fetchBalance } from '../features/balance/balanceSlice';
import SessionExpiredModal from '../common/components/SessionExpiredModal';
import Spinner from '../common/components/Spinner';
import AppRoutes from '../routes/AppRoutes';



function App() {

  const dispatch = useDispatch();
  const { accessToken, refreshToken, user, status, error } = useSelector(state => state.auth);
  const {sessionExpiredModalVisible} = useSelector(state => state.ui)

// On mount or token change: login or fetch user
  useEffect(() => {
    console.log("auth", accessToken, refreshToken)
    if (!accessToken && refreshToken) {
      // спробувати оновити accessToken
      dispatch(refreshAccessToken());
    } else if (!accessToken && !refreshToken) {
      dispatch(loginWithTelegram());
    } else if (accessToken && !user) {
      dispatch(fetchCurrentUser());
      dispatch(fetchBalance());
    }
  }, [dispatch, accessToken, refreshToken, user]);

  // After successful auth, fetch balance
  useEffect(() => {
    if (accessToken && user) {
      // console.log("fetchBalance", accessToken, status)
      dispatch(fetchBalance());
    }
  }, [dispatch, accessToken, status]);


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