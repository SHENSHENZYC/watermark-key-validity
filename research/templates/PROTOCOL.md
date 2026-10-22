# <Study name> — protocol v<X.Y>

Date: <YYYY-MM-DD>. **Status: DRAFT (not locked)** → becomes "LOCKED before outcomes (`outputs/<name>_v<X.Y>/PRE_RUN_LOCK.json`)".
Script: `<path>`. Supersedes: <none / earlier version, kept as the record>.

1. **Question and type:** <new method | adequacy check | applied evaluation>
2. **Information timing:** <what is known when>
3. **Target, sign, units:** <…>
4. **Data, split and holdout:** <sources and hashes; the holdout is untouched and asserted in code>
5. **Competitors and baselines:** <with frozen settings>
6. **Primary metric and contrast:** <sign convention>
7. **Secondary diagnostics (descriptive):** <…>
8. **Uncertainty:** <method preserving dependence; seed, blocks, replicates, fixed now>
9. **Pre-registered rules and materiality thresholds:** <pass, fail and marginal definitions; integrity checks>
10. **Stop and pivot rules, and what a null result means:** <…>
11. **Inputs validated before the lock (no outcomes):** <calibration, assignments, run structure>
12. **Nearest published work; what is not claimed:** <…>

Lock: write PRE_RUN_LOCK.json {protocol_sha256, script_sha256, input hashes, date, "before outcomes", approved_by}. Commit and push it **before** running.
