// src/features/rates/rateSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export const fetchRate = createAsyncThunk(
  'rates/fetchRate',
  async (symbol, { rejectWithValue }) => {
    try {
      const response = await api.rates.getOne(symbol)
      return { symbol, rate: response.data } // response.data – рядок з числом курсу
    } catch (err) {
      return rejectWithValue({ symbol, error: err.response?.data || err.message })
    }
  }
)

const initialState = {
  rates: {},          // { USDT: "1.0000", USDC: "1.0000", … }
  ratesLoading: false,
  ratesError: null
}

const rateSlice = createSlice({
  name: 'rates',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchRate.pending, (state) => {
        state.ratesLoading = true
        state.ratesError = null
      })
      .addCase(fetchRate.fulfilled, (state, action) => {
        state.ratesLoading = false
        state.rates[action.payload.symbol] = action.payload.rate
      })
      .addCase(fetchRate.rejected, (state, action) => {
        state.ratesLoading = false
        state.ratesError = action.payload.error
      })
  }
})

export default rateSlice.reducer
