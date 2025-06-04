import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TablePagination,
    CircularProgress,
    Alert,
    Typography,
    Box,
    Button,
    Chip
} from '@mui/material';
import { fetchWithdrawHistory } from './historySlice';

const WithdrawHistoryPage = () => {
    const dispatch = useDispatch();
    const { withdrawals, loading, error } = useSelector(state => state.history);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    useEffect(() => {
        dispatch(fetchWithdrawHistory({ limit: rowsPerPage, offset: page * rowsPerPage }));
    }, [dispatch, page, rowsPerPage]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert 
                severity="error" 
                sx={{ mt: 2 }}
                action={
                    <Button 
                        color="inherit" 
                        size="small"
                        onClick={() => dispatch(fetchWithdrawHistory({ limit: rowsPerPage, offset: page * rowsPerPage }))}
                    >
                        Retry
                    </Button>
                }
            >
                {error.message || 'Failed to load withdrawal history'}
            </Alert>
        );
    }

    // Перевіряємо структуру даних
    const withdrawalsList = withdrawals?.withdrawals || [];

    if (!withdrawalsList.length) {
        return (
            <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                justifyContent="center" 
                minHeight="200px"
                p={3}
            >
                <Typography variant="h6" color="textSecondary" gutterBottom>
                    No withdrawals found
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Your withdrawal history will appear here
                </Typography>
            </Box>
        );
    }

    return (
        <Paper>
            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Date</TableCell>
                            <TableCell>To Address</TableCell>
                            <TableCell>Amount</TableCell>
                            <TableCell>Fee</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Confirmations</TableCell>
                            <TableCell>Transaction Hash</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {withdrawalsList.map((withdrawal) => (
                            <TableRow key={withdrawal.id}>
                                <TableCell>{new Date(withdrawal.created_at).toLocaleString()}</TableCell>
                                <TableCell>{withdrawal.to_address.slice(0, 10)}...</TableCell>
                                <TableCell>{withdrawal.amount_coin}</TableCell>
                                <TableCell>{withdrawal.fee_coin}</TableCell>
                                <TableCell>
                                    <Chip 
                                        label={withdrawal.status}
                                        color={
                                            withdrawal.status === 'confirmed' ? 'success' :
                                            withdrawal.status === 'pending' ? 'warning' :
                                            withdrawal.status === 'failed' ? 'error' : 'default'
                                        }
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>{withdrawal.confirmations}</TableCell>
                                <TableCell>
                                    {withdrawal.tx_hash ? (
                                        <a 
                                            href={`https://etherscan.io/tx/${withdrawal.tx_hash}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {withdrawal.tx_hash.slice(0, 10)}...
                                        </a>
                                    ) : (
                                        <Typography variant="body2" color="textSecondary">
                                            Pending
                                        </Typography>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                rowsPerPageOptions={[5, 10, 25]}
                component="div"
                count={-1}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
            />
        </Paper>
    );
};

export default WithdrawHistoryPage;
