"""Gate rule loader for the RFE agentic pipeline.

format_lint runs fully (deterministic regex). completeness_check and
trigger_scan dispatch deterministic rules to a predicate registry and hand
judgment/checklist rules to the LLM gates as routed defects.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

RULES_DIR = Path(__file__).parent.parent / "rules"


@dataclass
class Defect:
    id: str
    severity: str
    rule_violated: str
    target_agent: str
    fix_instruction: str
    criterion: str = ""
    affected: str = ""
    engine: str = "deterministic"


def load_rules(rules_dir: Path = RULES_DIR) -> dict:
    out = {}
    for name in ("banned_categorical", "completeness", "rfe_noid_triggers"):
        with open(rules_dir / f"{name}.yml") as f:
            out[name] = yaml.safe_load(f)
    return out


def _compile_categorical(banned: dict):
    compiled = []
    for category, entries in banned.items():
        if category == "meta":
            continue
        for e in entries:
            compiled.append((category, re.compile(rf"\b(?:{e['term']})\b", re.I), e["fix"]))
    return compiled, banned["meta"]["severity"]


def format_lint(text: str, surface: str, banned: dict) -> list[Defect]:
    compiled, sev = _compile_categorical(banned)
    severity = sev.get("table" if "table" in surface else "narrative", "warn")
    hits = []
    for category, pat, fix in compiled:
        for m in pat.finditer(text):
            hits.append(Defect(
                id=f"LINT.{category}.{m.start()}",
                severity=severity,
                rule_violated=f"banned_categorical/{category}: '{m.group(0)}'",
                target_agent="synthesizer",
                fix_instruction=fix,
                affected=m.group(0),
            ))
    return hits


PRESENCE: dict[str, callable] = {}
TRIGGER: dict[str, callable] = {}


def presence(rule_id):
    def deco(fn):
        PRESENCE[rule_id] = fn
        return fn
    return deco


def trigger(tid):
    def deco(fn):
        TRIGGER[tid] = fn
        return fn
    return deco


def _facts(ledger, tag=None, kind=None):
    for f in ledger:
        if tag and tag not in f.get("criterion_tags", []):
            continue
        if kind and f.get("kind") != kind:
            continue
        yield f


@presence("HS.comp_total")
def _(ledger):
    return any(f.get("src_type") == "primary_exhibit" and f.get("comp_kind") == "total"
               for f in _facts(ledger, "HS"))


@presence("HS.peer_correct")
def _(ledger):
    return any(f.get("soc") == "15-2051" and f.get("tier") in {"lead", "senior", "principal"}
               for f in _facts(ledger, "HS", kind="benchmark"))


@presence("HS.source_objective")
def _(ledger):
    bms = list(_facts(ledger, "HS", kind="benchmark"))
    return bool(bms) and all(f.get("src_type") in {"gov", "lca_disclosure"} for f in bms)


@presence("OC.external_corroboration")
def _(ledger):
    ext = {"citation", "press", "standards", "patent_by_other", "adoption"}
    return any(f.get("src_type") in ext for f in _facts(ledger, "OC"))


def completeness_check(ledger, criterion, completeness):
    blockers, judgment = [], []
    for rule in completeness.get(criterion, []):
        fn = PRESENCE.get(rule["id"])
        present = fn(ledger) if fn else None
        if present is False:
            blockers.append(Defect(
                id=f"COMP.{rule['id']}",
                severity=rule["severity"],
                rule_violated=f"completeness/{rule['id']}: not present",
                target_agent="hunter",
                fix_instruction=rule.get("basis", "supply the missing element"),
                criterion=criterion,
            ))
        elif present is None:
            judgment.append({"id": rule["id"], "kind": "presence_unimplemented",
                             "spec": rule["present"], "severity": rule["severity"]})
        if "satisfies" in rule:
            judgment.append({"id": rule["id"], "kind": "satisfies",
                             "question": rule["satisfies"], "severity": rule["severity"]})
    return blockers, judgment


@trigger("average_not_peer")
def _(pkg):
    return any(f.get("kind") == "benchmark" and f.get("peer_scope") == "general"
               for f in pkg["ledger"])


@trigger("ad_as_benchmark")
def _(pkg):
    return any(f.get("src_type") == "job_ad" and f.get("role") != "supporting"
               for f in pkg["ledger"])


@trigger("occupation_mismatch")
def _(pkg):
    claimed = pkg.get("claimed_occupation")
    return any(f.get("kind") == "benchmark" and f.get("soc") not in (None, claimed)
               for f in pkg["ledger"])


@trigger("unsourced_number")
def _(pkg):
    ids = {f["id"] for f in pkg["ledger"]}
    return any(ref not in ids for ref in pkg.get("draft_refs", []))


def trigger_scan(pkg, triggers):
    fired, dispatch = [], []
    for t in triggers["triggers"]:
        if t["engine"] == "deterministic":
            fn = TRIGGER.get(t["id"])
            if fn is None:
                dispatch.append({"id": t["id"], "engine": "deterministic",
                                 "to_gate": "coherence_checker", "route": t["route"],
                                 "status": "predicate_unimplemented"})
            elif fn(pkg):
                fired.append(Defect(
                    id=f"TRIG.{t['id']}", severity=t["severity"],
                    rule_violated=f"trigger/{t['id']}", target_agent=t["route"],
                    fix_instruction=t.get("basis", ""), engine="deterministic"))
        else:
            to = "officer_critic" if t["engine"] == "judgment" else "coherence_checker"
            dispatch.append({"id": t["id"], "engine": t["engine"], "to_gate": to,
                             "route": t["route"], "severity": t["severity"]})
    return fired, dispatch


if __name__ == "__main__":
    rules = load_rules()

    bad = ("Mr. T's world-class, groundbreaking contribution was widely adopted "
           "and his remuneration is significantly higher than numerous peers.")
    print("== format_lint (evidentiary_table) ==")
    for d in format_lint(bad, "evidentiary_table", rules["banned_categorical"]):
        print(f"  [{d.severity}] {d.rule_violated}")

    ledger = [
        {"id": "HS-01", "criterion_tags": ["HS", "FM"],
         "src_type": "primary_exhibit", "comp_kind": "total"},
        {"id": "HS-14", "criterion_tags": ["HS"], "kind": "benchmark",
         "src_type": "job_ad", "role": "primary", "soc": "15-2041",
         "peer_scope": "general"},
    ]
    print("\n== completeness_check: high_salary ==")
    blockers, judgment = completeness_check(ledger, "high_salary", rules["completeness"])
    for b in blockers:
        print(f"  BLOCKER {b.id} -> {b.target_agent}")
    for j in judgment:
        if j["kind"] == "satisfies":
            print(f"  judgment {j['id']}: {j['question']}")

    pkg = {"ledger": ledger, "claimed_occupation": "15-2051", "draft_refs": ["HS-99"]}
    print("\n== trigger_scan ==")
    fired, dispatch = trigger_scan(pkg, rules["rfe_noid_triggers"])
    for d in fired:
        print(f"  FIRED {d.id} [{d.severity}] -> {d.target_agent}")
    print(f"  {len(dispatch)} routed to judgment/checklist gates")
