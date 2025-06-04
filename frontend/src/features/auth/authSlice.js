// src/features/auth/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';
import { showSessionExpiredModal } from '../../common/slices/uiSlice'; // action to show modal
import TelegramWebAppPromise from '../../mocks/WebAppTG';

const initialState = {
  accessToken: null,
  refreshToken: null,
  user: null,
  status: 'idle', // 'loading' | 'succeeded' | 'failed'
  error: null,
};

export const refreshAccessToken = createAsyncThunk(
  'auth/refresh',
  async (_, { getState, rejectWithValue, dispatch }) => {
    try {
      const { refreshToken } = getState().auth;
      // Якщо refreshToken зберігається в Redux
      if (!refreshToken) {
        return rejectWithValue('No refresh token');
      }
      // Запит на бекенд:
      const res = await api.auth.refresh({ refresh_token: refreshToken });
      // Очікуємо, що бек поверне { access_token: '...', refresh_token: '...' }
      return res.data;
    } catch (err) {
      // якщо бек видав 401 або іншу помилку, кидаємо reject
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

export const loginWithTelegram = createAsyncThunk(
  'auth/login',
  async (_, { rejectWithValue }) => {
    try {
      const WebApp = await TelegramWebAppPromise;
      const initData = WebApp.initData;
      const res = await api.auth.telegram(initData);
      return res.data;
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
      state.accessToken = null;
      state.refreshToken = null;
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
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token

      })
      .addCase(loginWithTelegram.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      .addCase(refreshAccessToken.pending, state => {
        // можемо ставити окремий статус, але для простоти залишимо існуючий
      })
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        // Якщо бек повернув нові токени:
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
      })
      .addCase(refreshAccessToken.rejected, (state, action) => {
        // якщо не вдалось оновити — логаут
        state.accessToken = null;
        state.refreshToken = null;
        state.user = null;
        state.status = 'idle';
        state.error = 'SessionExpired';
      })
      // FETCH USER
      .addCase(fetchCurrentUser.pending, state => {
        state.error = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        // state.token = null
        // state.user = null
        state.error = action.payload;

      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;
