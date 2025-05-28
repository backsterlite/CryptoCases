import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const connectWallet = createAsyncThunk(
  'wallet/connectWallet',
  async (_, { rejectWithValue }) => {
    try {
      // реалізація підключення гаманця
      const data = await api.wallet.connect();
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

export const depositFunds = createAsyncThunk(
  'wallet/depositFunds',
  async ({ token, network, amount }, { rejectWithValue }) => {
    try {
      const data = await api.wallet.deposit(token, network, amount);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

export const withdrawFunds = createAsyncThunk(
  'wallet/withdrawFunds',
  async ({ symbol, network, amount, toAddress }, { rejectWithValue }) => {
    try {
      const data = await api.withdrawals.open(symbol, network, amount, toAddress);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

const walletSlice = createSlice({
  name: 'wallet',
  initialState: {
    connected: false,
    wallets: [],
    depositStatus: { loading: false, error: null, result: null },
    withdrawStatus: { loading: false, error: null, result: null }
  },
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(connectWallet.fulfilled, (state, action) => {
        state.connected = true;
      })
      .addCase(depositFunds.pending, state => {
        state.depositStatus.loading = true;
        state.depositStatus.error = null;
      })
      .addCase(depositFunds.fulfilled, (state, action) => {
        state.depositStatus.loading = false;
        state.depositStatus.result = action.payload;
      })
      .addCase(depositFunds.rejected, (state, action) => {
        state.depositStatus.loading = false;
        state.depositStatus.error = action.payload;
      })
      .addCase(withdrawFunds.pending, state => {
        state.withdrawStatus.loading = true;
        state.withdrawStatus.error = null;
      })
      .addCase(withdrawFunds.fulfilled, (state, action) => {
        state.withdrawStatus.loading = false;
        state.withdrawStatus.result = action.payload;
      })
      .addCase(withdrawFunds.rejected, (state, action) => {
        state.withdrawStatus.loading = false;
        state.withdrawStatus.error = action.payload;
      });
  }
});

export default walletSlice.reducer;