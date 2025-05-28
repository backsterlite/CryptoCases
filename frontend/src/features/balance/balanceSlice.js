import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchBalance = createAsyncThunk(
  'balance/fetchBalance',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.balance.usd();
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

const balanceSlice = createSlice({
  name: 'balance',
  initialState: { amount: null, loading: false, error: null },
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchBalance.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBalance.fulfilled, (state, action) => {
        state.loading = false;
        state.amount = action.payload;
      })
      .addCase(fetchBalance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export default balanceSlice.reducer;