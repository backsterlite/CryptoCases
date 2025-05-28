import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchCases } from './casesSlice';
import CaseCard from './components/CaseCard';
import Spinner from '../../common/components/Spinner';
import InsufficientFundsModal from './components/InsufficientFundsModal';

export default function GamePage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { items: cases, loading, error } = useSelector(state => state.cases);
  const balance = useSelector(state => state.balance.amount);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    dispatch(fetchCases());
  }, [dispatch]);

  const handleCardClick = (caseInfo) => {
    if (Number(balance) < Number(caseInfo.price_usd)) {
      setShowModal(true);
    } else {
      navigate(`/play/${caseInfo.case_id}`);
    }
  };

  if (loading) return <Spinner />;
  if (error)   return <div className="p-4 text-red-500">Error loading cases: {error}</div>;

  return (
    <>
      <div className="grid grid-cols-2 gap-4 p-4">
        {cases.map(c => (
          <CaseCard
            key={c.case_id}
            caseInfo={c}
            onClick={() => handleCardClick(c)}
          />
        ))}
      </div>
      {showModal && (
        <InsufficientFundsModal onClose={() => setShowModal(false)} />
      )}
    </>
  );
}
