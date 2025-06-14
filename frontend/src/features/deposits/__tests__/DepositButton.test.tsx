import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DepositButton } from '../DepositButton';
import * as api from '../depositApi';
jest.mock('@tonconnect/ui-react', () => ({
  TonConnectButton: () => <button>connect</button>,
  useTonConnectUI: () => [ { sendTransaction: jest.fn().mockResolvedValue({ boc: 'tx' }) } ],
  useTonWallet: () => ({ account: { address: 'wallet' } })
}));

jest.mock('../depositApi');

const mockedApi = api as jest.Mocked<typeof api>;

describe('DepositButton', () => {
  beforeEach(() => {
    mockedApi.requestDepositAddress.mockResolvedValue({ data: { address: 'addr' } });
    mockedApi.initiateDeposit.mockResolvedValue({});
  });

  it('validates amount', async () => {
    render(<DepositButton network="test" />);
    const input = screen.getByRole('spinbutton');
    fireEvent.change(input, { target: { value: '1' } });
    fireEvent.submit(input.closest('form')!);
    await waitFor(() => expect(mockedApi.requestDepositAddress).toHaveBeenCalled());
  });
});
