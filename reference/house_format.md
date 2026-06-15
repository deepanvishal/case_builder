# House Format — EB-1A RFE response (single source of format truth)

STATUS: All drafting/synthesis agents load this and match it. Defines the
USCIS-facing format of the Final Merits section so it is visually and structurally
identical to Parts A, B, C. <...> = confirm against the existing Part C .docx.

## 1. Voice and register
- Third person throughout: "the Petitioner", "he". Never first person, never "I/we".
- Formal, declarative, evidence-led. No conclusory or categorical language
  (world-class, groundbreaking, leading, widely adopted). Standing is shown with
  ranks, percentiles, counts, and exhibit citations — never asserted with adjectives.
- Tables over narrative for any quantitative comparison. Prose carries argument and
  legal tie; tables carry numbers.

## 2. Section structure (Final Merits = package section 9)
Mirror the per-criterion drafts' pattern:
1. Section heading (see numbering) stating the determination at issue.
2. The governing standard in plain language, tracking the regulation/Policy Manual
   ("The final merits determination requires (1)... (2)...").
3. The woven evidence argument, organized by the totality threads (sustained
   acclaim, top-of-field, cross-criterion reinforcement), each claim exhibit-cited.
4. Explicit tie to the legal standard (Kazarian step two; Chawathe preponderance),
   citing authorities from legal_framework.md.
5. A closing statement: the whole record, more likely than not, establishes
   sustained acclaim and top-of-field standing.

## 3. Numbering and headings
- Decimal section numbering consistent with Parts A/B (e.g. "9.", "9.1", "9.2").
- Headings: navy, bold. <heading font + sizes: confirm from Part C>.
- Body: <font, size, line spacing, margins: confirm from Part C>.
- Running header + footer with page numbers, matching Parts A/B/C.

## 4. Exhibit and citation conventions
- The USCIS-facing document cites EXHIBITS, not ledger IDs. During drafting, every
  factual claim carries its ledger ID (e.g. HS-01); at formatting these map to the
  exhibit citation via the ledger's `src.exhibit`.
- Inline exhibit citation form: "(Exhibit E-3, p.2)". Every figure, date, and
  quantitative claim carries one. No claim without an exhibit cite.
- Public sources (URLs) go in numbered footnotes, as in the petition letter — not
  inline in the body.
- Legal authorities: full citation on first use, case name italicized
  (e.g. *Matter of Chawathe*, 25 I&N Dec. 369 (AAO 2010)); short form / "Id."
  thereafter.

## 5. Evidentiary tables
- Used for comparator/quantitative evidence (e.g. salary percentile, citation counts).
- Green margin-highlight styling consistent with Part C.
- Columns: claim/metric | value (number, unit, period) | source (Exhibit + page).
- Objective values only — no categorical or hedged language inside a table cell.
- Every value traces to a verified ledger fact / exhibit.

## 6. Do-not
- No first person, no rhetorical or conclusory adjectives, no undated claims.
- No figure, peer group, or field description that diverges from definitions.yml.
- No inline raw URLs in body text — footnote them.
