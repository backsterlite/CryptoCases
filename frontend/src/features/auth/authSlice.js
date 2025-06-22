// frontend/src/features/auth/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';
import { showSessionExpiredModal } from '../../common/slices/uiSlice';
import TelegramWebAppPromise from '../../mocks/WebAppTG';

// Глобальні змінні для контролю станів (поза Redux)
let isCurrentlyRefreshing = false;
let isCurrentlyLoggingIn = false;
let refreshAttempts = 0;
let loginAttempts = 0;

const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000;

// Утиліта для затримки
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Утиліта для скидання глобальних флагів
const resetGlobalFlags = () => {
  isCurrentlyRefreshing = false;
  isCurrentlyLoggingIn = false;
  refreshAttempts = 0;
  loginAttempts = 0;
};

export const refreshAccessToken = createAsyncThunk(
  'auth/refresh',
  async (_, { getState, rejectWithValue }) => {
    try {
      // Перевіряємо глобальний флаг замість Redux state
      if (isCurrentlyRefreshing) {
        return rejectWithValue('Refresh already in progress');
      }
      
      const { refreshToken } = getState().auth;
      
      if (!refreshToken) {
        return rejectWithValue('No refresh token available');
      }

      // Перевіряємо кількість спроб
      if (refreshAttempts >= MAX_RETRY_ATTEMPTS) {
        refreshAttempts = 0;
        return rejectWithValue('Max refresh attempts exceeded');
      }

      // Встановлюємо глобальний флаг
      isCurrentlyRefreshing = true;
      refreshAttempts++;
      
      console.log(`Refreshing token (attempt ${refreshAttempts}/${MAX_RETRY_ATTEMPTS})`);
      
      const res = await api.auth.refresh({ refresh_token: refreshToken });
      
      // Скидаємо лічильник при успіху
      refreshAttempts = 0;
      
      return res.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      
      // При помилці 401 скидаємо лічильник
      if (err.response?.status === 401) {
        refreshAttempts = 0;
      }
      
      return rejectWithValue(errorMessage);
    } finally {
      // Завжди скидаємо флаг
      isCurrentlyRefreshing = false;
    }
  }
);

export const loginWithTelegram = createAsyncThunk(
  'auth/login',
  async (_, { rejectWithValue }) => {
    try {
      // Перевіряємо глобальний флаг замість Redux state
      if (isCurrentlyLoggingIn) {
        console.warn('Login already in progress, skipping...');
        return rejectWithValue('Login already in progress');
      }

      // Перевіряємо кількість спроб
      if (loginAttempts >= MAX_RETRY_ATTEMPTS) {
        loginAttempts = 0;
        return rejectWithValue('Max login attempts exceeded. Please try again later.');
      }

      // Встановлюємо глобальний флаг
      isCurrentlyLoggingIn = true;
      loginAttempts++;
      
      console.log(`Attempting Telegram login (attempt ${loginAttempts}/${MAX_RETRY_ATTEMPTS})`);

      const WebApp = await TelegramWebAppPromise;
      const initData = WebApp.initData;

      if (!initData) {
        throw new Error('No Telegram WebApp data available');
      }

      const res = await api.auth.telegram(initData);
      
      // Скидаємо лічильник при успіху
      loginAttempts = 0;
      
      return res.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      
      // При критичних помилках скидаємо лічильник
      if (err.response?.status === 400 || err.response?.status === 403) {
        loginAttempts = 0;
      }
      
      return rejectWithValue(errorMessage);
    } finally {
      // Завжди скидаємо флаг
      isCurrentlyLoggingIn = false;
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { getState, rejectWithValue, dispatch }) => {
    try {
      const { accessToken } = getState().auth;
      
      if (!accessToken) {
        return rejectWithValue('No access token available');
      }

      const res = await api.users.me();
      return res.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      
      // При 401 показуємо модальне вікно, але НЕ запускаємо автоматичне оновлення
      if (err.response?.status === 401) {
        dispatch(showSessionExpiredModal());
      }
      
      return rejectWithValue(errorMessage);
    }
  }
);

// Новий thunk для ручного перезапуску авторизації
export const retryLogin = createAsyncThunk(
  'auth/retryLogin',
  async (_, { dispatch, rejectWithValue }) => {
    try {
      // Скидаємо всі глобальні флаги та лічильники
      resetGlobalFlags();
      
      // Очікуємо трохи перед повторною спробою
      await delay(RETRY_DELAY);
      
      const result = await dispatch(loginWithTelegram()).unwrap();
      return result;
    } catch (err) {
      return rejectWithValue(err);
    }
  }
);

// Утиліта для безпечного виклику loginWithTelegram
export const safeLoginWithTelegram = createAsyncThunk(
  'auth/safeLogin',
  async (_, { dispatch, rejectWithValue }) => {
    // Перевіряємо глобальні флаги перед викликом
    if (isCurrentlyLoggingIn || isCurrentlyRefreshing) {
      console.warn('Auth operation already in progress, skipping safe login');
      return rejectWithValue('Auth operation already in progress');
    }
    
    try {
      const result = await dispatch(loginWithTelegram()).unwrap();
      return result;
    } catch (err) {
      return rejectWithValue(err);
    }
  }
);

const initialState = {
  accessToken: null,
  refreshToken: null,
  user: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
  // Redux state флаги тепер тільки для UI
  isRefreshingUI: false,
  isLoggingInUI: false,
  lastLoginAttempt: null,
  canRetryLogin: true,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.user = null;
      state.status = 'idle';
      state.error = null;
      state.isRefreshingUI = false;
      state.isLoggingInUI = false;
      state.canRetryLogin = true;
      
      // Скидаємо глобальні флаги
      resetGlobalFlags();
    },
    clearError(state) {
      state.error = null;
    },
    setCanRetryLogin(state, action) {
      state.canRetryLogin = action.payload;
    },
    resetLoginAttempts(state) {
      state.canRetryLogin = true;
      state.lastLoginAttempt = null;
      // Скидаємо глобальні лічильники
      resetGlobalFlags();
    },
    // Новий reducer для ручного скидання флагів у екстрених випадках
    forceResetFlags(state) {
      state.isRefreshingUI = false;
      state.isLoggingInUI = false;
      resetGlobalFlags();
    }
  },
  extraReducers: builder => {
    builder
      // LOGIN WITH TELEGRAM
      .addCase(loginWithTelegram.pending, state => {
        state.status = 'loading';
        state.isLoggingInUI = true; // Тільки для UI
        state.error = null;
        state.lastLoginAttempt = Date.now();
      })
      .addCase(loginWithTelegram.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.isLoggingInUI = false;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.error = null;
        state.canRetryLogin = true;
      })
      .addCase(loginWithTelegram.rejected, (state, action) => {
        state.status = 'failed';
        state.isLoggingInUI = false;
        state.error = action.payload;
        
        // Блокуємо повторні спроби на деякий час при досягненні максимуму
        if (loginAttempts >= MAX_RETRY_ATTEMPTS) {
          state.canRetryLogin = false;
          // Автоматично розблокуємо через 30 секунд
          setTimeout(() => {
            resetGlobalFlags();
          }, 30000);
        }
      })
      
      // REFRESH ACCESS TOKEN
      .addCase(refreshAccessToken.pending, state => {
        state.isRefreshingUI = true;
        state.error = null;
      })
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.isRefreshingUI = false;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.error = null;
        
        // Якщо статус був failed, змінюємо на succeeded
        if (state.status === 'failed') {
          state.status = 'succeeded';
        }
      })
      .addCase(refreshAccessToken.rejected, (state, action) => {
        state.isRefreshingUI = false;
        state.error = action.payload;
        
        // При невдачі refresh НЕ очищаємо токени автоматично
        if (refreshAttempts >= MAX_RETRY_ATTEMPTS) {
          state.accessToken = null;
          state.refreshToken = null;
          state.user = null;
          state.status = 'failed';
        }
      })
      
      // FETCH CURRENT USER
      .addCase(fetchCurrentUser.pending, state => {
        state.error = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
        if (state.status !== 'succeeded') {
          state.status = 'succeeded';
        }
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.error = action.payload;
      })
      
      // RETRY LOGIN
      .addCase(retryLogin.pending, state => {
        state.status = 'loading';
        state.error = null;
        state.isLoggingInUI = true;
      })
      .addCase(retryLogin.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.canRetryLogin = true;
        state.isLoggingInUI = false;
      })
      .addCase(retryLogin.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.isLoggingInUI = false;
      })
      
      // SAFE LOGIN
      .addCase(safeLoginWithTelegram.pending, state => {
        state.status = 'loading';
        state.isLoggingInUI = true;
        state.error = null;
      })
      .addCase(safeLoginWithTelegram.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isLoggingInUI = false;
        state.error = null;
      })
      .addCase(safeLoginWithTelegram.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.isLoggingInUI = false;
      });
  },
});

export const { 
  logout, 
  clearError, 
  setCanRetryLogin, 
  resetLoginAttempts,
  forceResetFlags 
} = authSlice.actions;

export default authSlice.reducer;