Table — The H-language disparity: the per-key ratio of the largest to the smallest of a key's six Wikipedia-language levels at L = 256, by tokenizer, family, width and rule; empirical ratios over the sampled keys and realised texts, never a discrimination claim. Extracted verbatim from the Study 2 report's generated Table 20 (block `language` of `outputs/study2_v0.1/report/tables.md`, written by the report builder from the locked record and agreed at checkpoint R06); the report's own column note follows the table.

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
