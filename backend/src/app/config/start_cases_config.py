
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
                        "sub_chance": 1/6
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
                        "sub_chance": 1/6
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
                            "network": "DOGECOIN",
                            "amount": 1
                        },
                        "sub_chance": 1/6
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
                        "sub_chance": 1/6
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "the-open-network",
                                "symbol": "ton",
                                "name": "The Open Network",
                                "decimal_places": [
                                    {"network": "TON", "decimals": 9}
                                ],
                                "networks": ["TON"]
                            },
                            "network": "TON",
                            "amount": 1
                        },
                        "sub_chance": 1/6
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
                            "network": "ZILLIQA",
                            "amount": 1
                        },
                        "sub_chance": 1/6
                    },
                ]
            },
            {
                "name": "rare",
                "chance": 0.35,
                "rewards": [
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "matic-network",
                                "symbol": "matic",
                                "name": "Polygon",
                                "decimal_places": [
                                    {"network": "MATIC", "decimals": 18}
                                ],
                                "networks": ["MATIC"]
                            },
                            "network": "MATIC",
                            "amount": 1
                        },
                        "sub_chance": 1/4
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "algorand",
                                "symbol": "algo",
                                "name": "Algorand",
                                "decimal_places": [
                                    {"network": "ALGO", "decimals": 6}
                                ],
                                "networks": ["ALGO"]
                            },
                            "network": "ALGO",
                            "amount": 1
                        },
                        "sub_chance": 1/4
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
                        "sub_chance": 1/4
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "harmony",
                                "symbol": "one",
                                "name": "Harmony",
                                "decimal_places": [
                                    {"network": "ONE", "decimals": 18}
                                ],
                                "networks": ["ONE"]
                            },
                            "network": "ONE",
                            "amount": 1
                        },
                        "sub_chance": 1/4
                    },
                ]
            },
            {
                "name": "epic",
                "chance": 0.15,
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
                        "sub_chance": 1/3
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "near",
                                "symbol": "near",
                                "name": "NEAR Protocol",
                                "decimal_places": [
                                    {"network": "NEAR", "decimals": 24}
                                ],
                                "networks": ["NEAR"]
                            },
                            "network": "NEAR",
                            "amount": 1
                        },
                        "sub_chance": 1/3
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
                        "sub_chance": 1/3
                    },
                ]
            },
            {
                "name": "legendary",
                "chance": 0.15,
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
                            "amount": 1
                        },
                        "sub_chance": 1/3
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "injective-protocol",
                                "symbol": "inj",
                                "name": "Injective Protocol",
                                "decimal_places": [
                                    {"network": "INJ", "decimals": 18}
                                ],
                                "networks": ["INJ"]
                            },
                            "network": "INJ",
                            "amount": 1
                        },
                        "sub_chance": 1/3
                    },
                    {
                        "coin_amount": {
                            "coin": {
                                "id": "mask-network",
                                "symbol": "mask",
                                "name": "Mask Network",
                                "decimal_places": [
                                    {"network": "MASK", "decimals": 18}
                                ],
                                "networks": ["MASK"]
                            },
                            "network": "MASK",
                            "amount": 1
                        },
                        "sub_chance": 1/3
                    },
                ]
            },
        ],
        "pity_after": None,
        "pity_bonus_tier": None,
        "global_pool_usd": 100,
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
            "chance": 0.74,
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
                    "sub_chance": round(20.00/ (20+18+15+13+8),4)  # example calc
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "cardano",
                            "symbol": "ada",
                            "name": "Cardano",
                            "networks": ["CARDANO"],
                            "decimal_places": [
                                {"network":"CARDANO","decimals":6}
                            ]
                        },
                        "network": "CARDANO",
                        "amount": 1
                    },
                    "sub_chance": round(18.00/ (20+18+15+13+8),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "tron",
                            "symbol": "trx",
                            "name": "TRON",
                            "networks": ["TRON"],
                            "decimal_places": [
                                {"network":"TRON","decimals":6}
                            ]
                        },
                        "network": "TRON",
                        "amount": 1
                    },
                    "sub_chance": round(15.00/ (20+18+15+13+8),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "stellar",
                            "symbol": "xlm",
                            "name": "Stellar",
                            "networks": ["STELLAR"],
                            "decimal_places": [
                                {"network":"STELLAR","decimals":7}
                            ]
                        },
                        "network": "STELLAR",
                        "amount": 1
                    },
                    "sub_chance": round(13.00/ (20+18+15+13+8),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "vechain",
                            "symbol": "vet",
                            "name": "VeChain",
                            "networks": ["VECHAIN"],
                            "decimal_places": [
                                {"network":"VECHAIN","decimals":0}
                            ]
                        },
                        "network": "VECHAIN",
                        "amount": 1
                    },
                    "sub_chance": round(8.00/ (20+18+15+13+8),4)
                }
            ]
        },
        {
            "name": "rare",
            "chance": 0.14,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "ripple",
                            "symbol": "xrp",
                            "name": "XRP",
                            "networks": ["XRP"],
                            "decimal_places": [
                                {"network":"XRP","decimals":6}
                            ]
                        },
                        "network": "XRP",
                        "amount": 1
                    },
                    "sub_chance": round(5.00/ (5+4+2.5+2.5),4)
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
                    "sub_chance": round(4.00/ (5+4+2.5+2.5),4)
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
                    "sub_chance": round(2.5/ (5+4+2.5+2.5),4)
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
                    "sub_chance": round(2.5/ (5+4+2.5+2.5),4)
                }
            ]
        },
        {
            "name": "epic",
            "chance": 0.11,
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
                    "sub_chance": round(4.00/ (4+3.5+3.5),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "avalanche-2",
                            "symbol": "avax",
                            "name": "Avalanche",
                            "networks": ["AVALANCHE"],
                            "decimal_places": [
                                {"network":"AVALANCHE","decimals":18}
                            ]
                        },
                        "network": "AVALANCHE",
                        "amount": 1
                    },
                    "sub_chance": round(3.5/ (4+3.5+3.5),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "hyperliquid",
                            "symbol": "hype",
                            "name": "Hyperliquid",
                            "networks": ["HYPERLIQUID"],
                            "decimal_places": [
                                {"network":"HYPERLIQUID","decimals":18}
                            ]
                        },
                        "network": "HYPERLIQUID",
                        "amount": 1
                    },
                    "sub_chance": round(3.5/ (4+3.5+3.5),4)
                }
            ]
        },
        {
            "name": "legendary",
            "chance": 0.01,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "litecoin",
                            "symbol": "ltc",
                            "name": "Litecoin",
                            "networks": ["LTC"],
                            "decimal_places": [
                                {"network":"LTC","decimals":8}
                            ]
                        },
                        "network": "LTC",
                        "amount": 1
                    },
                    "sub_chance": 0.5
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
                        "amount": 1
                    },
                    "sub_chance": 0.5
                }
            ]
        }
    ],
    "pity_after": None,
    "pity_bonus_tier": None,
    "global_pool_usd": 100,
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
            "chance": 0.75,
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
                    "sub_chance": round(20.00/(20+18+15+13+8),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "ripple",
                            "symbol": "xrp",
                            "name": "XRP",
                            "networks": ["XRP"],
                            "decimal_places": [
                                {"network":"XRP","decimals":6}
                            ]
                        },
                        "network": "XRP",
                        "amount": 1
                    },
                    "sub_chance": round(18.00/(20+18+15+13+8),4)
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
                    "sub_chance": round(15.00/(20+18+15+13+8),4)
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
                    "sub_chance": round(13.00/(20+18+15+13+8),4)
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "polkadot",
                            "symbol": "dot",
                            "name": "Polkadot",
                            "networks": ["DOT"],
                            "decimal_places": [
                                {"network":"DOT","decimals":10}
                            ]
                        },
                        "network": "DOT",
                        "amount": 1
                    },
                    "sub_chance": round(8.00/(20+18+15+13+8),4)
                }
            ]
        },
        {
            "name": "rare",
            "chance": 0.15,
            "rewards": [
                {
                    "coin_amount": {
                        "coin": {
                            "id": "injective-protocol",
                            "symbol": "inj",
                            "name": "Injective Protocol",
                            "networks": ["INJ"],
                            "decimal_places": [
                                {"network":"INJ","decimals":18}
                            ]
                        },
                        "network": "INJ",
                        "amount": 1
                    },
                    "sub_chance": round(5.00/(5+4+3),4)
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
                    "sub_chance": round(4.00/(5+4+3),4)
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
                    "sub_chance": round(3.00/(5+4+3),4)
                }
            ]
        },
        {
            "name": "epic",
            "chance": 0.09,
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
                            "networks": ["LTC"],
                            "decimal_places": [
                                {"network":"LTC","decimals":8}
                            ]
                        },
                        "network": "LTC",
                        "amount": 1
                    },
                    "sub_chance": 0.5
                }
            ]
        },
        {
            "name": "legendary",
            "chance": 0.01,
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
                        "amount": 1
                    },
                    "sub_chance": 0.5
                },
                {
                    "coin_amount": {
                        "coin": {
                            "id": "ethereum",
                            "symbol": "eth",
                            "name": "Ethereum",
                            "networks": ["ERC20"],
                            "decimal_places": [
                                {"network":"ERC20","decimals":18}
                            ]
                        },
                        "network": "ERC20",
                        "amount": 0.01
                    },
                    "sub_chance": 0.5
                }
            ]
        }
    ],
    "pity_after": None,
    "pity_bonus_tier": None,
    "global_pool_usd": 200,
    "pool_reset_interval": "24h",
    "ev_target": 0.5
}

]