"""Build the curated context pack for a section (default: Final Merits).

Selects the verified ledger facts tagged for the section, plus the RFE governing
language and the single-source definitions, into one small markdown pack so an
agent never sees the full corpus.

Run: python gates/curate.py [TAG]      (TAG default: FM)
Writes: work/<tag>/context_pack.md
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "corpus" / "ledger"
DEFINITIONS = REPO / "corpus" / "definitions.yml"
RFE = REPO / "case" / "rfe.md"

INCLUDE_TRUST = {"verified", "derived"}


def load_facts() -> list[dict]:
    facts = []
    for f in sorted(LEDGER.glob("*.yml")):
        if f.name.startswith("_"):
            continue
        try:
            d = yaml.safe_load(f.read_text())
        except yaml.YAMLError:
            print(f"  skip (invalid YAML): {f.name}")
            continue
        if isinstance(d, dict):
            facts.append(d)
    return facts


def render_fact(d: dict) -> str:
    src = d.get("src") or {}
    if isinstance(src, dict):
        loc = src.get("exhibit") or src.get("file") or "derived"
        page = src.get("page") or src.get("locus")
        cite = f"{loc}" + (f", {page}" if page else "")
    else:
        cite = str(src)
    val = d.get("value", "")
    unit = d.get("unit")
    val = f"{val} {unit}" if unit else f"{val}"
    lines = [
        f"### {d.get('id', '?')} — {d.get('label', '')}",
        f"- value: {val}",
        f"- source: {cite}  ({d.get('src_type', '?')}, trust={d.get('trust', '?')})",
        f"- criteria: {', '.join(d.get('criterion_tags', []))}",
    ]
    if d.get("src_type") == "derived" and isinstance(d.get("derivation"), dict):
        deriv = d["derivation"]
        lines.append(f"- derived: {deriv.get('method', '?')} of {deriv.get('inputs', [])}")
    return "\n".join(lines)


def main(tag: str) -> int:
    out_dir = REPO / "work" / tag.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "context_pack.md"

    facts = load_facts()
    included, held = [], []
    for d in facts:
        if tag not in d.get("criterion_tags", []):
            continue
        if d.get("trust") in INCLUDE_TRUST and d.get("status", "active") == "active":
            included.append(d)
        else:
            held.append(d)

    defs_text = DEFINITIONS.read_text() if DEFINITIONS.exists() else "(definitions.yml missing)"
    rfe_text = RFE.read_text() if RFE.exists() else "(case/rfe.md missing)"

    parts = [
        f"# Context Pack — {tag}",
        f"_Generated {date.today().isoformat()}. Curated inputs only — not the full corpus._",
        "",
        "## Definitions (single source of truth — use VERBATIM)",
        "```yaml",
        defs_text.rstrip(),
        "```",
        "",
        "## RFE — governing language",
        rfe_text.rstrip(),
        "",
        f"## Evidence set ({len(included)} verified facts tagged {tag})",
    ]
    if included:
        parts += [render_fact(d) + "\n" for d in included]
    else:
        parts.append(f"_No verified {tag}-tagged facts in the ledger yet._")
    out.write_text("\n".join(parts) + "\n")

    print(f"context pack -> {out.relative_to(REPO)}")
    print(f"  included: {len(included)} verified/derived {tag}-tagged facts")
    if held:
        print(f"  held back ({len(held)} {tag}-tagged but not verified/active):")
        for d in held:
            print(f"    - {d.get('id', '?')}: trust={d.get('trust', '?')} status={d.get('status', 'active')}")
    if "<" in defs_text:
        print("  WARNING: definitions.yml still has unfilled placeholders (<...>).")
    if not RFE.exists() or len(rfe_text.strip()) < 50:
        print("  WARNING: case/rfe.md looks empty/stub — totality language missing.")
    return 0


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "FM"
    sys.exit(main(tag))
