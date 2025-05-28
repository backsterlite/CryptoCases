import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchCaseDetail,
  precheckCase,
  commitCase,
  openCaseDetail,
  revealCaseDetail,
  deleteServerSeed,
  resetCaseDetail
} from './caseDetailSlice';

export function useCaseDetail(caseId) {
  const dispatch = useDispatch();
  const state = useSelector(s => s.caseDetail);
  const {
    detail,
    clientSeed,
    commitData,
    spinResult,
    precheckStatus,
    commitStatus,
    openStatus,
    revealStatus
  } = state;

  useEffect( () => {
    dispatch(resetCaseDetail())
    dispatch(fetchCaseDetail(caseId));
  }, [dispatch, caseId]);


  useEffect(() => {
    if(commitData === null) {
      const prepareSpin = async () => {
      const pre = await dispatch(precheckCase(caseId)).unwrap();
      if (!pre.spin) return alert(`Blocked: ${pre.reason}`);

      await dispatch(commitCase()).unwrap();

      dispatch(fetchCaseDetail(caseId));
    }
    prepareSpin()
    }
  }, [dispatch, caseId, commitData])
  const handlePlay = async () => {
    const open = await dispatch(
      openCaseDetail({
        caseId,
        clientSeed,
        nonce: detail.nonce + 1,
        serverSeedId: commitData?.server_seed_id
      })
    ).unwrap();

    // await dispatch(revealCaseDetail(open.spin_log_id)).unwrap();
  };

  const handleVerify = () => {
    // local HMAC check could go here
  };

  const handleReset = () => {
    dispatch(resetCaseDetail());
  };

  return {
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
  };
}