// Файл: webAppInit.js
import WebApp from '@twa-dev/sdk';

let ComputedWebApp;

const initializeWebApp = async () => {
  
   if (WebApp.initData) {
    ComputedWebApp = WebApp
   }else {
    const { initTelegramStub } = await import('./telegramWebApp.stub');
    initTelegramStub();
    ComputedWebApp = window.Telegram.WebApp;
   }
  
    
  
  return ComputedWebApp;
};

// Експортуємо проміс, який резолвиться до WebApp
export default initializeWebApp();