#!/usr/bin/env python3
"""
merge_policy.py
===============
Merge deposit/withdrawal allow-lists from `data/policy_tokens.json` into
`data/chain_registry.json`.

For each network code present in the policy file, this script will set
(or overwrite) the following fields in the chain registry entry:
  - `deposit_tokens`   (list of canonical coin IDs)
  - `withdrawal_tokens` (list of canonical coin IDs)

Existing entries for these fields will be replaced entirely by policy.

Usage:
    python scripts/merge_policy.py \
        --policy data/policy_tokens.json \
        --registry data/chain_registry.json \
        --output data/chain_registry.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_POLICY = BASE_DIR / "data" / "policy_tokens.json"
DEFAULT_REGISTRY = BASE_DIR / "data" / "chain_registry.json"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("merge_policy")

# ---------------------------------------------------------------------------
# JSON utilities
# ---------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    if not path.exists():
        log.error("File not found: %s", path)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.error("Failed to load JSON from %s: %s", path, exc)
        sys.exit(1)


def save_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def merge_policy(
    registry: Dict[str, Any],
    policy: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge policy into registry entries and return the updated registry."""
    for network, rules in policy.items():
        entry = registry.get(network)
        if entry is None:
            log.warning("Policy specified for unknown network '%s'", network)
            continue
        # Overwrite deposit/withdrawal lists
        if 'deposit' in rules:
            entry['deposit_tokens'] = rules.get('deposit', [])
        if 'withdraw' in rules:
            entry['withdrawal_tokens'] = rules.get('withdraw', [])
        log.info(
            "Updated policy for %s: deposit=%s, withdraw=%s",
            network,
            entry.get('deposit_tokens'),
            entry.get('withdrawal_tokens')
        )
    return registry

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Merge policy_tokens into chain_registry")
    parser.add_argument(
        "--policy", type=Path, default=DEFAULT_POLICY,
        help="Path to policy_tokens.json"
    )
    parser.add_argument(
        "--registry", type=Path, default=DEFAULT_REGISTRY,
        help="Path to existing chain_registry.json"
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_REGISTRY,
        help="Output path for updated chain_registry.json"
    )
    args = parser.parse_args()

    policy = load_json(args.policy)
    registry = load_json(args.registry)

    updated = merge_policy(registry, policy)
    save_json(updated, args.output)
    log.info("Merged policy into %s", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
