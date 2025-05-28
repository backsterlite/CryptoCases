
export const convertRewardChance = (rewardChance, tierChance) => {
    return (parseFloat(rewardChance) * parseFloat(tierChance) * 100).toFixed(2)
}

