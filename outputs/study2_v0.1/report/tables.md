### rules

| Rule (protocol §9) | Pre-registered criterion | Observed | Verdict |
|---|---|---|---|
| S1 adequacy of the common-factor predictor on real text (primary; KGW, independent colouring, γ = 0.25, raw and distinct rules, h ∈ {1, 2, 3, 4}, every corpus cell, both tokenizers, every length, α = 0.01) | ≥ 30 resolved cells and ≥ 80% of the resolved cells consistent (key-bootstrap ratio interval inside [0.667, 1.50]); eligible when mean M ≥ 30, theory share ≥ 0.75, no σ² flag | candidates 544; eligible 217; resolved 184; consistent 178; inconsistent 6; unresolved 33; share consistent 96.7% | **PASS** |
| S2 the key-mean audit (distinct rule; KGW independent both γ and Gumbel; every α) | no check with a two-sided Hoeffding–KL bound below 1e-06 (per-check false audit ≤ 1e-06; union bound over the checks) | 3,060 checks (0 structural zeros counted separately; KGW 2,040, Gumbel 1,020); flagged 0 (KGW 0, Gumbel 0); smallest bound 1.00; union bound 3.06e-03; normal (ā − μ)/SE: SD 0.985, max \|·\| 3.50, share above 3 0.20% (diagnostic) | **PASS** |
| S3 the exact identities (every live cell; the known-mean variance estimator of q̂ or s̄ against the identity at the realised weights) | no gross failure: \|s₀² − σ²_exact\| ≤ 6·SE + τ; structural zeros ≤ τ | 3,468 checks (0 structural zeros; independent 2,040, fixed 408, Gumbel 1,020); gross failures 0; (s₀² − σ²)/SE: SD 0.944, max \|·\| 3.56; nominal-95% coverage 94.8% of 3468 (diagnostic) | **PASS** |
| S4 H-length on the observed dispersion (per chain: corpus cell × tokenizer × h; KGW independent γ = 0.25, raw rule, α = 0.01) | SD_K(α̂) non-decreasing in L within 2(se_L + se_L′) in every chain (the counts are the result) | 100 chains; holding 76; failing: news/en@256 Llama-3.2 h = 1; news/en@256 Llama-3.2 h = 2; news/en@256 Llama-3.2 h = 3; news/en@256 Llama-3.2 h = 4; news/en@256 Qwen2.5 h = 1; news/en@256 Qwen2.5 h = 4; wikipedia/en@256 Llama-3.2 h = 4; wikipedia/en@256 Qwen2.5 h = 4; stackexchange/en@256 Llama-3.2 h = 4; stackexchange/en@256 Qwen2.5 h = 4; wikipedia/de@256 Llama-3.2 h = 1; wikipedia/de@256 Llama-3.2 h = 4; wikipedia/de@256 Qwen2.5 h = 4; wikipedia/ru@256 Llama-3.2 h = 1; wikipedia/ru@256 Llama-3.2 h = 4; wikipedia/ru@256 Qwen2.5 h = 4; wikipedia/zh@256 Llama-3.2 h = 4; wikipedia/zh@256 Qwen2.5 h = 4; wikipedia/ja@256 Llama-3.2 h = 4; wikipedia/ja@256 Qwen2.5 h = 4; wikipedia/en@1024 Llama-3.2 h = 4; wikipedia/en@1024 Qwen2.5 h = 4; gutenberg/en@1024 Llama-3.2 h = 4; gutenberg/en@1024 Qwen2.5 h = 4 | **FAIL** |
| S5 H-width on the observed dispersion (per chain: corpus cell × tokenizer × rule ∈ {raw, distinct} at the longest length; KGW independent γ = 0.25, α = 0.01) | SD_K(α̂) non-increasing in h within 2(se_h + se_h+1) in every chain (the counts are the result) | 40 chains; holding 40; failing: none | **PASS** |

### s1_by_cell

| Corpus cell | Rule | Candidates | Eligible | Resolved | Consistent | Inconsistent | Unresolved | Ratio range (resolved) | Median ratio | Widths with eligible cells |
|---|---|---|---|---|---|---|---|---|---|---|
| news/en@256 | raw | 24 | 20 | 16 | 14 | 2 | 4 | 0.999–1.65 | 1.26 | 1, 2, 3, 4 |
| news/en@256 | distinct | 24 | 20 | 18 | 18 | 0 | 2 | 1.08–1.35 | 1.20 | 1, 2, 3, 4 |
| wikipedia/en@256 | raw | 24 | 10 | 7 | 6 | 1 | 3 | 1.07–1.66 | 1.27 | 1, 2, 3 |
| wikipedia/en@256 | distinct | 24 | 9 | 8 | 8 | 0 | 1 | 1.16–1.32 | 1.23 | 1, 2 |
| stackexchange/en@256 | raw | 24 | 6 | 6 | 6 | 0 | 0 | 1.02–1.41 | 1.13 | 1 |
| stackexchange/en@256 | distinct | 24 | 6 | 6 | 6 | 0 | 0 | 1.17–1.32 | 1.22 | 1 |
| wikipedia/de@256 | raw | 24 | 9 | 7 | 6 | 1 | 2 | 0.999–1.76 | 1.33 | 1, 2 |
| wikipedia/de@256 | distinct | 24 | 8 | 7 | 7 | 0 | 1 | 1.13–1.35 | 1.21 | 1, 2 |
| wikipedia/ru@256 | raw | 24 | 10 | 8 | 8 | 0 | 2 | 1.10–1.36 | 1.21 | 1, 2 |
| wikipedia/ru@256 | distinct | 24 | 9 | 9 | 9 | 0 | 0 | 1.13–1.29 | 1.20 | 1, 2 |
| wikipedia/ar@256 | raw | 24 | 11 | 7 | 5 | 2 | 4 | 1.17–1.78 | 1.35 | 1, 2, 3 |
| wikipedia/ar@256 | distinct | 24 | 9 | 7 | 7 | 0 | 2 | 1.22–1.33 | 1.25 | 1, 2 |
| wikipedia/zh@256 | raw | 24 | 7 | 6 | 6 | 0 | 1 | 1.00–1.36 | 1.20 | 1, 2 |
| wikipedia/zh@256 | distinct | 24 | 6 | 6 | 6 | 0 | 0 | 1.16–1.30 | 1.21 | 1 |
| wikipedia/ja@256 | raw | 24 | 10 | 8 | 8 | 0 | 2 | 1.03–1.30 | 1.18 | 1, 2 |
| wikipedia/ja@256 | distinct | 24 | 9 | 8 | 8 | 0 | 1 | 1.16–1.38 | 1.22 | 1, 2 |
| wikipedia/en@1024 | raw | 40 | 20 | 15 | 15 | 0 | 5 | 0.983–1.32 | 1.20 | 1, 2, 3 |
| wikipedia/en@1024 | distinct | 40 | 15 | 14 | 14 | 0 | 1 | 1.06–1.31 | 1.16 | 1, 2 |
| gutenberg/en@1024 | raw | 40 | 13 | 11 | 11 | 0 | 2 | 0.833–1.19 | 1.05 | 1, 2 |
| gutenberg/en@1024 | distinct | 40 | 10 | 10 | 10 | 0 | 0 | 1.15–1.36 | 1.25 | 1 |

Both tokenizers pooled; candidates = every length of the cell's chain × h ∈ {1, 2, 3, 4}.

### s1_by_tok

| Tokenizer | Rule | Candidates | Eligible | Resolved | Consistent | Inconsistent | Unresolved | Ratio range (resolved) | Median ratio |
|---|---|---|---|---|---|---|---|---|---|
| Llama-3.2 | raw | 136 | 46 | 38 | 36 | 2 | 8 | 0.833–1.78 | 1.13 |
| Llama-3.2 | distinct | 136 | 40 | 38 | 38 | 0 | 2 | 1.06–1.38 | 1.23 |
| Qwen2.5 | raw | 136 | 70 | 53 | 49 | 4 | 17 | 0.947–1.76 | 1.24 |
| Qwen2.5 | distinct | 136 | 61 | 55 | 55 | 0 | 6 | 1.08–1.36 | 1.22 |

### s1_by_h

| Width | Candidates | Eligible | Resolved | Consistent | Inconsistent | Unresolved | Ratio range (resolved) | Median ratio |
|---|---|---|---|---|---|---|---|---|
| h = 1 | 136 | 136 | 115 | 112 | 3 | 21 | 0.999–1.76 | 1.21 |
| h = 2 | 136 | 60 | 51 | 50 | 1 | 9 | 0.833–1.78 | 1.23 |
| h = 3 | 136 | 15 | 14 | 14 | 0 | 1 | 0.999–1.31 | 1.15 |
| h = 4 | 136 | 6 | 4 | 2 | 2 | 2 | 1.15–1.65 | 1.42 |

Both rules, both tokenizers, every corpus cell and length pooled.

### s1_by_hL

| Width | L = 64 | L = 128 | L = 256 | L = 512 | L = 1,024 |
|---|---|---|---|---|---|
| h = 1 | 18 / 21 / 40 of 40 | 40 / 40 / 40 of 40 | 38 / 38 / 40 of 40 | 8 / 8 / 8 of 8 | 8 / 8 / 8 of 8 |
| h = 2 | 16 / 16 / 16 of 40 | 9 / 9 / 15 of 40 | 16 / 17 / 20 of 40 | 4 / 4 / 4 of 8 | 5 / 5 / 5 of 8 |
| h = 3 | 4 / 4 / 4 of 40 | 4 / 4 / 4 of 40 | 4 / 4 / 5 of 40 | 1 / 1 / 1 of 8 | 1 / 1 / 1 of 8 |
| h = 4 | 0 / 2 / 4 of 40 | 2 / 2 / 2 of 40 | 0 / 0 / 0 of 40 | 0 / 0 / 0 of 8 | 0 / 0 / 0 of 8 |

Each entry: consistent / resolved / eligible of the candidate cells (both rules, both tokenizers, every corpus cell whose chain has that length; the @256 cells stop at L = 256). An eligible cell needs mean M ≥ 30 and a theory share ≥ 0.75.

### s1_failures

| Block | Corpus cell | Tokenizer | Family | Rule | h | L | Colouring | γ | α | Status | Ratio [95% CI] | SD obs (pp) | SD pred (pp) | σ_δ = √ρ̄ | Mean M | Theory share | σ² predictor / identities / observed | Key-mean level obs / pred / exact-binomial (%) | Pairwise ratio, subsample 1 / 2 | Pairwise subsampling difference (pp) | Pair-cov CV | Pair-corr q50 / q90 / q99 / max | Simulated-shift ratio | Unit-σ ratio | Keys at 0 / at 1 / distinct levels / keys > 5α |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | news/en@256 | Llama-3.2 | kgw | raw | 4 | 64 | independent | 0.25 | 0.01 | inconsistent | 1.63 [1.53, 1.73] | 0.352 | 0.216 | 0.069 | 60 | 0.780 | 1.01 / 1.01 / 1.01 | 1.60 / 1.03 / 1.54 | 1.46 / 1.44 | 3.27e-03 | 4.59 | 0 / 0 / 0.133 / 0.400 | 1.63 | 1.65 | 0 / 0 / 159 / 0 |
| primary | news/en@256 | Qwen2.5 | kgw | raw | 4 | 64 | independent | 0.25 | 0.01 | inconsistent | 1.65 [1.53, 1.80] | 0.478 | 0.290 | 0.097 | 60 | 0.877 | 1.01 / 1.01 / 1.01 | 1.60 / 1.05 / 1.54 | 1.42 / 1.49 | 0.017 | 2.72 | 0 / 0.033 / 0.150 / 0.450 | 1.63 | 1.67 | 0 / 0 / 203 / 0 |
| primary | wikipedia/ar@256 | Llama-3.2 | kgw | raw | 2 | 256 | independent | 0.25 | 0.01 | inconsistent | 1.78 [1.61, 1.93] | 0.558 | 0.314 | 0.067 | 254 | 0.805 | 1.27 / 1.27 / 1.27 | 2.26 / 1.96 / 1.15 | 1.26 / 1.43 | 0.054 | 11.7 | 0 / 5.29e-03 / 0.026 / 0.854 | 1.76 | 2.71 | 0 / 0 / 213 / 3 |
| primary | wikipedia/ar@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | inconsistent | 1.67 [1.54, 1.78] | 0.870 | 0.522 | 0.144 | 63 | 0.947 | 1.12 / 1.12 / 1.12 | 2.14 / 1.45 / 1.47 | 1.65 / 1.52 | 0.044 | 2.20 | 0 / 0.055 / 0.154 / 0.819 | 1.59 | 2.05 | 0 / 0 / 281 / 15 |
| primary | wikipedia/de@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | inconsistent | 1.76 [1.57, 1.94] | 0.945 | 0.538 | 0.150 | 63 | 0.951 | 1.11 / 1.11 / 1.11 | 2.11 / 1.43 / 1.47 | 1.57 / 1.45 | 0.051 | 2.12 | 0 / 0.059 / 0.208 / 0.667 | 1.65 | 2.13 | 0 / 0 / 300 / 19 |
| primary | wikipedia/en@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | inconsistent | 1.66 [1.53, 1.79] | 1.48 | 0.889 | 0.233 | 63 | 0.981 | 1.10 / 1.10 / 1.10 | 2.25 / 1.52 / 1.47 | 1.41 / 1.39 | 0.013 | 1.28 | 0.029 / 0.123 / 0.262 / 0.568 | 1.55 | 1.97 | 0 / 0 / 365 / 57 |
| primary | gutenberg/en@1024 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.46 [1.37, 1.56] | 0.588 | 0.403 | 0.112 | 63 | 0.914 | 1.11 / 1.11 / 1.11 | 2.02 / 1.41 / 1.47 | 1.49 / 1.48 | 3.17e-03 | 1.91 | 0 / 0.031 / 0.083 / 0.356 | 1.42 | 1.79 | 0 / 0 / 238 / 2 |
| primary | gutenberg/en@1024 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.50 [1.42, 1.57] | 0.632 | 0.422 | 0.115 | 63 | 0.920 | 1.12 / 1.12 / 1.12 | 2.06 / 1.45 / 1.47 | 1.42 / 1.53 | 0.032 | 1.87 | 0 / 0.041 / 0.093 / 0.347 | 1.45 | 1.87 | 0 / 0 / 257 / 2 |
| primary | news/en@256 | Llama-3.2 | kgw | distinct | 4 | 64 | independent | 0.25 | 0.01 | unresolved | 1.58 [1.49, 1.68] | 0.335 | 0.211 | 0.070 | 60 | 0.779 | 0.995 / 0.995 / 0.996 | 1.50 / 1.00 / 1.49 | 1.46 / 1.42 | 7.12e-03 | 4.81 | 0 / 0 / 0.133 / 0.533 | 1.56 | 1.57 | 0 / 0 / 158 / 0 |
| primary | news/en@256 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.34, 1.52] | 0.843 | 0.591 | 0.177 | 63 | 0.964 | 1.05 / 1.05 / 1.05 | 1.81 / 1.27 / 1.47 | 1.29 / 1.26 | 0.012 | 1.46 | 0.015 / 0.072 / 0.214 / 0.899 | 1.37 | 1.57 | 0 / 0 / 304 / 4 |
| primary | news/en@256 | Llama-3.2 | kgw | raw | 2 | 128 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.35, 1.51] | 0.452 | 0.316 | 0.094 | 126 | 0.876 | 1.07 / 1.07 / 1.07 | 1.74 / 1.25 / 1.38 | 1.34 / 1.38 | 0.011 | 2.29 | 0 / 0.022 / 0.087 / 0.605 | 1.41 | 1.63 | 0 / 0 / 197 / 0 |
| primary | news/en@256 | Qwen2.5 | kgw | distinct | 4 | 64 | independent | 0.25 | 0.01 | unresolved | 1.60 [1.47, 1.72] | 0.443 | 0.277 | 0.096 | 60 | 0.871 | 0.991 / 0.991 / 0.992 | 1.48 / 1.00 / 1.49 | 1.46 / 1.48 | 3.54e-03 | 3.21 | 0 / 0.018 / 0.151 / 0.500 | 1.59 | 1.57 | 0 / 0 / 191 / 0 |
| primary | news/en@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.62 [1.47, 1.78] | 1.65 | 1.02 | 0.279 | 63 | 0.987 | 1.04 / 1.04 / 1.03 | 1.98 / 1.38 / 1.47 | 1.43 / 1.46 | 0.021 | 1.08 | 0.051 / 0.154 / 0.318 / 0.696 | 1.46 | 1.72 | 0 / 0 / 378 / 62 |
| primary | news/en@256 | Qwen2.5 | kgw | raw | 2 | 128 | independent | 0.25 | 0.01 | unresolved | 1.46 [1.36, 1.56] | 0.816 | 0.560 | 0.165 | 126 | 0.959 | 1.07 / 1.07 / 1.06 | 1.77 / 1.31 / 1.38 | 1.35 / 1.46 | 0.046 | 1.24 | 0.016 / 0.055 / 0.135 / 0.566 | 1.35 | 1.65 | 0 / 0 / 281 / 8 |
| primary | wikipedia/ar@256 | Llama-3.2 | kgw | distinct | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.41 [1.32, 1.50] | 0.316 | 0.225 | 0.075 | 60 | 0.804 | 0.994 / 0.994 / 0.995 | 1.29 / 1.00 / 1.28 | 1.40 / 1.29 | 0.019 | 2.90 | 0 / 0.017 / 0.053 / 0.633 | 1.41 | 1.39 | 0 / 0 / 151 / 0 |
| primary | wikipedia/ar@256 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.48 [1.40, 1.56] | 0.426 | 0.287 | 0.078 | 63 | 0.835 | 1.11 / 1.11 / 1.11 | 2.02 / 1.39 / 1.47 | 1.41 / 1.25 | 0.038 | 3.43 | 0 / 0.015 / 0.063 / 0.772 | 1.47 | 1.82 | 0 / 0 / 186 / 0 |
| primary | wikipedia/ar@256 | Qwen2.5 | kgw | distinct | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.33, 1.54] | 0.484 | 0.338 | 0.119 | 59 | 0.913 | 0.986 / 0.986 / 0.987 | 1.29 / 1.00 / 1.28 | 1.22 / 1.16 | 0.020 | 1.92 | 0 / 0.050 / 0.117 / 0.770 | 1.40 | 1.39 | 0 / 0 / 198 / 0 |
| primary | wikipedia/ar@256 | Qwen2.5 | kgw | raw | 2 | 128 | independent | 0.25 | 0.01 | unresolved | 1.55 [1.44, 1.67] | 0.540 | 0.348 | 0.094 | 126 | 0.882 | 1.12 / 1.12 / 1.12 | 1.97 / 1.44 / 1.38 | 1.37 / 1.26 | 0.035 | 2.96 | 0 / 0.023 / 0.080 / 0.678 | 1.52 | 1.95 | 0 / 0 / 211 / 1 |
| primary | wikipedia/ar@256 | Qwen2.5 | kgw | raw | 2 | 256 | independent | 0.25 | 0.01 | unresolved | 1.54 [1.42, 1.65] | 0.869 | 0.566 | 0.123 | 254 | 0.936 | 1.29 / 1.29 / 1.29 | 2.44 / 2.08 / 1.15 | 1.21 / 1.19 | 0.015 | 3.19 | 0 / 0.034 / 0.122 / 0.801 | 1.50 | 2.41 | 0 / 0 / 299 / 16 |
| primary | wikipedia/ar@256 | Qwen2.5 | kgw | raw | 3 | 256 | independent | 0.25 | 0.01 | unresolved | 1.50 [1.39, 1.60] | 0.413 | 0.276 | 0.068 | 253 | 0.800 | 1.16 / 1.16 / 1.16 | 1.65 / 1.54 / 1.04 | 1.28 / 1.14 | 0.039 | 6.83 | 0 / 7.12e-03 / 0.043 / 0.744 | 1.48 | 1.96 | 0 / 0 / 181 / 0 |
| primary | wikipedia/de@256 | Qwen2.5 | kgw | distinct | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.30, 1.57] | 0.492 | 0.345 | 0.121 | 60 | 0.917 | 0.985 / 0.985 / 0.985 | 1.29 / 1.00 / 1.27 | 1.38 / 1.33 | 0.013 | 1.91 | 0 / 0.035 / 0.134 / 0.353 | 1.38 | 1.38 | 0 / 0 / 200 / 1 |
| primary | wikipedia/de@256 | Qwen2.5 | kgw | raw | 1 | 256 | independent | 0.25 | 0.01 | unresolved | 1.52 [1.40, 1.68] | 1.82 | 1.20 | 0.230 | 255 | 0.983 | 1.37 / 1.37 / 1.37 | 3.25 / 2.56 / 1.28 | 1.54 / 1.42 | 0.098 | 1.48 | 0.017 / 0.080 / 0.201 / 0.679 | 1.42 | 2.48 | 0 / 0 / 429 / 130 |
| primary | wikipedia/de@256 | Qwen2.5 | kgw | raw | 2 | 128 | independent | 0.25 | 0.01 | unresolved | 1.46 [1.37, 1.53] | 0.434 | 0.297 | 0.083 | 126 | 0.850 | 1.10 / 1.10 / 1.10 | 1.86 / 1.35 / 1.38 | 1.43 / 1.32 | 0.026 | 2.85 | 0 / 0.019 / 0.081 / 0.359 | 1.43 | 1.75 | 0 / 0 / 190 / 0 |
| primary | wikipedia/en@1024 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.49 [1.39, 1.60] | 0.778 | 0.521 | 0.151 | 63 | 0.951 | 1.08 / 1.08 / 1.09 | 1.98 / 1.35 / 1.47 | 1.38 / 1.51 | 0.047 | 1.23 | 0.015 / 0.056 / 0.116 / 0.813 | 1.44 | 1.74 | 0 / 0 / 287 / 6 |
| primary | wikipedia/en@1024 | Qwen2.5 | kgw | distinct | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.37 [1.24, 1.53] | 0.681 | 0.498 | 0.176 | 59 | 0.960 | 0.969 / 0.969 / 0.970 | 1.30 / 1.00 / 1.27 | 1.34 / 1.29 | 0.021 | 0.934 | 0.018 / 0.068 / 0.116 / 0.473 | 1.31 | 1.28 | 0 / 0 / 249 / 1 |
| primary | wikipedia/en@1024 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.64 [1.50, 1.79] | 1.40 | 0.848 | 0.227 | 63 | 0.980 | 1.09 / 1.09 / 1.09 | 2.19 / 1.48 / 1.47 | 1.48 / 1.56 | 0.049 | 1.26 | 0.029 / 0.112 / 0.235 / 0.781 | 1.54 | 1.92 | 0 / 0 / 372 / 50 |
| primary | wikipedia/en@1024 | Qwen2.5 | kgw | raw | 1 | 256 | independent | 0.25 | 0.01 | unresolved | 1.39 [1.26, 1.51] | 3.08 | 2.21 | 0.373 | 255 | 0.994 | 1.38 / 1.38 / 1.38 | 3.72 / 2.97 / 1.28 | 1.47 / 1.35 | 0.181 | 0.795 | 0.069 / 0.159 / 0.270 / 0.482 | 1.30 | 2.06 | 0 / 0 / 542 / 226 |
| primary | wikipedia/en@1024 | Qwen2.5 | kgw | raw | 2 | 128 | independent | 0.25 | 0.01 | unresolved | 1.53 [1.42, 1.62] | 0.692 | 0.451 | 0.130 | 126 | 0.934 | 1.09 / 1.09 / 1.09 | 1.88 / 1.36 / 1.38 | 1.36 / 1.26 | 0.038 | 2.00 | 0 / 0.044 / 0.123 / 0.490 | 1.46 | 1.82 | 0 / 0 / 265 / 1 |
| primary | wikipedia/en@1024 | Qwen2.5 | kgw | raw | 2 | 256 | independent | 0.25 | 0.01 | unresolved | 1.41 [1.28, 1.51] | 0.946 | 0.672 | 0.167 | 254 | 0.963 | 1.18 / 1.18 / 1.18 | 2.04 / 1.71 / 1.15 | 1.17 / 1.08 | 0.064 | 1.70 | 9.48e-03 / 0.068 / 0.164 / 0.576 | 1.31 | 1.89 | 0 / 0 / 305 / 12 |
| primary | wikipedia/en@256 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.48 [1.39, 1.60] | 0.793 | 0.537 | 0.153 | 63 | 0.953 | 1.09 / 1.09 / 1.09 | 2.01 / 1.38 / 1.47 | 1.39 / 1.40 | 4.62e-03 | 1.19 | 0.015 / 0.056 / 0.113 / 0.384 | 1.43 | 1.75 | 0 / 0 / 298 / 7 |
| primary | wikipedia/en@256 | Qwen2.5 | kgw | distinct | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.38 [1.26, 1.51] | 0.705 | 0.510 | 0.180 | 59 | 0.962 | 0.968 / 0.968 / 0.969 | 1.31 / 1.00 / 1.27 | 1.34 / 1.36 | 7.52e-03 | 0.916 | 0.032 / 0.069 / 0.126 / 0.459 | 1.32 | 1.30 | 0 / 0 / 248 / 1 |
| primary | wikipedia/en@256 | Qwen2.5 | kgw | raw | 2 | 128 | independent | 0.25 | 0.01 | unresolved | 1.53 [1.43, 1.62] | 0.747 | 0.487 | 0.137 | 126 | 0.942 | 1.10 / 1.10 / 1.11 | 1.95 / 1.41 / 1.38 | 1.35 / 1.42 | 0.029 | 1.82 | 5.99e-03 / 0.050 / 0.138 / 0.340 | 1.44 | 1.85 | 0 / 0 / 272 / 4 |
| primary | wikipedia/en@256 | Qwen2.5 | kgw | raw | 2 | 256 | independent | 0.25 | 0.01 | unresolved | 1.44 [1.34, 1.54] | 1.12 | 0.777 | 0.181 | 254 | 0.969 | 1.22 / 1.22 / 1.22 | 2.25 / 1.88 / 1.15 | 1.19 / 1.35 | 0.109 | 1.55 | 0.012 / 0.077 / 0.186 / 0.488 | 1.33 | 2.03 | 0 / 0 / 335 / 30 |
| primary | wikipedia/ja@256 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.35, 1.51] | 0.636 | 0.444 | 0.112 | 63 | 0.918 | 1.17 / 1.17 / 1.17 | 2.36 / 1.64 / 1.47 | 1.39 / 1.43 | 0.015 | 2.33 | 0 / 0.029 / 0.109 / 0.702 | 1.41 | 1.94 | 0 / 0 / 260 / 3 |
| primary | wikipedia/ja@256 | Qwen2.5 | kgw | distinct | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.30, 1.55] | 0.739 | 0.518 | 0.182 | 58 | 0.963 | 0.967 / 0.967 / 0.967 | 1.31 / 1.00 / 1.28 | 1.40 / 1.40 | 6.06e-04 | 1.12 | 0.033 / 0.055 / 0.175 / 0.633 | 1.33 | 1.34 | 0 / 0 / 256 / 3 |
| primary | wikipedia/ja@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.44 [1.33, 1.54] | 1.10 | 0.759 | 0.188 | 63 | 0.971 | 1.17 / 1.17 / 1.17 | 2.49 / 1.71 / 1.47 | 1.35 / 1.37 | 0.012 | 1.32 | 0.026 / 0.059 / 0.207 / 0.714 | 1.34 | 1.91 | 0 / 0 / 348 / 34 |
| primary | wikipedia/ru@256 | Llama-3.2 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.47 [1.39, 1.54] | 0.901 | 0.614 | 0.177 | 63 | 0.965 | 1.07 / 1.07 / 1.07 | 1.98 / 1.35 / 1.47 | 1.44 / 1.39 | 0.026 | 1.04 | 0.026 / 0.059 / 0.120 / 0.654 | 1.32 | 1.68 | 0 / 0 / 295 / 4 |
| primary | wikipedia/ru@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.43 [1.33, 1.53] | 1.00 | 0.701 | 0.195 | 63 | 0.972 | 1.09 / 1.09 / 1.09 | 2.01 / 1.42 / 1.47 | 1.41 / 1.34 | 0.037 | 1.10 | 0.028 / 0.074 / 0.167 / 0.652 | 1.30 | 1.67 | 0 / 0 / 324 / 17 |
| primary | wikipedia/zh@256 | Qwen2.5 | kgw | raw | 1 | 64 | independent | 0.25 | 0.01 | unresolved | 1.46 [1.38, 1.53] | 0.560 | 0.384 | 0.095 | 63 | 0.890 | 1.18 / 1.18 / 1.18 | 2.39 / 1.65 / 1.47 | 1.41 / 1.42 | 2.49e-03 | 2.52 | 0 / 0.027 / 0.083 / 0.535 | 1.45 | 2.00 | 0 / 0 / 238 / 0 |

### secondary

| Block (descriptive; the same statistic) | Candidates | Eligible | Resolved | Consistent | Inconsistent | Unresolved | Share consistent | Median ratio | Ratio range (resolved) |
|---|---|---|---|---|---|---|---|---|---|
| **primary: KGW independent, γ = 0.25, raw and distinct, h ≥ 1, α = 0.01** | 544 | 217 | 184 | 178 | 6 | 33 | 96.7% | 1.21 | 0.833–1.78 |
| h = 0 (raw and distinct; γ = 0.25) | 136 | 136 | 116 | 116 | 0 | 20 | 100.0% | 1.09 | 0.982–1.33 |
| the first rule (γ = 0.25, every h) | 340 | 97 | 89 | 89 | 0 | 8 | 100.0% | 1.23 | 1.07–1.41 |
| γ = 0.5 (raw and distinct, every h) | 680 | 353 | 348 | 348 | 0 | 5 | 100.0% | 0.984 | 0.786–1.24 |
| the primary cells at α = 0.05 | 544 | 315 | 315 | 315 | 0 | 0 | 100.0% | 1.08 | 0.864–1.29 |
| the primary cells at α = 0.001 | 544 | 94 | 60 | 25 | 35 | 34 | 41.7% | 1.72 | 0.981–2.80 |
| the fixed-size colouring at h = 0 (every rule, both γ) | 408 | 272 | 241 | 241 | 0 | 31 | 100.0% | 1.00 | 0.795–1.33 |
| Gumbel-max, raw and distinct (every h) | 680 | 335 | 195 | 115 | 80 | 140 | 59.0% | 1.33 | 0.842–2.27 |
| Gumbel-max, the first rule | 340 | 78 | 49 | 23 | 26 | 29 | 46.9% | 1.65 | 1.12–2.13 |
| the unit-σ predictor on the primary cells (computed by the builder; §5) | 544 | 213 | 195 | 112 | 83 | 18 | 57.4% | 1.32 | 0.988–2.71 |

### s2_flagged

_No flagged check._

### s3_gross

_No gross failure._

### s4_grid

| Corpus cell | Tokenizer | h = 0 | h = 1 | h = 2 | h = 3 | h = 4 |
|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | holds | FAILS at L = 128 | FAILS at L = 256 | FAILS at L = 256 | FAILS at L = 128 |
| news/en@256 | Qwen2.5 | holds | FAILS at L = 128 | holds | holds | FAILS at L = 128 |
| wikipedia/en@256 | Llama-3.2 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/en@256 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| stackexchange/en@256 | Llama-3.2 | holds | holds | holds | holds | FAILS at L = 128 |
| stackexchange/en@256 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/de@256 | Llama-3.2 | holds | FAILS at L = 128 | holds | holds | FAILS at L = 128 |
| wikipedia/de@256 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/ru@256 | Llama-3.2 | holds | FAILS at L = 128 | holds | holds | FAILS at L = 128 |
| wikipedia/ru@256 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/ar@256 | Llama-3.2 | holds | holds | holds | holds | holds |
| wikipedia/ar@256 | Qwen2.5 | holds | holds | holds | holds | holds |
| wikipedia/zh@256 | Llama-3.2 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/zh@256 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/ja@256 | Llama-3.2 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/ja@256 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/en@1024 | Llama-3.2 | holds | holds | holds | holds | FAILS at L = 128 |
| wikipedia/en@1024 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |
| gutenberg/en@1024 | Llama-3.2 | holds | holds | holds | holds | FAILS at L = 128 |
| gutenberg/en@1024 | Qwen2.5 | holds | holds | holds | holds | FAILS at L = 128 |

S4 per chain (KGW independent γ = 0.25, raw rule, α = 0.01): the observed across-key SD of the level non-decreasing along the cell's length chain within 2(se_L + se_L′).

### s4_failing

| Corpus cell | Tokenizer | h | L chain | SD of the level (pp) ± key-bootstrap SE, along L | ρ̄ along L | Mean M along L |
|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | 1 | 64, 128, 256 | 0.843 ± 0.027 → 0.666 ± 0.021 → 1.17 ± 0.044 | 0.031 → 0.030 → 0.043 | 63 → 127 → 255 |
| news/en@256 | Llama-3.2 | 2 | 64, 128, 256 | 0.490 ± 0.018 → 0.452 ± 0.014 → 0.391 ± 0.011 | 0.015 → 8.79e-03 → 6.34e-03 | 62 → 126 → 254 |
| news/en@256 | Llama-3.2 | 3 | 64, 128, 256 | 0.311 ± 0.015 → 0.294 ± 9.06e-03 → 0.237 ± 6.60e-03 | 8.53e-03 → 4.58e-03 → 2.85e-03 | 61 → 125 → 253 |
| news/en@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.352 ± 0.011 → 0.199 ± 4.75e-03 → 0.213 ± 5.54e-03 | 4.81e-03 → 2.56e-03 → 1.59e-03 | 60 → 124 → 252 |
| news/en@256 | Qwen2.5 | 1 | 64, 128, 256 | 1.65 ± 0.080 → 1.29 ± 0.069 → 1.93 ± 0.087 | 0.078 → 0.070 → 0.089 | 63 → 127 → 255 |
| news/en@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.478 ± 0.019 → 0.272 ± 8.71e-03 → 0.299 ± 8.49e-03 | 9.50e-03 → 5.48e-03 → 3.82e-03 | 60 → 124 → 252 |
| wikipedia/en@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.130 ± 2.70e-03 → 0.106 ± 2.68e-03 → 0.127 ± 2.60e-03 | 6.16e-05 → 5.09e-05 → 5.76e-05 | 60 → 124 → 252 |
| wikipedia/en@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.146 ± 3.40e-03 → 0.124 ± 2.77e-03 → 0.172 ± 3.85e-03 | 4.20e-04 → 5.77e-04 → 9.90e-04 | 60 → 124 → 252 |
| stackexchange/en@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.131 ± 2.79e-03 → 0.113 ± 2.67e-03 → 0.140 ± 2.90e-03 | 5.45e-05 → 4.56e-05 → 5.46e-05 | 60 → 124 → 252 |
| stackexchange/en@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.144 ± 3.74e-03 → 0.112 ± 2.55e-03 → 0.150 ± 3.32e-03 | 1.52e-04 → 1.23e-04 → 1.44e-04 | 60 → 124 → 252 |
| wikipedia/de@256 | Llama-3.2 | 1 | 64, 128, 256 | 0.483 ± 0.012 → 0.422 ± 0.011 → 0.712 ± 0.019 | 9.26e-03 → 0.011 → 0.017 | 63 → 127 → 255 |
| wikipedia/de@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.141 ± 3.18e-03 → 0.120 ± 2.78e-03 → 0.136 ± 2.72e-03 | 3.07e-04 → 2.52e-04 → 2.66e-04 | 60 → 124 → 252 |
| wikipedia/de@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.161 ± 4.24e-03 → 0.125 ± 2.83e-03 → 0.148 ± 3.31e-03 | 5.21e-04 → 4.24e-04 → 4.60e-04 | 60 → 124 → 252 |
| wikipedia/ru@256 | Llama-3.2 | 1 | 64, 128, 256 | 0.901 ± 0.024 → 0.763 ± 0.020 → 1.22 ± 0.029 | 0.031 → 0.030 → 0.037 | 63 → 127 → 255 |
| wikipedia/ru@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.160 ± 3.69e-03 → 0.124 ± 2.78e-03 → 0.154 ± 3.23e-03 | 4.37e-04 → 4.40e-04 → 3.72e-04 | 60 → 124 → 252 |
| wikipedia/ru@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.172 ± 4.61e-03 → 0.138 ± 3.78e-03 → 0.172 ± 4.61e-03 | 5.53e-04 → 7.08e-04 → 7.66e-04 | 60 → 124 → 252 |
| wikipedia/zh@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.129 ± 3.11e-03 → 0.110 ± 2.63e-03 → 0.139 ± 2.96e-03 | 4.60e-05 → 4.31e-05 → 5.58e-05 | 60 → 124 → 252 |
| wikipedia/zh@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.136 ± 3.07e-03 → 0.119 ± 2.47e-03 → 0.157 ± 3.34e-03 | 8.77e-05 → 1.39e-04 → 2.64e-04 | 60 → 124 → 252 |
| wikipedia/ja@256 | Llama-3.2 | 4 | 64, 128, 256 | 0.169 ± 3.56e-03 → 0.126 ± 3.02e-03 → 0.157 ± 3.59e-03 | 5.30e-04 → 3.94e-04 → 3.94e-04 | 60 → 124 → 252 |
| wikipedia/ja@256 | Qwen2.5 | 4 | 64, 128, 256 | 0.203 ± 5.30e-03 → 0.146 ± 3.68e-03 → 0.185 ± 4.92e-03 | 1.19e-03 → 8.88e-04 → 8.99e-04 | 60 → 124 → 252 |
| wikipedia/en@1024 | Llama-3.2 | 4 | 64, 128, 256, 512, 1024 | 0.133 ± 2.77e-03 → 0.104 ± 2.28e-03 → 0.120 ± 2.85e-03 → 0.117 ± 2.45e-03 → 0.118 ± 2.53e-03 | 6.60e-05 → 5.49e-05 → 5.54e-05 → 6.98e-05 → 1.10e-04 | 60 → 124 → 252 → 508 → 1,020 |
| wikipedia/en@1024 | Qwen2.5 | 4 | 64, 128, 256, 512, 1024 | 0.154 ± 3.34e-03 → 0.126 ± 3.27e-03 → 0.166 ± 3.85e-03 → 0.190 ± 4.41e-03 → 0.235 ± 6.45e-03 | 3.93e-04 → 5.13e-04 → 8.01e-04 → 1.44e-03 → 2.70e-03 | 60 → 124 → 252 → 508 → 1,020 |
| gutenberg/en@1024 | Llama-3.2 | 4 | 64, 128, 256, 512, 1024 | 0.140 ± 2.88e-03 → 0.120 ± 2.63e-03 → 0.133 ± 3.06e-03 → 0.134 ± 2.61e-03 → 0.132 ± 2.80e-03 | 1.96e-05 → 3.24e-05 → 5.54e-05 → 1.10e-04 → 1.90e-04 | 60 → 124 → 252 → 508 → 1,020 |
| gutenberg/en@1024 | Qwen2.5 | 4 | 64, 128, 256, 512, 1024 | 0.138 ± 3.02e-03 → 0.121 ± 2.58e-03 → 0.138 ± 3.13e-03 → 0.136 ± 3.14e-03 → 0.139 ± 3.32e-03 | 2.19e-05 → 4.03e-05 → 6.74e-05 → 1.27e-04 → 2.16e-04 | 60 → 124 → 252 → 508 → 1,020 |

### s4_descriptive

| Family | γ | Rule | Chains | Non-decreasing within the tolerance |
|---|---|---|---|---|
| kgw | 0.25 | distinct | 100 | 71 |
| kgw | 0.25 | first | 100 | 67 |
| gumbel | na | raw | 100 | 96 |
| gumbel | na | distinct | 100 | 92 |
| gumbel | na | first | 100 | 90 |
| kgw | 0.5 | raw | 100 | 91 |
| kgw | 0.5 | distinct | 100 | 89 |
| kgw | 0.5 | first | 100 | 89 |

The same monotonicity statement under the other rules, γ = 0.5 and the Gumbel family (descriptive; saturation and non-monotonicity are allowed there; protocol §9).

### s5_grid

| Corpus cell | Tokenizer | raw rule | distinct rule |
|---|---|---|---|
| news/en@256 | Llama-3.2 | holds | holds |
| news/en@256 | Qwen2.5 | holds | holds |
| wikipedia/en@256 | Llama-3.2 | holds | holds |
| wikipedia/en@256 | Qwen2.5 | holds | holds |
| stackexchange/en@256 | Llama-3.2 | holds | holds |
| stackexchange/en@256 | Qwen2.5 | holds | holds |
| wikipedia/de@256 | Llama-3.2 | holds | holds |
| wikipedia/de@256 | Qwen2.5 | holds | holds |
| wikipedia/ru@256 | Llama-3.2 | holds | holds |
| wikipedia/ru@256 | Qwen2.5 | holds | holds |
| wikipedia/ar@256 | Llama-3.2 | holds | holds |
| wikipedia/ar@256 | Qwen2.5 | holds | holds |
| wikipedia/zh@256 | Llama-3.2 | holds | holds |
| wikipedia/zh@256 | Qwen2.5 | holds | holds |
| wikipedia/ja@256 | Llama-3.2 | holds | holds |
| wikipedia/ja@256 | Qwen2.5 | holds | holds |
| wikipedia/en@1024 | Llama-3.2 | holds | holds |
| wikipedia/en@1024 | Qwen2.5 | holds | holds |
| gutenberg/en@1024 | Llama-3.2 | holds | holds |
| gutenberg/en@1024 | Qwen2.5 | holds | holds |

S5 per chain (KGW independent γ = 0.25, the cell's longest length, α = 0.01): the observed across-key SD of the level non-increasing in h within 2(se_h + se_h+1).

### s5_failing

_No failing S5 chain._

### s5_descriptive

| Family | γ | Rule | Chains | Non-increasing within the tolerance |
|---|---|---|---|---|
| kgw | 0.25 | first | 20 | 0 |
| gumbel | na | raw | 20 | 20 |
| gumbel | na | distinct | 20 | 20 |
| gumbel | na | first | 20 | 20 |
| kgw | 0.5 | raw | 20 | 20 |
| kgw | 0.5 | distinct | 20 | 20 |
| kgw | 0.5 | first | 20 | 0 |

The same statement under the first rule, γ = 0.5 and the Gumbel family (descriptive).

### curves_h1

| Corpus cell | Tokenizer | Rule | L = 64 | L = 128 | L = 256 | L = 512 | L = 1,024 |
|---|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | raw | 0.843 / 0.591 | 0.666 / 0.655 | 1.17 / 0.940 | — | — |
| news/en@256 | Llama-3.2 | distinct | 0.630 / 0.483 | 0.507 / 0.438 | 0.499 / 0.449 | — | — |
| news/en@256 | Llama-3.2 | first | 0.594 / 0.426 | 0.441 / 0.366 | 0.373 / 0.326 | — | — |
| news/en@256 | Qwen2.5 | raw | 1.65 / 1.02 | 1.29 / 1.09 | 1.93 / 1.47 | — | — |
| news/en@256 | Qwen2.5 | distinct | 0.890 / 0.660 | 0.687 / 0.563 | 0.592 / 0.536 | — | — |
| news/en@256 | Qwen2.5 | first | 0.744 / 0.534 | 0.560 / 0.445 | 0.442 / 0.384 | — | — |
| wikipedia/en@256 | Llama-3.2 | raw | 0.793 / 0.537 | 0.847 / 0.792 | 1.60 / 1.33 | — | — |
| wikipedia/en@256 | Llama-3.2 | distinct | 0.519 / 0.392 | 0.529 / 0.427 | 0.541 / 0.468 | — | — |
| wikipedia/en@256 | Llama-3.2 | first | 0.475 / 0.341 | 0.404 / 0.319 | 0.366 / 0.305 | — | — |
| wikipedia/en@256 | Qwen2.5 | raw | 1.48 / 0.889 | 1.76 / 1.38 | 3.38 / 2.45 | — | — |
| wikipedia/en@256 | Qwen2.5 | distinct | 0.705 / 0.510 | 0.687 / 0.531 | 0.681 / 0.560 | — | — |
| wikipedia/en@256 | Qwen2.5 | first | 0.582 / 0.416 | 0.505 / 0.388 | 0.449 / 0.359 | — | — |
| stackexchange/en@256 | Llama-3.2 | raw | 0.595 / 0.421 | 0.572 / 0.561 | 0.970 / 0.873 | — | — |
| stackexchange/en@256 | Llama-3.2 | distinct | 0.410 / 0.311 | 0.397 / 0.322 | 0.432 / 0.358 | — | — |
| stackexchange/en@256 | Llama-3.2 | first | 0.402 / 0.297 | 0.350 / 0.277 | 0.328 / 0.275 | — | — |
| stackexchange/en@256 | Qwen2.5 | raw | 0.660 / 0.477 | 0.691 / 0.669 | 1.27 / 1.10 | — | — |
| stackexchange/en@256 | Qwen2.5 | distinct | 0.406 / 0.331 | 0.408 / 0.347 | 0.452 / 0.388 | — | — |
| stackexchange/en@256 | Qwen2.5 | first | 0.397 / 0.312 | 0.347 / 0.293 | 0.334 / 0.289 | — | — |
| wikipedia/de@256 | Llama-3.2 | raw | 0.483 / 0.339 | 0.422 / 0.422 | 0.712 / 0.620 | — | — |
| wikipedia/de@256 | Llama-3.2 | distinct | 0.370 / 0.275 | 0.345 / 0.287 | 0.371 / 0.329 | — | — |
| wikipedia/de@256 | Llama-3.2 | first | 0.377 / 0.267 | 0.322 / 0.262 | 0.318 / 0.275 | — | — |
| wikipedia/de@256 | Qwen2.5 | raw | 0.945 / 0.538 | 0.983 / 0.740 | 1.82 / 1.20 | — | — |
| wikipedia/de@256 | Qwen2.5 | distinct | 0.492 / 0.345 | 0.459 / 0.353 | 0.474 / 0.392 | — | — |
| wikipedia/de@256 | Qwen2.5 | first | 0.443 / 0.305 | 0.391 / 0.297 | 0.373 / 0.303 | — | — |
| wikipedia/ru@256 | Llama-3.2 | raw | 0.901 / 0.614 | 0.763 / 0.695 | 1.22 / 0.949 | — | — |
| wikipedia/ru@256 | Llama-3.2 | distinct | 0.509 / 0.396 | 0.419 / 0.349 | 0.396 / 0.348 | — | — |
| wikipedia/ru@256 | Llama-3.2 | first | 0.533 / 0.397 | 0.422 / 0.340 | 0.366 / 0.310 | — | — |
| wikipedia/ru@256 | Qwen2.5 | raw | 1.00 / 0.701 | 0.972 / 0.885 | 1.73 / 1.33 | — | — |
| wikipedia/ru@256 | Qwen2.5 | distinct | 0.561 / 0.446 | 0.501 / 0.422 | 0.497 / 0.435 | — | — |
| wikipedia/ru@256 | Qwen2.5 | first | 0.551 / 0.429 | 0.467 / 0.386 | 0.419 / 0.363 | — | — |
| wikipedia/ar@256 | Llama-3.2 | raw | 0.426 / 0.287 | 0.508 / 0.435 | 1.06 / 0.787 | — | — |
| wikipedia/ar@256 | Llama-3.2 | distinct | 0.316 / 0.225 | 0.322 / 0.259 | 0.378 / 0.309 | — | — |
| wikipedia/ar@256 | Llama-3.2 | first | 0.326 / 0.209 | 0.312 / 0.231 | 0.330 / 0.261 | — | — |
| wikipedia/ar@256 | Qwen2.5 | raw | 0.870 / 0.522 | 0.994 / 0.787 | 1.93 / 1.39 | — | — |
| wikipedia/ar@256 | Qwen2.5 | distinct | 0.484 / 0.338 | 0.474 / 0.364 | 0.494 / 0.402 | — | — |
| wikipedia/ar@256 | Qwen2.5 | first | 0.404 / 0.272 | 0.380 / 0.285 | 0.373 / 0.301 | — | — |
| wikipedia/zh@256 | Llama-3.2 | raw | 0.400 / 0.294 | 0.385 / 0.384 | 0.661 / 0.596 | — | — |
| wikipedia/zh@256 | Llama-3.2 | distinct | 0.260 / 0.204 | 0.254 / 0.211 | 0.276 / 0.239 | — | — |
| wikipedia/zh@256 | Llama-3.2 | first | 0.271 / 0.203 | 0.250 / 0.208 | 0.258 / 0.227 | — | — |
| wikipedia/zh@256 | Qwen2.5 | raw | 0.560 / 0.384 | 0.689 / 0.612 | 1.43 / 1.12 | — | — |
| wikipedia/zh@256 | Qwen2.5 | distinct | 0.323 / 0.249 | 0.341 / 0.277 | 0.370 / 0.320 | — | — |
| wikipedia/zh@256 | Qwen2.5 | first | 0.307 / 0.233 | 0.287 / 0.237 | 0.277 / 0.237 | — | — |
| wikipedia/ja@256 | Llama-3.2 | raw | 0.636 / 0.444 | 0.588 / 0.570 | 0.974 / 0.841 | — | — |
| wikipedia/ja@256 | Llama-3.2 | distinct | 0.438 / 0.318 | 0.401 / 0.325 | 0.411 / 0.353 | — | — |
| wikipedia/ja@256 | Llama-3.2 | first | 0.453 / 0.323 | 0.406 / 0.321 | 0.390 / 0.330 | — | — |
| wikipedia/ja@256 | Qwen2.5 | raw | 1.10 / 0.759 | 0.974 / 0.937 | 1.70 / 1.41 | — | — |
| wikipedia/ja@256 | Qwen2.5 | distinct | 0.739 / 0.518 | 0.613 / 0.477 | 0.583 / 0.483 | — | — |
| wikipedia/ja@256 | Qwen2.5 | first | 0.729 / 0.524 | 0.602 / 0.468 | 0.538 / 0.440 | — | — |
| wikipedia/en@1024 | Llama-3.2 | raw | 0.778 / 0.521 | 0.833 / 0.764 | 1.59 / 1.26 | 2.49 / 2.24 | 4.19 / 3.97 |
| wikipedia/en@1024 | Llama-3.2 | distinct | 0.505 / 0.384 | 0.527 / 0.424 | 0.553 / 0.471 | 0.581 / 0.515 | 0.587 / 0.551 |
| wikipedia/en@1024 | Llama-3.2 | first | 0.458 / 0.333 | 0.396 / 0.314 | 0.359 / 0.304 | 0.341 / 0.306 | 0.336 / 0.313 |
| wikipedia/en@1024 | Qwen2.5 | raw | 1.40 / 0.848 | 1.63 / 1.30 | 3.08 / 2.21 | 4.83 / 3.99 | 7.73 / 6.91 |
| wikipedia/en@1024 | Qwen2.5 | distinct | 0.681 / 0.498 | 0.667 / 0.523 | 0.672 / 0.554 | 0.678 / 0.590 | 0.686 / 0.623 |
| wikipedia/en@1024 | Qwen2.5 | first | 0.565 / 0.406 | 0.500 / 0.380 | 0.446 / 0.354 | 0.404 / 0.337 | 0.373 / 0.330 |
| gutenberg/en@1024 | Llama-3.2 | raw | 0.588 / 0.403 | 0.709 / 0.672 | 1.43 / 1.20 | 2.29 / 2.20 | 4.18 / 3.91 |
| gutenberg/en@1024 | Llama-3.2 | distinct | 0.374 / 0.275 | 0.447 / 0.338 | 0.501 / 0.403 | 0.574 / 0.473 | 0.633 / 0.550 |
| gutenberg/en@1024 | Llama-3.2 | first | 0.274 / 0.197 | 0.264 / 0.206 | 0.256 / 0.218 | 0.271 / 0.234 | 0.281 / 0.256 |
| gutenberg/en@1024 | Qwen2.5 | raw | 0.632 / 0.422 | 0.784 / 0.716 | 1.51 / 1.28 | 2.35 / 2.33 | 4.17 / 4.09 |
| gutenberg/en@1024 | Qwen2.5 | distinct | 0.381 / 0.279 | 0.450 / 0.343 | 0.511 / 0.410 | 0.590 / 0.480 | 0.676 / 0.558 |
| gutenberg/en@1024 | Qwen2.5 | first | 0.282 / 0.201 | 0.276 / 0.211 | 0.282 / 0.222 | 0.278 / 0.238 | 0.294 / 0.259 |

Each entry: observed / predicted across-key SD of the per-key level at α = 0.01 (percentage points), KGW γ = 0.25, independent colouring, h = 1; the @256 cells stop at L = 256.

### width_sd

| Corpus cell | Tokenizer | L | h = 0 | h = 1 | h = 2 | h = 3 | h = 4 |
|---|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | 256 | 15.0 / 1.65 | 1.17 / 0.499 | 0.391 / 0.266 | 0.237 / 0.206 | 0.213 / 0.169 |
| news/en@256 | Qwen2.5 | 256 | 15.0 / 1.74 | 1.93 / 0.592 | 0.787 / 0.362 | 0.393 / 0.266 | 0.299 / 0.217 |
| wikipedia/en@256 | Llama-3.2 | 256 | 16.4 / 1.54 | 1.60 / 0.541 | 0.264 / 0.181 | 0.130 / 0.119 | 0.127 / 0.113 |
| wikipedia/en@256 | Qwen2.5 | 256 | 17.1 / 1.78 | 3.38 / 0.681 | 1.12 / 0.310 | 0.342 / 0.197 | 0.172 / 0.134 |
| stackexchange/en@256 | Llama-3.2 | 256 | 11.8 / 1.86 | 0.970 / 0.432 | 0.233 / 0.149 | 0.139 / 0.110 | 0.140 / 0.112 |
| stackexchange/en@256 | Qwen2.5 | 256 | 11.7 / 1.93 | 1.27 / 0.452 | 0.327 / 0.166 | 0.177 / 0.121 | 0.150 / 0.112 |
| wikipedia/de@256 | Llama-3.2 | 256 | 8.59 / 1.65 | 0.712 / 0.371 | 0.245 / 0.177 | 0.148 / 0.132 | 0.136 / 0.119 |
| wikipedia/de@256 | Qwen2.5 | 256 | 9.32 / 1.76 | 1.82 / 0.474 | 0.567 / 0.239 | 0.200 / 0.159 | 0.148 / 0.128 |
| wikipedia/ru@256 | Llama-3.2 | 256 | 8.50 / 1.55 | 1.22 / 0.396 | 0.305 / 0.201 | 0.161 / 0.139 | 0.154 / 0.129 |
| wikipedia/ru@256 | Qwen2.5 | 256 | 9.98 / 2.42 | 1.73 / 0.497 | 0.510 / 0.256 | 0.214 / 0.174 | 0.172 / 0.138 |
| wikipedia/ar@256 | Llama-3.2 | 256 | 9.05 / 2.18 | 1.06 / 0.378 | 0.558 / 0.212 | 0.358 / 0.173 | 0.283 / 0.170 |
| wikipedia/ar@256 | Qwen2.5 | 256 | 10.4 / 2.36 | 1.93 / 0.494 | 0.869 / 0.280 | 0.413 / 0.203 | 0.316 / 0.189 |
| wikipedia/zh@256 | Llama-3.2 | 256 | 7.87 / 1.48 | 0.661 / 0.276 | 0.239 / 0.137 | 0.145 / 0.110 | 0.139 / 0.108 |
| wikipedia/zh@256 | Qwen2.5 | 256 | 11.7 / 1.48 | 1.43 / 0.370 | 0.442 / 0.188 | 0.171 / 0.126 | 0.157 / 0.118 |
| wikipedia/ja@256 | Llama-3.2 | 256 | 9.96 / 1.94 | 0.974 / 0.411 | 0.323 / 0.206 | 0.176 / 0.145 | 0.157 / 0.127 |
| wikipedia/ja@256 | Qwen2.5 | 256 | 12.1 / 1.83 | 1.70 / 0.583 | 0.553 / 0.297 | 0.262 / 0.188 | 0.185 / 0.143 |
| wikipedia/en@1024 | Llama-3.2 | 1,024 | 27.7 / 1.51 | 4.19 / 0.587 | 0.460 / 0.207 | 0.170 / 0.121 | 0.118 / 0.105 |
| wikipedia/en@1024 | Qwen2.5 | 1,024 | 28.2 / 1.57 | 7.73 / 0.686 | 2.65 / 0.305 | 0.783 / 0.207 | 0.235 / 0.153 |
| gutenberg/en@1024 | Llama-3.2 | 1,024 | 28.6 / 1.66 | 4.18 / 0.633 | 0.318 / 0.184 | 0.154 / 0.108 | 0.132 / 0.102 |
| gutenberg/en@1024 | Qwen2.5 | 1,024 | 28.0 / 1.44 | 4.17 / 0.676 | 0.424 / 0.197 | 0.166 / 0.113 | 0.139 / 0.105 |

Observed across-key SD of the per-key level at α = 0.01 (pp), raw / distinct rule, KGW γ = 0.25, independent colouring, at the cell's longest length.

### width_A

| Corpus cell | Tokenizer | L | h = 0 | h = 1 | h = 2 | h = 3 | h = 4 |
|---|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | 256 | 5.79e-03 (1.48) | 1.69e-04 (0.043) | 2.50e-05 (6.34e-03) | 1.13e-05 (2.85e-03) | 6.31e-06 (1.59e-03) |
| news/en@256 | Qwen2.5 | 256 | 6.00e-03 (1.54) | 3.49e-04 (0.089) | 9.98e-05 (0.025) | 4.23e-05 (0.011) | 1.52e-05 (3.82e-03) |
| wikipedia/en@256 | Llama-3.2 | 256 | 7.39e-03 (1.89) | 2.39e-04 (0.061) | 1.09e-05 (2.78e-03) | 1.35e-06 (3.41e-04) | 2.29e-07 (5.76e-05) |
| wikipedia/en@256 | Qwen2.5 | 256 | 7.82e-03 (2.00) | 5.90e-04 (0.150) | 1.29e-04 (0.033) | 2.71e-05 (6.86e-03) | 3.93e-06 (9.90e-04) |
| stackexchange/en@256 | Llama-3.2 | 256 | 3.85e-03 (0.986) | 8.85e-05 (0.023) | 6.05e-06 (1.54e-03) | 9.20e-07 (2.33e-04) | 2.17e-07 (5.46e-05) |
| stackexchange/en@256 | Qwen2.5 | 256 | 4.12e-03 (1.05) | 1.31e-04 (0.033) | 1.11e-05 (2.83e-03) | 1.87e-06 (4.74e-04) | 5.72e-07 (1.44e-04) |
| wikipedia/de@256 | Llama-3.2 | 256 | 2.80e-03 (0.717) | 6.55e-05 (0.017) | 1.03e-05 (2.61e-03) | 3.05e-06 (7.72e-04) | 1.06e-06 (2.66e-04) |
| wikipedia/de@256 | Qwen2.5 | 256 | 3.06e-03 (0.785) | 2.07e-04 (0.053) | 4.32e-05 (0.011) | 7.95e-06 (2.01e-03) | 1.83e-06 (4.60e-04) |
| wikipedia/ru@256 | Llama-3.2 | 256 | 2.97e-03 (0.760) | 1.45e-04 (0.037) | 1.43e-05 (3.63e-03) | 3.58e-06 (9.05e-04) | 1.48e-06 (3.72e-04) |
| wikipedia/ru@256 | Qwen2.5 | 256 | 3.46e-03 (0.886) | 2.43e-04 (0.062) | 3.90e-05 (9.91e-03) | 8.91e-06 (2.25e-03) | 3.04e-06 (7.66e-04) |
| wikipedia/ar@256 | Llama-3.2 | 256 | 2.99e-03 (0.766) | 7.63e-05 (0.019) | 1.74e-05 (4.43e-03) | 7.99e-06 (2.02e-03) | 4.30e-06 (1.08e-03) |
| wikipedia/ar@256 | Qwen2.5 | 256 | 3.80e-03 (0.973) | 2.15e-04 (0.055) | 5.97e-05 (0.015) | 1.84e-05 (4.65e-03) | 6.68e-06 (1.68e-03) |
| wikipedia/zh@256 | Llama-3.2 | 256 | 2.25e-03 (0.575) | 3.41e-05 (8.69e-03) | 4.25e-06 (1.08e-03) | 7.38e-07 (1.87e-04) | 2.21e-07 (5.58e-05) |
| wikipedia/zh@256 | Qwen2.5 | 256 | 3.84e-03 (0.982) | 1.25e-04 (0.032) | 1.94e-05 (4.92e-03) | 3.31e-06 (8.36e-04) | 1.05e-06 (2.64e-04) |
| wikipedia/ja@256 | Llama-3.2 | 256 | 3.33e-03 (0.852) | 8.19e-05 (0.021) | 1.33e-05 (3.37e-03) | 4.45e-06 (1.13e-03) | 1.56e-06 (3.94e-04) |
| wikipedia/ja@256 | Qwen2.5 | 256 | 4.22e-03 (1.08) | 2.04e-04 (0.052) | 4.02e-05 (0.010) | 1.02e-05 (2.58e-03) | 3.57e-06 (8.99e-04) |
| wikipedia/en@1024 | Llama-3.2 | 1,024 | 7.23e-03 (7.40) | 2.01e-04 (0.205) | 6.58e-06 (6.72e-03) | 7.29e-07 (7.44e-04) | 1.08e-07 (1.10e-04) |
| wikipedia/en@1024 | Qwen2.5 | 1,024 | 7.60e-03 (7.78) | 4.73e-04 (0.483) | 9.04e-05 (0.092) | 1.85e-05 (0.019) | 2.64e-06 (2.70e-03) |
| gutenberg/en@1024 | Llama-3.2 | 1,024 | 8.25e-03 (8.45) | 2.01e-04 (0.206) | 4.43e-06 (4.53e-03) | 3.79e-07 (3.87e-04) | 1.86e-07 (1.90e-04) |
| gutenberg/en@1024 | Qwen2.5 | 1,024 | 8.11e-03 (8.30) | 2.11e-04 (0.216) | 6.09e-06 (6.22e-03) | 5.71e-07 (5.83e-04) | 2.11e-07 (2.16e-04) |

Ã(h), the between-text collision of the retained-tuple weights under the raw rule (ρ̄ in parentheses), KGW γ = 0.25, at the cell's longest length.

### deployer_kgw

| Corpus cell | Tokenizer | Rule | L | Mean M | K / N_eff | Key-mean (%) | 1% key (%) [crossed 95% CI] | 5% key (%) [CI] | Median key (%) [CI] | 95% key (%) [CI] | 99% key (%) [CI] | Worst sampled key (%) [CI] | Keys > 2α [CI, in %] | Keys > 5α [CI, in %] | SD of the level (pp) [key-bootstrap 95% CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.52 | 0.79 [0.720, 0.890] | 1.08 [1.01, 1.14] | 2.27 [2.18, 2.35] | 4.66 [4.47, 4.97] | 6.20 [5.63, 7.10] | 8.49 [7.76, 8.98] | 61.4% [57.7, 65.0] | 3.3% [2.40, 4.90] | 1.17 [1.10, 1.27] |
| news/en@256 | Llama-3.2 | distinct | 256 | 229 | 1,000 / 10,000 | 1.12 | 0.36 [0.300, 0.390] | 0.50 [0.450, 0.520] | 1.03 [0.990, 1.07] | 2.09 [2.00, 2.23] | 2.80 [2.50, 3.01] | 3.61 [3.11, 3.92] | 6.1% [5.00, 8.00] | 0.0% [0, 0] | 0.499 [0.466, 0.527] |
| news/en@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 2.79 | 0.63 [0.480, 0.650] | 0.83 [0.750, 0.879] | 2.23 [2.11, 2.35] | 6.46 [6.06, 7.23] | 9.37 [8.44, 11.9] | 15.0 [12.1, 15.6] | 55.5% [53.0, 59.1] | 10.9% [9.00, 12.9] | 1.93 [1.78, 2.08] |
| news/en@256 | Qwen2.5 | distinct | 256 | 226 | 1,000 / 10,000 | 1.14 | 0.32 [0.239, 0.340] | 0.44 [0.390, 0.460] | 1.00 [0.960, 1.04] | 2.32 [2.18, 2.42] | 3.03 [2.72, 3.47] | 4.62 [3.66, 5.00] | 8.5% [7.20, 10.7] | 0.0% [0, 2.50e-03] | 0.592 [0.549, 0.643] |
| wikipedia/en@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.31 | 1.12 [1.03, 1.22] | 1.48 [1.37, 1.55] | 2.95 [2.84, 3.09] | 6.16 [5.88, 6.63] | 9.13 [8.44, 10.2] | 12.7 [10.5, 13.3] | 82.0% [79.1, 84.4] | 12.1% [10.5, 14.4] | 1.60 [1.48, 1.71] |
| wikipedia/en@256 | Llama-3.2 | distinct | 256 | 223 | 1,000 / 10,000 | 1.16 | 0.36 [0.300, 0.380] | 0.50 [0.449, 0.520] | 1.07 [1.02, 1.10] | 2.17 [2.05, 2.35] | 3.16 [2.73, 3.53] | 3.94 [3.54, 4.25] | 6.8% [5.50, 8.90] | 0.0% [0, 0] | 0.541 [0.503, 0.576] |
| wikipedia/en@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 4.10 | 0.74 [0.640, 0.800] | 0.99 [0.910, 1.07] | 3.14 [2.96, 3.33] | 10.9 [9.49, 12.5] | 18.0 [16.1, 19.3] | 24.5 [19.9, 25.4] | 71.7% [69.6, 75.3] | 26.2% [23.6, 29.0] | 3.38 [3.08, 3.65] |
| wikipedia/en@256 | Qwen2.5 | distinct | 256 | 217 | 1,000 / 10,000 | 1.18 | 0.29 [0.220, 0.310] | 0.40 [0.359, 0.420] | 1.05 [1.00, 1.09] | 2.50 [2.32, 2.71] | 3.42 [3.14, 4.05] | 6.58 [4.03, 7.12] | 10.3% [8.50, 12.7] | 0.2% [0, 0.400] | 0.681 [0.635, 0.737] |
| stackexchange/en@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.65 | 1.98 [1.83, 2.12] | 2.39 [2.25, 2.42] | 3.48 [3.40, 3.58] | 5.36 [5.22, 5.63] | 6.60 [6.13, 7.42] | 8.27 [7.44, 8.86] | 98.9% [98.1, 99.4] | 9.1% [7.40, 11.2] | 0.970 [0.915, 1.03] |
| stackexchange/en@256 | Llama-3.2 | distinct | 256 | 217 | 1,000 / 10,000 | 1.17 | 0.49 [0.400, 0.500] | 0.62 [0.559, 0.620] | 1.10 [1.07, 1.13] | 1.96 [1.89, 2.11] | 2.50 [2.31, 2.90] | 3.54 [3.01, 3.89] | 4.5% [3.40, 6.30] | 0.0% [0, 0] | 0.432 [0.401, 0.462] |
| stackexchange/en@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.80 | 1.79 [1.61, 1.85] | 2.12 [1.99, 2.21] | 3.58 [3.47, 3.69] | 6.23 [5.93, 6.58] | 7.88 [7.31, 8.45] | 9.10 [8.49, 9.62] | 96.9% [94.8, 97.8] | 15.9% [13.3, 18.4] | 1.27 [1.21, 1.35] |
| stackexchange/en@256 | Qwen2.5 | distinct | 256 | 215 | 1,000 / 10,000 | 1.15 | 0.44 [0.370, 0.460] | 0.57 [0.510, 0.580] | 1.07 [1.04, 1.11] | 2.00 [1.93, 2.15] | 2.52 [2.41, 2.76] | 3.32 [2.83, 3.64] | 4.8% [3.90, 7.00] | 0.0% [0, 0] | 0.452 [0.422, 0.479] |
| wikipedia/de@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.79 | 1.56 [1.39, 1.59] | 1.76 [1.66, 1.82] | 2.70 [2.62, 2.76] | 4.05 [3.98, 4.30] | 4.84 [4.64, 5.16] | 6.11 [5.18, 6.56] | 87.8% [84.4, 89.8] | 0.4% [0.200, 1.31] | 0.712 [0.680, 0.749] |
| wikipedia/de@256 | Llama-3.2 | distinct | 256 | 229 | 1,000 / 10,000 | 1.14 | 0.49 [0.410, 0.510] | 0.62 [0.570, 0.640] | 1.08 [1.05, 1.12] | 1.81 [1.75, 1.93] | 2.24 [2.09, 2.45] | 2.69 [2.43, 3.07] | 2.3% [1.60, 4.20] | 0.0% [0, 0] | 0.371 [0.352, 0.388] |
| wikipedia/de@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.25 | 1.22 [1.06, 1.27] | 1.47 [1.40, 1.55] | 2.71 [2.61, 2.82] | 6.99 [6.46, 7.63] | 10.1 [8.91, 11.7] | 14.5 [12.6, 15.2] | 78.1% [75.2, 80.9] | 13.0% [11.1, 15.0] | 1.82 [1.68, 2.01] |
| wikipedia/de@256 | Qwen2.5 | distinct | 256 | 226 | 1,000 / 10,000 | 1.16 | 0.42 [0.350, 0.470] | 0.58 [0.530, 0.600] | 1.07 [1.03, 1.10] | 2.08 [1.96, 2.22] | 2.74 [2.52, 3.10] | 3.64 [3.21, 4.00] | 5.7% [4.60, 8.00] | 0.0% [0, 0] | 0.474 [0.440, 0.511] |
| wikipedia/ru@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.92 | 1.32 [1.17, 1.39] | 1.56 [1.48, 1.61] | 2.52 [2.45, 2.61] | 5.49 [5.28, 5.77] | 6.35 [6.03, 6.74] | 7.34 [6.92, 7.87] | 77.0% [73.5, 80.4] | 8.7% [6.70, 11.2] | 1.22 [1.15, 1.27] |
| wikipedia/ru@256 | Llama-3.2 | distinct | 256 | 227 | 1,000 / 10,000 | 1.14 | 0.49 [0.400, 0.500] | 0.61 [0.560, 0.630] | 1.07 [1.04, 1.11] | 1.86 [1.80, 1.97] | 2.37 [2.17, 2.55] | 2.81 [2.65, 3.12] | 2.9% [2.10, 4.60] | 0.0% [0, 0] | 0.396 [0.373, 0.417] |
| wikipedia/ru@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.26 | 1.05 [0.889, 1.14] | 1.39 [1.29, 1.45] | 2.79 [2.68, 2.90] | 6.87 [6.29, 7.15] | 8.96 [8.19, 10.7] | 13.3 [12.0, 13.9] | 76.7% [73.5, 79.8] | 14.0% [11.7, 16.0] | 1.73 [1.60, 1.88] |
| wikipedia/ru@256 | Qwen2.5 | distinct | 256 | 222 | 1,000 / 10,000 | 1.15 | 0.38 [0.310, 0.400] | 0.50 [0.460, 0.540] | 1.05 [1.02, 1.09] | 2.15 [2.04, 2.29] | 2.74 [2.54, 2.95] | 4.02 [2.98, 4.34] | 6.8% [5.30, 8.61] | 0.0% [0, 0] | 0.497 [0.465, 0.525] |
| wikipedia/ar@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.48 | 1.88 [1.69, 1.92] | 2.15 [2.03, 2.19] | 3.31 [3.21, 3.38] | 5.53 [5.24, 5.77] | 6.80 [6.31, 7.38] | 8.86 [7.54, 9.40] | 97.8% [95.2, 98.1] | 8.7% [6.70, 10.7] | 1.06 [0.996, 1.11] |
| wikipedia/ar@256 | Llama-3.2 | distinct | 256 | 220 | 1,000 / 10,000 | 1.14 | 0.54 [0.450, 0.540] | 0.62 [0.590, 0.650] | 1.08 [1.05, 1.12] | 1.83 [1.75, 1.94] | 2.43 [2.16, 2.74] | 3.21 [2.79, 3.50] | 2.9% [2.00, 4.30] | 0.0% [0, 0] | 0.378 [0.351, 0.400] |
| wikipedia/ar@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.83 | 1.40 [1.17, 1.51] | 1.74 [1.64, 1.82] | 3.28 [3.19, 3.44] | 7.67 [7.25, 8.39] | 10.4 [9.30, 11.4] | 15.6 [12.7, 16.2] | 89.6% [87.4, 91.4] | 20.3% [17.4, 23.3] | 1.93 [1.78, 2.07] |
| wikipedia/ar@256 | Qwen2.5 | distinct | 256 | 217 | 1,000 / 10,000 | 1.16 | 0.38 [0.329, 0.430] | 0.56 [0.500, 0.580] | 1.05 [1.03, 1.09] | 2.09 [1.98, 2.26] | 2.87 [2.53, 3.14] | 4.42 [3.29, 4.75] | 6.2% [4.80, 8.01] | 0.0% [0, 0] | 0.494 [0.451, 0.529] |
| wikipedia/zh@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 4.23 | 2.94 [2.71, 2.97] | 3.23 [3.10, 3.28] | 4.18 [4.09, 4.25] | 5.40 [5.31, 5.58] | 5.98 [5.75, 6.30] | 6.63 [6.27, 7.14] | 100.0% [100, 100] | 13.3% [11.0, 16.5] | 0.661 [0.633, 0.688] |
| wikipedia/zh@256 | Llama-3.2 | distinct | 256 | 215 | 1,000 / 10,000 | 1.16 | 0.64 [0.540, 0.650] | 0.77 [0.690, 0.760] | 1.13 [1.11, 1.16] | 1.66 [1.63, 1.75] | 1.91 [1.86, 2.06] | 2.19 [2.05, 2.44] | 0.5% [0.198, 1.50] | 0.0% [0, 0] | 0.276 [0.263, 0.287] |
| wikipedia/zh@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 4.31 | 2.29 [2.08, 2.31] | 2.59 [2.45, 2.63] | 4.00 [3.91, 4.14] | 7.27 [6.90, 7.57] | 8.51 [8.24, 8.92] | 12.2 [8.94, 12.7] | 99.8% [99.2, 100] | 24.7% [21.9, 27.8] | 1.43 [1.36, 1.52] |
| wikipedia/zh@256 | Qwen2.5 | distinct | 256 | 215 | 1,000 / 10,000 | 1.15 | 0.53 [0.430, 0.540] | 0.66 [0.590, 0.660] | 1.10 [1.07, 1.14] | 1.82 [1.79, 1.92] | 2.16 [2.08, 2.43] | 3.09 [2.51, 3.37] | 2.2% [1.70, 3.70] | 0.0% [0, 0] | 0.370 [0.352, 0.392] |
| wikipedia/ja@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.80 | 2.10 [1.92, 2.18] | 2.42 [2.33, 2.50] | 3.67 [3.60, 3.76] | 5.56 [5.35, 5.80] | 6.79 [6.31, 7.29] | 8.42 [7.57, 8.87] | 99.3% [98.5, 99.7] | 10.6% [9.10, 13.6] | 0.974 [0.920, 1.03] |
| wikipedia/ja@256 | Llama-3.2 | distinct | 256 | 217 | 1,000 / 10,000 | 1.16 | 0.49 [0.380, 0.490] | 0.59 [0.540, 0.629] | 1.10 [1.06, 1.12] | 1.90 [1.83, 1.98] | 2.45 [2.20, 2.71] | 3.64 [2.87, 4.01] | 3.2% [2.60, 4.60] | 0.0% [0, 0] | 0.411 [0.381, 0.439] |
| wikipedia/ja@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 4.21 | 1.70 [1.50, 1.76] | 2.09 [1.97, 2.19] | 3.85 [3.73, 3.98] | 7.59 [7.19, 8.00] | 8.93 [8.72, 10.7] | 13.0 [10.9, 13.6] | 96.0% [94.5, 97.4] | 25.9% [23.0, 29.2] | 1.70 [1.61, 1.81] |
| wikipedia/ja@256 | Qwen2.5 | distinct | 256 | 212 | 1,000 / 10,000 | 1.17 | 0.33 [0.270, 0.370] | 0.48 [0.420, 0.490] | 1.05 [1.00, 1.10] | 2.27 [2.17, 2.42] | 3.03 [2.80, 3.56] | 4.42 [3.87, 4.74] | 9.1% [7.40, 10.8] | 0.0% [0, 0] | 0.583 [0.535, 0.624] |
| wikipedia/en@1024 | Llama-3.2 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 6.66 | 1.70 [1.49, 1.88] | 2.26 [2.12, 2.48] | 5.56 [5.31, 5.86] | 14.3 [13.5, 15.9] | 23.0 [20.0, 27.7] | 29.0 [28.2, 29.9] | 97.5% [96.0, 98.4] | 56.6% [54.0, 60.1] | 4.19 [3.86, 4.57] |
| wikipedia/en@1024 | Llama-3.2 | distinct | 1,024 | 806 | 1,000 / 10,000 | 1.09 | 0.29 [0.200, 0.310] | 0.42 [0.370, 0.430] | 0.96 [0.920, 1.00] | 2.21 [2.05, 2.42] | 3.10 [2.81, 3.57] | 4.53 [3.66, 4.97] | 7.3% [5.60, 9.00] | 0.0% [0, 0] | 0.587 [0.545, 0.635] |
| wikipedia/en@1024 | Qwen2.5 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 8.65 | 1.00 [0.860, 1.11] | 1.47 [1.35, 1.62] | 6.28 [5.91, 6.73] | 24.8 [21.5, 27.6] | 38.3 [34.0, 41.9] | 51.6 [42.2, 52.4] | 88.3% [86.4, 90.5] | 60.0% [56.6, 63.2] | 7.73 [7.04, 8.28] |
| wikipedia/en@1024 | Qwen2.5 | distinct | 1,024 | 779 | 1,000 / 10,000 | 1.11 | 0.23 [0.170, 0.250] | 0.34 [0.290, 0.350] | 0.96 [0.920, 1.01] | 2.43 [2.29, 2.71] | 3.65 [3.35, 3.92] | 4.61 [3.96, 4.93] | 9.7% [7.90, 11.6] | 0.0% [0, 0] | 0.686 [0.633, 0.734] |
| gutenberg/en@1024 | Llama-3.2 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 5.65 | 1.22 [1.06, 1.37] | 1.74 [1.59, 1.88] | 4.33 [4.15, 4.61] | 13.4 [12.6, 14.5] | 20.7 [17.7, 25.2] | 39.0 [26.3, 39.7] | 91.4% [88.8, 93.3] | 42.0% [38.9, 45.5] | 4.18 [3.72, 4.63] |
| gutenberg/en@1024 | Llama-3.2 | distinct | 1,024 | 871 | 1,000 / 10,000 | 1.10 | 0.25 [0.190, 0.300] | 0.39 [0.350, 0.410] | 0.95 [0.910, 0.990] | 2.32 [2.18, 2.50] | 3.27 [2.93, 3.66] | 6.09 [3.65, 6.48] | 8.5% [7.00, 10.8] | 0.1% [0, 0.303] | 0.633 [0.579, 0.686] |
| gutenberg/en@1024 | Qwen2.5 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 5.84 | 1.01 [0.840, 1.22] | 1.66 [1.52, 1.83] | 4.58 [4.37, 4.88] | 13.9 [12.6, 15.2] | 21.2 [18.4, 23.5] | 36.8 [24.8, 37.8] | 91.2% [89.0, 92.9] | 45.4% [42.2, 48.4] | 4.17 [3.79, 4.63] |
| gutenberg/en@1024 | Qwen2.5 | distinct | 1,024 | 861 | 1,000 / 10,000 | 1.10 | 0.23 [0.180, 0.270] | 0.38 [0.320, 0.390] | 0.92 [0.880, 0.980] | 2.40 [2.26, 2.64] | 3.37 [2.98, 4.04] | 6.20 [4.25, 6.57] | 9.1% [7.90, 11.3] | 0.1% [0, 0.300] | 0.676 [0.619, 0.735] |

Per-key false-positive levels at α = 0.01 over the K = 1,000 production keys on the N_eff = N = 10,000 realised texts of each corpus cell (the nominal level is 1%); h = 1, the cell's longest length. The 1%, 5%, 50%, 95% and 99% key quantiles, the worst sampled key and the shares carry their crossed key-by-document bootstrap intervals (200 resamples of texts and keys; the worst key's interval is the sampled maximum's under resampling, never a population extreme; gate constraint 12); the SD carries its key-bootstrap interval conditional on the texts. KGW, γ = 0.25, independent colouring.

### deployer_gumbel

| Corpus cell | Tokenizer | Rule | L | Mean M | K / N_eff | Key-mean (%) | 1% key (%) [crossed 95% CI] | 5% key (%) [CI] | Median key (%) [CI] | 95% key (%) [CI] | 99% key (%) [CI] | Worst sampled key (%) [CI] | Keys > 2α [CI, in %] | Keys > 5α [CI, in %] | SD of the level (pp) [key-bootstrap 95% CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| news/en@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.14 | 0.67 [0.570, 0.750] | 0.92 [0.859, 0.980] | 1.88 [1.81, 1.96] | 4.02 [3.81, 4.46] | 6.27 [5.50, 7.42] | 12.6 [8.34, 13.1] | 46.0% [41.5, 48.2] | 2.8% [1.60, 3.70] | 1.13 [1.03, 1.25] |
| news/en@256 | Llama-3.2 | distinct | 256 | 229 | 1,000 / 10,000 | 1.00 | 0.30 [0.240, 0.340] | 0.44 [0.389, 0.450] | 0.92 [0.890, 0.950] | 1.84 [1.77, 1.99] | 2.54 [2.32, 3.09] | 5.46 [3.54, 5.78] | 3.8% [2.90, 4.90] | 0.1% [0, 0.300] | 0.491 [0.447, 0.541] |
| news/en@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 2.35 | 0.45 [0.360, 0.540] | 0.72 [0.649, 0.760] | 1.80 [1.73, 1.90] | 5.91 [5.43, 6.24] | 9.25 [7.73, 10.6] | 17.1 [12.0, 17.7] | 43.2% [40.1, 46.2] | 8.5% [6.70, 9.90] | 1.80 [1.56, 1.98] |
| news/en@256 | Qwen2.5 | distinct | 256 | 226 | 1,000 / 10,000 | 0.99 | 0.27 [0.200, 0.290] | 0.39 [0.340, 0.410] | 0.85 [0.820, 0.900] | 1.99 [1.91, 2.20] | 2.69 [2.55, 3.04] | 6.24 [3.17, 6.71] | 4.9% [3.90, 6.70] | 0.1% [0, 0.400] | 0.553 [0.500, 0.618] |
| wikipedia/en@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.79 | 0.97 [0.790, 0.990] | 1.20 [1.10, 1.25] | 2.40 [2.30, 2.49] | 5.77 [5.33, 6.24] | 8.31 [7.45, 9.92] | 16.3 [12.8, 16.9] | 63.7% [60.3, 67.3] | 8.5% [6.60, 9.70] | 1.62 [1.42, 1.83] |
| wikipedia/en@256 | Llama-3.2 | distinct | 256 | 223 | 1,000 / 10,000 | 1.00 | 0.33 [0.230, 0.330] | 0.42 [0.370, 0.420] | 0.89 [0.860, 0.940] | 2.00 [1.86, 2.11] | 2.52 [2.38, 3.07] | 4.93 [3.17, 5.28] | 5.0% [3.60, 6.10] | 0.0% [0, 0.300] | 0.512 [0.472, 0.559] |
| wikipedia/en@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.33 | 0.61 [0.500, 0.690] | 0.88 [0.810, 0.969] | 2.33 [2.22, 2.53] | 9.28 [8.30, 10.1] | 14.1 [11.7, 17.0] | 34.9 [18.2, 36.0] | 58.8% [56.0, 62.7] | 17.1% [15.1, 19.6] | 3.00 [2.65, 3.43] |
| wikipedia/en@256 | Qwen2.5 | distinct | 256 | 217 | 1,000 / 10,000 | 0.98 | 0.24 [0.180, 0.260] | 0.35 [0.310, 0.360] | 0.85 [0.820, 0.890] | 2.04 [1.90, 2.25] | 2.99 [2.75, 3.20] | 4.90 [3.27, 5.32] | 5.4% [4.09, 7.30] | 0.0% [0, 0.300] | 0.566 [0.521, 0.614] |
| stackexchange/en@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.08 | 1.64 [1.47, 1.70] | 1.92 [1.81, 1.96] | 2.94 [2.86, 3.01] | 4.73 [4.62, 4.99] | 5.53 [5.33, 6.02] | 7.23 [6.13, 7.70] | 92.4% [89.6, 94.0] | 3.8% [2.40, 4.81] | 0.881 [0.834, 0.931] |
| stackexchange/en@256 | Llama-3.2 | distinct | 256 | 217 | 1,000 / 10,000 | 1.01 | 0.41 [0.340, 0.410] | 0.49 [0.450, 0.500] | 0.93 [0.905, 0.960] | 1.78 [1.69, 1.90] | 2.22 [2.08, 2.55] | 3.30 [2.69, 3.60] | 2.8% [1.50, 3.90] | 0.0% [0, 0] | 0.408 [0.383, 0.433] |
| stackexchange/en@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.23 | 1.51 [1.32, 1.56] | 1.84 [1.71, 1.90] | 2.99 [2.88, 3.08] | 5.40 [5.20, 5.82] | 7.12 [6.66, 7.80] | 9.99 [7.91, 10.6] | 91.1% [86.9, 92.7] | 7.8% [6.40, 10.1] | 1.18 [1.10, 1.26] |
| stackexchange/en@256 | Qwen2.5 | distinct | 256 | 215 | 1,000 / 10,000 | 1.00 | 0.38 [0.300, 0.380] | 0.49 [0.440, 0.500] | 0.91 [0.880, 0.940] | 1.86 [1.72, 1.99] | 2.34 [2.23, 2.81] | 3.62 [2.83, 3.92] | 3.7% [2.30, 4.90] | 0.0% [0, 0] | 0.425 [0.389, 0.461] |
| wikipedia/de@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.34 | 1.26 [1.12, 1.27] | 1.46 [1.35, 1.46] | 2.24 [2.19, 2.31] | 3.53 [3.47, 3.71] | 4.19 [3.93, 4.67] | 5.69 [4.92, 6.13] | 66.8% [61.8, 68.3] | 0.4% [0, 0.700] | 0.670 [0.636, 0.702] |
| wikipedia/de@256 | Llama-3.2 | distinct | 256 | 229 | 1,000 / 10,000 | 1.00 | 0.41 [0.340, 0.430] | 0.54 [0.480, 0.530] | 0.94 [0.910, 0.970] | 1.65 [1.60, 1.75] | 2.05 [1.91, 2.33] | 2.79 [2.41, 3.07] | 1.3% [0.700, 2.40] | 0.0% [0, 0] | 0.360 [0.338, 0.383] |
| wikipedia/de@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 2.64 | 1.01 [0.850, 1.05] | 1.25 [1.16, 1.29] | 2.23 [2.17, 2.34] | 5.30 [4.79, 5.83] | 8.84 [7.49, 11.0] | 17.4 [12.3, 17.9] | 61.9% [57.8, 64.2] | 5.8% [4.40, 7.51] | 1.54 [1.32, 1.77] |
| wikipedia/de@256 | Qwen2.5 | distinct | 256 | 226 | 1,000 / 10,000 | 0.99 | 0.37 [0.290, 0.370] | 0.48 [0.420, 0.480] | 0.90 [0.880, 0.950] | 1.77 [1.66, 1.86] | 2.30 [2.15, 2.58] | 2.69 [2.56, 3.05] | 2.5% [1.50, 3.90] | 0.0% [0, 0] | 0.405 [0.380, 0.429] |
| wikipedia/ru@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 2.46 | 1.08 [0.960, 1.13] | 1.33 [1.24, 1.35] | 2.16 [2.09, 2.23] | 4.48 [4.23, 5.03] | 7.79 [6.31, 9.76] | 12.9 [11.0, 13.6] | 58.8% [55.1, 63.1] | 3.6% [2.60, 5.10] | 1.27 [1.07, 1.42] |
| wikipedia/ru@256 | Llama-3.2 | distinct | 256 | 227 | 1,000 / 10,000 | 1.00 | 0.43 [0.360, 0.440] | 0.55 [0.490, 0.540] | 0.94 [0.910, 0.970] | 1.72 [1.62, 1.83] | 2.25 [2.08, 2.42] | 2.88 [2.44, 3.18] | 2.2% [1.50, 3.40] | 0.0% [0, 0] | 0.372 [0.349, 0.391] |
| wikipedia/ru@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 2.75 | 1.00 [0.870, 1.04] | 1.22 [1.14, 1.26] | 2.36 [2.27, 2.47] | 5.50 [5.09, 6.05] | 9.10 [7.59, 10.3] | 13.2 [10.8, 13.9] | 64.6% [60.7, 67.6] | 6.8% [5.40, 8.60] | 1.53 [1.40, 1.70] |
| wikipedia/ru@256 | Qwen2.5 | distinct | 256 | 222 | 1,000 / 10,000 | 1.00 | 0.35 [0.280, 0.370] | 0.46 [0.410, 0.470] | 0.92 [0.890, 0.960] | 1.81 [1.73, 1.95] | 2.40 [2.21, 2.81] | 3.29 [2.88, 3.68] | 2.9% [2.00, 4.50] | 0.0% [0, 0] | 0.442 [0.412, 0.465] |
| wikipedia/ar@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.00 | 1.52 [1.36, 1.58] | 1.77 [1.68, 1.83] | 2.80 [2.72, 2.87] | 4.88 [4.69, 5.17] | 6.00 [5.63, 6.37] | 7.75 [6.76, 8.26] | 88.4% [85.6, 90.1] | 4.4% [3.00, 6.00] | 0.973 [0.913, 1.03] |
| wikipedia/ar@256 | Llama-3.2 | distinct | 256 | 220 | 1,000 / 10,000 | 1.01 | 0.46 [0.370, 0.470] | 0.57 [0.510, 0.570] | 0.95 [0.920, 0.970] | 1.63 [1.58, 1.76] | 2.04 [1.91, 2.39] | 3.43 [2.47, 3.77] | 1.2% [0.600, 2.30] | 0.0% [0, 0] | 0.351 [0.324, 0.379] |
| wikipedia/ar@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.23 | 1.14 [1.02, 1.25] | 1.47 [1.38, 1.55] | 2.78 [2.65, 2.88] | 6.24 [5.95, 6.73] | 8.99 [8.02, 10.8] | 12.0 [11.2, 12.6] | 78.8% [75.6, 81.5] | 12.7% [10.6, 15.0] | 1.63 [1.50, 1.77] |
| wikipedia/ar@256 | Qwen2.5 | distinct | 256 | 217 | 1,000 / 10,000 | 0.99 | 0.37 [0.300, 0.380] | 0.48 [0.420, 0.490] | 0.90 [0.875, 0.935] | 1.78 [1.69, 1.92] | 2.32 [2.16, 2.75] | 3.50 [2.76, 3.82] | 2.7% [2.00, 4.21] | 0.0% [0, 0] | 0.422 [0.391, 0.454] |
| wikipedia/zh@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.65 | 2.52 [2.28, 2.54] | 2.77 [2.65, 2.79] | 3.60 [3.54, 3.67] | 4.70 [4.61, 4.87] | 5.27 [5.04, 5.58] | 6.99 [5.56, 7.49] | 99.9% [99.5, 100] | 1.8% [1.30, 3.50] | 0.599 [0.569, 0.631] |
| wikipedia/zh@256 | Llama-3.2 | distinct | 256 | 215 | 1,000 / 10,000 | 1.01 | 0.55 [0.440, 0.540] | 0.65 [0.590, 0.640] | 0.99 [0.960, 1.01] | 1.43 [1.43, 1.54] | 1.67 [1.62, 1.86] | 2.78 [1.93, 3.01] | 0.2% [0, 0.700] | 0.0% [0, 0] | 0.257 [0.241, 0.275] |
| wikipedia/zh@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.67 | 1.95 [1.80, 1.98] | 2.18 [2.08, 2.23] | 3.36 [3.27, 3.45] | 6.19 [5.74, 6.54] | 8.65 [7.69, 9.95] | 12.0 [10.6, 12.7] | 98.2% [96.4, 98.8] | 12.6% [10.6, 15.3] | 1.34 [1.22, 1.45] |
| wikipedia/zh@256 | Qwen2.5 | distinct | 256 | 215 | 1,000 / 10,000 | 1.01 | 0.44 [0.370, 0.460] | 0.56 [0.500, 0.570] | 0.95 [0.920, 0.970] | 1.64 [1.59, 1.76] | 2.14 [1.93, 2.42] | 3.35 [2.53, 3.63] | 1.6% [0.800, 2.50] | 0.0% [0, 0] | 0.354 [0.325, 0.377] |
| wikipedia/ja@256 | Llama-3.2 | raw | 256 | 255 | 1,000 / 10,000 | 3.23 | 1.75 [1.62, 1.82] | 2.05 [1.95, 2.09] | 3.06 [3.01, 3.14] | 4.94 [4.71, 5.16] | 5.84 [5.55, 6.57] | 8.50 [6.67, 8.99] | 95.9% [93.9, 96.8] | 4.7% [3.10, 5.90] | 0.895 [0.838, 0.947] |
| wikipedia/ja@256 | Llama-3.2 | distinct | 256 | 217 | 1,000 / 10,000 | 1.00 | 0.42 [0.350, 0.430] | 0.51 [0.460, 0.520] | 0.94 [0.900, 0.960] | 1.77 [1.69, 1.87] | 2.23 [2.09, 2.40] | 2.43 [2.39, 2.79] | 2.3% [1.50, 3.60] | 0.0% [0, 0] | 0.388 [0.367, 0.407] |
| wikipedia/ja@256 | Qwen2.5 | raw | 256 | 255 | 1,000 / 10,000 | 3.59 | 1.49 [1.30, 1.55] | 1.80 [1.69, 1.86] | 3.24 [3.09, 3.32] | 7.00 [6.32, 7.53] | 9.85 [8.90, 10.7] | 12.7 [10.8, 13.3] | 89.3% [86.3, 91.7] | 15.2% [12.5, 17.3] | 1.67 [1.54, 1.79] |
| wikipedia/ja@256 | Qwen2.5 | distinct | 256 | 212 | 1,000 / 10,000 | 1.01 | 0.31 [0.240, 0.330] | 0.42 [0.370, 0.420] | 0.90 [0.850, 0.925] | 2.14 [1.99, 2.32] | 2.92 [2.68, 3.28] | 4.59 [3.33, 4.89] | 6.5% [4.90, 8.20] | 0.0% [0, 0] | 0.554 [0.508, 0.593] |
| wikipedia/en@1024 | Llama-3.2 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 6.01 | 1.56 [1.41, 1.73] | 2.09 [1.95, 2.21] | 4.95 [4.68, 5.16] | 14.2 [13.3, 15.0] | 23.1 [18.3, 26.0] | 39.7 [26.5, 40.5] | 96.2% [94.2, 97.1] | 48.9% [46.1, 52.2] | 4.24 [3.82, 4.68] |
| wikipedia/en@1024 | Llama-3.2 | distinct | 1,024 | 806 | 1,000 / 10,000 | 0.99 | 0.24 [0.180, 0.250] | 0.34 [0.300, 0.360] | 0.88 [0.835, 0.915] | 2.03 [1.95, 2.17] | 2.76 [2.48, 3.27] | 6.07 [3.56, 6.48] | 5.8% [4.20, 7.30] | 0.1% [0, 0.300] | 0.568 [0.522, 0.626] |
| wikipedia/en@1024 | Qwen2.5 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 7.55 | 1.06 [0.860, 1.15] | 1.54 [1.37, 1.67] | 5.12 [4.74, 5.46] | 21.9 [20.6, 23.9] | 32.1 [29.6, 36.2] | 57.7 [44.5, 58.7] | 89.0% [87.0, 90.9] | 50.7% [47.8, 53.7] | 7.09 [6.26, 7.87] |
| wikipedia/en@1024 | Qwen2.5 | distinct | 1,024 | 779 | 1,000 / 10,000 | 0.99 | 0.20 [0.160, 0.230] | 0.31 [0.270, 0.320] | 0.86 [0.820, 0.900] | 2.11 [1.99, 2.29] | 3.02 [2.64, 3.39] | 4.80 [3.71, 5.13] | 5.7% [4.90, 7.81] | 0.0% [0, 0.200] | 0.591 [0.548, 0.637] |
| gutenberg/en@1024 | Llama-3.2 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 4.79 | 1.01 [0.879, 1.15] | 1.45 [1.30, 1.54] | 3.64 [3.43, 3.87] | 12.1 [11.1, 13.0] | 19.6 [16.1, 21.8] | 34.1 [23.4, 34.9] | 83.9% [81.1, 86.4] | 32.1% [29.2, 35.0] | 3.76 [3.37, 4.17] |
| gutenberg/en@1024 | Llama-3.2 | distinct | 1,024 | 871 | 1,000 / 10,000 | 1.00 | 0.24 [0.180, 0.250] | 0.33 [0.290, 0.350] | 0.87 [0.835, 0.915] | 2.02 [1.90, 2.16] | 2.71 [2.42, 3.14] | 5.58 [3.42, 5.92] | 5.1% [3.70, 6.80] | 0.1% [0, 0.300] | 0.551 [0.509, 0.594] |
| gutenberg/en@1024 | Qwen2.5 | raw | 1,024 | 1,023 | 1,000 / 10,000 | 4.94 | 0.99 [0.829, 1.11] | 1.38 [1.27, 1.49] | 3.87 [3.67, 4.01] | 12.3 [11.1, 13.7] | 20.7 [17.2, 25.3] | 39.0 [26.3, 39.8] | 83.8% [80.8, 86.4] | 33.7% [31.7, 36.9] | 3.91 [3.51, 4.40] |
| gutenberg/en@1024 | Qwen2.5 | distinct | 1,024 | 861 | 1,000 / 10,000 | 0.98 | 0.22 [0.170, 0.250] | 0.34 [0.310, 0.369] | 0.84 [0.810, 0.880] | 1.98 [1.87, 2.13] | 2.88 [2.47, 3.43] | 6.32 [3.68, 6.71] | 4.6% [3.50, 6.30] | 0.1% [0, 0.300] | 0.571 [0.509, 0.622] |

Per-key false-positive levels at α = 0.01 over the K = 1,000 production keys on the N_eff = N = 10,000 realised texts of each corpus cell (the nominal level is 1%); h = 1, the cell's longest length. The 1%, 5%, 50%, 95% and 99% key quantiles, the worst sampled key and the shares carry their crossed key-by-document bootstrap intervals (200 resamples of texts and keys; the worst key's interval is the sampled maximum's under resampling, never a population extreme; gate constraint 12); the SD carries its key-bootstrap interval conditional on the texts. Gumbel-max (the per-text Gamma threshold).

### population

| Family | Rule | h | Cells | With a positive mixture variance | Ratio two-way / mixture, median | Range | Within 2 bootstrap SEs | Negative two-way estimates |
|---|---|---|---|---|---|---|---|---|
| KGW γ = 0.25 | raw | 0 | 68 | 68 | 1.10 | 0.965–1.38 | 64 | 0 |
| KGW γ = 0.25 | raw | 1 | 68 | 68 | 1.58 | 0.997–3.17 | 16 | 0 |
| KGW γ = 0.25 | raw | 2 | 68 | 68 | 1.75 | 0.678–3.64 | 11 | 0 |
| KGW γ = 0.25 | raw | 3 | 68 | 68 | 1.46 | 0.845–12.3 | 45 | 0 |
| KGW γ = 0.25 | raw | 4 | 68 | 68 | 2.20 | −0.129–25.8 | 42 | 1 |
| KGW γ = 0.25 | distinct | 0 | 68 | 68 | 1.57 | 1.03–2.12 | 21 | 0 |
| KGW γ = 0.25 | distinct | 1 | 68 | 68 | 1.54 | 1.13–2.15 | 1 | 0 |
| KGW γ = 0.25 | distinct | 2 | 68 | 68 | 1.52 | 1.03–2.20 | 19 | 0 |
| KGW γ = 0.25 | distinct | 3 | 68 | 68 | 1.39 | 0.189–12.3 | 45 | 0 |
| KGW γ = 0.25 | distinct | 4 | 68 | 68 | 1.68 | −5.45–36.4 | 50 | 9 |
| KGW γ = 0.25 | first | 0 | 68 | 68 | 0 | 0–0 | 0 | 0 |
| KGW γ = 0.25 | first | 1 | 68 | 68 | 1.63 | 1.15–2.74 | 1 | 0 |
| KGW γ = 0.25 | first | 2 | 68 | 68 | 1.52 | 1.10–2.26 | 20 | 0 |
| KGW γ = 0.25 | first | 3 | 68 | 68 | 1.54 | 0.730–10.7 | 45 | 0 |
| KGW γ = 0.25 | first | 4 | 68 | 68 | 1.78 | −2.11–37.3 | 50 | 7 |
| KGW γ = 0.5 | raw | 0 | 68 | 68 | 0.838 | 0.633–1.10 | 34 | 0 |
| KGW γ = 0.5 | raw | 1 | 68 | 68 | 1.08 | 0.615–1.46 | 28 | 0 |
| KGW γ = 0.5 | raw | 2 | 68 | 68 | 0.806 | 0.451–2.64 | 27 | 0 |
| KGW γ = 0.5 | raw | 3 | 68 | 68 | 1.13 | 0.621–8.94 | 57 | 0 |
| KGW γ = 0.5 | raw | 4 | 68 | 68 | 1.19 | −0.848–10.7 | 56 | 1 |
| KGW γ = 0.5 | distinct | 0 | 68 | 68 | 0.892 | 0.663–1.79 | 53 | 0 |
| KGW γ = 0.5 | distinct | 1 | 68 | 68 | 1.04 | 0.789–1.19 | 65 | 0 |
| KGW γ = 0.5 | distinct | 2 | 68 | 68 | 0.973 | 0.676–1.25 | 58 | 0 |
| KGW γ = 0.5 | distinct | 3 | 68 | 68 | 1.08 | −0.398–2.38 | 63 | 1 |
| KGW γ = 0.5 | distinct | 4 | 68 | 68 | 1.01 | −1.44–11.5 | 62 | 6 |
| KGW γ = 0.5 | first | 0 | 68 | 68 | 0 | 0–0 | 0 | 0 |
| KGW γ = 0.5 | first | 1 | 68 | 68 | 1.01 | 0.857–1.28 | 65 | 0 |
| KGW γ = 0.5 | first | 2 | 68 | 68 | 1.00 | 0.751–1.35 | 68 | 0 |
| KGW γ = 0.5 | first | 3 | 68 | 68 | 1.10 | −0.470–3.86 | 64 | 2 |
| KGW γ = 0.5 | first | 4 | 68 | 68 | 1.04 | −3.38–13.2 | 63 | 5 |
| KGW fixed (h = 0) | raw | 0 | 136 | 136 | 1.01 | 0.632–1.42 | 95 | 0 |
| KGW fixed (h = 0) | distinct | 0 | 136 | 136 | 1.19 | 0.665–2.17 | 78 | 0 |
| KGW fixed (h = 0) | first | 0 | 136 | 136 | 0 | 0–0 | 0 | 0 |
| Gumbel-max | raw | 0 | 68 | 68 | 1.42 | 1.02–3.50 | 21 | 0 |
| Gumbel-max | raw | 1 | 68 | 68 | 2.26 | 0.998–4.51 | 6 | 0 |
| Gumbel-max | raw | 2 | 68 | 68 | 2.89 | 0.698–5.73 | 3 | 0 |
| Gumbel-max | raw | 3 | 68 | 68 | 3.16 | 0.890–21.0 | 24 | 0 |
| Gumbel-max | raw | 4 | 68 | 68 | 2.96 | −2.06–36.5 | 40 | 1 |
| Gumbel-max | distinct | 0 | 68 | 68 | 2.47 | 1.29–4.76 | 4 | 0 |
| Gumbel-max | distinct | 1 | 68 | 68 | 2.22 | 1.14–4.02 | 1 | 0 |
| Gumbel-max | distinct | 2 | 68 | 68 | 2.26 | 1.27–5.02 | 6 | 0 |
| Gumbel-max | distinct | 3 | 68 | 68 | 2.13 | −4.47–5.06 | 29 | 2 |
| Gumbel-max | distinct | 4 | 68 | 68 | 2.36 | −1.54–57.4 | 44 | 6 |
| Gumbel-max | first | 0 | 68 | 68 | 24,109 | 11,339–30,331 | 0 | 0 |
| Gumbel-max | first | 1 | 68 | 68 | 2.55 | 1.45–4.75 | 0 | 0 |
| Gumbel-max | first | 2 | 68 | 68 | 2.38 | 1.25–5.00 | 9 | 0 |
| Gumbel-max | first | 3 | 68 | 68 | 2.20 | −2.44–5.34 | 29 | 1 |
| Gumbel-max | first | 4 | 68 | 68 | 2.31 | −10.4–64.8 | 46 | 5 |

The secondary population target (protocol §3): the two-way decomposition s_K² − MS_E/N_eff of the per-key levels (texts random; a two-way bootstrap SE, 100 resamples) against the predictor's population variance Var(α_k) (the mixture without the finite-text floor), at α = 0.01, every live cell of the setting. Descriptive; noisy where the across-key variance is small (Study 1 §5).

### corr_summary

| Tokenizer | Family | h | Rule | Pairs | Undefined (a constant cell) | Pearson range | Pearson median | Spearman range | Spearman median |
|---|---|---|---|---|---|---|---|---|---|
| Llama-3.2 | kgw | 0 | raw | 45 | 0 | −0.035–0.998 | 0.160 | −3.14e-03–0.995 | 0.218 |
| Llama-3.2 | kgw | 0 | distinct | 45 | 0 | −0.013–0.993 | 0.075 | 0.012–0.985 | 0.131 |
| Llama-3.2 | kgw | 1 | raw | 45 | 0 | −0.014–0.983 | 0.037 | −9.17e-03–0.974 | 0.041 |
| Llama-3.2 | kgw | 1 | distinct | 45 | 0 | −0.028–0.961 | 0.034 | −0.030–0.941 | 0.040 |
| Llama-3.2 | kgw | 2 | raw | 45 | 0 | −0.036–0.733 | 0.025 | −0.052–0.721 | 0.023 |
| Llama-3.2 | kgw | 2 | distinct | 45 | 0 | −0.052–0.668 | 0.026 | −0.060–0.661 | 0.023 |
| Qwen2.5 | kgw | 0 | raw | 45 | 0 | 0.075–0.997 | 0.247 | 0.124–0.996 | 0.270 |
| Qwen2.5 | kgw | 0 | distinct | 45 | 0 | 0.046–0.994 | 0.177 | 0.099–0.986 | 0.206 |
| Qwen2.5 | kgw | 1 | raw | 45 | 0 | 0.138–0.994 | 0.495 | 0.136–0.989 | 0.475 |
| Qwen2.5 | kgw | 1 | distinct | 45 | 0 | 0.058–0.974 | 0.281 | 0.063–0.963 | 0.265 |
| Qwen2.5 | kgw | 2 | raw | 45 | 0 | 0.040–0.978 | 0.271 | 0.028–0.960 | 0.269 |
| Qwen2.5 | kgw | 2 | distinct | 45 | 0 | 0.030–0.881 | 0.186 | 0.018–0.855 | 0.181 |
| Llama-3.2 | gumbel | 0 | raw | 45 | 0 | 0.011–0.998 | 0.188 | 9.70e-03–0.995 | 0.217 |
| Llama-3.2 | gumbel | 0 | distinct | 45 | 0 | 0.024–0.994 | 0.092 | 0.017–0.984 | 0.141 |
| Llama-3.2 | gumbel | 1 | raw | 45 | 0 | −0.047–0.986 | 0.051 | −0.046–0.971 | 0.051 |
| Llama-3.2 | gumbel | 1 | distinct | 45 | 0 | −0.064–0.965 | 0.048 | −0.073–0.950 | 0.052 |
| Llama-3.2 | gumbel | 2 | raw | 45 | 0 | −0.043–0.703 | 0.035 | −0.044–0.668 | 0.032 |
| Llama-3.2 | gumbel | 2 | distinct | 45 | 0 | −0.028–0.653 | 0.030 | −0.042–0.610 | 0.025 |
| Qwen2.5 | gumbel | 0 | raw | 45 | 0 | 0.031–0.997 | 0.251 | 0.100–0.995 | 0.326 |
| Qwen2.5 | gumbel | 0 | distinct | 45 | 0 | 0.023–0.995 | 0.135 | 0.082–0.985 | 0.217 |
| Qwen2.5 | gumbel | 1 | raw | 45 | 0 | 0.100–0.994 | 0.456 | 0.110–0.985 | 0.422 |
| Qwen2.5 | gumbel | 1 | distinct | 45 | 0 | 0.037–0.967 | 0.225 | 0.055–0.953 | 0.218 |
| Qwen2.5 | gumbel | 2 | raw | 45 | 0 | 0.073–0.986 | 0.288 | 0.073–0.937 | 0.282 |
| Qwen2.5 | gumbel | 2 | distinct | 45 | 0 | −8.45e-03–0.866 | 0.189 | −0.017–0.819 | 0.175 |

The across-key correlation of the per-key levels between corpus cells at L = 256 (45 pairs of the 10 cells per setting); a correlation is undefined when a cell's levels are constant over the keys.

### corr_matrix

|  | gutenberg/en@1024 | news/en@256 | stackexchange/en@256 | wikipedia/ar@256 | wikipedia/de@256 | wikipedia/en@1024 | wikipedia/en@256 | wikipedia/ja@256 | wikipedia/ru@256 | wikipedia/zh@256 |
|---|---|---|---|---|---|---|---|---|---|---|
| gutenberg/en@1024 | 1 | 0.525 | 0.469 | 0.019 | 5.72e-03 | 0.614 | 0.598 | 0.013 | −0.028 | 0.030 |
| news/en@256 | 0.505 | 1 | 0.452 | 0.014 | 0.025 | 0.624 | 0.617 | 0.050 | 0.028 | 0.030 |
| stackexchange/en@256 | 0.483 | 0.453 | 1 | 0.026 | −0.015 | 0.434 | 0.420 | 0.050 | −0.011 | 0.024 |
| wikipedia/ar@256 | 4.64e-03 | 0.022 | 0.022 | 1 | 4.03e-03 | 0.076 | 0.082 | 0.036 | 0.071 | 9.36e-03 |
| wikipedia/de@256 | 9.89e-04 | 0.034 | 2.30e-03 | 0.013 | 1 | 0.034 | 0.037 | 0.036 | 0.032 | 6.55e-03 |
| wikipedia/en@1024 | 0.586 | 0.627 | 0.403 | 0.061 | 0.034 | 1 | 0.961 | 0.052 | 7.66e-03 | 0.027 |
| wikipedia/en@256 | 0.568 | 0.615 | 0.392 | 0.080 | 0.040 | 0.941 | 1 | 0.066 | 7.53e-03 | 0.039 |
| wikipedia/ja@256 | −5.88e-03 | 0.055 | 0.045 | 0.039 | 0.050 | 0.044 | 0.056 | 1 | 6.92e-03 | 0.176 |
| wikipedia/ru@256 | −0.030 | 0.020 | −7.25e-03 | 0.051 | 0.058 | −0.021 | −0.019 | −0.018 | 1 | −0.028 |
| wikipedia/zh@256 | 0.017 | 0.032 | 0.044 | 0.010 | 0.032 | 0.029 | 0.048 | 0.194 | −0.013 | 1 |

Llama-3.2, kgw, h = 1, distinct rule, L = 256, α = 0.01: Pearson above the diagonal, Spearman below. Every setting is in `tables_correlations_full.md`.

### language

| Tokenizer | Family | h | Rule | K | Keys with all six levels 0 | Keys with a 0 and a positive level | Keys with all six positive | Share with max/min > 2 | Share with max/min > 5 | Median max/min | Largest max/min | SD of the pairwise difference (pp), range over the 15 pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Llama-3.2 | kgw | 0 | raw | 1000 | 0 | 0 | 1000 | 99.8% | 90.9% | 16.6 | 998 | 9.00–19.1 |
| Llama-3.2 | kgw | 0 | distinct | 1000 | 0 | 45 | 955 | 99.9% | 93.9% | 23.3 | 881 | 1.89–2.83 |
| Llama-3.2 | kgw | 1 | raw | 1000 | 0 | 0 | 1000 | 75.1% | 0.9% | 2.38 | 6.40 | 0.978–2.01 |
| Llama-3.2 | kgw | 1 | distinct | 1000 | 0 | 0 | 1000 | 66.5% | 1.4% | 2.30 | 6.96 | 0.453–0.668 |
| Llama-3.2 | kgw | 2 | raw | 1000 | 0 | 0 | 1000 | 11.2% | 0.0% | 1.61 | 3.42 | 0.340–0.638 |
| Llama-3.2 | kgw | 2 | distinct | 1000 | 0 | 0 | 1000 | 3.7% | 0.0% | 1.48 | 2.71 | 0.223–0.292 |
| Qwen2.5 | kgw | 0 | raw | 1000 | 0 | 0 | 1000 | 100.0% | 91.5% | 16.2 | 1,609 | 10.0–18.9 |
| Qwen2.5 | kgw | 0 | distinct | 1000 | 0 | 93 | 907 | 99.7% | 94.4% | 26.4 | 1,236 | 1.67–3.11 |
| Qwen2.5 | kgw | 1 | raw | 1000 | 0 | 0 | 1000 | 76.4% | 3.6% | 2.53 | 9.39 | 1.45–3.09 |
| Qwen2.5 | kgw | 1 | distinct | 1000 | 0 | 0 | 1000 | 74.4% | 4.0% | 2.44 | 9.19 | 0.511–0.783 |
| Qwen2.5 | kgw | 2 | raw | 1000 | 0 | 0 | 1000 | 28.4% | 0.0% | 1.79 | 3.99 | 0.512–1.09 |
| Qwen2.5 | kgw | 2 | distinct | 1000 | 0 | 0 | 1000 | 12.4% | 0.0% | 1.62 | 3.43 | 0.276–0.387 |
| Llama-3.2 | gumbel | 0 | raw | 1000 | 0 | 0 | 1000 | 99.6% | 87.4% | 14.7 | 422 | 9.79–19.5 |
| Llama-3.2 | gumbel | 0 | distinct | 1000 | 0 | 63 | 937 | 99.7% | 93.5% | 22.6 | 1,365 | 1.61–2.84 |
| Llama-3.2 | gumbel | 1 | raw | 1000 | 0 | 0 | 1000 | 78.5% | 2.0% | 2.48 | 9.51 | 0.893–2.00 |
| Llama-3.2 | gumbel | 1 | distinct | 1000 | 0 | 0 | 1000 | 70.3% | 2.1% | 2.35 | 12.5 | 0.410–0.633 |
| Llama-3.2 | gumbel | 2 | raw | 1000 | 0 | 0 | 1000 | 13.9% | 0.0% | 1.63 | 3.82 | 0.321–0.635 |
| Llama-3.2 | gumbel | 2 | distinct | 1000 | 0 | 0 | 1000 | 4.8% | 0.0% | 1.50 | 2.58 | 0.207–0.277 |
| Qwen2.5 | gumbel | 0 | raw | 1000 | 0 | 0 | 1000 | 99.7% | 88.4% | 15.3 | 551 | 9.72–20.0 |
| Qwen2.5 | gumbel | 0 | distinct | 1000 | 0 | 110 | 890 | 99.9% | 94.2% | 25.7 | 2,220 | 1.72–2.97 |
| Qwen2.5 | gumbel | 1 | raw | 1000 | 0 | 0 | 1000 | 79.3% | 5.4% | 2.57 | 13.5 | 1.36–2.91 |
| Qwen2.5 | gumbel | 1 | distinct | 1000 | 0 | 0 | 1000 | 77.3% | 4.8% | 2.55 | 15.7 | 0.463–0.712 |
| Qwen2.5 | gumbel | 2 | raw | 1000 | 0 | 0 | 1000 | 30.7% | 0.2% | 1.77 | 5.78 | 0.510–1.27 |
| Qwen2.5 | gumbel | 2 | distinct | 1000 | 0 | 0 | 1000 | 16.4% | 0.0% | 1.63 | 4.14 | 0.245–0.356 |

The per-key disparity across the six Wikipedia language cells at L = 256 (en, de, ru, ar, zh, ja), α = 0.01: the ratio of the largest to the smallest of a key's six levels is defined only for the keys with all six positive, and the shares, median and maximum are over those keys (their number is the denominator); empirical finite-text ratios over the sampled keys, not calibrated population language effects (protocol §7).

### tokenizer_axis

| Family | h | Rule | Cells | SD ratio Qwen / Llama, range | Median | Across-tokenizer Pearson, range | Median | Key-mean level, Llama (%) | Key-mean level, Qwen (%) |
|---|---|---|---|---|---|---|---|---|---|
| kgw | 0 | raw | 10 | 0.984–1.49 | 1.06 | 0.048–0.931 | 0.670 | 6.59%–12.06% | 7.36%–12.15% |
| kgw | 0 | distinct | 10 | 0.941–1.56 | 1.06 | 0.034–0.569 | 0.382 | 1.09%–1.23% | 1.12%–1.25% |
| kgw | 0 | first | 10 | — | — | — | — | 0.00%–0.00% | 0.00%–0.00% |
| kgw | 1 | raw | 10 | 1.06–2.56 | 1.78 | −0.013–0.759 | 0.176 | 2.52%–4.23% | 2.79%–4.31% |
| kgw | 1 | distinct | 10 | 1.02–1.42 | 1.26 | 0.012–0.618 | 0.203 | 1.12%–1.17% | 1.14%–1.18% |
| kgw | 1 | first | 10 | 1.02–1.38 | 1.16 | −0.025–0.403 | 0.114 | 1.14%–1.19% | 1.16%–1.19% |
| kgw | 2 | raw | 10 | 1.24–4.24 | 1.78 | −0.054–0.172 | 0.014 | 1.64%–2.38% | 1.69%–2.44% |
| kgw | 2 | distinct | 10 | 1.09–1.71 | 1.36 | −0.037–0.209 | 0.026 | 1.13%–1.16% | 1.13%–1.15% |
| kgw | 2 | first | 10 | 1.04–1.53 | 1.23 | −0.057–0.125 | 0.021 | 1.13%–1.16% | 1.13%–1.16% |
| kgw | 3 | raw | 10 | 1.07–2.64 | 1.34 | −0.015–0.041 | 0.026 | 1.25%–1.73% | 1.28%–1.79% |
| kgw | 3 | distinct | 10 | 1.05–1.65 | 1.22 | −0.052–0.048 | 0.011 | 1.12%–1.15% | 1.12%–1.15% |
| kgw | 3 | first | 10 | 1.04–1.49 | 1.19 | −0.056–0.052 | 6.06e-03 | 1.13%–1.16% | 1.13%–1.15% |
| kgw | 4 | raw | 10 | 1.04–1.40 | 1.12 | −0.062–0.047 | −0.022 | 1.46%–1.91% | 1.50%–1.95% |
| kgw | 4 | distinct | 10 | 1.00–1.28 | 1.10 | −0.050–0.050 | −6.03e-03 | 1.17%–1.30% | 1.17%–1.29% |
| kgw | 4 | first | 10 | 1.00–1.25 | 1.10 | −0.040–0.059 | −0.012 | 1.14%–1.25% | 1.13%–1.25% |
| gumbel | 0 | raw | 10 | 0.951–1.31 | 1.02 | 0.012–0.935 | 0.713 | 6.70%–11.97% | 7.16%–12.34% |
| gumbel | 0 | distinct | 10 | 0.919–1.21 | 1.06 | 0.016–0.573 | 0.384 | 1.01%–1.12% | 0.98%–1.16% |
| gumbel | 0 | first | 10 | 0.782–1.43 | 1.11 | −0.045–0.935 | 0.059 | 0.90%–1.04% | 0.98%–1.06% |
| gumbel | 1 | raw | 10 | 1.08–2.30 | 1.72 | −0.048–0.773 | 0.220 | 2.14%–3.65% | 2.35%–3.67% |
| gumbel | 1 | distinct | 10 | 1.03–1.43 | 1.13 | −0.036–0.542 | 0.221 | 1.00%–1.01% | 0.98%–1.01% |
| gumbel | 1 | first | 10 | 1.03–1.39 | 1.10 | −0.016–0.314 | 0.134 | 1.00%–1.02% | 0.99%–1.01% |
| gumbel | 2 | raw | 10 | 1.31–5.50 | 1.80 | −0.021–0.147 | 2.62e-03 | 1.41%–2.17% | 1.49%–2.19% |
| gumbel | 2 | distinct | 10 | 1.06–1.68 | 1.34 | −0.018–0.150 | 0.025 | 0.99%–1.01% | 0.98%–1.01% |
| gumbel | 2 | first | 10 | 1.03–1.50 | 1.23 | −0.027–0.096 | 0.013 | 0.99%–1.00% | 0.98%–1.01% |
| gumbel | 3 | raw | 10 | 1.07–3.41 | 1.34 | −0.042–0.078 | 0.021 | 1.20%–1.67% | 1.24%–1.72% |
| gumbel | 3 | distinct | 10 | 1.01–1.76 | 1.22 | −0.065–0.052 | 0.032 | 0.99%–1.00% | 1.00%–1.02% |
| gumbel | 3 | first | 10 | 1.02–1.54 | 1.16 | −0.081–0.066 | 0.027 | 0.99%–1.00% | 0.99%–1.01% |
| gumbel | 4 | raw | 10 | 1.00–1.44 | 1.15 | −0.030–0.035 | 0.015 | 1.10%–1.48% | 1.13%–1.51% |
| gumbel | 4 | distinct | 10 | 1.000–1.33 | 1.10 | −0.026–0.042 | 0.011 | 0.99%–1.01% | 0.99%–1.01% |
| gumbel | 4 | first | 10 | 0.995–1.27 | 1.08 | −0.028–0.030 | −8.11e-04 | 0.99%–1.01% | 0.99%–1.01% |

The same texts under both tokenizers at L = 256, α = 0.01: the ratio of the across-key SDs of the level and the across-key correlation of the per-key levels (the identity predicts a non-zero correlation only through coinciding integer ids; protocol §7). Every (cell, L) is in `tables_tokenizer_full.md`.

### reduction

| Rule | Cells (both tokenizers, every L) | Reduction (1/C_cond − 1)/(V − 1), range | Largest, where | Cells at or above 1% | 1/C_cond, range | Covered share of V, range | Observed Var_fixed/Var_indep, range | Exact (V − 1/C_cond)/(V − 1), range |
|---|---|---|---|---|---|---|---|---|
| raw | 68 | 0.079%–0.346% | wikipedia/zh@256 Llama-3.2 L = 256 | 0 | 120–445 | 5.0%–48.7% | 0.9812–1.0165 | 0.9965–0.9992 |
| distinct | 68 | 0.164%–2.101% | gutenberg/en@1024 Llama-3.2 L = 1,024 | 7 | 250–2,695 | 5.0%–48.7% | 0.9750–1.0253 | 0.9790–0.9984 |
| first | 68 | 0.011%–0.139% | wikipedia/zh@256 Llama-3.2 L = 64 | 0 | 18–191 | 0.2%–2.9% | 0.9879–1.0281 | 0.9986–0.9999 |

At h = 0, γ = 0.25, at the realised q-weights of the production texts (a key-free quantity, in INPUTS.json before the lock; the observed ratio is the across-key sample variance of q̂ under the fixed colouring over that under the independent colouring, `q_hat.var_across_keys`, K = 1,000 each; S3's known-mean estimator is a separate check). V = 128,256 (Llama) and 151,936 (Qwen).

### integrity

| Check | Observed |
|---|---|
| Inventory | 3468 cells exactly as the grid expects, 3468 live, 0 markers; N_eff = N = 10,000 in every cell (the body contract) |
| Predictor flags (σ² negative or non-finite) | 0 |
| (cell, α) levels with a zero prediction (the registered non-finite ratio) | 0 |
| Live cells with texts at M = 0 | 0 |
| The first rule at h = 0 (one token per text): structural zeros | 680 of 816 (cell, α) levels in 272 KGW cells |
| KGW: \|per-text closed form − Study 1's single-threshold closed form\| for the predicted SD, largest | 0.0e+00 |
| S3 cells whose squared estimator was constant over the keys (recorded, never used) | 0 |
| Deployer subset selected from the grid | 240 cells × 3 α = 720 rows, every one with a populated crossed block (B = 200) |
| The secondary unit-σ block (protocol §6) | listed by the protocol, not computed by the locked analyzer; computed by the builder from the stored unit-σ predictor and reported in Table 5 as the builder's (a text/code discrepancy of the locked protocol, disclosed in §5) |
| Re-computation of s₀² from the 6-decimal mean-score values | largest relative difference from the stored estimator 1.9e-04 (the stored estimates and SEs are the record; protocol §3) |
| The predictions compared with the outcomes are the ones disclosed before the lock (INPUTS.json, pinned) | 9,180 (cell, α) predictions compared; largest \|difference\| 0.0e+00 (predicted SD, mean level, theory share), 0.0e+00 (exact key-mean), 0.0e+00 (ρ̄) |

### timing

| Chain (the five longest) | \|D\| tuples | Contexts | Build (s) | Key loop (s) | Cells | Cell statistics (s) | Chain (s) measured | Chain (s) projected (fitted model) | Peak RSS so far (GB) |
|---|---|---|---|---|---|---|---|---|---|
| gutenberg_en_1024__llama__h4 | 9,799,419 | 8,830,404 | 4.1 | 623.4 | 45 | 116.8 | 745.9 | 622.2 | 5.41 |
| gutenberg_en_1024__qwen__h4 | 9,691,513 | 8,677,139 | 4.2 | 610.8 | 45 | 113.7 | 730.9 | 619.8 | 5.41 |
| gutenberg_en_1024__llama__h3 | 8,838,542 | 6,086,336 | 3.9 | 577.4 | 45 | 109.4 | 692.7 | 604.9 | 5.41 |
| wikipedia_en_1024__llama__h4 | 9,351,709 | 8,357,975 | 4.0 | 575.2 | 45 | 111.1 | 692.2 | 611.1 | 5.41 |
| gutenberg_en_1024__qwen__h3 | 8,685,216 | 5,969,208 | 4.0 | 572.4 | 45 | 108.8 | 687.1 | 601.2 | 5.41 |

Measured 4.85 h in all (chain times sum to 4.85 h) against the validation's fitted projection of 6.08 h and the probe-scaled 8.13 h (protocol §11); every chain's measured and projected time is in `RUN_MANIFEST.json`.
