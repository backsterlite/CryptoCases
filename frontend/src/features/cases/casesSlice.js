import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunk to fetch list of cases
export const fetchCases = createAsyncThunk(
  'cases/fetchList',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.cases.list();
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

// Async thunk to open a case
export const openCase = createAsyncThunk(
  'cases/open',
  async ({ caseId, clientSeed, nonce, serverSeedId }, { rejectWithValue }) => {
    try {
      const result = await api.cases.open(caseId, clientSeed, nonce, serverSeedId);
      return result;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

const casesSlice = createSlice({
  name: 'cases',
  initialState: {
    items: [],
    loading: false,
    error: null,
    openStatus: { loading: false, error: null, result: null },
  },
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchCases.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCases.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchCases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(openCase.pending, state => {
        state.openStatus = { loading: true, error: null, result: null };
      })
      .addCase(openCase.fulfilled, (state, action) => {
        state.openStatus = { loading: false, error: null, result: action.payload };
      })
      .addCase(openCase.rejected, (state, action) => {
        state.openStatus = { loading: false, error: action.payload, result: null };
      });
  },
});

export default casesSlice.reducer;