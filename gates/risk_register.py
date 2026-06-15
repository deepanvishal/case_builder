"""Aggregate the live weakness map into work/risk_register.md.

Pure aggregation, no new analysis: combines the open defects in
work/defects.jsonl with the evidence gaps implied by the matrix (criteria with
no usable evidence, and evidence found but not yet verified). Read-only;
you adjudicate from it.

Run: python gates/risk_register.py
Writes: work/risk_register.md
"""
from __future__ import annotations

import json
from datetime import date

from matrix import REPO, columns, load_facts, mark

DEFECTS = REPO / "work" / "defects.jsonl"
OUT = REPO / "work" / "risk_register.md"

SEV_ORDER = {"blocker": 0, "warn": 1, "": 2}


def _cell(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def read_defects() -> list[dict]:
    if not DEFECTS.exists():
        return []
    out = []
    for i, line in enumerate(DEFECTS.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"  skip (bad JSON) defects.jsonl line {i}")
    return out


def evidence_risks() -> list[dict]:
    facts = load_facts()
    cols = columns()
    ready = {c: 0 for c in cols}
    pending = {c: 0 for c in cols}
    for d in facts.values():
        if d.get("status", "active") == "superseded":
            continue
        _, bucket = mark(d, facts)
        for c in d.get("criterion_tags") or []:
            if c in cols:
                (ready if bucket == "ready" else pending)[c] += 1
    risks = []
    for c in cols:
        if c == "FM":
            continue
        if ready[c] == 0:
            risks.append({"source": "matrix", "severity": "blocker",
                          "weakness": f"No usable evidence for criterion {c}",
                          "mitigation": f"hunt + verify evidence for {c}",
                          "owner": "hunter + human", "status": "open"})
        elif pending[c]:
            risks.append({"source": "matrix", "severity": "warn",
                          "weakness": f"{c}: {pending[c]} item(s) found but unverified",
                          "mitigation": "verify vs primary source; promote staging -> ledger",
                          "owner": "human", "status": "pending-verification"})
    return risks


def defect_risks(defects: list[dict]) -> list[dict]:
    risks = []
    for x in defects:
        weak = x.get("rule_violated", "?")
        aff = x.get("affected")
        if aff:
            weak += f" - {str(aff)[:80]}"
        risks.append({"source": x.get("id", "defect"), "severity": x.get("severity", ""),
                      "weakness": weak, "mitigation": x.get("fix_instruction", ""),
                      "owner": x.get("target_agent", "?"), "status": "open"})
    return risks


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    defects = read_defects()
    risks = evidence_risks() + defect_risks(defects)
    risks.sort(key=lambda r: (SEV_ORDER.get(r["severity"], 2), r["source"]))

    blockers = sum(1 for r in risks if r["severity"] == "blocker")
    warns = sum(1 for r in risks if r["severity"] == "warn")

    rows = ["| Severity | Weakness | Mitigation | Owner | Status | Source |",
            "|---|---|---|---|---|---|"]
    for r in risks:
        rows.append(f"| {_cell(r['severity'] or '-')} | {_cell(r['weakness'])} | "
                    f"{_cell(r['mitigation'])} | {_cell(r['owner'])} | "
                    f"{_cell(r['status'])} | {_cell(r['source'])} |")
    if len(rows) == 2:
        rows.append("| - | none | - | - | - | - |")

    parts = [
        "# Risk Register",
        f"_Generated {date.today().isoformat()}. Aggregated from defects.jsonl + the matrix. "
        "Read-only; adjudicate from it._",
        "",
        f"**{blockers} blocker(s), {warns} warn(s).** Blockers must clear before a section ships.",
        "",
        "\n".join(rows),
    ]
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")

    print(f"risk register -> {OUT.relative_to(REPO)}")
    print(f"  {blockers} blocker(s), {warns} warn(s), {len(risks)} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
