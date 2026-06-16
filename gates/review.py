#!/usr/bin/env python3
"""Interactive review of staged facts: approve -> ledger, reject -> rejected, edit, skip.
Verification is the human's job; this only makes the approve/reject ACTION fast.
Usage: python gates/review.py [--no-open] [--criterion OC]"""
import sys, os, json, subprocess, platform, datetime, argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STAGING = REPO / "corpus" / "staging"
LEDGER = REPO / "corpus" / "ledger"
REJECTED = REPO / "corpus" / "rejected"
EXHIBITS = REPO / "corpus" / "exhibits"
TRACE = REPO / "trace" / "review-log.jsonl"

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml"); sys.exit(1)

def log(entry):
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(TRACE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def open_file(p: Path):
    try:
        s = platform.system()
        if s == "Windows": os.startfile(str(p))            # noqa
        elif s == "Darwin": subprocess.run(["open", str(p)])
        else: subprocess.run(["xdg-open", str(p)])
    except Exception as e:
        print(f"  (could not auto-open {p.name}: {e})")

def open_in_editor(p: Path):
    ed = os.environ.get("EDITOR") or ("notepad" if platform.system() == "Windows" else "nano")
    try: subprocess.run([ed, str(p)])
    except Exception as e: print(f"  (could not open editor: {e})")

def load(p: Path):
    with open(p, encoding="utf-8") as f: return yaml.safe_load(f)

def dump(data: dict, p: Path):
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=100)

def panel(fact, fname):
    line = "=" * 72
    print(f"\n{line}\n  {fact.get('id','?')}   ({fname})\n{line}")
    print(f"  value : {fact.get('value','')}")
    if "normalized" in fact: print(f"  norm  : {fact.get('normalized')}")
    print(f"  label : {fact.get('label','')}")
    print(f"  type  : {fact.get('src_type','')}    tags: {fact.get('criterion_tags','')}")
    src = fact.get("src", {}) or {}
    print(f"  exhibit: {src.get('exhibit','')}")
    print(f"  locus : {src.get('locus','')}")
    if fact.get("src_note"): print(f"  note  : {fact.get('src_note')}")

def validate():
    print("\n--- validating ledger ---")
    subprocess.run([sys.executable, str(REPO/"gates"/"ledger_schema.py"), str(LEDGER)])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-open", action="store_true", help="do not auto-open exhibit PDFs")
    ap.add_argument("--criterion", help="only review facts whose id starts with this, e.g. OC")
    args = ap.parse_args()

    LEDGER.mkdir(parents=True, exist_ok=True); REJECTED.mkdir(parents=True, exist_ok=True)
    files = sorted(STAGING.glob("*.yml"))
    if args.criterion:
        files = [f for f in files if f.stem.upper().startswith(args.criterion.upper())]
    if not files:
        print("Nothing in staging to review."); return

    # group by exhibit so one PDF is opened once per cluster
    facts = [(f, load(f)) for f in files]
    facts.sort(key=lambda t: ((t[1].get("src") or {}).get("exhibit",""), t[0].stem))
    print(f"{len(facts)} staged fact(s) to review."
          f"  Keys: [a]pprove [r]eject [e]dit [s]kip [q]uit")

    opened = set()
    stats = {"approved":0,"rejected":0,"skipped":0}
    for f, fact in facts:
        ex = (fact.get("src") or {}).get("exhibit","")
        if ex and not args.no_open and ex not in opened:
            p = EXHIBITS / ex
            if p.exists(): open_file(p); opened.add(ex)
            else: print(f"  (exhibit not found on disk: {ex})")
        while True:
            panel(fact, f.name)
            c = input("\n  [a/r/e/s/q] > ").strip().lower()
            if c == "a":
                fact["trust"] = "verified"
                fact.pop("needs_human_check", None); fact.pop("confidence", None)
                fact["as_of"] = datetime.date.today().isoformat()
                dump(fact, LEDGER / f.name); f.unlink()
                log({"action":"approve","id":fact.get("id"),"file":f.name})
                stats["approved"] += 1; print(f"  -> approved to ledger/{f.name}"); break
            elif c == "r":
                reason = input("  reason for reject > ").strip()
                fact["rejected_reason"] = reason; fact["status"] = "rejected"
                dump(fact, REJECTED / f.name); f.unlink()
                log({"action":"reject","id":fact.get("id"),"file":f.name,"reason":reason})
                stats["rejected"] += 1; print(f"  -> moved to rejected/{f.name}"); break
            elif c == "e":
                dump(fact, f); open_in_editor(f); fact = load(f)   # reload after edit
                print("  (reloaded; review again)"); continue
            elif c == "s":
                stats["skipped"] += 1; print("  -> left in staging"); break
            elif c == "q":
                print("\n  quit.");
                print(f"  approved {stats['approved']} | rejected {stats['rejected']} | skipped {stats['skipped']}")
                validate(); return
            else:
                print("  ? use a / r / e / s / q")
    print(f"\n  done. approved {stats['approved']} | rejected {stats['rejected']} | skipped {stats['skipped']}")
    validate()

if __name__ == "__main__":
    main()
