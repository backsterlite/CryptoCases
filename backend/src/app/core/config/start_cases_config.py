
START_CASES = [
    # ——— CASE 5 ———
    {
        "case_id": "case_5",
        "price_usd": "5.00",
        "tiers": [
            {
                "name": "common",
                "chance": 0.70,
                "rewards": [
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "shiba-inu",
                                "symbol": "shib",
                                "name": "Shiba Inu",
                                "decimal_places": [
                                    {"network": "ERC20", "decimals": 18}
                                ],
                                "networks": ["ERC20"]
                            },
                            "network": "ERC20",
                            "amount": 1
                        },
                        "sub_chance": 0.167
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "pepe",
                                "symbol": "pepe",
                                "name": "Pepe",
                                "decimal_places": [
                                    {"network": "ERC20", "decimals": 18},
                                    {"network": "BEP20", "decimals": 18},
                                    {"network": "ARB",   "decimals": 18}
                                ],
                                "networks": ["ERC20","BEP20","ARB"]
                            },
                            "network": "ERC20",
                            "amount": 1
                        },
                        "sub_chance": 0.166
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "dogecoin",
                                "symbol": "doge",
                                "name": "Dogecoin",
                                "decimal_places": [],
                                "networks": []
                            },
                            "network": "native",
                            "amount": 1
                        },
                        "sub_chance": 0.167
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "usd-coin",
                                "symbol": "usdc",
                                "name": "USD Coin",
                                "decimal_places": [
                                    {"network": "ERC20", "decimals": 6},
                                    {"network": "TRC20", "decimals": 6},
                                    {"network": "NEAR",  "decimals": 6},
                                    {"network": "APTOS", "decimals": 6},
                                    {"network": "ALGO",  "decimals": 6},
                                    {"network": "HBAR",  "decimals": 6},
                                    {"network": "XLM",   "decimals": 7}
                                ],
                                "networks": ["ERC20","TRC20","NEAR","APTOS","ALGO","HBAR","XLM"]
                            },
                            "network": "ERC20",
                            "amount": 1
                        },
                        "sub_chance": 0.166
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "the-open-network",
                                "symbol": "ton",
                                "name": "Toncoin",
                                "decimal_places": [
                                    {"network": "TON", "decimals": 9}
                                ],
                                "networks": ["TON"]
                            },
                            "network": "TON",
                            "amount": 1
                        },
                        "sub_chance": 0.167
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "zilliqa",
                                "symbol": "zil",
                                "name": "Zilliqa",
                                "decimal_places": [],
                                "networks": []
                            },
                            "network": "BEP20",
                            "amount": 1
                        },
                        "sub_chance": 0.167
                    },
                ]
            },
            {
                "name": "rare",
                "chance": 0.20,
                "rewards": [
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "matic-network",
                                "symbol": "matic",
                                "name": "Polygon",
                                "decimal_places": [
                                    {"network": "native", "decimals": 18}
                                ],
                                "networks": ["native"]
                            },
                            "network": "native",
                            "amount": 1
                        },
                        "sub_chance": 0.25
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "algorand",
                                "symbol": "algo",
                                "name": "Algorand",
                                "decimal_places": [
                                    {"network": "native", "decimals": 6}
                                ],
                                "networks": ["native"]
                            },
                            "network": "native",
                            "amount": 1
                        },
                        "sub_chance": 0.25
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "1inch",
                                "symbol": "1inch",
                                "name": "1inch",
                                "decimal_places": [],
                                "networks": []
                            },
                            "network": "ERC20",
                            "amount": 1
                        },
                        "sub_chance": 0.25
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "harmony",
                                "symbol": "one",
                                "name": "Harmony",
                                "decimal_places": [
                                    {"network": "native", "decimals": 18}
                                ],
                                "networks": ["native"]
                            },
                            "network": "native",
                            "amount": 1
                        },
                        "sub_chance": 0.25
                    },
                ]
            },
            {
                "name": "epic",
                "chance": 0.07,
                "rewards": [
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "arbitrum",
                                "symbol": "arb",
                                "name": "Arbitrum",
                                "decimal_places": [
                                    {"network": "ARB", "decimals": 18}
                                ],
                                "networks": ["ARB"]
                            },
                            "network": "ARB",
                            "amount": 1
                        },
                        "sub_chance": 0.33
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "near",
                                "symbol": "near",
                                "name": "NEAR Protocol",
                                "decimal_places": [
                                    {"network": "ERC20", "decimals": 24}
                                ],
                                "networks": ["ERC20"]
                            },
                            "network": "ERC20",
                            "amount": 1
                        },
                        "sub_chance": 0.33
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "internet-computer",
                                "symbol": "icp",
                                "name": "Internet Computer",
                                "decimal_places": [
                                    {"network": "ICP", "decimals": 8}
                                ],
                                "networks": ["ICP"]
                            },
                            "network": "ICP",
                            "amount": 1
                        },
                        "sub_chance": 0.34
                    },
                ]
            },
            {
                "name": "legendary",
                "chance": 0.03,
                "rewards": [
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "the-graph",
                                "symbol": "grt",
                                "name": "The Graph",
                                "decimal_places": [
                                    {"network": "ERC20", "decimals": 18}
                                ],
                                "networks": ["ERC20"]
                            },
                            "network": "ERC20",
                            "amount": 350
                        },
                        "sub_chance": 0.42
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "injective-protocol",
                                "symbol": "inj",
                                "name": "Injective Protocol",
                                "decimal_places": [
                                    {"network": "ERC20", "decimals": 18}
                                ],
                                "networks": ["ERC20"]
                            },
                            "network": "ERC20",
                            "amount": 3.53
                        },
                        "sub_chance": 0.16
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "mask-network",
                                "symbol": "mask",
                                "name": "Mask Network",
                                "decimal_places": [
                                    {"network": "POLYGON", "decimals": 18}
                                ],
                                "networks": ["POLYGON"]
                            },
                            "network": "POLYGON",
                            "amount": 23
                        },
                        "sub_chance": 0.42
                    },
                ]
            },
        ],
        "pity_after": 20,
        "pity_bonus_tier": "epic",
        "global_pool_usd": 3000,
        "pool_reset_interval": "34",
        "ev_target": 0.5
    },

    # ——— CASE 10 ———
    {
    "case_id": "case_10",
    "price_usd": "10.00",
    "tiers": [
        {
            "name": "common",
            "chance": 0.70,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "tether",
                            "symbol": "usdt",
                            "name": "Tether",
                            "networks": ["ERC20","TRC20","SOLANA","AVALANCHE","APTOS","NEAR","TON"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":6},
                                {"network":"TRC20","decimals":6},
                                {"network":"SOLANA","decimals":6},
                                {"network":"AVALANCHE","decimals":6},
                                {"network":"APTOS","decimals":6},
                                {"network":"NEAR","decimals":6},
                                {"network":"TON","decimals":9}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.20  # example calc
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "cardano",
                            "symbol": "ada",
                            "name": "Cardano",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":6}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "tron",
                            "symbol": "trx",
                            "name": "TRON",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":6}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "stellar",
                            "symbol": "xlm",
                            "name": "Stellar",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":7}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "vechain",
                            "symbol": "vet",
                            "name": "VeChain",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":18}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                }
            ]
        },
        {
            "name": "rare",
            "chance": 0.20,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "ripple",
                            "symbol": "xrp",
                            "name": "XRP",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":6}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.25
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "sui",
                            "symbol": "sui",
                            "name": "Sui",
                            "networks": ["SUI"],
                            "decimal_places": [
                                {"network":"SUI","decimals":9}
                            ]
                        },
                        "network": "SUI",
                        "amount": 1
                    },
                    "sub_chance": 0.25
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "aptos",
                            "symbol": "apt",
                            "name": "Aptos",
                            "networks": ["APTOS"],
                            "decimal_places": [
                                {"network":"APTOS","decimals":8}
                            ]
                        },
                        "network": "APTOS",
                        "amount": 1
                    },
                    "sub_chance": 0.25
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "cosmos",
                            "symbol": "atom",
                            "name": "Cosmos Hub",
                            "networks": ["COSMOS","OSMOSIS"],
                            "decimal_places": [
                                {"network":"COSMOS","decimals":6},
                                {"network":"OSMOSIS","decimals":6}
                            ]
                        },
                        "network": "COSMOS",
                        "amount": 1
                    },
                    "sub_chance": 0.25
                }
            ]
        },
        {
            "name": "epic",
            "chance": 0.07,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "chainlink",
                            "symbol": "link",
                            "name": "Chainlink",
                            "networks": ["ERC20","OP","NEAR","BASE","SPL","HT","XDAI","ONE","OSMO"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18},
                                {"network":"OP","decimals":18},
                                {"network":"NEAR","decimals":24},
                                {"network":"BASE","decimals":18},
                                {"network":"SPL","decimals":9},
                                {"network":"HT","decimals":18},
                                {"network":"XDAI","decimals":18},
                                {"network":"ONE","decimals":18},
                                {"network":"OSMO","decimals":6}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.33
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "avalanche-2",
                            "symbol": "avax",
                            "name": "Avalanche",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":18}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.33
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "hyperliquid",
                            "symbol": "hype",
                            "name": "Hyperliquid",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":18}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.33
                }
            ]
        },
        {
            "name": "legendary",
            "chance": 0.03,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "litecoin",
                            "symbol": "ltc",
                            "name": "Litecoin",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":8}
                            ]
                        },
                        "network": "native",
                        "amount":  0.738163
                    },
                    "sub_chance": 0.65
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "okb",
                            "symbol": "okb",
                            "name": "OKB",
                            "networks": ["ERC20","OKT"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18},
                                {"network":"OKT","decimals":18}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1.9
                    },
                    "sub_chance": 0.35
                }
            ]
        }
    ],
    "pity_after": 20,
    "pity_bonus_tier": "epic",
    "global_pool_usd": 6000,
    "pool_reset_interval": "24h",
    "ev_target": 0.5
},

    # ——— CASE 20 ———
    {
    "case_id": "case_20",
    "price_usd": "20.00",
    "tiers": [
        {
            "name": "common",
            "chance": 0.70,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "tether",
                            "symbol": "usdt",
                            "name": "Tether",
                            "networks": ["ERC20","TRC20","SOLANA","AVALANCHE","APTOS","NEAR","TON"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":6},
                                {"network":"TRC20","decimals":6},
                                {"network":"SOLANA","decimals":6},
                                {"network":"AVALANCHE","decimals":6},
                                {"network":"APTOS","decimals":6},
                                {"network":"NEAR","decimals":6},
                                {"network":"TON","decimals":9}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "ripple",
                            "symbol": "xrp",
                            "name": "XRP",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":6}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "sui",
                            "symbol": "sui",
                            "name": "Sui",
                            "networks": ["SUI"],
                            "decimal_places": [
                                {"network":"SUI","decimals":9}
                            ]
                        },
                        "network": "SUI",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "aptos",
                            "symbol": "apt",
                            "name": "Aptos",
                            "networks": ["APTOS"],
                            "decimal_places": [
                                {"network":"APTOS","decimals":8}
                            ]
                        },
                        "network": "APTOS",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "polkadot",
                            "symbol": "dot",
                            "name": "Polkadot",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":10}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.20
                }
            ]
        },
        {
            "name": "rare",
            "chance": 0.20,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "injective-protocol",
                            "symbol": "inj",
                            "name": "Injective Protocol",
                            "networks": ["ERC20"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.3333
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "chainlink",
                            "symbol": "link",
                            "name": "Chainlink",
                            "networks": ["ERC20","OP","NEAR","BASE","SPL","HT","XDAI","ONE","OSMO"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18},
                                {"network":"OP","decimals":18},
                                {"network":"NEAR","decimals":24},
                                {"network":"BASE","decimals":18},
                                {"network":"SPL","decimals":9},
                                {"network":"HT","decimals":18},
                                {"network":"XDAI","decimals":18},
                                {"network":"ONE","decimals":18},
                                {"network":"OSMO","decimals":6}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.3333
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "gate-token",
                            "symbol": "gt",
                            "name": "GateToken",
                            "networks": ["ERC20"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.3333
                }
            ]
        },
        {
            "name": "epic",
            "chance": 0.08,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "okb",
                            "symbol": "okb",
                            "name": "OKB",
                            "networks": ["ERC20","OKT"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18},
                                {"network":"OKT","decimals":18}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 1
                    },
                    "sub_chance": 0.5
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "litecoin",
                            "symbol": "ltc",
                            "name": "Litecoin",
                            "networks": ["native"],
                            "decimal_places": [
                                {"network":"native","decimals":8}
                            ]
                        },
                        "network": "native",
                        "amount": 1
                    },
                    "sub_chance": 0.5
                }
            ]
        },
        {
            "name": "legendary",
            "chance": 0.02,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "quant-network",
                            "symbol": "qnt",
                            "name": "Quant Network",
                            "networks": ["QNT"],
                            "decimal_places": [
                                {"network":"QNT","decimals":18}
                            ]
                        },
                        "network": "QNT",
                        "amount": 1.508
                    },
                    "sub_chance": 0.65
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "ethereum",
                            "symbol": "eth",
                            "name": "Ethereum",
                            "networks": ["ERC20"],
                            "decimal_places": [
                                {"network":"native","decimals":18}
                            ]
                        },
                        "network": "native",
                        "amount": 0.07752
                    },
                    "sub_chance": 0.35
                }
            ]
        }
    ],
    "pity_after": 20,
    "pity_bonus_tier": "epic",
    "global_pool_usd": 12000,
    "pool_reset_interval": "24h",
    "ev_target": 0.5
}

]