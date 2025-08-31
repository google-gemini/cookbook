# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, re, json, time, pathlib, subprocess, nbformat, requests, sys
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

def _discover():
    nb = os.getenv("NB")
    if nb:
        nb_list = re.split(r"[,\s]+", nb)    
        paths = []
        for n in nb_list:
            if not n: continue
            p = (ROOT / n) if not n.startswith(("/", "./")) else pathlib.Path(n)
            paths.append(p.resolve())
        return paths
    return sorted(p for p in ROOT.rglob("*.ipynb") if ".ipynb_checkpoints" not in str(p))

def _run(cmd):
    return subprocess.run(cmd, check=False, text=True, capture_output=True)

def _ensure_requirements(nb_path):
    try:
        import pipreqsnb
    except ImportError:
        inst = _run([os.sys.executable, "-m", "pip", "install", "pipreqsnb"])
        if inst.returncode:
            print(f"[pip install] warn: install failed for pipreqsnb:\n{inst.stdout}\n{inst.stderr}")
            return

    req_out = REPORTS / f"reqs.txt"
    gen = _run(["pipreqsnb", str(nb_path), "--savepath", str(req_out)])
    if gen.returncode: return
    if not req_out.exists() or req_out.stat().st_size == 0: return
    inst = _run([os.sys.executable, "-m", "pip", "install", "-r", str(req_out)])
    if inst.returncode:
        print(f"[pip install] warn: install failed for {req_out}:\n{inst.stdout}\n{inst.stderr}")
    _run(["rm", str(req_out)])

_USERDATA_RE = re.compile(r"userdata\.get\s*\(\s*(['\"])([^'\"]+)\1\s*(?:,\s*([^)]+))?\s*\)")

def _patch_colab_userdata(nb):
    for cell in nb.cells:
        if cell.cell_type != "code": continue
        src = cell.source or ""
        lines, had_os = [], False
        for line in src.splitlines():
            if line.strip().startswith(("from google.colab import userdata", "import google.colab")): continue
            if re.match(r"^\s*import\s+os(\s|$)", line): had_os = True
            lines.append(line)
        src = "\n".join(lines)
        def _sub(m):
            key, default = m.group(2), m.group(3)
            return f"os.getenv('{key}', {default})" if default else f"os.getenv('{key}')"
        if "userdata.get(" in src:
            src2 = _USERDATA_RE.sub(_sub, src)
            if src2 != src and not had_os: src = "import os\n" + src2
            else: src = src2
        cell.source = src
    return nb

def _summarize_outputs(outputs):
    buf, img_count, err = [], 0, None
    for out in outputs or []:
        ot = out.get("output_type")
        if ot == "stream": buf.append(out.get("text", ""))
        elif ot in ("execute_result", "display_data"):
            data = out.get("data", {})
            text = data.get("text/plain") or ""
            buf.append("".join(text) if isinstance(text, list) else str(text))
        elif ot == "error": err = {"ename": out.get("ename"), "evalue": out.get("evalue")}
    return {"text": "".join(buf).strip(), "images": img_count, "error": err}

def _collect_cell_snapshots(nb):
    return [{"index": i, "type": c.cell_type, "code": c.source,
             "summary": _summarize_outputs(c.get("outputs")) if c.cell_type == "code" else None}
            for i, c in enumerate(nb.cells)]

def _gemini_compare_batches(file_name, diffs, batch_size=20, progress_callback=None):
    if not diffs: return [], []
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return [], ["<AI compare skipped: GOOGLE_API_KEY missing>"]

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    system_text = ("""
        You are an output-diff judge for notebook cells. Given code, OLD output, and NEW output, 
        classify each cell into EXACTLY one of:
        - wrong (Wrong or totally different)
        - slightly_changed (Slightly different)
        - ok_cells (Outputs are effectively the same. Allowed minor variations include: 
            - wording/phrasing differences, 
            - timing/speed values (e.g., download progress), 
            - harmless pip/installation warnings.
          Do NOT count these as real changes.)
        Return ONLY a JSON array of objects: {index:int, bucket:string, note:string}. 
        No extra keys, no narration.
    """)


    def _coerce_json(text):
        t = text.strip()
        if t.startswith("```"):
            t = t.strip("`")
            if "\n" in t: t = t.split("\n", 1)[1]
        start, end = t.find("["), t.rfind("]")
        if start != -1 and end != -1 and end > start:
            t = t[start:end+1]
        t = re.sub(r",\s*(\]|\})", r"\1", t)
        return json.loads(t)

    results, raw_texts = [], []
    total_batches = (len(diffs) + batch_size - 1) // batch_size
    for i in range(0, len(diffs), batch_size):
        if progress_callback:
            progress_callback(i // batch_size + 1, total_batches)

        batch = diffs[i:i+batch_size]
        blocks = [f"Cell {d['index']}\n```python\n{d['code'] or ''}\n```\n"
                  f"OLD OUTPUT:\n{d['old_text'] or '(empty)'}\n\n"
                  f"NEW OUTPUT:\n{d['new_text'] or '(empty)'}\n----\n" for d in batch]

        payload = {
            "system_instruction": {"parts": [{"text": system_text}]},
            "contents": [{"role": "user", "parts": [{"text": f"File: {file_name}\nEvaluate these cells:\n\n{''.join(blocks)}"}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192, "response_mime_type": "application/json"}
        }

        try:
            resp = requests.post(url, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            part = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0]
            parsed = part if 'text' not in part else _coerce_json(part.get('text', '[]'))

            for item in parsed:
                idx = int(item.get("index"))
                raw_bucket = (item.get("bucket") or "").strip().lower()
                bucket = ("ok_cells" if raw_bucket in ("ok", "same", "almost_same", "ok_cells") else
                         "slightly_changed" if raw_bucket in ("slightly", "slightly_changed") else "wrong")
                results.append({"index": idx, "bucket": bucket, "note": (item.get("note") or "").strip()})
        except Exception as e:
            raw_texts.append(f"<AI compare error: {e}>")

    return results

def _clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class TestProgressUI:
    def __init__(self, total_files):
        self.total_files = total_files
        self.history = []
        self.current_file = ""
        self.current_step = ""
        self.files_done = 0

    def start_file(self, path):
        self.current_file = str(path.relative_to(ROOT))
        self.current_step = "Initializing..."
        # Add a "running" entry for the current file
        running_report = {
            "file": str(path),
            "status": "running",
            "buckets": {"ok_cells": {}, "slightly_changed": {}, "wrong": {}}
        }
        # Remove any previous running entry for this file
        self.history = [r for r in self.history if r["file"] != str(path)]
        self.history.append(running_report)
        self.draw()

    def update_progress(self, step_message):
        self.current_step = step_message
        self.draw()

    def finish_file(self, report):
        self.history = [r for r in self.history if r["file"] != report["file"]]
        self.history.append(report)
        self.current_step = "Completed."
        self.current_file = ""
        self.files_done += 1

    def draw(self, final_summary=False):
        _clear_screen()
        percent = (self.files_done / self.total_files * 100) if self.total_files > 0 else 0
        status_line = f"Test suite finished for {self.total_files} notebooks.\n" if final_summary \
            else f"Running test suite for {self.total_files} notebooks... ({percent:.0f}% complete)\n"
        sys.stdout.write(status_line)

        if self.current_file:
            sys.stdout.write(f"Current: {self.current_file}\nStep: {self.current_step}\n\n")

        ai_compare = os.getenv("AI_COMPARE", "0") == "1"
        if ai_compare:
            header = f"{'File':<50} {'Status':<10} {'OK':>5} {'Slightly Changed':>18} {'Wrong':>7}"
        else:
            header = f"{'File':<50} {'Status':<10}"

        sys.stdout.write("\n" + header + "\n" + "─" * len(header) + "\n")
        for r in self.history:
            status = r['status']
            file_rel = str(pathlib.Path(r["file"]).relative_to(ROOT))
            if ai_compare:
                buckets = r.get("buckets", {})
                ok, slight, wrong = len(buckets.get("ok_cells", {})), len(buckets.get("slightly_changed", {})), len(buckets.get("wrong", {}))
                if status == 'running':
                    ok_str, slight_str, wrong_str = ('...', '...', '...')
                elif status == 'passed':
                    ok_str, slight_str, wrong_str = (str(ok), str(slight), str(wrong))
                else:
                    ok_str, slight_str, wrong_str = ('-', '-', str(wrong or 1))
                sys.stdout.write(f"{file_rel:<50} {status:<10} {ok_str:>5} {slight_str:>18} {wrong_str:>7}\n")
            else:
                sys.stdout.write(f"{file_rel:<50} {status:<10}\n")
        sys.stdout.flush()

def run_notebook_test(nb_path, ui):
    """Contains the logic for running a single notebook."""
    ui.start_file(nb_path)
    ui.update_progress("Ensuring requirements...")
    _ensure_requirements(nb_path)

    nb = nbformat.read(nb_path, as_version=4)
    old_snaps = _collect_cell_snapshots(nb)
    nb = _patch_colab_userdata(nb)

    client = NotebookClient(nb, timeout=int(os.getenv("NB_TIMEOUT", "900")),
                            kernel_name=os.getenv("NB_KERNEL", "python3"),
                            allow_errors=True, record_timing=True, store_widget_state=False)

    started = time.time()
    first_error_msg = None
    code_cells_with_indices = [(i, c) for i, c in enumerate(nb.cells) if c.cell_type == 'code']
    total_code_cells = len(code_cells_with_indices)

    with client.setup_kernel():
        for i, (cell_index, cell) in enumerate(code_cells_with_indices):
            ui.update_progress(f"Executing cell {i + 1}/{total_code_cells}...")
            try:
                client.execute_cell(cell, cell_index)
            except CellExecutionError as e:
                if not first_error_msg:
                    first_error_msg = str(e).split("\n", 1)[0]

    new_snaps = _collect_cell_snapshots(nb)
    rel = str(nb_path.relative_to(ROOT)).replace("/", "__")
    file_report = {
        "file": str(nb_path),
        "duration_sec": round(time.time() - started, 3),
        "status": "failed" if first_error_msg else "passed",
        "buckets": {"ok_cells": {}, "slightly_changed": {}, "wrong": {}}
    }

    if first_error_msg:
        for c in new_snaps:
            if c["type"] == "code" and c["summary"] and c["summary"]["error"]:
                file_report["buckets"]["wrong"][str(c["index"])] = {
                    "cell_code": c["code"], "ai_note": "Execution error in this run."
                }

    if os.getenv("AI_COMPARE", "0") == "1" and not first_error_msg:
        diffs = [{"index": new["index"], "code": new["code"],
                  "old_text": (old.get("summary") or {}).get("text", ""),
                  "new_text": (new.get("summary") or {}).get("text", "")}
                 for old, new in zip(old_snaps, new_snaps) if new["type"] == "code"]

        def ai_progress(batch_num, total_batches):
            ui.update_progress(f"AI comparing batch {batch_num}/{total_batches}...")

        ai_results = _gemini_compare_batches(str(nb_path), diffs, progress_callback=ai_progress)
        by_cell = {r["index"]: r for r in ai_results}

        for d in diffs:
            r = by_cell.get(d["index"])
            if not r: continue
            bucket = r["bucket"]
            file_report["buckets"].setdefault(bucket, {})[str(d["index"])] = {
                "cell_code": d["code"], "old_text": d["old_text"], "new_text": d["new_text"], "ai_note": (r.get("note") or "")[:280]
            }

    (REPORTS / f"{rel}.compare.json").write_text(json.dumps(file_report, indent=2), encoding="utf-8")
    ui.finish_file(file_report)
    if first_error_msg:
        print(f"\nERROR in {nb_path.name}: {first_error_msg}\n")


def main():
    """Main execution function."""
    notebooks = _discover()
    if not notebooks:
        print("No notebooks found to test.")
        sys.exit(0)

    ui = TestProgressUI(len(notebooks))

    for nb_path in notebooks:
        run_notebook_test(nb_path, ui)

    ui.draw(final_summary=True)

if __name__ == "__main__":
    main()