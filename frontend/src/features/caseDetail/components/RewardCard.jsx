import React from 'react';
import { convertRewardChance } from '../../../common/utils/rewardChancePercent';

/**
 * Single reward tier card
 */
export default function RewardCard({ reward, tier_chance, tierName }) {
  console.log(`reward sub_chance: ${reward.sub_chance} tier chance: ${tier_chance}`)
  return (
    <div
      className={`border p-4 rounded-lg`}
    >
      <div className="font-semibold">{tierName}</div>
      <div className="font-semibold">{reward.coin_id}</div>
      <div className="font-semibold"> Network: {reward.network}</div>
      <div className="font-semibold">Amount: {reward.amount}</div>
      <div className="font-semibold">Win chance: {convertRewardChance(reward.sub_chance, tier_chance)}%</div>
    </div>
  );
}
