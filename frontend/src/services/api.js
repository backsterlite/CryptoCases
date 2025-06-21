import client from '../app/api/client';



const api = {
  auth: {
    telegram: (initData) =>
      client.post('/auth/telegram', { init_data: initData }),
    refresh: (payload) =>
      client.post('/auth/refresh', payload),
  },
  users: {
    me: () => client.get('/users/me'),
  },
  balance: {
    usd: () => client.get('/balance/usd'),
  },
  cases: {
    precheck: (caseId) =>
      client.get('/cases/precheck', { params: { case_id: caseId } }),
    open: (
      caseId,
      clientSeed,
      nonce,
      serverSeedId
    ) =>
      client.post('/cases/open', {
        case_id: caseId,
        client_seed: clientSeed,
        nonce,
        server_seed_id: serverSeedId,
      }),
    list: () => client.get('/cases/list'),
    getDetail: (caseId) =>
      client.get('cases/get_one', { params: { case_id: caseId } }),
  },
  fairness: {
    commit: () => client.post('fairness/commit')
  },
  wallet: {
    all: () => client.get('/wallet/all'),
    quote: (payload) =>
      client.post('/wallet/swap/quote', payload),
    execute: (payload) =>
      client.post('/wallet/swap/execute', payload),
    deposit: (token, network, amount) =>
      client.post('/wallet/deposit', { token, network, amount }),
    connect: () => client.post('/wallet/connect'),
  },
  deposits: {
    requestAddress: (data) =>
      client.post('/deposits/address', data),
    initiate: (data) =>
      client.post('/deposits/initiate', data),
    getManualAddress: (network) =>
      client.get(`/deposits/address?network=${network}`),
  },
  withdrawals: {
    getAddresses: () =>
      client.get('/withdrawals/addresses'),
    saveAddress: (address, network) =>
      client.post('/withdrawals/addresses', { address, network }),
    getBalance: (network, token) =>
      client.get(`/balance?network=${network}&token=${token}`),
    initiate: (payload) =>
      client.post('/withdrawals/initiate', payload),
  },
};

export default api;
