#!/usr/bin/env python3
"""Baseline Claude vs Claude + Roblox Apex on representative Roblox tasks.

For each task: run the same plain prompt (no /roblox prefix: Apex must auto-route) in a
temp project WITHOUT the skills (baseline) and WITH them (apex). A separate judge session
compares the two answers blind (random A/B order) against the task rubric.

Usage: python3 benchmarks/run.py [--model sonnet] [--judge-model opus] [--only B01,B03] [--jobs 6]
Output: benchmarks/results/<timestamp>/{<task>.<mode>.json, <task>.judge.json, summary.md}

Not a scientific evaluation: one sample per arm, an LLM judge, and rubrics written by the
same authors as the skills. Its purpose is regression detection and a sanity check that the
skills change behavior in the intended direction.
"""
import argparse, concurrent.futures as cf, datetime, json, os, random, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tests"))
from run_case import run  # noqa: E402

JUDGE_PROMPT = """You are an expert Roblox engineer and game designer grading two answers to the same task.
You do not know which system produced which answer. Grade strictly; length is not quality.
Your Roblox knowledge may be older than the answers (Roblox changes often). Flag a claim as
incorrect_or_stale only if you are confident it is wrong, not merely because it is unfamiliar.

TASK:
{task}

RUBRIC (expert expectations):
{rubric}

ANSWER A:
<<<
{a}
>>>

ANSWER B:
<<<
{b}
>>>

For each rubric item, mark each answer "met", "partial" or "missed". Also flag, per answer:
- incorrect_or_stale: technically wrong, invented or outdated Roblox claims (list them, [] if none)
- slop: generic, unjustified genre-default mechanics or generic advice (list, [] if none)
- overengineering: unnecessary complexity for the task (list, [] if none)
Then give an overall preference: "A", "B" or "tie", with a one-sentence reason.

Reply with ONLY a JSON object:
{{"items":[{{"item":"...","A":"met|partial|missed","B":"met|partial|missed"}}],
 "A_flags":{{"incorrect_or_stale":[],"slop":[],"overengineering":[]}},
 "B_flags":{{"incorrect_or_stale":[],"slop":[],"overengineering":[]}},
 "preference":"A|B|tie","reason":"..."}}"""

PTS = {"met": 1.0, "partial": 0.5, "missed": 0.0}


def judge(task, ans_base, ans_apex, model):
    flip = random.random() < 0.5
    a, b = (ans_apex, ans_base) if flip else (ans_base, ans_apex)
    prompt = JUDGE_PROMPT.format(task=task["prompt"], rubric="\n".join(f"- {r}" for r in task["rubric"]), a=a, b=b)
    d = tempfile.mkdtemp(prefix="apex-judge-")  # empty dir: judge sees no skills
    p = subprocess.run(["claude", "-p", prompt, "--model", model, "--output-format", "json",
                        "--max-turns", "1", "--disallowedTools", "Bash Edit Write Read Glob Grep Skill WebFetch WebSearch Agent"],
                       cwd=d, capture_output=True, text=True, timeout=600)
    out = json.loads(p.stdout)
    txt = out.get("result", "")
    j, _ = json.JSONDecoder().raw_decode(txt[txt.index("{"):])  # tolerate trailing text
    apex_key, base_key = ("A", "B") if flip else ("B", "A")
    score = lambda k: sum(PTS.get(i.get(k, "missed"), 0) for i in j["items"]) / max(1, len(j["items"]))
    pref = j.get("preference", "tie")
    return {"apex_label": apex_key, "raw": j, "judge_cost": out.get("total_cost_usd"),
            "apex_score": round(score(apex_key), 3), "base_score": round(score(base_key), 3),
            "winner": "apex" if pref == apex_key else "baseline" if pref == base_key else "tie",
            "apex_flags": j.get(f"{apex_key}_flags", {}), "base_flags": j.get(f"{base_key}_flags", {}),
            "reason": j.get("reason", "")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--judge-model", default="opus")
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    tasks = json.load(open(os.path.join(HERE, "tasks.json")))
    if a.only:
        tasks = [t for t in tasks if any(t["id"].startswith(x) for x in a.only.split(","))]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(HERE, "results", stamp)
    os.makedirs(out, exist_ok=True)
    runs = {}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(run, t["prompt"], mode, a.model, None, 12, 900): (t["id"], mode) for t in tasks for mode in ("baseline", "apex")}
        for f in cf.as_completed(futs):
            k = futs[f]
            runs[k] = f.result()
            json.dump(runs[k], open(os.path.join(out, f"{k[0]}.{k[1]}.json"), "w"), indent=2)
            print(f"ran {k[0]} {k[1]} skills={runs[k]['skills_invoked']} ${runs[k]['cost_usd'] or 0:.2f}", flush=True)
    judged = {}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(judge, t, runs[(t["id"], "baseline")]["final_text"], runs[(t["id"], "apex")]["final_text"], a.judge_model): t["id"] for t in tasks}
        for f in cf.as_completed(futs):
            tid = futs[f]
            try:
                judged[tid] = f.result()
            except Exception as e:  # keep the run going; record the failure
                judged[tid] = {"error": repr(e)}
            json.dump(judged[tid], open(os.path.join(out, f"{tid}.judge.json"), "w"), indent=2)
            print(f"judged {tid}: {judged[tid].get('winner')} apex={judged[tid].get('apex_score')} base={judged[tid].get('base_score')}", flush=True)
    lines = [f"# Benchmark {stamp}", f"Subject model: {a.model} · judge: {a.judge_model} · blind pairwise, randomized order", "",
             "| task | Apex skills used | rubric baseline | rubric apex | winner | apex stale/wrong flags | baseline stale/wrong flags |", "|---|---|---|---|---|---|---|"]
    tot = {"apex": 0, "baseline": 0, "tie": 0}
    sa = sb = cost = 0.0
    for t in tasks:
        j, r = judged[t["id"]], runs[(t["id"], "apex")]
        cost += (r["cost_usd"] or 0) + (runs[(t["id"], "baseline")]["cost_usd"] or 0) + (j.get("judge_cost") or 0)
        if "error" in j:
            lines.append(f"| {t['id']} | {', '.join(r['skills_invoked'])} | ? | ? | judge error | | |")
            continue
        tot[j["winner"]] += 1
        sa += j["apex_score"]; sb += j["base_score"]
        lines.append(f"| {t['id']} | {', '.join(r['skills_invoked']) or '—'} | {j['base_score']:.2f} | {j['apex_score']:.2f} | {j['winner']} | "
                     f"{len(j['apex_flags'].get('incorrect_or_stale', []))} | {len(j['base_flags'].get('incorrect_or_stale', []))} |")
    n = max(1, sum(tot.values()))
    lines += ["", f"**Wins:** apex {tot['apex']} · baseline {tot['baseline']} · tie {tot['tie']}",
              f"**Mean rubric coverage:** baseline {sb / n:.2f} · apex {sa / n:.2f}",
              f"**Total cost:** ${cost:.2f}", "", "## Judge reasons"] + \
             [f"- **{t['id']}** ({judged[t['id']].get('winner')}): {judged[t['id']].get('reason', judged[t['id']].get('error'))}" for t in tasks]
    open(os.path.join(out, "summary.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
