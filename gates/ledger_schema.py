"""Validate that a ledger fact-sheet is well-formed, and check cross-fact
dependency integrity.

Run: python gates/ledger_schema.py corpus/ledger/   (file or dir)
Exits non-zero if any fact-sheet has errors OR a derived fact depends on a
missing/superseded/blocked fact (an orphaned dependent). Enforces: agent-found
facts cannot be 'verified', numbers/dates must be normalized, derived facts must
declare their inputs, and a fact whose input was retired must not stay active.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

CRITERIA = {"OC", "CR", "HS", "FM", "JU", "AU"}   # + Judging, Authorship (accepted)
VALUE_TYPES = {"number", "date", "string", "claim"}
SRC_TYPES = {"primary_exhibit", "uscis_doc", "user_analysis", "agent_staged", "derived", "secondary_aggregator"}
TRUST = {"verified", "staged", "disputed", "derived"}
STATUS = {"active", "superseded", "blocked"}

ID_RE = re.compile(rf"^(?:{'|'.join(sorted(CRITERIA))})-D?\d+$")

REQUIRED = ["id", "value", "value_type", "label", "src_type", "trust",
            "criterion_tags", "status"]


def validate(fact: dict) -> list[str]:
    errs: list[str] = []

    def need(cond, msg):
        if not cond:
            errs.append(msg)

    for f in REQUIRED:
        need(f in fact and fact[f] not in (None, "", []), f"missing required field: {f}")
    if errs:
        return errs

    need(ID_RE.match(str(fact["id"])), f"id '{fact['id']}' breaks convention CRIT-NN / CRIT-DNN")
    need(fact["value_type"] in VALUE_TYPES, f"value_type not in {sorted(VALUE_TYPES)}")
    need(fact["src_type"] in SRC_TYPES, f"src_type not in {sorted(SRC_TYPES)}")
    need(fact["trust"] in TRUST, f"trust not in {sorted(TRUST)}")
    need(fact["status"] in STATUS, f"status not in {sorted(STATUS)}")

    tags = fact["criterion_tags"]
    need(isinstance(tags, list) and tags, "criterion_tags must be a non-empty list")
    if isinstance(tags, list):
        for t in tags:
            need(t in CRITERIA, f"unknown criterion tag: {t}")

    vt, st, tr = fact["value_type"], fact["src_type"], fact["trust"]

    if vt in {"number", "date"}:
        need("normalized" in fact, f"value_type '{vt}' requires a 'normalized' field for diffing")

    if st == "agent_staged":
        need(tr in {"staged", "disputed"},
             "agent_staged facts cannot be 'verified' — human verification promotes them first")

    if st == "primary_exhibit":
        src = fact.get("src")
        need(isinstance(src, dict) and src.get("file"),
             "primary_exhibit requires src.file (path to the exhibit)")
        if isinstance(src, dict):
            need(src.get("page") or src.get("locus"),
                 "primary_exhibit src should pin a page or locus")

    if st == "derived" or tr == "derived":
        need(st == "derived" and tr == "derived",
             "derived facts must have src_type='derived' AND trust='derived'")
        d = fact.get("derivation")
        need(isinstance(d, dict) and d.get("method") and d.get("inputs"),
             "derived facts require derivation.method and derivation.inputs")
        need(isinstance(fact.get("depends_on"), list) and fact.get("depends_on"),
             "derived facts require a non-empty depends_on list")
    else:
        need(fact.get("src"), "non-derived facts require a src")

    if "confidence" in fact:
        c = fact["confidence"]
        need(isinstance(c, (int, float)) and 0 <= c <= 1, "confidence must be a number in [0,1]")

    return errs


def check_dependencies(facts: dict) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    for fid, d in facts.items():
        if d.get("status", "active") != "active":
            continue
        for dep in d.get("depends_on") or []:
            if dep not in facts:
                errors.append(f"{fid}: depends_on missing fact '{dep}' (dangling reference)")
                continue
            dd = facts[dep]
            st = dd.get("status", "active")
            tr = dd.get("trust")
            if st in ("superseded", "blocked"):
                errors.append(f"{fid}: depends on '{dep}' which is {st} -> mark {fid} blocked")
            elif tr in ("staged", "disputed"):
                warns.append(f"{fid}: depends on unverified '{dep}' (trust={tr}) -> pending until verified")
    return errors, warns


def validate_path(path: Path) -> tuple[int, dict]:
    files = sorted(f for f in path.glob("*.yml") if not f.name.startswith("_")) \
        if path.is_dir() else [path]
    facts: dict = {}
    if not files:
        print(f"no .yml fact-sheets found at {path}")
        return 0, facts
    bad = 0
    for f in files:
        try:
            fact = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            print(f"FAIL {f.name}: invalid YAML — {e}")
            bad += 1
            continue
        errs = validate(fact) if isinstance(fact, dict) else ["top-level YAML is not a mapping"]
        if errs:
            bad += 1
            print(f"FAIL {f.name}")
            for e in errs:
                print(f"   - {e}")
        else:
            facts[fact["id"]] = fact
            print(f"ok   {f.name}  [{fact['id']}]")
    print(f"\n{len(files) - bad}/{len(files)} valid")
    return bad, facts


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("corpus/ledger")
    bad, facts = validate_path(target)
    derr, dwarn = check_dependencies(facts)
    if derr or dwarn:
        print("\n== dependency integrity ==")
        for e in derr:
            print(f"  ERROR {e}")
        for w in dwarn:
            print(f"  warn  {w}")
    elif facts:
        print("dependency integrity: ok")
    sys.exit(1 if (bad or derr) else 0)
