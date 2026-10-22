"""Study 3 key namespace (v1). tools/key_policy.py (pinned by Study 1's lock) and research/study2/s2_keys.py (pinned by Study 2's
lock) are NOT edited; this module imports their constants and adds the Study 3 production ranges (decision D11, 2026-10-13).

- Study 3 evaluation keys: 23,000-23,999 (the K keys whose per-key thresholds and realised levels are the outcomes).
- Study 3 fitting keys: 24,000-24,999 (used ONLY to fit the scheme-level thresholds, the empirical multiplier and the pooled
  threshold, on the calibration sets; never evaluated). Disjoint from the evaluation keys, so a scheme-level threshold is never
  fitted on the keys it is judged on.
- Both ranges are fresh: disjoint from Study 1's 20,000-21,999, Study 2's 22,000-22,999, the reserved confirmatory range
  30,000-30,999 and the validation namespace 1,000,000+ (validation and pilot keys, never used in a study cell).
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "research/study2"))
from key_policy import check_keys as _check_v1, KeyPolicyError, RESERVED_CONFIRMATORY, STUDY1_PRODUCTION, VALIDATION_MIN  # noqa: F401
from s2_keys import STUDY2_PRODUCTION  # noqa: F401

STUDY3_EVAL = (23000, 23999)
STUDY3_FIT = (24000, 24999)


def check_keys(keys, purpose):
    """Raise KeyPolicyError unless every key is admissible for the purpose ('study3_eval', 'study3_fit' or 'validation')."""
    keys = [int(k) for k in keys]
    if not keys:
        raise KeyPolicyError("empty key list")
    lo, hi = min(keys), max(keys)
    if lo <= RESERVED_CONFIRMATORY[1] and hi >= RESERVED_CONFIRMATORY[0]:
        raise KeyPolicyError(f"keys {lo}-{hi} touch the reserved confirmatory range {RESERVED_CONFIRMATORY[0]}-{RESERVED_CONFIRMATORY[1]}")
    for name, rng in (("Study 1", STUDY1_PRODUCTION), ("Study 2", STUDY2_PRODUCTION)):
        if lo <= rng[1] and hi >= rng[0]:
            raise KeyPolicyError(f"keys {lo}-{hi} overlap {name}'s production range {rng[0]}-{rng[1]}")
    if purpose in ("study3_eval", "study3_fit"):
        r = STUDY3_EVAL if purpose == "study3_eval" else STUDY3_FIT
        if lo < r[0] or hi > r[1]:
            raise KeyPolicyError(f"{purpose} keys must lie in {r[0]}-{r[1]}; got {lo}-{hi}")
    elif purpose == "validation":
        return _check_v1(keys, "validation")
    else:
        raise KeyPolicyError(f"unknown purpose {purpose!r}")
    return True
