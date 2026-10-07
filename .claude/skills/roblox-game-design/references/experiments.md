# Iteration and experiments

## Loop
OBSERVE → IDENTIFY PROBLEM → FORM HYPOTHESIS → CHANGE → TEST → COMPARE → KEEP / REVERT → RECORD EVIDENCE

## Write the hypothesis *before* changing anything
```
Observation: players quit around 90 s (source: funnel step 3, n=…; or "3 of 5 playtesters")
Hypothesis: the objective is unclear after the intro cutscene
Mechanism: no on-screen goal, and the first prompt is out of view
Prediction if true: an explicit goal marker raises step-3 completion; playtesters stop asking "what do I do?"
Prediction if false: no change in step-3 completion, so look at reward delay or difficulty next
Change: add a diegetic goal cue (one variable only)
Test: A/B (Experiments/Configs if available) or before/after with the same playtest script
Keep if: step-3 completion improves and session length doesn't drop
```

## Differential diagnosis for "players leave / it's boring"
List the competing explanations: unclear goal, weak first reward, low agency, too much complexity, no novelty, poor feedback, technical friction (lag, load time), wrong audience. For each, name the evidence that would distinguish it, and test the cheapest discriminator first.

## Rules
- Change **one** thing per comparison when you can. Note confounds when you can't.
- Use live tuning (`ConfigService` or attribute-driven config) so variants don't need code forks. Use Roblox Experiments for real A/B where available.
- Watch for novelty effects in UI and feel changes, and run past them.
- Record results in `.apex/decisions.md` (or an `experiments` section): hypothesis, change, result, evidence level, decision. Failed experiments are valuable and go in the record too.
- Small samples (5 playtesters) give **qualitative** signal only. Say so.
