"""Build index.html from src/template.html and the JSON files in data/.

Usage (from the repository root):
    python3 src/build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def dump(obj):
    return json.dumps(obj, ensure_ascii=False)

template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
abcs = load("abcs_data.json")
cautions = load("cautions.json")
typei = load("typei_data.json")
at = load("at_data.json")

# Type I frost HOTs (Table 2/3 and Adj-2/3). The docx merge covers every OAT band.
typei["frost"] = {"IAL": ["0:45", "0:34"], "ICOMP": ["0:35", "0:27"]}
typei["frostRange"] = [None, None]

page = (template
        .replace("__DATA__", dump(abcs))
        .replace("__CAUTIONS__", dump({k: cautions[k] for k in ["9", "11", "32", "66"]}))
        .replace("__TYPEI__", dump(typei))
        .replace("__AT__", dump(at)))

html = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written ({len(html)} bytes)")
