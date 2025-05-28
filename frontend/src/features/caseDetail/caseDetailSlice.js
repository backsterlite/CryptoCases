import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

/**
 * Fetch case metadata (price, tiers, nonce, server_seed_hash)
 */
export const fetchCaseDetail = createAsyncThunk(
  'caseDetail/fetchCaseDetail',
  async (caseId, { rejectWithValue }) => {
    try {
      const response = await api.cases.getDetail(caseId);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

/**
 * Check if spin is allowed (enough reserve)
 */
export const precheckCase = createAsyncThunk(
  'caseDetail/precheckCase',
  async (caseId, { rejectWithValue }) => {
    try {
      const response = await api.cases.precheck(caseId);
      return response.data; // { spin: boolean, reason: string|null }
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

/**
 * Commit server seed and obtain hash
 */
export const commitCase = createAsyncThunk(
  'caseDetail/commitCase',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.fairness.commit();
      return response.data; // { server_seed_id, hash }
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

/**
 * Open (spin) the case
 */
export const openCaseDetail = createAsyncThunk(
  'caseDetail/openCaseDetail',
  async (
    { caseId, clientSeed, nonce, serverSeedId },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.cases.open(caseId, clientSeed, nonce, serverSeedId);
      return response.data; // { spin_log_id, result }
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

/**
 * Reveal server seed for proof
 */
export const revealCaseDetail = createAsyncThunk(
  'caseDetail/revealCaseDetail',
  async (spinLogId, { rejectWithValue }) => {
    try {
      const response = await api.fairness.reveal(spinLogId);
      return response.data.server_seed;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

/**
 * Delete unused server seed commitment
 */
export const deleteServerSeed = createAsyncThunk(
  'caseDetail/deleteServerSeed',
  async (seedId, { rejectWithValue }) => {
    try {
      await api.fairness.deleteCommit(seedId);
      return seedId;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

const initialState = {
  caseDetailsById: {},
  precheckStatus: 'idle',     // 'idle' | 'loading' | 'succeeded' | 'failed'
  precheckError: null,
  commitData: null,           // { server_seed_id, hash }
  commitStatus: 'idle',
  commitError: null,
  clientSeed: null,
  spinResult: null,
  openStatus: 'idle',         // 'idle' | 'loading' | 'succeeded' | 'failed'
  openError: null,
  revealStatus: 'idle',
  revealError: null,
  error: null
};

const caseDetailSlice = createSlice({
  name: 'caseDetail',
  initialState,
  reducers: {
    resetCaseDetail(state) {
      // Reset only the spin/fairness flow state, keep fetched case detail & clientSeed intact
      state.precheckStatus = 'idle';
      state.precheckError  = null;
      state.commitData     = null;
      state.commitStatus   = 'idle';
      state.commitError    = null;
      state.openStatus     = 'idle';
      state.openError      = null;
      state.revealStatus   = 'idle';
      state.revealError    = null;
      state.spinResult     = null;
    }
  },
  extraReducers: builder => {
    builder
      // fetch case metadata
      .addCase(fetchCaseDetail.pending, state => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchCaseDetail.fulfilled, (state, action) => {
        state.detail = action.payload;
        state.clientSeed = crypto.randomUUID();
        state.status = 'succeeded';
      })
      .addCase(fetchCaseDetail.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      // precheck
      .addCase(precheckCase.pending, state => {
        state.precheckStatus = 'loading';
        state.precheckError = null;
      })
      .addCase(precheckCase.fulfilled, (state, action) => {
        state.precheckStatus = 'succeeded';
        state.precheckError = action.payload.reason;
      })
      .addCase(precheckCase.rejected, (state, action) => {
        state.precheckStatus = 'failed';
        state.precheckError = action.payload;
      })
      // commit
      .addCase(commitCase.pending, state => {
        state.commitStatus = 'loading';
        state.commitError = null;
      })
      .addCase(commitCase.fulfilled, (state, action) => {
        state.commitStatus = 'succeeded';
        state.commitData = action.payload;
      })
      .addCase(commitCase.rejected, (state, action) => {
        state.commitStatus = 'failed';
        state.commitError = action.payload;
      })
      // open
      .addCase(openCaseDetail.pending, state => {
        state.openStatus = 'loading';
        state.openError = null;
      })
      .addCase(openCaseDetail.fulfilled, (state, action) => {
        state.openStatus = 'succeeded';
        state.spinResult = action.payload;
      })
      .addCase(openCaseDetail.rejected, (state, action) => {
        state.openStatus = 'failed';
        state.openError = action.payload;
      })
      // reveal
      // .addCase(revealCaseDetail.pending, state => {
      //   state.revealStatus = 'loading';
      //   state.revealError = null;
      // })
      // .addCase(revealCaseDetail.fulfilled, (state, action) => {
      //   state.revealStatus = 'succeeded';
      //   state.serverSeed = action.payload;
      // })
      // .addCase(revealCaseDetail.rejected, (state, action) => {
      //   state.revealStatus = 'failed';
      //   state.revealError = action.payload;
      // })
      // delete unused seed
      .addCase(deleteServerSeed.fulfilled, (state, action) => {
        if (state.commitData?.server_seed_id === action.payload) {
          state.commitData = null;
        }
      });
  }
});

export const { resetCaseDetail } = caseDetailSlice.actions;
export default caseDetailSlice.reducer;