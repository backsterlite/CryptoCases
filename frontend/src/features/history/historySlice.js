import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchDepositHistory = createAsyncThunk(
  'history/fetchDepositHistory',
  async (_, { rejectWithValue }) => {
    try {
      const data = await api.history.deposits();
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

export const fetchCaseOpensHistory = createAsyncThunk(
  'history/fetchCaseOpensHistory',
  async (_, { rejectWithValue }) => {
    try {
      const data = await api.history.opens();
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

export const fetchWithdrawHistory = createAsyncThunk(
  'history/fetchWithdrawHistory',
  async (_, { rejectWithValue }) => {
    try {
      const data = await api.history.withdrawals();
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

const historySlice = createSlice({
  name: 'history',
  initialState: {
    deposits: [],
    opens: [],
    withdrawals: [],
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchDepositHistory.fulfilled, (state, action) => {
        state.deposits = action.payload;
      })
      .addCase(fetchCaseOpensHistory.fulfilled, (state, action) => {
        state.opens = action.payload;
      })
      .addCase(fetchWithdrawHistory.fulfilled, (state, action) => {
        state.withdrawals = action.payload;
      })
      .addMatcher(
        action => action.type.endsWith('/pending'),
        state => { state.loading = true; state.error = null; }
      )
      .addMatcher(
        action => action.type.endsWith('/fulfilled'),
        state => { state.loading = false; }
      )
      .addMatcher(
        action => action.type.endsWith('/rejected'),
        (state, action) => { state.loading = false; state.error = action.payload; }
      );
  }
});

export default historySlice.reducer;