export function initTelegramStub() {
  window.Telegram = {
    WebApp: {
      initData: 'query_id=a2aa0745dc905a45504b216e875e3aeddb67c5d5&user={"id": 123456789, "first_name": "Ivan", "last_name": "Yarmoliuk", "username": "backster", "language_code": "en"}&auth_date=1749220143&hash=74655423b2732d89f33d1a06e89cd309709dd4fde9965db3fb24dada5ba01209',
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