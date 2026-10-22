Table — The labelled post-hoc overlap account of the across-tokenizer co-movement (the side computation `research/study2/tokenizer_overlap.py` of 2026-10-13, not pre-registered; its first version compared string-identical ids and was corrected at checkpoint R06, the superseded output kept beside it): per corpus cell at its longest length (L = 256, or 1,024 for the two 1,024-token cells), at h = 0 and h = 1 under the raw rule, over the N = 10,000 realised texts and the stored q̂ values of the K = 1,000 production keys: the number of integer tuple ids shared by the two tokenizers' document-averaged weight vectors, the share of each tokenizer's occurrence weight that sits on the shared tuples (Llama-3.2 / Qwen2.5), the identity-predicted correlation of the per-key mean green fraction q̂ from the shared hash inputs, and the observed correlation of the stored q̂ values of the two production cells; the last column is the semantic diagnostic (the share of each tokenizer's token occurrences on the 410 ids of 128,256 whose token string is the same in both vocabularies), not the hash-overlap estimand. The colouring hash is a function of the integer ids alone, so the identity, not shared strings, accounts for the co-movement; the shared-id account of the cross-language correlations under Qwen2.5 remains a hypothesis.

| Cell | h = 0: shared ids | weight on shared (L / Q) | predicted corr. | observed corr. | h = 1: shared pairs | weight on shared (L / Q) | predicted corr. | observed corr. | same-string occurrence share (L / Q) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| news/en@256 | 24,192 | 77.9% / 80.5% | 0.874 | 0.863 | 25,175 | 12.3% / 14.6% | 0.399 | 0.387 | 29.8% / 33.9% |
| wikipedia/en@256 | 24,720 | 80.2% / 82.6% | 0.899 | 0.890 | 33,462 | 16.5% / 18.9% | 0.447 | 0.408 | 35.1% / 40.6% |
| stackexchange/en@256 | 35,002 | 92.5% / 93.3% | 0.855 | 0.844 | 35,319 | 15.3% / 17.3% | 0.441 | 0.455 | 31.6% / 34.7% |
| wikipedia/en@1024 | 35,778 | 86.0% / 87.3% | 0.908 | 0.899 | 104,656 | 20.0% / 22.2% | 0.482 | 0.440 | 34.4% / 39.4% |
| gutenberg/en@1024 | 29,481 | 84.7% / 84.8% | 0.944 | 0.938 | 94,348 | 22.5% / 22.9% | 0.766 | 0.783 | 35.4% / 36.8% |
| wikipedia/de@256 | 8,387 | 55.9% / 63.3% | 0.579 | 0.567 | 11,585 | 6.0% / 7.3% | 0.084 | 0.068 | 22.9% / 26.7% |
| wikipedia/ru@256 | 2,392 | 19.2% / 23.6% | 0.415 | 0.410 | 2,081 | 1.1% / 2.5% | 0.028 | -0.002 | 10.3% / 13.8% |
| wikipedia/ar@256 | 2,319 | 14.2% / 19.2% | 0.171 | 0.160 | 1,863 | 1.0% / 2.7% | 0.038 | 0.006 | 7.1% / 11.4% |
| wikipedia/zh@256 | 7,174 | 51.6% / 31.4% | 0.066 | 0.087 | 3,596 | 0.8% / 1.2% | 0.006 | 0.008 | 9.1% / 11.7% |
| wikipedia/ja@256 | 3,216 | 25.9% / 29.1% | 0.065 | 0.096 | 2,458 | 0.7% / 1.2% | 0.005 | -0.013 | 6.9% / 14.0% |
