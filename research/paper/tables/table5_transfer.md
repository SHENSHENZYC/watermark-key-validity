Table — Transfer of a per-key conformal threshold (N_cal = 5,000) across text laws and tokenizers: KGW distinct rule, h = 1, α = 0.01; medians over the ordered (calibration cell, evaluation cell) pairs of each class, each pair over K = 1,000 keys on the evaluation cell's N_E texts. The ratio is the observed to the predicted across-key SD (the key-free predictor); T1 counts the pairs whose ratio interval lies inside [2/3, 3/2] among the resolved and eligible pairs of the class at this setting, T2 the material pairs whose observed sign of calibration's effect agrees with the predicted one. A measurement with its own error, not a transfer guarantee; the raw rule and h = 2 by class are in Table D13a, the cross-tokenizer rows in Table D13b, T1 by block in Table D13c, and every ordered pair in the Study 3 report's supplement `tables_pairs_kgw_alpha0.01_full.md` in the companion repository.

| Pair class | Pairs | Key-mean (%) | SD (pp) | 99% key (%) | Keys > 2α (%) | Median SD ratio, observed / predicted | T1 consistent of resolved | T2 agree of material |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| diagonal (own law) | 20 | 1.00 | 0.17 | 1.43 | 0.0 | 0.997 | not eligible (the Beta term is of the order of the floor) | 19 of 19 |
| near-identical pair | 4 | 1.00 | 0.18 | 1.45 | 0.0 | 0.977 | not eligible (the Beta term is of the order of the floor) | 4 of 4 |
| within English | 36 | 1.06 | 0.47 | 2.50 | 4.5 | 1.005 | 36 of 36 (36 eligible) | no material row |
| English–other | 100 | 1.11 | 0.59 | 3.02 | 8.3 | 0.986 | 100 of 100 (100 eligible) | 50 of 50 |
| other–other | 40 | 1.08 | 0.52 | 2.69 | 5.8 | 1.041 | 40 of 40 (40 eligible) | 18 of 18 |
| cross-tokenizer | 200 | 1.11 | 0.61 | 3.14 | 8.3 | 0.995 | ratio median 0.995 (the predictor's check in Appendix D) | — |
