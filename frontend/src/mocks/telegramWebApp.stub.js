/**
 * Stub Telegram WebApp SDK for local development.
 * Provides a fake initData so auth flow can proceed without real Telegram.
 */
export function initTelegramStub() {
  window.Telegram = {
    WebApp: {
      initData: 'stub_user_id=123456&auth_date=1700000000&hash=abcdef1234567890',
      ready: () => console.log('Telegram WebApp stub ready'),
      expand: () => console.log('Telegram WebApp stub expand'),
      close: () => console.log('Telegram WebApp stub close'),
      user: { id: 123456, first_name: 'Dev', is_bot: false },
    },
  };
}
