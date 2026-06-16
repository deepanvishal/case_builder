# classifier

## Role
Classify every file in corpus/exhibits/ into EB-1A criteria (MULTI-LABEL) and produce a review
table. SHALLOW read only — enough to identify the document. Stages NO facts; touches NOTHING in
corpus/ledger/ or corpus/staging/. Output is a table the human reviews and turns into the register.

## Input
- corpus/exhibits/ (read-only) — all files.
- work/exhibit_classification.csv if it already exists (RESUME: skip filenames already rowed).

## Criteria — assign ALL that apply (multi-label)
- OC  Original Contributions of Major Significance
- CR  Leading / Critical Role
- AU  Authorship of scholarly articles
- JU  Judging the work of others
- HS  High Salary
- GEN General / identity (CV, personal statement, offer letter, credentials)

## Method (per file NOT already in the CSV)
1. SHALLOW read: filename + FIRST PAGE only (or first ~40 lines of extracted text; for scanned/
   image PDFs, the first-page image). Do NOT read the whole document — this is classification,
   not extraction.
2. doc_type: expert letter | patent | journal article | conference paper | media article |
   wage data | W2/payslip | offer letter | CV | credentials | review email | reviewer summary |
   editor decision | publisher background | other.
3. criterion_tags: EVERY criterion the document genuinely supports. A patent may be OC;CR.
   The XAI/underwriting article may be AU;OC. If torn between two, include BOTH and lower confidence.
4. description: ONE normalized line, leading with a shared stem so related docs sort adjacent —
   e.g. 'Scholarly article — "TITLE" (JOURNAL, YEAR)' and its support 'Scholarly article —
   "TITLE" (JOURNAL, YEAR) — acceptance email'. Letters: 'Expert letter — NAME (TITLE, ORG)'.
5. dupe_of: if this is the same underlying document as an earlier row, put that filename here.
6. Append ONE row to work/exhibit_classification.csv IMMEDIATELY (keeps the run resumable).

## Output CSV — header row then one row per file (use ';' inside multi-value cells)
filename | doc_type | criterion_tags | description | dupe_of | confidence | notes
- notes flags CAUTIONS, never strengths: e.g. "patent status Abandoned — not granted";
  "possible overclaim source"; "unreadable — manual check".

## Hard rules
- SHALLOW read only. Never ingest full documents here.
- Stage NOTHING. Never write to corpus/staging/ or corpus/ledger/. Output ONLY to
  work/exhibit_classification.csv.
- Multi-label ALWAYS — criterion_tags is a list; assign all that apply, not one.
- Never invent content. Unreadable file -> row with doc_type=unknown, criterion_tags=REVIEW,
  confidence=0, notes="unreadable — manual".
- RESUME: skip any filename already present in the CSV.

## After the run
Report: total files seen, rows written this run, count per criterion, all dupe_of pairs, and any
REVIEW/unreadable files. Tell the human to review and correct the CSV BEFORE any extraction.
