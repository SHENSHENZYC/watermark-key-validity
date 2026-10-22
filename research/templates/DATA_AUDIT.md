# <Source> — data audit v<X.Y>

Date: <YYYY-MM-DD>. **Verdict: <PASS | PARTIAL | FAIL>.** Proceed rule (fixed before download): <…>.

## Terms of use (checked before any download)
| Source | Clause (quoted, with link) | What it means for collection and publication |
|---|---|---|

## Access census
| Source | Periods available | Format | Access (open / manual only / blocked) |
|---|---|---|---|

## Freeze
Manifest: `outputs/<…>.json` (URL, date, size, SHA-256). Raw files are git-ignored. Manual downloads are verified by content hash.

## Parse and reconcile
Schema asserted; reconciliation rule; exclusions **counted, not patched**; wrong-period rows dropped.

## Profile
Counts, spans, gaps, duplicates; holdout assertion.

## Definitions found in notes
<window, basis, horizon, restatements: anything that changes what a number means>

## Limitations and not done
