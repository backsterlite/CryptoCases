import React from 'react';
import RewardCard from './RewardCard';

/**
 * List of reward tiers, highlights selected tier
 */
export default function RewardsList({ tiers }) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {tiers.map(tier => (
        tier.rewards.map( reward => (
          <RewardCard
          key={reward.coin_id}
          reward={reward}
          tier_chance={tier.chance}
          tierName={tier.name}
        />
        ))
      ))}
    </div>
  );
}