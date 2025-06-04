import client from "../app/api/client"


const api = {
  auth: {
    telegram: (initData) => client.post('/auth/telegram', { init_data: initData }),
    refresh: () => client.post('/auth/refresh'),
  },
  users: {
    me: () => client.get('/users/me'),
  },
  balance: {
    usd: () => client.get('/balance/usd'),
  },
  cases: {
    precheck: (caseId) => client.get('/cases/precheck', { params: { case_id: caseId } }),
    open: (caseId, clientSeed, nonce, serverSeedId) =>
      client.post('/cases/open', { case_id: caseId, client_seed: clientSeed, nonce, server_seed_id: serverSeedId }),
    list: () => client.get('/cases/list'),
    getDetail: (caseId) => client.get('cases/get_one', {params: {case_id: caseId}})
  },
  fairness: {
    odds: (caseId, version) => client.get(`/fairness/odds/${caseId}/${version}`),
    commit: () => client.post('/fairness/commit'),
    reveal: (spinLogId) => client.get(`/fairness/reveal/${spinLogId}`),
  },
  rates: {
    list: () => client.get('/rates'),
    getOne: (symbol) => client.get(`/rates/${symbol}`),
  },
  withdrawals: {
    open: (symbol, network, amount, toAddress) =>
      client.post('/withdraw/', { token: symbol, network, amount, to_address: toAddress }),
  },
  history: {
    spins: () => client.get('/history/spins'),
    deposits: () => client.get('/history/deposits'),
    withdrawals: () => client.get('/history/withdrawals'),
  },
  wallet: {
    all: () =>
      client.get('/wallet/all'),
    quote:     (payload) => client.post('/wallet/swap/quote', payload),
    execute:   (payload) => client.post('/wallet/swap/execute', payload),
    deposit:   (token, network, amount) => client.post('/wallet/deposit', { token, network, amount }),
    connect:   () => client.post('/wallet/connect')
  },
  dev: {
    genToken: (telegramId, botToken) =>
      client.get('/dev/gen_token', { params: { telegram_id: telegramId, bot_token: botToken } }),
    createUser: (userCreateDto) =>
      client.post('/dev/user/create', userCreateDto),
  },
};

export default api;