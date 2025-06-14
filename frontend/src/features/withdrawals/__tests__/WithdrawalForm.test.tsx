import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WithdrawalForm } from '../WithdrawalForm';
import * as api from '../withdrawalApi';

jest.mock('../withdrawalApi');

const mockedApi = api as jest.Mocked<typeof api>;

describe('WithdrawalForm', () => {
  beforeEach(() => {
    mockedApi.getSavedAddresses.mockResolvedValue({ data: [] });
    mockedApi.fetchBalance.mockResolvedValue({ data: { amount: 10 } });
    mockedApi.saveAddress.mockResolvedValue({ data: [] });
    mockedApi.initiateWithdrawal.mockResolvedValue({});
  });

  it('prevents withdrawal over balance', async () => {
    render(<WithdrawalForm network="net" token="T" />);
    await waitFor(() => expect(mockedApi.getSavedAddresses).toHaveBeenCalled());
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '20' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => expect(mockedApi.initiateWithdrawal).not.toHaveBeenCalled());
  });
});
