---
name: roblox-review
description: "Structured, evidence-based critique of Roblox code or designs after significant work: correctness, security, data safety, multiplayer edge cases, performance, maintainability, design quality, genericness, feel, over- or under-engineering. Use for review, audit, or before calling major work done."
---

# Roblox review

Be the skeptical senior reviewer, not the author defending the work. Find real problems, rank them, and back each with evidence.

## Procedure
1. **Restate the intent** in one line: what player experience or behavior was this supposed to deliver? Check `.apex/project.md` and `.apex/decisions.md` if present, so that you review against *this project's* decisions.
2. **Inspect, don't assume.** Read the actual code and its callers (`script_grep`/Grep for writers of the same state, remotes, DataStore calls). If Studio is connected, check runtime state and console output.
3. **Pass through the lenses that apply**:

| Lens | Key questions |
|---|---|
| Correctness | Does it do what was intended in all paths? Nil and edge cases? Lifecycle (join, leave, respawn, shutdown)? |
| Security | Any client→server input trusted? Value writers outside the owner module? Yield inside check→write? Rate limits? (`roblox-security`) |
| Data | Can it lose or duplicate data? Session lock? Save before load? Migration? (`roblox-data`) |
| Multiplayer | Two players at once? Late join? High latency? Streaming? |
| Performance | Per-frame work, polling loops, leaks, unbounded growth, network spam? Measured or assumed? |
| Maintainability | One owner per state? Clear module boundaries? Consistent with project conventions? Dead code? |
| Design | Does it serve the fantasy and pillars? Is there a real player decision? Is anything generic or imported without reason (anti-slop)? |
| Experience | Will a new player understand it? Is the feedback clear? Does it *feel* good (`roblox-game-feel` channels)? Mobile? |
| Proportionality | Over-engineered for the stakes? Or oversimplified, with the requested ambition quietly reduced? |
| Evidence | Which important claims were verified (E5/E4), and which are assumptions? |

4. **Report**, most severe first:
```
[BLOCKER|MAJOR|MINOR|NIT] <title>
  Where: <file:line or system>
  Problem: <what is wrong and the concrete failure scenario>
  Evidence: <code reference / runtime observation / doc>  (or: "theoretical")
  Fix direction: <specific>
```
Then: **What's good** (brief, only real strengths), **Unverified assumptions** (and how to verify them), and **Verdict**: ship / fix blockers first / rethink.

## Rules
- No numeric quality scores. No vague advice ("consider adding error handling"); name the failure.
- A finding without evidence is labeled *theoretical* and can't be a BLOCKER unless the exploit or failure is obvious from the code.
- Don't pad. If it's good, say so in two lines.
- Judge against the project's phase: a prototype isn't faulted for polish, but it is faulted for security holes that would ship.
