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
import { fetchDepositHistory } from './historySlice';

const DepositHistoryPage = () => {
    const dispatch = useDispatch();
    const { deposits, loading, error } = useSelector(state => state.history);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    useEffect(() => {
        dispatch(fetchDepositHistory({ limit: rowsPerPage, offset: page * rowsPerPage }));
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
                        onClick={() => dispatch(fetchDepositHistory({ limit: rowsPerPage, offset: page * rowsPerPage }))}
                    >
                        Retry
                    </Button>
                }
            >
                {error.message || 'Failed to load deposit history'}
            </Alert>
        );
    }

    // Перевіряємо структуру даних
    const depositsList = deposits?.deposits || [];

    if (!depositsList.length) {
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
                    No deposits found
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Your deposit history will appear here
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
                            <TableCell>Coin</TableCell>
                            <TableCell>Amount</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Confirmations</TableCell>
                            <TableCell>Transaction Hash</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {depositsList.map((deposit) => (
                            <TableRow key={deposit.id}>
                                <TableCell>{new Date(deposit.created_at).toLocaleString()}</TableCell>
                                <TableCell>{deposit.coin}</TableCell>
                                <TableCell>{deposit.amount}</TableCell>
                                <TableCell>
                                    <Chip 
                                        label={deposit.status}
                                        color={
                                            deposit.status === 'confirmed' ? 'success' :
                                            deposit.status === 'pending' ? 'warning' :
                                            deposit.status === 'failed' ? 'error' : 'default'
                                        }
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>{deposit.confirmations}</TableCell>
                                <TableCell>
                                    {deposit.tx_hash ? (
                                        <a 
                                            href={`https://etherscan.io/tx/${deposit.tx_hash}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {deposit.tx_hash.slice(0, 10)}...
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

export default DepositHistoryPage;