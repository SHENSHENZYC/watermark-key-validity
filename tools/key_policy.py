"""Key (PRNG seed) namespaces for the whole project, in one place (R03 round 1, F8).

- Corpora development keys: 0-999 (corpora audit v0.3 §5).
- Reserved confirmatory keys: 30,000-30,999 (re-reserved on 2026-10-09 after a toy identity check had touched the former
  range 10,000-10,999; never used before the final lock of a confirmatory study).
- Study 1 production keys: 20,000-21,999 (core cells 20,000-20,499; illustration cells 20,000-21,999).
- Validation and pilot keys: 1,000,000 and above (never used in a study cell).
"""
RESERVED_CONFIRMATORY = (30000, 30999)
STUDY1_PRODUCTION = (20000, 21999)
VALIDATION_MIN = 1_000_000


class KeyPolicyError(ValueError):
    pass


def check_keys(keys, purpose):
    """Raise KeyPolicyError unless every key is admissible for the purpose ('study1' or 'validation')."""
    keys = [int(k) for k in keys]
    if not keys:
        raise KeyPolicyError("empty key list")
    lo, hi = min(keys), max(keys)
    if lo <= RESERVED_CONFIRMATORY[1] and hi >= RESERVED_CONFIRMATORY[0]:
        raise KeyPolicyError(f"keys {lo}-{hi} touch the reserved confirmatory range {RESERVED_CONFIRMATORY[0]}-{RESERVED_CONFIRMATORY[1]}")
    if purpose == "study1":
        if lo < STUDY1_PRODUCTION[0] or hi > STUDY1_PRODUCTION[1]:
            raise KeyPolicyError(f"study1 keys must lie in {STUDY1_PRODUCTION[0]}-{STUDY1_PRODUCTION[1]}; got {lo}-{hi}")
    elif purpose == "validation":
        if lo < VALIDATION_MIN:
            raise KeyPolicyError(f"validation keys must be >= {VALIDATION_MIN}; got {lo}-{hi}")
    else:
        raise KeyPolicyError(f"unknown purpose {purpose!r}")
    return True
