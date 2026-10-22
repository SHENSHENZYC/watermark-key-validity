Table — The per-key power cost of each remedy on Qwen2.5-1.5B's KGW generations (γ = 0.25, L = 256, α = 0.01, the diagonal calibration source): the key-mean power (pp) and the median per-key cost against the nominal threshold with its 5th–95th percentiles across keys [pp], over K₄ = 100 keys with n = 50 texts each. Every cost carries its conditions and none ranks the remedies; the multiplier arm is read under Proposition 1's prerequisite only; the per-key shares above α on both null laws are in Figure 6 and Table D7b; priority on pricing per-key calibration and on per-key operating points is Genhatharan 2026's and AutoMark's [@genhatharan2026nominal; @gloaguen2026automark].

| Arm | Rule | Method | news: power | cost, median [5%, 95%] | Wikipedia: power | cost, median [5%, 95%] | Stack Exchange: power | cost, median [5%, 95%] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h = 1, δ = 0.5 | raw | nominal | 66.2 | 0.0 [0.0, 0.0] | 53.4 | 0.0 [0.0, 0.0] | 56.3 | 0.0 [0.0, 0.0] |
| h = 1, δ = 0.5 | raw | multiplier 1/β | 33.2 | 34.0 [24.0, 42.0] | 25.6 | 28.0 [20.0, 38.1] | 28.1 | 28.0 [18.0, 38.0] |
| h = 1, δ = 0.5 | raw | empirical multiplier | 29.2 | 37.0 [28.0, 48.0] | 11.5 | 42.0 [28.0, 54.1] | 21.5 | 36.0 [22.0, 46.0] |
| h = 1, δ = 0.5 | raw | pooled | 46.6 | 20.0 [12.0, 28.0] | 25.6 | 28.0 [20.0, 38.1] | 31.9 | 24.0 [14.0, 32.1] |
| h = 1, δ = 0.5 | raw | conformal, N_cal 5,000 | 52.2 | 14.0 [-4.0, 34.0] | 32.0 | 20.0 [1.9, 44.0] | 30.4 | 26.0 [10.0, 42.0] |
| h = 1, δ = 0.5 | raw | tolerance, N_cal 5,000 | 48.4 | 18.0 [0.0, 36.2] | 28.1 | 24.0 [7.9, 48.1] | 26.7 | 30.0 [13.9, 46.1] |
| h = 1, δ = 0.5 | distinct | nominal | 60.9 | 0.0 [0.0, 0.0] | 47.0 | 0.0 [0.0, 0.0] | 48.2 | 0.0 [0.0, 0.0] |
| h = 1, δ = 0.5 | distinct | multiplier 1/β | 27.7 | 32.0 [24.0, 46.0] | 19.0 | 28.0 [19.9, 38.0] | 20.0 | 28.0 [18.0, 38.1] |
| h = 1, δ = 0.5 | distinct | empirical multiplier | 48.7 | 12.0 [6.0, 18.1] | 34.8 | 12.0 [6.0, 20.0] | 38.9 | 8.0 [2.0, 16.0] |
| h = 1, δ = 0.5 | distinct | pooled | 59.2 | 2.0 [0.0, 4.0] | 45.2 | 2.0 [0.0, 4.0] | 46.5 | 2.0 [0.0, 6.0] |
| h = 1, δ = 0.5 | distinct | conformal, N_cal 5,000 | 61.9 | 0.0 [-12.0, 10.1] | 47.9 | 0.0 [-12.0, 10.0] | 46.6 | 0.0 [-8.0, 12.0] |
| h = 1, δ = 0.5 | distinct | tolerance, N_cal 5,000 | 58.9 | 1.0 [-8.1, 14.0] | 44.7 | 2.0 [-8.1, 12.1] | 43.9 | 4.0 [-6.0, 16.2] |
| h = 1, δ = 2.0 | raw | nominal | 100.0 | 0.0 [0.0, 0.0] | 99.9 | 0.0 [0.0, 0.0] | 99.8 | 0.0 [0.0, 0.0] |
| h = 1, δ = 2.0 | raw | conformal, N_cal 5,000 | 100.0 | 0.0 [0.0, 0.0] | 99.8 | 0.0 [0.0, 0.1] | 99.7 | 0.0 [0.0, 2.0] |
| h = 2, δ = 0.5 | raw | nominal | 65.4 | 0.0 [0.0, 0.0] | 52.3 | 0.0 [0.0, 0.0] | 53.7 | 0.0 [0.0, 0.0] |
| h = 2, δ = 0.5 | raw | conformal, N_cal 5,000 | 54.5 | 10.0 [1.9, 24.0] | 37.7 | 14.0 [2.0, 32.0] | 37.4 | 16.0 [7.9, 26.0] |
