#!/usr/bin/env python3
"""Static validation of the Roblox Apex skill set. No network, no model calls.

Checks: frontmatter parses; name == directory; description present and <= 1536 chars
(Claude Code listing limit); router references only existing skills and every
model-invocable specialist is routable; referenced reference files exist; SKILL.md size;
total always-loaded description budget.
Exit code 1 on any error.
"""
import os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude", "skills")
errors, warnings = [], []


def frontmatter(text: str) -> dict:
    """Parse with a real YAML parser: invalid YAML makes Claude Code load the skill with EMPTY
    metadata (no description => no auto-routing), so this must be strict."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    try:
        import yaml
        data = yaml.safe_load(text[4:end])
        return {k: (v if isinstance(v, (dict, list)) else str(v)) for k, v in (data or {}).items()}
    except ImportError:
        pass
    except Exception as e:  # yaml.YAMLError
        errors.append(f"invalid YAML frontmatter: {str(e).splitlines()[0]}")
        return {}
    fm, out, key = text[4:end], {}, None
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            out[key] = val.strip('"')
        elif key and line.startswith("  "):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


skills = {}
for d in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, d, "SKILL.md")
    if not d.startswith("roblox") or not os.path.isfile(p):
        continue
    raw = open(p, "rb").read()
    if b"\r\n" in raw:
        errors.append(f"{d}: CRLF line endings (breaks frontmatter parsing on some setups; see .gitattributes)")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    fm = frontmatter(text)
    skills[d] = (fm, text)
    if not fm:
        errors.append(f"{d}: missing/invalid frontmatter")
        continue
    if fm.get("name") != d:
        errors.append(f"{d}: name '{fm.get('name')}' != directory")
    desc = fm.get("description", "")
    if not desc:
        errors.append(f"{d}: missing description")
    if len(desc) > 1536:
        errors.append(f"{d}: description {len(desc)} chars > 1536")
    lines = text.count("\n")
    if lines > 500:
        errors.append(f"{d}: SKILL.md {lines} lines > 500")
    elif lines > 160:
        warnings.append(f"{d}: SKILL.md {lines} lines (keep specialists lean)")
    for ref in re.findall(r"`(references/[\w./-]+\.md)`", text):
        if not os.path.isfile(os.path.join(ROOT, d, ref)):
            errors.append(f"{d}: referenced file missing: {ref}")
    for ref in re.findall(r"`roblox/(references/[\w./-]+\.md)`", text):
        if not os.path.isfile(os.path.join(ROOT, "roblox", ref)):
            errors.append(f"{d}: referenced router file missing: roblox/{ref}")
    for other in set(re.findall(r"`(roblox-[a-z-]+)`", text)):
        if other not in os.listdir(ROOT):
            errors.append(f"{d}: mentions unknown skill `{other}`")

user_only = {d for d, (fm, _) in skills.items() if fm.get("disable-model-invocation", "").lower() in ("true", "yes", "on", "1")}
model_inv = set(skills) - user_only
router_text = skills.get("roblox", ({}, ""))[1]
routed = set(re.findall(r"`(roblox-[a-z-]+)`", router_text))
for s in sorted(model_inv - {"roblox"} - routed):
    errors.append(f"router: specialist `{s}` is never routed to")

budget = sum(len(skills[s][0].get("description", "")) for s in model_inv)
print(f"skills: {len(skills)} total, {len(model_inv)} model-invocable, user-only: {sorted(user_only)}")
print(f"always-loaded description budget: {budget} chars (~{budget // 4} tokens)")
if budget > 8000:
    warnings.append(f"description budget {budget} chars is high; tighten descriptions")
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print("OK" if not errors else f"{len(errors)} error(s)")
sys.exit(1 if errors else 0)
