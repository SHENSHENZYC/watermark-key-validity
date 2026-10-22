Table — Study 4 (the power side): the pre-registered rules W1, W2 and W3 with their pass conditions, observed counts and verdicts; W2's failure is every row unresolved (Tables D6a and D6b). Extracted verbatim from the Study 4 report's generated Table 2 (block `rules` of `outputs/study4_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R10); the report's own column note follows the table.

| rule | pre-registered pass condition (protocol §6, §9) | observed | verdict |
|---|---|---|---|
| W1 (the cost is the threshold shift alone) | at least 2 of 3 cells consistent and none inconsistent (the key-median cost's 95% key-bootstrap interval inside the predicted median ± the cell's tolerance) | 2 consistent, 0 inconsistent, 1 unresolved of 3 | PASS |
| W2 (the dispersion of power changes in the predicted direction) | at least 5 of 6 rows agree and none disagrees (raw: the ratio's interval below 1; distinct: inside [2/3, 3/2]; the prompt-conditioned target) | 0 agree, 0 disagree, 6 unresolved of 6 | FAIL |
| W3 (Study 3's predictor out of sample on the model's null law) | at least 30 resolved rows and at least 80% of the resolved consistent (the ratio's interval inside [2/3, 3/2]) | 240 candidate, 221 eligible, 216 resolved, 216 consistent, 0 inconsistent, 5 unresolved | PASS |
