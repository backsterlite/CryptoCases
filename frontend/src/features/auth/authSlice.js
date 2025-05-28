// src/features/auth/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';
import { showSessionExpiredModal } from '../../common/slices/uiSlice'; // action to show modal
import TelegramWebAppPromise from '../../mocks/WebAppTG';

const initialState = {
  token: null,
  user: null,
  status: 'idle', // 'loading' | 'succeeded' | 'failed'
  error: null,
};

export const loginWithTelegram = createAsyncThunk(
  'auth/login',
  async (_, { rejectWithValue }) => {
    try {
      const WebApp = await TelegramWebAppPromise;
      const initData = WebApp.initData;
      const res = await api.auth.telegram(initData);
      console.log(res.data.access_token)
      return res.data.access_token;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

// fetch user info
export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { getState, rejectWithValue, dispatch }) => {
    try {
      const { token } = getState().auth;
      const res = await api.users.me(token);
      return res.data; // { user_id, username }
    } catch (err) {
      if (err.response?.status === 401) {
        dispatch(showSessionExpiredModal())
        return rejectWithValue('Session expired');
      }
      return rejectWithValue(err.message);
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      state.token = null;
      state.user = null;
      state.status = 'idle';
    },
  },
  extraReducers: builder => {
    builder
      // LOGIN
      .addCase(loginWithTelegram.pending, state => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginWithTelegram.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.token = action.payload;
      })
      .addCase(loginWithTelegram.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })

      // FETCH USER
      .addCase(fetchCurrentUser.pending, state => {
        state.error = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.token = null
        state.user = null
        state.error = action.payload;

      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;
