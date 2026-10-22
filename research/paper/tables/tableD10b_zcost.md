Table — The null-side cost z(t) − z_α of each method: the key quantiles of the threshold in z-units, the abstaining keys counted. Extracted verbatim from the Study 3 report's generated Table 11 (block `zcost` of `outputs/study3_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R08); the report's own column note follows the table.

| Family | Rule | h | Method | Units | Abstaining keys (sum) | Cost q05, median over units | Cost q50, median | Cost q95, median | Cost q50, range over units | κ̂ median (range) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kgw | raw | 1 | empirical | 20 | 0 | — | 1.036 | — | 0.75–1.61 | 25.89 (9.44–246.38) |
| kgw | raw | 1 | pooled | 20 | 0 | — | 0.675 | — | 0.46–0.89 | — |
| kgw | raw | 1 | conformal@500 | 20 | 0 | 0.024 | 0.602 | 1.398 | 0.46–1.04 | — |
| kgw | raw | 1 | conformal@1000 | 20 | 0 | 0.168 | 0.602 | 1.181 | 0.31–0.89 | — |
| kgw | raw | 1 | conformal@2000 | 20 | 0 | 0.168 | 0.602 | 1.181 | 0.31–0.89 | — |
| kgw | raw | 1 | conformal@5000 | 20 | 0 | 0.168 | 0.602 | 1.036 | 0.31–0.89 | — |
| kgw | raw | 1 | tolerance@500 | 20 | 0 | 0.458 | 1.253 | 2.269 | 0.89–1.76 | — |
| kgw | raw | 1 | tolerance@1000 | 20 | 0 | 0.458 | 1.036 | 1.904 | 0.75–1.33 | — |
| kgw | raw | 1 | tolerance@2000 | 20 | 0 | 0.313 | 0.891 | 1.398 | 0.60–1.18 | — |
| kgw | raw | 1 | tolerance@5000 | 20 | 0 | 0.313 | 0.747 | 1.181 | 0.46–1.04 | — |
| kgw | raw | 2 | empirical | 20 | 0 | — | 0.644 | — | 0.35–0.93 | 6.73 (2.72–17.97) |
| kgw | raw | 2 | pooled | 20 | 0 | — | 0.354 | — | 0.21–0.50 | — |
| kgw | raw | 2 | conformal@500 | 20 | 0 | −0.080 | 0.354 | 0.789 | 0.21–0.50 | — |
| kgw | raw | 2 | conformal@1000 | 20 | 0 | 0.065 | 0.354 | 0.644 | 0.21–0.50 | — |
| kgw | raw | 2 | conformal@2000 | 20 | 0 | 0.065 | 0.354 | 0.644 | 0.21–0.50 | — |
| kgw | raw | 2 | conformal@5000 | 20 | 0 | 0.065 | 0.354 | 0.644 | 0.21–0.50 | — |
| kgw | raw | 2 | tolerance@500 | 20 | 0 | 0.354 | 0.862 | 1.659 | 0.64–1.08 | — |
| kgw | raw | 2 | tolerance@1000 | 20 | 0 | 0.354 | 0.644 | 1.151 | 0.50–0.93 | — |
| kgw | raw | 2 | tolerance@2000 | 20 | 0 | 0.209 | 0.499 | 0.789 | 0.35–0.79 | — |
| kgw | raw | 2 | tolerance@5000 | 20 | 0 | 0.209 | 0.427 | 0.717 | 0.35–0.64 | — |
| kgw | distinct | 1 | empirical | 20 | 0 | — | 0.296 | — | 0.21–0.36 | 2.29 (1.79–2.78) |
| kgw | distinct | 1 | pooled | 20 | 0 | — | 0.053 | — | 0.05–0.06 | — |
| kgw | distinct | 1 | conformal@500 | 20 | 0 | −0.314 | 0.054 | 0.463 | 0.01–0.08 | — |
| kgw | distinct | 1 | conformal@1000 | 20 | 0 | −0.272 | 0.036 | 0.375 | 0.01–0.06 | — |
| kgw | distinct | 1 | conformal@2000 | 20 | 0 | −0.243 | 0.032 | 0.327 | −0.01–0.05 | — |
| kgw | distinct | 1 | conformal@5000 | 20 | 0 | −0.222 | 0.030 | 0.296 | −0.01–0.05 | — |
| kgw | distinct | 1 | tolerance@500 | 20 | 0 | −0.028 | 0.427 | 0.992 | 0.39–0.46 | — |
| kgw | distinct | 1 | tolerance@1000 | 20 | 0 | −0.042 | 0.313 | 0.697 | 0.28–0.34 | — |
| kgw | distinct | 1 | tolerance@2000 | 20 | 0 | −0.087 | 0.208 | 0.510 | 0.16–0.22 | — |
| kgw | distinct | 1 | tolerance@5000 | 20 | 0 | −0.130 | 0.122 | 0.399 | 0.10–0.14 | — |
| kgw | distinct | 2 | empirical | 20 | 0 | — | 0.177 | — | 0.14–0.25 | 1.63 (1.49–2.01) |
| kgw | distinct | 2 | pooled | 20 | 0 | — | 0.057 | — | 0.04–0.06 | — |
| kgw | distinct | 2 | conformal@500 | 20 | 0 | −0.212 | 0.077 | 0.405 | 0.06–0.08 | — |
| kgw | distinct | 2 | conformal@1000 | 20 | 0 | −0.158 | 0.059 | 0.305 | 0.04–0.08 | — |
| kgw | distinct | 2 | conformal@2000 | 20 | 0 | −0.111 | 0.056 | 0.250 | 0.04–0.06 | — |
| kgw | distinct | 2 | conformal@5000 | 20 | 0 | −0.077 | 0.053 | 0.197 | 0.03–0.06 | — |
| kgw | distinct | 2 | tolerance@500 | 20 | 0 | 0.060 | 0.460 | 0.967 | 0.43–0.48 | — |
| kgw | distinct | 2 | tolerance@1000 | 20 | 0 | 0.063 | 0.335 | 0.662 | 0.31–0.35 | — |
| kgw | distinct | 2 | tolerance@2000 | 20 | 0 | 0.038 | 0.229 | 0.438 | 0.21–0.23 | — |
| kgw | distinct | 2 | tolerance@5000 | 20 | 0 | 0.014 | 0.145 | 0.295 | 0.12–0.15 | — |
