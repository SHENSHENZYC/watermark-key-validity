Table — The remedies on the null side when the calibration law is the deployment law (the diagonal): KGW, γ = 0.25, h = 1, α = 0.01; medians over the 20 (tokenizer, cell) units of K = 1,000 keys on the N_E = 10,000 evaluation texts (Gutenberg 7,122). The share of keys above α is the finite-evaluation estimand, measured and predicted; the reference law's population share is a model quantity. The multiplier arm is read under Proposition 1's prerequisite only (the distinct rule); the empirical plug-in is not AutoMark's test; the null-side cost is the median key's threshold in z-units above z_α (the scheme-level methods' fitted threshold). The h = 2 rows are in Table D8b; every α and every unit are in the Study 3 report's supplement `tables_remedy_full.md` in the companion repository.

| Rule | Method | Key-mean (%) | SD (pp) | 99% key (%) | Keys > α, measured (%) | predicted, finite-evaluation (%) | predicted, population (%) | Median key's cost (z) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw | nominal | 3.355 | 1.363 | 7.81 | 99.8 | 96.9 | 97.2 | 0.00 |
| raw | multiplier 1/β | 0.626 | 0.352 | 1.87 | 10.1 | 1.0 | 1.0 | 0.96 |
| raw | empirical multiplier | 0.425 | 0.261 | 1.34 | 3.1 | 5.3 | 4.9 | 1.04 |
| raw | pooled | 0.891 | 0.466 | 2.50 | 28.4 | 41.4 | 41.6 | 0.67 |
| raw | conformal, N_cal 1,000 | 0.860 | 0.291 | 1.69 | 28.7 | 42.8 | 43.3 | 0.60 |
| raw | conformal, N_cal 5,000 | 0.878 | 0.167 | 1.30 | 20.7 | 46.8 | 48.0 | 0.60 |
| raw | tolerance, N_cal 1,000 | 0.423 | 0.202 | 1.04 | 1.4 | 2.9 | 2.5 | 1.04 |
| raw | tolerance, N_cal 5,000 | 0.681 | 0.145 | 1.07 | 2.3 | 7.6 | 4.6 | 0.75 |
| distinct | nominal | 1.132 | 0.441 | 2.44 | 54.8 | 43.1 | 43.4 | 0.00 |
| distinct | multiplier 1/β | 0.072 | 0.048 | 0.22 | 0.0 | 0.0 | 0.0 | 0.96 |
| distinct | empirical multiplier | 0.521 | 0.240 | 1.33 | 4.5 | 5.5 | 5.0 | 0.30 |
| distinct | pooled | 0.994 | 0.397 | 2.18 | 41.4 | 43.1 | 43.4 | 0.05 |
| distinct | conformal, N_cal 1,000 | 1.002 | 0.332 | 1.95 | 45.4 | 45.3 | 45.9 | 0.04 |
| distinct | conformal, N_cal 5,000 | 0.996 | 0.172 | 1.43 | 45.6 | 47.0 | 48.1 | 0.03 |
| distinct | tolerance, N_cal 1,000 | 0.501 | 0.234 | 1.18 | 3.3 | 3.3 | 2.9 | 0.31 |
| distinct | tolerance, N_cal 5,000 | 0.777 | 0.153 | 1.17 | 7.3 | 7.7 | 4.7 | 0.12 |
