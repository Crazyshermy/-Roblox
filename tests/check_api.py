#!/usr/bin/env python3
"""Hallucination guard: verify every `Class.Member` / `Class:Method()` / `Enum.X.Y` mentioned in the
skills exists in the official Roblox engine API reference (Roblox/creator-docs YAML).

Usage:
  git clone --depth 1 --filter=blob:none --sparse https://github.com/Roblox/creator-docs.git /tmp/cd
  git -C /tmp/cd sparse-checkout set content/en-us/reference/engine
  python3 tests/check_api.py /tmp/cd
Also reports members marked deprecated in the reference.
"""
import os, re, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
REF = os.path.join(sys.argv[1], "content", "en-us", "reference", "engine")
SKILLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude", "skills")

classes, members, deprecated, enums = set(), {}, set(), {}
for kind in ("classes", "datatypes", "libraries", "globals"):
    d = os.path.join(REF, kind)
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if not f.endswith(".yaml"):
            continue
        cname = f[:-5]
        classes.add(cname)
        text = open(os.path.join(d, f), encoding="utf-8").read()
        names = re.findall(r"^\s*- name: ([\w.:]+)\s*$", text, re.M)
        members.setdefault(cname, set()).update(n.split(".")[-1].split(":")[-1] for n in names)
        for block in re.split(r"\n\s*- name: ", text):
            head = block.splitlines()[0].strip() if block else ""
            if re.search(r"^\s*deprecation_message: '?[^'\n]", block, re.M) and head:
                deprecated.add(head)
        if re.search(r"^deprecation_message: '?[^'\n]", text, re.M):
            deprecated.add(cname)
edir = os.path.join(REF, "enums")
if os.path.isdir(edir):
    for f in os.listdir(edir):
        text = open(os.path.join(edir, f), encoding="utf-8").read()
        enums[f[:-5]] = set(re.findall(r"^\s*- name: ([\w]+)\s*$", text, re.M))

refs = {}
for root, _, files in os.walk(SKILLS):
    for f in files:
        if f.endswith(".md"):
            text = open(os.path.join(root, f), encoding="utf-8").read()
            for m in re.finditer(r"\b(Enum\.\w+\.\w+|[A-Z]\w+[.:][A-Z]\w+)\b", text):
                refs.setdefault(m.group(1), set()).add(os.path.relpath(os.path.join(root, f), SKILLS))

# Known non-engine paths used in examples, and deliberate "X is deprecated" warnings.
ALLOW_MISSING = {"ReplicatedStorage.Remotes", "ReplicatedStorage.Shared"}
ALLOW_DEPRECATED = {"Lighting.Technology"}

bad, dep, unknown_class = [], [], []
for ref, where in sorted(refs.items()):
    if ref.startswith("Enum."):
        _, en, item = ref.split(".")
        if en in enums and item not in enums[en]:
            bad.append((ref, where))
        elif en not in enums:
            unknown_class.append((ref, where))
        continue
    cls, mem = re.split(r"[.:]", ref)
    if cls not in classes:
        unknown_class.append((ref, where))  # often a project module name; reported, not failed
        continue
    if ref in ALLOW_MISSING:
        continue
    if mem not in members.get(cls, set()):
        # members can be inherited; accept if any class defines it
        if not any(mem in s for s in members.values()):
            bad.append((ref, where))
    if (f"{cls}.{mem}" in deprecated or f"{cls}:{mem}" in deprecated) and ref not in ALLOW_DEPRECATED:
        dep.append((ref, where))

# Second pass: bare backticked API-looking identifiers, e.g. `SetNetworkOwner` or `GetPartBoundsInBox()`.
known = set(classes) | set(enums) | {m for s in members.values() for m in s} | {i for s in enums.values() for i in s}
NOT_API = {"ProfileStore", "ProfileService", "Knit", "Matter", "Fusion", "TestEZ", "Jest", "Lune", "Rojo", "StyLua",
           "DataStoreWrapper", "SessionLockedDataStoreWrapper", "Simulation", "ServerLoader", "ClientLoader", "Catalog",
           "Inventory", "ShopService", "Remotes", "Shared", "Config", "PurchaseGranted", "NotProcessedYet", "PurchaseId",
           "RenderStepped", "TeleportInitFailed", "Hit", "Persistent", "Atomic", "Experimental", "Default", "Future",
           "Deferred", "Server", "Client", "Edit", "Legacy", "Box", "Hull", "PreciseConvexDecomposition", "Automatic",
           "HumanoidRootPart",  # instance name
           "ArePaidRandomItemsRestricted"}  # key in PolicyService:GetPolicyInfoForPlayerAsync() result (verified in PolicyService.yaml)
bare = {}
for root, _, files in os.walk(SKILLS):
    for f in files:
        if f.endswith(".md"):
            for m in re.finditer(r"`([A-Z][A-Za-z0-9]{3,})(?:\(\))?`", open(os.path.join(root, f), encoding="utf-8").read()):
                bare.setdefault(m.group(1), set()).add(os.path.relpath(os.path.join(root, f), SKILLS))
unverified = sorted((n, w) for n, w in bare.items() if n not in known and n not in NOT_API)

print(f"checked {len(refs)} qualified + {len(bare)} bare identifiers;  against {len(classes)} classes/datatypes")
for r, w in bad:
    print(f"MISSING    {r:45} in {', '.join(sorted(w))}")
for r, w in dep:
    print(f"DEPRECATED {r:45} in {', '.join(sorted(w))}")
for r, w in unverified:
    print(f"UNVERIFIED {r:45} in {', '.join(sorted(w))}")
for r, w in unknown_class:
    print(f"not-engine {r:45} in {', '.join(sorted(w))}")
sys.exit(1 if bad or dep or unverified else 0)
