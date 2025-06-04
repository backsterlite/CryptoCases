import { useState } from 'react';
import { Tabs, Tab, Box } from '@mui/material';
import CaseOpensHistoryPage from './CaseOpensHistoryPage';
import DepositHistoryPage from './DepositHistoryPage';
import WithdrawHistoryPage from './WithdrawHistoryPage';

const HistoryPage = () => {
    const [activeTab, setActiveTab] = useState(0);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={activeTab} onChange={handleTabChange}>
                    <Tab label="Case Opens" />
                    <Tab label="Deposits" />
                    <Tab label="Withdrawals" />
                </Tabs>
            </Box>
            <Box sx={{ p: 3 }}>
                {activeTab === 0 && <CaseOpensHistoryPage />}
                {activeTab === 1 && <DepositHistoryPage />}
                {activeTab === 2 && <WithdrawHistoryPage />}
            </Box>
        </Box>
    );
};

export default HistoryPage;