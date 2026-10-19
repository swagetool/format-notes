"""Run every snippet of every note and compare its output with the output stored in the note.

A difference is information, not a failure: the script always exits 0 and writes
a Markdown report. Usage: python3 ci/check_notes.py REPORT.md
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNIPPET = re.compile(r"^Snippet file: `([^`]+)`", re.M)
OUTPUT = re.compile(r"^Output, as printed[^\n]*\n\n```\n(.*?)\n```", re.M | re.S)


def run(path):
    # Same shape as the stored output: standard output, then standard error
    # behind a "[stderr] " tag. -W ignore hides only the Python deprecation notice.
    work = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, "-W", "ignore", path], capture_output=True, cwd=work)
    text = r.stdout.decode("utf-8", "replace")
    if r.stderr.strip():
        text += "[stderr] " + r.stderr.decode("utf-8", "replace")
    if r.returncode:
        text += "[exit code %d]\n" % r.returncode
    return text.rstrip("\n")


def version():
    try:
        from osgeo import gdal
        return gdal.VersionInfo("RELEASE_NAME")
    except Exception as e:
        return "unknown (%s)" % e


def main():
    report = sys.argv[1] if len(sys.argv) > 1 else "report.md"
    rows, details = [], []
    for note in sorted(glob.glob(os.path.join(ROOT, "*", "*.md"))):
        text = open(note, encoding="utf-8").read()
        names = SNIPPET.findall(text)
        outputs = OUTPUT.findall(text)
        rel = os.path.relpath(note, ROOT).replace(os.sep, "/")
        if len(names) != len(outputs):
            rows.append((rel, "?", "%d snippets, %d outputs in the note" % (len(names), len(outputs))))
            continue
        for name, stored in zip(names, outputs):
            actual = run(os.path.join(os.path.dirname(note), name))
            same = actual.strip() == stored.strip()
            rows.append((rel + " / " + name, "same" if same else "DIFFERENT", ""))
            if not same:
                details.append("### %s / %s\n\nStored in the note:\n\n```\n%s\n```\n\nPrinted now:\n\n```\n%s\n```\n"
                               % (rel, name, stored, actual))
    same_n = sum(1 for r in rows if r[1] == "same")
    out = ["# Snippet check", "", "GDAL: %s, Python %s" % (version(), sys.version.split()[0]), "",
           "%d of %d snippets print what the note stores." % (same_n, len(rows)), "",
           "| Snippet | Result | Remark |", "|---|---|---|"]
    out += ["| %s | %s | %s |" % r for r in rows]
    out += [""] + details
    open(report, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out[:6]))


main()
