Table — What one fixed key faces on real null text: per-key levels at the nominal α = 1% under the Llama-3.2 tokenizer at h = 1 and each cell's longest length (K = 1,000 keys on the N = 10,000 realised texts of each cell; Gutenberg's window starts at token 1,000). Key-mean, median and 99% key in %, the 99% key with its crossed key-by-document 95% interval; "worst" is the worst of the sampled keys, never a population extreme. The Qwen2.5 rows and every quantile's crossed interval are in Table D12a (Gumbel-max in Table D12b).

| Corpus cell | KGW raw: key-mean | median key | 99% key [crossed 95% CI] | keys > 2α (%) | KGW distinct: key-mean | median key | 99% key [CI] | worst sampled key | keys > 2α (%) | Gumbel-max distinct: 99% key [CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| news/en@256 | 2.52 | 2.27 | 6.20 [5.63, 7.10] | 61.4 | 1.12 | 1.03 | 2.80 [2.50, 3.01] | 3.61 | 6.1 | 2.54 [2.32, 3.09] |
| wikipedia/en@256 | 3.31 | 2.95 | 9.13 [8.44, 10.15] | 82.0 | 1.16 | 1.07 | 3.16 [2.73, 3.53] | 3.94 | 6.8 | 2.52 [2.38, 3.07] |
| stackexchange/en@256 | 3.65 | 3.48 | 6.60 [6.13, 7.42] | 98.9 | 1.17 | 1.10 | 2.50 [2.31, 2.90] | 3.54 | 4.5 | 2.22 [2.08, 2.55] |
| wikipedia/en@1024 | 6.66 | 5.56 | 23.03 [19.97, 27.67] | 97.5 | 1.09 | 0.96 | 3.10 [2.81, 3.57] | 4.53 | 7.3 | 2.76 [2.48, 3.27] |
| gutenberg/en@1024 | 5.65 | 4.33 | 20.71 [17.70, 25.15] | 91.4 | 1.10 | 0.95 | 3.27 [2.93, 3.66] | 6.09 | 8.5 | 2.71 [2.42, 3.14] |
| wikipedia/de@256 | 2.79 | 2.70 | 4.84 [4.64, 5.16] | 87.8 | 1.14 | 1.08 | 2.24 [2.09, 2.45] | 2.69 | 2.3 | 2.05 [1.91, 2.33] |
| wikipedia/ru@256 | 2.92 | 2.52 | 6.35 [6.03, 6.74] | 77.0 | 1.14 | 1.07 | 2.37 [2.17, 2.55] | 2.81 | 2.9 | 2.25 [2.08, 2.42] |
| wikipedia/ar@256 | 3.48 | 3.31 | 6.80 [6.31, 7.38] | 97.8 | 1.14 | 1.08 | 2.43 [2.16, 2.74] | 3.21 | 2.9 | 2.04 [1.91, 2.39] |
| wikipedia/zh@256 | 4.23 | 4.18 | 5.98 [5.75, 6.30] | 100.0 | 1.16 | 1.13 | 1.91 [1.86, 2.06] | 2.19 | 0.5 | 1.67 [1.62, 1.86] |
| wikipedia/ja@256 | 3.80 | 3.67 | 6.79 [6.31, 7.29] | 99.3 | 1.16 | 1.10 | 2.45 [2.20, 2.71] | 3.64 | 3.2 | 2.23 [2.09, 2.40] |
