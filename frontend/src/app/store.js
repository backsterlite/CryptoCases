import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import { combineReducers } from 'redux'; 
import storage from 'redux-persist/lib/storage'; // localStorage
import authReducer from '../features/auth/authSlice';
import casesReducer from '../features/cases/casesSlice';
import caseDetailReducer from '../features/caseDetail/caseDetailSlice';
import balanceReducer from '../features/balance/balanceSlice';
// import historyReducer from '../features/history/historySlice';
// import walletReducer from '../features/wallet/walletSlice';
import uiReducer from '../common/slices/uiSlice'

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth'] // зберігаємо тільки auth (token + user)
};

const rootReducer = {
    auth: authReducer,
    ui: uiReducer,
       cases: casesReducer,
    caseDetail: caseDetailReducer,
    balance: balanceReducer,
//     history: historyReducer,
//     wallet: walletReducer,
}

const persistedReducer = persistReducer(persistConfig, combineReducers(rootReducer));

export const store = configureStore({
  reducer: persistedReducer,
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({ serializableCheck: false }), // дозволяємо non-serializable (Date, Decimal тощо)
});

export const persistor = persistStore(store);