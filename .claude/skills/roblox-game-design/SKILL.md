---
name: roblox-game-design
description: "Use when inventing, evaluating or improving a Roblox game concept, mechanic, progression, economy or reward system, or when asking whether something is fun. Covers core fantasy, loops, pacing, social systems, onboarding, failure and recovery, anti-slop challenges to genre-default mechanics, and evidence-driven iteration."
---

# Roblox game design

Design serves an **intended player experience**. Every system must answer *what does the player feel or decide here, and why does this system belong in this game?*

## 1. Anchor before designing
Get or infer these, and ask only if they're genuinely missing and they matter:
- **Core fantasy**, in player language: "I'm a lone night-shift guard and something is learning my routine."
- **Pillars**: 2–4 experience qualities every feature must serve (e.g. *dread through anticipation*, *improvised cooperation*).
- **Core loop** at three scales: moment-to-moment (seconds), session (minutes), long-term (days).
- **Audience and context**: Roblox players skew young and mobile-heavy and often play with friends. Sessions are short and the first minute is brutal. Treat these as E3 platform tendencies and let the project's own analytics override them.

## 2. Evaluate a mechanic (use the relevant lines)
- **Decision:** what interesting choice does the player make? If there's none, it's a chore or a cutscene. Is that intended?
- **Feedback:** can the player perceive the result and its cause within about a second?
- **Fantasy fit:** does it express the core fantasy, or is it imported from another genre?
- **Mastery:** is there a skill or knowledge curve, or does it saturate on the first try?
- **Social:** does it create stories between players (cooperation, rivalry, spectacle, trading, showing off)?
- **Cost:** build cost, performance cost, cognitive load for a new player.
- **Failure:** what does failure feel like? Is it informative and recoverable, and does it invite a retry?

## 3. Progression and rewards
- Progression should change **what the player can do or understand**, not just numbers. A pure +X% stat ladder is the weakest form.
- Pace with novelty: introduce a new verb, space, threat or social situation on a cadence. Grind length should be a deliberate choice, not filler.
- Rewards: use a mix of predictable (goal clarity) and variable (surprise). Variable rewards mustn't become paid gambling (`PolicyService` and paid-random-item rules) or manipulative.
- **Economy:** list every source and sink. Each currency needs a distinct purpose. Model inflation over 30 days of play: what does a day-30 player do with their wealth? A currency with no meaningful sink is decoration. Details are in `references/economy.md`. For what to sell, game passes vs dev products vs subscriptions, analytics events and live tuning with `ConfigService`, read `references/monetization-liveops.md`.

## 4. Onboarding (the first 60 seconds decide retention)
The player should **act within seconds and understand the goal through play**. Teach by doing, with one new concept at a time. Remove menus before first fun. Mobile-first readability. Look for the first moment of the core fantasy and how fast the player gets there.

## 5. Anti-slop gate (always on, for what *you* propose)
Before **you propose** **pets, eggs, rebirths, generic coins or gems, rarity tiers, daily rewards, battle passes, generic shops, idle multipliers or copycat simulator progression**, run `references/anti-slop.md`. Verdicts are **justified** (state why), **transform** (make it specific to this fantasy) or **remove**. Common mechanics aren't banned.
**When the user explicitly asks for one** (or `.apex/decisions.md` records it), build it, and build it well. Make it fit the fantasy, give its economy real sinks, and keep it policy-compliant (paid random items → `PolicyService`). Raise at most **one** brief transform suggestion, and don't re-litigate it later.

## 6. Preserve ambition
If the user's idea is unusual, protect what makes it unusual. Don't steer it toward the nearest popular genre template. If something is hard to build, route to `roblox-boundary-breaker` rather than redesigning it into something easier.

## 7. "Is it fun?": evidence, not scores
Never output fake fun scores. Reason with **hypotheses**: name the expected experience, the mechanism, what you'd observe if it works, and how it could fail. Use the iteration loop in `references/experiments.md` (OBSERVE → PROBLEM → HYPOTHESIS → CHANGE → TEST → COMPARE → KEEP/REVERT → RECORD). Player-motivation reasoning lives in `references/player-model.md`: those are behavioral hypotheses, not validated psychology. **Real player behavior beats every model, including yours.**

## Output shape for design proposals
Fantasy and pillar served → mechanic → the player's decision → feedback → how it fails and recovers → why it belongs (the anti-slop answer) → **how we'd know it works** (what to observe in a playtest; never skip this line, even when asked to be brief) → risks and open questions. Keep it tight and skip the other lines that don't apply.
