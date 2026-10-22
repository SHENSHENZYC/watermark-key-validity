Table — Quality diagnostics per cell and arm with the human reference: the model's perplexity of its own tokens, rep-4, the loop share (rep-4 above 0.5); no text excluded. Extracted verbatim from the Study 4 report's generated Table 15 (block `quality` of `outputs/study4_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R10); the report's own column note follows the table.

| prompt cell | arm | units (generation arms: key-batches of 50 texts; unwatermarked: chunks of 500 texts; human: single continuations) | perplexity of the model's own tokens (admissible law; generation and unwatermarked rows: the mean over units of exp(−mean log-probability) over the 256 generated tokens; the human reference: exp(−pooled mean log-probability) over its 1,000 × 192 continuation tokens) | mean log-probability, first 192 tokens (the matched window) | rep-4 | loop share (rep-4 > 0.5, %) | green share (pp) | EOS mass |
|---|---|---|---|---|---|---|---|---|
| news/en@256 | h = 1, δ = 0.5 | 100 | 20.93 | -2.978 | 0.016 | 0.02 | 32.5 | 0.0004 |
| news/en@256 | h = 1, δ = 2.0 | 100 | 29.35 | -3.303 | 0.023 | 0.22 | 60.0 | 0.0005 |
| news/en@256 | h = 2, δ = 0.5 | 100 | 21.24 | -2.993 | 0.015 | 0.04 | 32.6 | 0.0005 |
| news/en@256 | unwatermarked | 10 | 21.12 | -2.990 | 0.016 | 0.02 | — | 0.0005 |
| wikipedia/en@256 | h = 1, δ = 0.5 | 100 | 11.22 | -2.362 | 0.040 | 0.08 | 31.5 | 0.0048 |
| wikipedia/en@256 | h = 1, δ = 2.0 | 100 | 16.60 | -2.733 | 0.047 | 0.32 | 55.9 | 0.0043 |
| wikipedia/en@256 | h = 2, δ = 0.5 | 100 | 11.40 | -2.375 | 0.040 | 0.04 | 31.5 | 0.0046 |
| wikipedia/en@256 | unwatermarked | 10 | 9.69 | -2.229 | 0.043 | 0.10 | — | 0.0057 |
| stackexchange/en@256 | h = 1, δ = 0.5 | 100 | 10.85 | -2.388 | 0.057 | 0.46 | 31.8 | 0.0014 |
| stackexchange/en@256 | h = 1, δ = 2.0 | 100 | 15.74 | -2.744 | 0.071 | 1.56 | 57.9 | 0.0013 |
| stackexchange/en@256 | h = 2, δ = 0.5 | 100 | 10.62 | -2.371 | 0.057 | 0.42 | 31.7 | 0.0014 |
| stackexchange/en@256 | unwatermarked | 10 | 10.61 | -2.378 | 0.059 | 0.58 | — | 0.0013 |
| news/en@256 | human continuation (reference, 192 tokens) | 1000 | 11.63 | -2.453 | 0.023 | — | — | — |
| wikipedia/en@256 | human continuation (reference, 192 tokens) | 1000 | 9.50 | -2.252 | 0.030 | — | — | — |
| stackexchange/en@256 | human continuation (reference, 192 tokens) | 1000 | 8.93 | -2.190 | 0.058 | — | — | — |
