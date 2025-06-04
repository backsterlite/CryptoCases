import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useCaseDetail } from './useCaseDetail';
import Spinner from '../../common/components/Spinner';
import DetailsAccordion from './components/DetailsAccordion';
import SpinArea from    './components/SpinArea';
import RewardsList from './components/RewardsList';

export default function CaseDetailPage() {
  const { caseId } = useParams();
  const {
    detail,
    clientSeed,
    commitData,
    spinResult,
    precheckStatus,
    commitStatus,
    openStatus,
    revealStatus,
    handlePlay,
    handleVerify,
    handleReset
  } = useCaseDetail(caseId);

  const [showPrizeModal, setShowPrizeModal] = useState(false);

  // Show win modal when spinResult arrives
  useEffect(() => {
    if (spinResult) {
      setShowPrizeModal(true);
    }
  }, [spinResult]);

  if (!detail) return <Spinner />;

  return (
    <div className="p-4 space-y-6">
      {/* Prize modal */}
      {showPrizeModal && spinResult && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white text-black p-6 rounded shadow-lg">
            <h2 className="text-xl font-bold mb-4">Congratulations!</h2>
            <p>{spinResult.prize.reward_tier}</p>
            <p>Coin: {spinResult.prize.coin_amount[0]}</p>
            <p>Network: {spinResult.prize.coin_amount[1]}</p>
            <p>Amount: {spinResult.prize.coin_amount[2]}</p>
            <p>Value (USD): ${parseFloat(spinResult.prize.usd_value).toFixed(4)}</p>
            <div className="mt-4 flex space-x-2">
              <button
                className="px-4 py-2 text-white bg-gray-300 rounded"
                onClick={() => setShowPrizeModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <SpinArea
        price={detail.price_usd}
        onPlay={handlePlay}
        disabled={
          Boolean(spinResult) ||
          precheckStatus === 'loading' ||
          commitStatus === 'loading' ||
          openStatus === 'loading'
        }
      />

      {commitData && (
        <DetailsAccordion title="Provably Fair">
          <div className="text-black">
            <div><strong>Server Seed Hash:</strong> {commitData.hash}</div>
            <div><strong>Client Seed:</strong> {clientSeed}</div>
            <div><strong>Nonce:</strong> {detail.nonce}</div>
            {revealStatus === 'loading' && <div>Revealing...</div>}
            {spinResult && (
              <>
                <div><strong>Server Seed:</strong> {spinResult.server_seed}</div>
                <div><strong>Table id:</strong> {spinResult.table_id}</div>
                <div><strong>Odds version:</strong> {spinResult.odds_version}</div>
              </>  
            )}
          </div>
          
        </DetailsAccordion>
      )}

       {spinResult && (
        <div className="space-x-2">
          <button onClick={handleVerify} disabled={revealStatus !== 'succeeded'}>
            Verify
          </button>
          <button onClick={handleReset}>New Draw</button>
        </div>
      )}

      <RewardsList tiers={detail.tiers} />
    </div>
  );
}