"""Study 4 key policy (v1; decisions D12-D14, 2026-10-16). tools/key_policy.py, research/study2/s2_keys.py and research/study3/s3_keys.py
(all pinned by earlier locks) are NOT edited; this module imports their constants.

Study 4 uses NO new key range. Its power side generates with a seeded uniform sample without replacement of K4 = 100 of Study 3's
1,000 evaluation keys (23,000-23,999), so that every power pairs with the same key's committed thresholds and stored null levels; its
model-null side scores all 1,000 evaluation keys (no generation depends on a key there). Fitting keys (24,000-24,999) never enter.
Validation and pilot generations use keys >= 1,000,000 only. The reserved confirmatory range 30,000-30,999 is never touched.
"""
import pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "research/study3"))
from key_policy import KeyPolicyError, RESERVED_CONFIRMATORY, VALIDATION_MIN  # noqa: F401
from s3_keys import STUDY3_EVAL, STUDY3_FIT  # noqa: F401

K4 = 100
SUBSET_SEED = 20261016          # fixed before any generation with an evaluation key (the grid records the resulting list)


def power_keys(seed=SUBSET_SEED, k4=K4):
    """The sorted K4 evaluation keys of the power side: a PCG64 uniform sample without replacement of the 1,000 Study 3 evaluation keys."""
    rng = np.random.default_rng(int(seed)); n = STUDY3_EVAL[1] - STUDY3_EVAL[0] + 1
    idx = np.sort(rng.choice(n, size=int(k4), replace=False))
    return [int(STUDY3_EVAL[0] + i) for i in idx]


def check_keys(keys, purpose):
    """Raise KeyPolicyError unless every key is admissible for the purpose ('study4_power', 'study4_null' or 'validation')."""
    keys = [int(k) for k in keys]
    if not keys:
        raise KeyPolicyError("empty key list")
    lo, hi = min(keys), max(keys)
    if lo <= RESERVED_CONFIRMATORY[1] and hi >= RESERVED_CONFIRMATORY[0]:
        raise KeyPolicyError(f"keys {lo}-{hi} touch the reserved confirmatory range")
    if lo <= STUDY3_FIT[1] and hi >= STUDY3_FIT[0]:
        raise KeyPolicyError(f"keys {lo}-{hi} touch Study 3's fitting range {STUDY3_FIT}; fitting keys never enter Study 4")
    if purpose == "study4_power":
        if set(keys) != set(power_keys()):
            raise KeyPolicyError("the power keys must be exactly the seeded K4 subset of Study 3's evaluation keys")
    elif purpose == "study4_null":
        if lo < STUDY3_EVAL[0] or hi > STUDY3_EVAL[1]:
            raise KeyPolicyError(f"null-block keys must lie in {STUDY3_EVAL}; got {lo}-{hi}")
    elif purpose == "validation":
        if lo < VALIDATION_MIN:
            raise KeyPolicyError(f"validation keys must be >= {VALIDATION_MIN}; got {lo}-{hi}")
    else:
        raise KeyPolicyError(f"unknown purpose {purpose!r}")
    return True


if __name__ == "__main__":
    ks = power_keys(); print(len(ks), ks[:8], "...", ks[-3:]); check_keys(ks, "study4_power"); print("policy ok")
