#!/usr/bin/env python3
"""Unit tests for smoke.py marker regexes (free, no model calls). Each example is a real or
realistic answer line; several are past false positives that must stay non-matching."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smoke import CASES  # noqa: E402

C = {c["id"]: c for c in CASES}
EXAMPLES = [
    # (case, list-key, index, text, should_match)
    ("design-auto", "must_not", 0, "No coins, pets, rebirths, rarity or daily rewards. They would break the isolation fantasy.", False),
    ("design-auto", "must_not", 0, "**Anti-slop verdicts:** I'd **remove** pets, eggs, rebirth, daily rewards, and generic coins.", False),
    ("design-auto", "must_not", 0, "Add a rebirth system that resets progress for a multiplier.", True),
    ("design-auto", "must_not", 0, "We should implement a pet system with rarity tiers.", True),
    ("currency", "must_not", 0, "The old \"60 + players × 10\" figure is outdated.", False),
    ("currency", "must_not", 0, "Server default: 60 + players × 40 per minute.", False),
    ("currency", "must_not", 0, "The server budget is 60 + numPlayers × 10 per minute.", True),
    ("currency", "must", 1, "Experience: 300 + CCU × 40 per minute", True),
    ("ambition", "must_not", 0, "Yes, good plan.", True),
    ("ambition", "must_not", 0, "Before you downgrade it: the darkness can creep.", False),
    # past false negatives (correct answers that earlier markers missed)
    ("design-auto", "must", 0, "**Core idea:** Progression changes what you can understand and do on the island, not stat numbers.", True),
    ("design-auto", "must", 0, "Progress changes what the player understands and can do, not their stats.", True),
    ("ambition", "must", 1, "Not yet. Roblox can do this. **How the real version works**", True),
]

bad = 0
for cid, key, idx, text, expect in EXAMPLES:
    got = bool(re.search(C[cid][key][idx], text, re.M))
    if got != expect:
        bad += 1
        print(f"FAIL {cid}.{key}[{idx}] expected {expect}: {text}")
print(f"{len(EXAMPLES) - bad}/{len(EXAMPLES)} pattern checks pass")
sys.exit(1 if bad else 0)
