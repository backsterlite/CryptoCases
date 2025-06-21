import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

const initialState = {
  connected: false,
  wallets: {},
  walletsLoading: false,
  walletsError: null,
  swapQuote: {
    loading: false,
    error: null,
    data: null,
  },
  swapStatus: {
    loading: false,
    error: null,
    success: false,
  },
  depositStatus: { loading: false, error: null, result: null },
  withdrawStatus: { loading: false, error: null, result: null },
};

export const fetchSwapQuote = createAsyncThunk(
  'wallet/fetchSwapQuote',
  async ({ fromToken, toToken, amount, fromNetwork, toNetwork }, { rejectWithValue }) => {
    try {
      const payload = {
        from_token: fromToken,
        from_network: fromNetwork,
        to_token: toToken,
        to_network: toNetwork,
        from_amount: amount,
      };
      const response = await api.wallet.quote(payload);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

export const swapCoins = createAsyncThunk(
  'wallet/swapCoins',
  async ({ fromToken, toToken, amount, fromNetwork, toNetwork }, { rejectWithValue }) => {
    try {
      const payload = {
        from_token: fromToken,
        from_network: fromNetwork,
        to_token: toToken,
        to_network: toNetwork,
        from_amount: amount,
      };
      const response = await api.wallet.execute(payload);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

export const fetchWallets = createAsyncThunk('wallet/fetchWallets', async (_, { rejectWithValue }) => {
  try {
    const response = await api.wallet.all();
    return response.data;
  } catch (err) {
    return rejectWithValue(err.response?.data || err.message);
  }
});

export const connectWallet = createAsyncThunk('wallet/connectWallet', async (_, { rejectWithValue }) => {
  try {
    const data = await api.wallet.connect();
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data || err.message);
  }
});

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
  initialState,
  reducers: {
    clearSwapQuote(state) {
      state.swapQuote.data = null;
      state.swapQuote.error = null;
    },
    clearSwapErrors(state) {
      state.swapQuote.error = null;
      state.swapStatus.error = null;
    },
    resetSwapStatus(state) {
      state.swapStatus.success = false;
      state.swapStatus.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWallets.pending, (state) => {
        state.walletsLoading = true;
        state.walletsError = null;
      })
      .addCase(fetchWallets.fulfilled, (state, action) => {
        state.walletsLoading = false;
        state.wallets = action.payload;
      })
      .addCase(fetchWallets.rejected, (state, action) => {
        state.walletsLoading = false;
        state.walletsError = action.payload;
      })
      .addCase(fetchSwapQuote.pending, (state) => {
        state.swapQuote.loading = true;
        state.swapQuote.error = null;
        state.swapQuote.data = null;
      })
      .addCase(fetchSwapQuote.fulfilled, (state, action) => {
        state.swapQuote.loading = false;
        state.swapQuote.data = action.payload;
      })
      .addCase(fetchSwapQuote.rejected, (state, action) => {
        state.swapQuote.loading = false;
        state.swapQuote.error = action.payload;
        state.swapQuote.data = null;
      })
      .addCase(swapCoins.pending, (state) => {
        state.swapStatus.loading = true;
        state.swapStatus.error = null;
        state.swapStatus.success = false;
      })
      .addCase(swapCoins.fulfilled, (state) => {
        state.swapStatus.loading = false;
        state.swapStatus.success = true;
      })
      .addCase(swapCoins.rejected, (state, action) => {
        state.swapStatus.loading = false;
        state.swapStatus.error = action.payload;
      });
  },
});

export const { clearSwapQuote, clearSwapErrors, resetSwapStatus } = walletSlice.actions;
export default walletSlice.reducer;
