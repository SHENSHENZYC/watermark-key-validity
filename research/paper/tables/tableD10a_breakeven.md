Table — The break-even calibration size on the diagonal: the smallest N_cal at which per-key conformal calibration's across-key dispersion falls below the nominal test's (paired key bootstrap). Extracted verbatim from the Study 3 report's generated Table 12 (block `breakeven` of `outputs/study3_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R08); the report's own column note follows the table.

| Family | Rule | h | Method | Units | break-even at N_cal = 500 | break-even at N_cal = 1,000 | break-even at N_cal = 2,000 | break-even at N_cal = 5,000 | never (within the grid) | Median R_obs at N_cal = 5,000 | Range | Median R_pred at 5,000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kgw | raw | 0 | per-key conformal | 20 | 20 | 0 | 0 | 0 | 0 | 0.014 | 0.01–0.02 | 0.015 |
| kgw | raw | 0 | per-key tolerance | 20 | 20 | 0 | 0 | 0 | 0 | 0.012 | 0.01–0.02 | 0.014 |
| kgw | raw | 1 | per-key conformal | 20 | 20 | 0 | 0 | 0 | 0 | 0.125 | 0.06–0.24 | 0.150 |
| kgw | raw | 1 | per-key tolerance | 20 | 20 | 0 | 0 | 0 | 0 | 0.110 | 0.05–0.21 | 0.133 |
| kgw | raw | 2 | per-key conformal | 20 | 8 | 3 | 6 | 3 | 0 | 0.464 | 0.15–0.86 | 0.601 |
| kgw | raw | 2 | per-key tolerance | 20 | 16 | 4 | 0 | 0 | 0 | 0.400 | 0.13–0.76 | 0.531 |
| kgw | distinct | 0 | per-key conformal | 20 | 20 | 0 | 0 | 0 | 0 | 0.094 | 0.08–0.13 | 0.120 |
| kgw | distinct | 0 | per-key tolerance | 20 | 20 | 0 | 0 | 0 | 0 | 0.083 | 0.07–0.11 | 0.106 |
| kgw | distinct | 1 | per-key conformal | 20 | 6 | 13 | 1 | 0 | 0 | 0.388 | 0.27–0.61 | 0.441 |
| kgw | distinct | 1 | per-key tolerance | 20 | 19 | 1 | 0 | 0 | 0 | 0.342 | 0.24–0.54 | 0.390 |
| kgw | distinct | 2 | per-key conformal | 20 | 0 | 1 | 6 | 6 | 7 | 0.873 | 0.46–1.18 | 1.025 |
| kgw | distinct | 2 | per-key tolerance | 20 | 2 | 5 | 2 | 8 | 3 | 0.780 | 0.39–1.05 | 0.906 |
| gumbel | raw | 0 | per-key conformal | 20 | 20 | 0 | 0 | 0 | 0 | 0.015 | 0.01–0.02 | 0.015 |
| gumbel | raw | 0 | per-key tolerance | 20 | 20 | 0 | 0 | 0 | 0 | 0.013 | 0.01–0.02 | 0.014 |
| gumbel | raw | 1 | per-key conformal | 20 | 20 | 0 | 0 | 0 | 0 | 0.128 | 0.05–0.29 | 0.150 |
| gumbel | raw | 1 | per-key tolerance | 20 | 20 | 0 | 0 | 0 | 0 | 0.113 | 0.04–0.25 | 0.133 |
| gumbel | raw | 2 | per-key conformal | 20 | 8 | 2 | 3 | 6 | 1 | 0.486 | 0.13–0.95 | 0.601 |
| gumbel | raw | 2 | per-key tolerance | 20 | 10 | 5 | 4 | 1 | 0 | 0.431 | 0.12–0.85 | 0.531 |
| gumbel | distinct | 0 | per-key conformal | 20 | 20 | 0 | 0 | 0 | 0 | 0.117 | 0.08–0.16 | 0.120 |
| gumbel | distinct | 0 | per-key tolerance | 20 | 20 | 0 | 0 | 0 | 0 | 0.105 | 0.07–0.14 | 0.106 |
| gumbel | distinct | 1 | per-key conformal | 20 | 6 | 11 | 2 | 1 | 0 | 0.391 | 0.27–0.71 | 0.441 |
| gumbel | distinct | 1 | per-key tolerance | 20 | 19 | 0 | 1 | 0 | 0 | 0.344 | 0.24–0.63 | 0.390 |
| gumbel | distinct | 2 | per-key conformal | 20 | 0 | 0 | 3 | 8 | 9 | 0.917 | 0.54–1.29 | 1.025 |
| gumbel | distinct | 2 | per-key tolerance | 20 | 1 | 5 | 2 | 7 | 5 | 0.808 | 0.47–1.14 | 0.906 |
