Table — The fixed-size reduction on real text at V ≥ 128k by rule. Extracted verbatim from the Study 2 report's generated Table 12 (block `reduction` of `outputs/study2_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R06); the report's own column note follows the table.

| Rule | Cells (both tokenizers, every L) | Reduction (1/C_cond − 1)/(V − 1), range | Largest, where | Cells at or above 1% | 1/C_cond, range | Covered share of V, range | Observed Var_fixed/Var_indep, range | Exact (V − 1/C_cond)/(V − 1), range |
|---|---|---|---|---|---|---|---|---|
| raw | 68 | 0.079%–0.346% | wikipedia/zh@256 Llama-3.2 L = 256 | 0 | 120–445 | 5.0%–48.7% | 0.9812–1.0165 | 0.9965–0.9992 |
| distinct | 68 | 0.164%–2.101% | gutenberg/en@1024 Llama-3.2 L = 1,024 | 7 | 250–2,695 | 5.0%–48.7% | 0.9750–1.0253 | 0.9790–0.9984 |
| first | 68 | 0.011%–0.139% | wikipedia/zh@256 Llama-3.2 L = 64 | 0 | 18–191 | 0.2%–2.9% | 0.9879–1.0281 | 0.9986–0.9999 |

At h = 0, γ = 0.25, at the realised q-weights of the production texts (a key-free quantity, in INPUTS.json before the lock; the observed ratio is the across-key sample variance of q̂ under the fixed colouring over that under the independent colouring, `q_hat.var_across_keys`, K = 1,000 each; S3's known-mean estimator is a separate check). V = 128,256 (Llama) and 151,936 (Qwen).
