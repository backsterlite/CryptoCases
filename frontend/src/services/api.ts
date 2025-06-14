import client from '../app/api/client';

export interface SwapQuotePayload {
  from_token: string;
  to_token: string;
  from_amount: number;
  from_network: string;
  to_network: string;
}

export interface SwapQuoteResponse {
  amount: string;
  rate: string;
}

type ApiResponse<T> = Promise<{ data: T }>;

const api = {
  auth: {
    telegram: (initData: string): ApiResponse<void> =>
      client.post('/auth/telegram', { init_data: initData }),
    refresh: (payload: unknown): ApiResponse<void> =>
      client.post('/auth/refresh', payload),
  },
  users: {
    me: (): ApiResponse<{ id: string }> => client.get('/users/me'),
  },
  balance: {
    usd: (): ApiResponse<{ amount: number }> => client.get('/balance/usd'),
  },
  cases: {
    precheck: (caseId: string): ApiResponse<unknown> =>
      client.get('/cases/precheck', { params: { case_id: caseId } }),
    open: (
      caseId: string,
      clientSeed: string,
      nonce: number,
      serverSeedId: string
    ): ApiResponse<unknown> =>
      client.post('/cases/open', {
        case_id: caseId,
        client_seed: clientSeed,
        nonce,
        server_seed_id: serverSeedId,
      }),
    list: (): ApiResponse<unknown[]> => client.get('/cases/list'),
    getDetail: (caseId: string): ApiResponse<unknown> =>
      client.get('cases/get_one', { params: { case_id: caseId } }),
  },
  wallet: {
    all: (): ApiResponse<unknown> => client.get('/wallet/all'),
    quote: (payload: SwapQuotePayload): ApiResponse<SwapQuoteResponse> =>
      client.post('/wallet/swap/quote', payload),
    execute: (payload: unknown): ApiResponse<unknown> =>
      client.post('/wallet/swap/execute', payload),
    deposit: (token: string, network: string, amount: number): ApiResponse<void> =>
      client.post('/wallet/deposit', { token, network, amount }),
    connect: (): ApiResponse<unknown> => client.post('/wallet/connect'),
  },
};

export default api;
