---
name: roblox-route
description: "Explains how Roblox Apex would route a given task, covering the classification, which specialist skills it would load and in what order, which mandatory bundles fire, which skills it deliberately skips, and why. The task itself is not executed."
argument-hint: "<task description>"
disable-model-invocation: true
---

# /roblox-route: routing inspection (dry run)

Task: $ARGUMENTS

Read the routing table and mandatory bundles in `${CLAUDE_SKILL_DIR}/../roblox/SKILL.md` (sections 1–2). **Don't load the specialist skills and don't perform the task.** Then output:

```
TASK: <task>
Classification: type=<…> size=<trivial|standard|system|ambitious>
Route: roblox → <skill> → <skill> → …   (primary first)
Why:
  <skill>: <signal in the task that matched / bundle that fired>
Bundles fired: <names or none>
Considered but skipped:
  <skill>: <why it is not needed for this task>
Context cost: <n> specialist skills (budget for this size: <…>)
Risks the route guards against: <one line each>
```

If the task is ambiguous, show the route for the most likely reading and note which detail would change it. If the routing table seems to miss something important for this task, say so explicitly. That is useful feedback for improving the router.
