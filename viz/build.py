"""Build the Benchmark Sum visualization page from the given runs.

Usage: python3 -I viz/build.py <out.html> <run-id> [<run-id> ...]
Run ids are those of testproject_benchmark_sum (lexis run list testproject_benchmark_sum).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LEXIS = os.path.expanduser("~/.vscode/extensions/lexis-platform.lexis-platform-0.17.9/bin/lexis")
out_html, run_ids = sys.argv[1], sys.argv[2:]

with tempfile.TemporaryDirectory() as tmp:
    data_path = os.path.join(tmp, "data.json")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "collect.py"), *run_ids, data_path], check=True)
    data = json.load(open(data_path, encoding="utf-8"))
    for run in data["runs"]:
        for output in run["outputs"]:
            dest = os.path.join(tmp, output["id"])
            os.makedirs(dest, exist_ok=True)
            subprocess.run([LEXIS, "dataset", "download", output["id"], "--to", dest, "--yes", "--quiet"],
                           check=True, capture_output=True)
            for f in output["files"]:
                path = os.path.join(dest, f["name"])
                if os.path.exists(path):
                    f["content"] = open(path, encoding="utf-8").read()

payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("__DATA__", payload)
open(out_html, "w", encoding="utf-8").write(html)
print("wrote", out_html)
