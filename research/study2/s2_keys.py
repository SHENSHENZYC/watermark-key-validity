"""Study 2 key namespace (v1). tools/key_policy.py is pinned by Study 1's lock and is NOT edited; this module imports its
constants and adds the Study 2 production range.

- Study 2 production keys: 22,000-22,999 (a fresh range: never used by any study, pilot or validation; disjoint from Study 1's
  production range 20,000-21,999, from the reserved confirmatory range 30,000-30,999 and from the validation namespace
  1,000,000+). The corpora audit's "development keys 0-999" are not reused because keys 0-499 were consumed by the Study 1 v0.1
  validation pilot on synthetic laws (retained on disk) and because a token id's colour at h = 0 under a key is the same integer
  function in every study (uniforms(key, tuple id)); a fresh range removes any overlap by construction.
- Validation and pilot keys: 1,000,000 and above (tools/key_policy.VALIDATION_MIN), never used in a study cell.
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from key_policy import check_keys as _check_v1, KeyPolicyError, RESERVED_CONFIRMATORY, STUDY1_PRODUCTION, VALIDATION_MIN  # noqa: F401

STUDY2_PRODUCTION = (22000, 22999)


def check_keys(keys, purpose):
    """Raise KeyPolicyError unless every key is admissible for the purpose ('study2' or 'validation')."""
    keys = [int(k) for k in keys]
    if not keys:
        raise KeyPolicyError("empty key list")
    lo, hi = min(keys), max(keys)
    if lo <= RESERVED_CONFIRMATORY[1] and hi >= RESERVED_CONFIRMATORY[0]:
        raise KeyPolicyError(f"keys {lo}-{hi} touch the reserved confirmatory range {RESERVED_CONFIRMATORY[0]}-{RESERVED_CONFIRMATORY[1]}")
    if purpose == "study2":
        if lo < STUDY2_PRODUCTION[0] or hi > STUDY2_PRODUCTION[1]:
            raise KeyPolicyError(f"study2 keys must lie in {STUDY2_PRODUCTION[0]}-{STUDY2_PRODUCTION[1]}; got {lo}-{hi}")
        if lo <= STUDY1_PRODUCTION[1] and hi >= STUDY1_PRODUCTION[0]:
            raise KeyPolicyError("study2 keys overlap Study 1's production range")
    elif purpose == "validation":
        return _check_v1(keys, "validation")
    else:
        raise KeyPolicyError(f"unknown purpose {purpose!r}")
    return True
