"""Build the evidence x criteria matrix (the Final Merits skeleton).

Tabulates which criteria each ledger fact supports, marking trust so pending
(staged / unsafe-derived) evidence is visible alongside usable evidence. Rows
that light >=2 criteria columns are weave anchors; columns with no usable
evidence are thin spots. Deterministic from the ledger; a read-only planning
artifact, never an input to drafting.

Run: python gates/matrix.py
Writes: work/fm/matrix.md
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "corpus" / "ledger"
DEFINITIONS = REPO / "corpus" / "definitions.yml"
OUT = REPO / "work" / "fm" / "matrix.md"

DEFAULT_COLUMNS = ["OC", "CR", "HS", "FM"]


def load_facts() -> dict:
    facts = {}
    for f in sorted(LEDGER.glob("*.yml")):
        if f.name.startswith("_"):
            continue
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            print(f"  skip (invalid YAML): {f.name}")
            continue
        if isinstance(d, dict) and d.get("id"):
            facts[d["id"]] = d
    return facts


def columns() -> list[str]:
    if not DEFINITIONS.exists():
        return DEFAULT_COLUMNS
    try:
        defs = yaml.safe_load(DEFINITIONS.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return DEFAULT_COLUMNS
    cip = defs.get("criteria_in_play") or {}
    cols = list(cip.get("rfe_challenged") or [])
    for a in (cip.get("accepted") or []):
        if isinstance(a, str) and not a.startswith("<") and a not in cols:
            cols.append(a)
    if "FM" not in cols:
        cols.append("FM")
    return cols or DEFAULT_COLUMNS


def mark(fact: dict, facts: dict) -> tuple[str, str]:
    if fact.get("status", "active") == "blocked":
        return "x", "pending"
    t = fact.get("trust")
    if t == "verified":
        return "Y", "ready"
    if t == "staged":
        return "~", "pending"
    if t == "disputed":
        return "x", "pending"
    if t == "derived":
        deps = fact.get("depends_on") or []
        ok = bool(deps) and all(
            d in facts and facts[d].get("trust") == "verified"
            and facts[d].get("status", "active") == "active"
            for d in deps
        )
        return ("Y*", "ready") if ok else ("~*", "pending")
    return "?", "pending"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    facts = load_facts()
    cols = columns()

    rows = [d for d in facts.values() if d.get("status", "active") != "superseded"]
    rows.sort(key=lambda d: d["id"])

    ready = {c: 0 for c in cols}
    pending = {c: 0 for c in cols}
    anchors = []

    table = ["| Fact | trust | " + " | ".join(cols) + " |",
             "|---|---|" + "---|" * len(cols)]
    for d in rows:
        tags = set(d.get("criterion_tags") or [])
        m, bucket = mark(d, facts)
        cells, lit = [], 0
        for c in cols:
            if c in tags:
                cells.append(m)
                (ready if bucket == "ready" else pending)[c] += 1
                if c != "FM":
                    lit += 1
            else:
                cells.append("")
        table.append(f"| {d['id']} | {d.get('trust', '?')} | " + " | ".join(cells) + " |")
        if lit >= 2:
            anchors.append(d["id"])

    table.append("| **ready** | | " + " | ".join(str(ready[c]) for c in cols) + " |")
    table.append("| **pending** | | " + " | ".join(str(pending[c]) for c in cols) + " |")

    thin = [c for c in cols if c != "FM" and ready[c] == 0]

    parts = [
        "# Evidence x Criteria Matrix - Final Merits skeleton",
        f"_Generated {date.today().isoformat()}. Read-only planning artifact, not a drafting input._",
        "",
        "Legend: Y verified | ~ staged | Y* derived (inputs verified) | ~* derived (input unverified) | x blocked/disputed",
        "ready = usable now (Y, Y*) | pending = found, awaiting verification (~, ~*, x)",
        "",
        "\n".join(table),
        "",
        f"**Weave anchors** (light >=2 criteria, excl. FM): {', '.join(anchors) if anchors else 'none yet'}",
        f"**Thin columns** (no usable evidence yet): {', '.join(thin) if thin else 'none'}",
    ]
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")

    print(f"matrix -> {OUT.relative_to(REPO)}")
    print(f"  facts: {len(rows)} | columns: {', '.join(cols)}")
    print(f"  weave anchors: {', '.join(anchors) if anchors else 'none yet'}")
    print(f"  thin columns: {', '.join(thin) if thin else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
