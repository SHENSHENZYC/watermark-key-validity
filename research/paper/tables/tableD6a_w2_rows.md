Table — W2 by prompt cell and rule (a stated design limit): the two-way between-key components of power before and after per-key calibration, the observed SDs, the binomial proxy, the ratio R_pow with its paired key-bootstrap interval for the prompt-conditioned target, the predicted side and the class (every row unresolved). Extracted verbatim from the Study 4 report's generated Table 4 (block `w2_rows` of `outputs/study4_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R10); the report's own column note follows the table.

| prompt cell | rule | K | SD_b nominal (two-way, pp) | SD_b conformal@5000 (pp) | observed SD nominal (pp) | observed SD conformal (pp) | proxy SD nominal (pp) | proxy SD conformal (pp) | R_pow | 95% key-bootstrap interval | finite resamples | predicted side | class | key-mean power nominal (pp) | key-mean power conformal (pp) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| news/en@256 | raw | 100 | 6.39 | 6.14 | 9.19 | 9.29 | 6.36 | 6.10 | 0.961 | [0.708, 1.271] | 200 | below_1 | unresolved | 66.2 | 52.2 |
| news/en@256 | distinct | 100 | 4.68 | 4.07 | 8.29 | 7.94 | 4.63 | 4.03 | 0.870 | [0.342, 1.737] | 199 | inside_band | unresolved | 60.9 | 61.9 |
| stackexchange/en@256 | raw | 100 | 4.97 | 4.36 | 8.49 | 7.77 | 4.83 | 4.29 | 0.876 | [0.334, 1.860] | 199 | below_1 | unresolved | 56.3 | 30.4 |
| stackexchange/en@256 | distinct | 100 | 3.14 | 2.12 | 7.61 | 7.24 | 2.85 | 1.64 | 0.676 | [0.000, 1.565] | 181 | inside_band | unresolved | 48.2 | 46.6 |
| wikipedia/en@256 | raw | 100 | 9.55 | 6.95 | 11.70 | 9.46 | 9.43 | 6.85 | 0.728 | [0.519, 1.002] | 200 | below_1 | unresolved | 53.4 | 32.0 |
| wikipedia/en@256 | distinct | 100 | 6.55 | 4.60 | 9.44 | 8.23 | 6.33 | 4.25 | 0.703 | [0.329, 0.945] | 200 | inside_band | unresolved | 47.0 | 47.9 |
