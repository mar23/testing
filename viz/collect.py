"""Collect run data of testproject_benchmark_sum from the lexis CLI into JSON."""
import json
import os
import subprocess
import sys

LEXIS = os.path.expanduser("~/.vscode/extensions/lexis-platform.lexis-platform-0.17.9/bin/lexis")
WF = "testproject_benchmark_sum"
RUNS = sys.argv[1:-1]
OUT = sys.argv[-1]


def cli(*args, as_json=True):
    cmd = [LEXIS, *args] + (["--output", "json"] if as_json else [])
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if res.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}: {res.stderr or res.stdout}")
    return json.loads(res.stdout) if as_json else res.stdout


runs = []
for run_id in RUNS:
    ref = f"{WF}/{run_id}"
    run = cli("run", "show", ref)["run"]
    tasks = cli("run", "tasks", ref)["items"]
    hpc = cli("logs", ref, "--hpc", "--tail", "200", as_json=False)
    datasets = cli("run", "datasets", ref)
    items = datasets.get("items", datasets) if isinstance(datasets, dict) else datasets
    outputs = []
    for d in items:
        did = d.get("id")
        files = cli("dataset", "files", did)
        outputs.append({"id": did, "title": d.get("title"), "files": files.get("items", files)})
    runs.append({"run": run, "tasks": tasks, "hpc": hpc, "outputs": outputs})

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump({"workflow": cli("workflow", "show", WF), "runs": runs}, fh, ensure_ascii=False, indent=1)
print("wrote", OUT, [r["run"]["state"] for r in runs])
