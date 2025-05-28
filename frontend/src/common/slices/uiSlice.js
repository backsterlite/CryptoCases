import { createSlice } from '@reduxjs/toolkit';

/**
 * UI slice for controlling global UI state (e.g. session‐expiry modal)
 */
const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    sessionExpiredModalVisible: false,
  },
  reducers: {
    showSessionExpiredModal(state) {
      state.sessionExpiredModalVisible = true;
    },
    hideSessionExpiredModal(state) {
      state.sessionExpiredModalVisible = false;
    },
  },
});

export const { showSessionExpiredModal, hideSessionExpiredModal } = uiSlice.actions;
export default uiSlice.reducer;
