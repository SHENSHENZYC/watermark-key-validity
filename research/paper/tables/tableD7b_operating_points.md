Table — The per-key operating points before and after calibration: Study 3's stored corpus null level (over its N_E = 10,000 texts) and the model-null level (over N₀ = 5000 unwatermarked generations) of each of the 100 power keys against its realised power over 50 generated texts, per method and prompt cell, on Qwen2.5-1.5B at the primary arm (δ = 0.5, h = 1), the raw rule, L = 256, α = 0.01, the per-key and scheme-level thresholds set on the same-cell human null texts (the diagonal source; N_cal = 5,000 for the per-key methods), with the correlation of a key's null level and its power under each method. The per-key operating point before and after calibration is the view Genhatharan 2026 and AutoMark report before this study [@genhatharan2026nominal; @gloaguen2026automark]; the aggregate comparison of the two negative classes is LUNA's [@park2026luna] and the two-key practice the artefact's [@xlr8harder2026synthid]; one model and three English prompt cells, no transfer claim. Extracted verbatim from the Study 4 report's generated Table 9 (block `operating_points` of `outputs/study4_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R10); the report's own column note follows the table.

| prompt cell | method | K | key-mean stored null level ℓ_k (Study 3, pp) | share of keys with ℓ_k > α | their mean power (pp) | the others' mean power (pp) | corr(ℓ_k, π_k) | key-mean model-null level ℓ̃_k (pp) | share with ℓ̃_k > α | corr(ℓ̃_k, π_k) |
|---|---|---|---|---|---|---|---|---|---|---|
| news/en@256 | nominal | 100 | 2.37 | 86.0 | 67.6 | 57.7 | 0.65 | 2.04 | 90.0 | 0.68 |
| news/en@256 | multiplier20 | 100 | 0.29 | 3.0 | 47.3 | 32.7 | 0.59 | 0.22 | 0.0 | 0.67 |
| news/en@256 | empirical | 100 | 0.21 | 0.0 | — | 29.2 | 0.60 | 0.17 | 0.0 | 0.63 |
| news/en@256 | pooled | 100 | 0.74 | 22.0 | 55.3 | 44.2 | 0.59 | 0.60 | 10.0 | 0.64 |
| news/en@256 | conformal@5000 | 100 | 0.87 | 21.0 | 54.9 | 51.5 | 0.28 | 0.82 | 23.0 | 0.61 |
| news/en@256 | tolerance@5000 | 100 | 0.69 | 3.0 | 55.3 | 48.2 | 0.27 | 0.63 | 9.0 | 0.55 |
| wikipedia/en@256 | nominal | 100 | 3.47 | 95.0 | 54.5 | 34.0 | 0.66 | 3.17 | 95.0 | 0.74 |
| wikipedia/en@256 | multiplier20 | 100 | 0.66 | 17.0 | 36.0 | 23.5 | 0.59 | 0.54 | 10.0 | 0.66 |
| wikipedia/en@256 | empirical | 100 | 0.20 | 3.0 | 22.7 | 11.2 | 0.56 | 0.15 | 0.0 | 0.63 |
| wikipedia/en@256 | pooled | 100 | 0.66 | 17.0 | 36.0 | 23.5 | 0.59 | 0.54 | 10.0 | 0.66 |
| wikipedia/en@256 | conformal@5000 | 100 | 0.82 | 12.0 | 41.2 | 30.8 | 0.31 | 0.79 | 18.0 | 0.53 |
| wikipedia/en@256 | tolerance@5000 | 100 | 0.64 | 2.0 | 43.0 | 27.8 | 0.42 | 0.62 | 11.0 | 0.54 |
| stackexchange/en@256 | nominal | 100 | 3.78 | 100.0 | 56.3 | — | 0.57 | 3.77 | 100.0 | 0.59 |
| stackexchange/en@256 | multiplier20 | 100 | 0.81 | 28.0 | 31.7 | 26.8 | 0.40 | 0.87 | 28.0 | 0.47 |
| stackexchange/en@256 | empirical | 100 | 0.53 | 3.0 | 20.0 | 21.6 | 0.43 | 0.59 | 7.0 | 0.43 |
| stackexchange/en@256 | pooled | 100 | 1.01 | 42.0 | 35.9 | 29.0 | 0.41 | 1.07 | 50.0 | 0.47 |
| stackexchange/en@256 | conformal@5000 | 100 | 0.90 | 24.0 | 32.1 | 29.9 | 0.22 | 0.97 | 45.0 | 0.39 |
| stackexchange/en@256 | tolerance@5000 | 100 | 0.69 | 1.0 | 26.0 | 26.7 | 0.25 | 0.77 | 10.0 | 0.40 |
