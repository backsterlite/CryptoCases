export function initTelegramStub() {
  window.Telegram = {
    WebApp: {
      initData: 'query_id=746dc4189c0bd518507e24f450fe052813d06688&user={"id": 123456789, "first_name": "Ivan", "last_name": "Yarmoliuk", "username": "backster", "language_code": "en"}&auth_date=1747858930&hash=f8855a0f69c572db7a59cfc3e0652c0e491b0794e8d6ee2c14dd1052f09c5006',
      initDataUnsafe: {
        user: { 
          id: 123456789, 
          first_name: 'Ivan',
          last_name: 'Yarmoliuk',
          username: 'backster',
          language_code: 'en',
          is_premium: true
        }
      },
      ready: () => console.log('[STUB] WebApp ready'),
      expand: () => console.log('[STUB] WebApp expanded'),
      close: () => console.log('[STUB] WebApp closed'),
      BackButton: {
        show: () => console.log('[STUB] BackButton shown'),
        hide: () => console.log('[STUB] BackButton hidden'),
        onClick: (cb) => console.log('[STUB] BackButton click handler set')
      },
      sendData: (data) => console.log('[STUB] Data sent:', data)
    }
  };
}