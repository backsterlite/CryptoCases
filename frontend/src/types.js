

/**
 * @typedef {Object} Reward
 * @property {string} coin_id
 * @property {string} amount
 * @property {string} network
 */

/**
 * @typedef {Object} Tier
 * @property {string} name
 * @property {string} chance
 * @property {Reward[]} rewards
 */

/**
 * @typedef {Object} Case
 * @property {string} case_id
 * @property {string} price_usd
 * @property {Tier[]} tiers
 * @property {number} pity_after
 * @property {string} pity_bonus_tier
 * @property {string} global_pool_usd
 * @property {string} ev_target
 */


export {};