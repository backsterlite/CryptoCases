// Файл: webAppInit.js
let WebApp;

const initializeWebApp = async () => {
  if (import.meta.env.PROD) {
    const module = await import('@twa-dev/sdk');
    WebApp = module.WebApp;
  } else {
    const { initTelegramStub } = await import('./telegramWebApp.stub');
    initTelegramStub();
    WebApp = window.Telegram.WebApp;
  }
  return WebApp;
};

// Експортуємо проміс, який резолвиться до WebApp
export default initializeWebApp();