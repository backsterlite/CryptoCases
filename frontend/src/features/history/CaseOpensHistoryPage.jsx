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
import { fetchCaseOpensHistory } from './historySlice';

const CaseOpensHistoryPage = () => {
    const dispatch = useDispatch();
    const { opens, loading, error } = useSelector(state => state.history);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    useEffect(() => {
        dispatch(fetchCaseOpensHistory({ limit: rowsPerPage, offset: page * rowsPerPage }));
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
                        onClick={() => dispatch(fetchCaseOpensHistory({ limit: rowsPerPage, offset: page * rowsPerPage }))}
                    >
                        Retry
                    </Button>
                }
            >
                {error.message || 'Failed to load case opens history'}
            </Alert>
        );
    }

    // Перевіряємо структуру даних
    const opensList = opens?.spins || [];

    if (!opensList.length) {
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
                    No case opens found
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Your case opens history will appear here
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
                            <TableCell>Case</TableCell>
                            <TableCell>Stake</TableCell>
                            <TableCell>Payout</TableCell>
                            <TableCell>Payout (USD)</TableCell>
                            <TableCell>Prize</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {opensList.map((spin) => (
                            <TableRow key={spin.id}>
                                <TableCell>{new Date(spin.created_at).toLocaleString()}</TableCell>
                                <TableCell>{spin.case_id}</TableCell>
                                <TableCell>{spin.stake}</TableCell>
                                <TableCell>{spin.payout}</TableCell>
                                <TableCell>{spin.payout_usd}</TableCell>
                                <TableCell>
                                    {spin.prize_id ? (
                                        <Chip 
                                            label={spin.prize_id}
                                            color="primary"
                                            size="small"
                                        />
                                    ) : (
                                        <Typography variant="body2" color="textSecondary">
                                            No prize
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

export default CaseOpensHistoryPage;