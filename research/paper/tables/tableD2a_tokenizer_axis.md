Table — The tokenizer axis: for the same texts, the across-key SD under Qwen2.5 tokens against the Llama-3.2 value and the across-tokenizer correlation of the per-key levels, by family, width and rule; the labelled post-hoc overlap account that explains the co-movement is Table D2b. Extracted verbatim from the Study 2 report's generated Table 21 (block `tokenizer_axis` of `outputs/study2_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R06); the report's own column note follows the table.

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
