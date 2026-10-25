from __future__ import annotations

import re


MAX_AUTHORITY_ID_LENGTH = 128
HARMONIZATION_AUTHORITY_PREFIX = "harm-auth-"
MAX_HARMONIZATION_CREATION_ID_LENGTH = (
    MAX_AUTHORITY_ID_LENGTH - len(HARMONIZATION_AUTHORITY_PREFIX)
)
_AUTHORITY_ID_RE = re.compile(
    rf"[A-Za-z0-9][A-Za-z0-9_-]{{0,{MAX_AUTHORITY_ID_LENGTH - 1}}}",
    re.ASCII,
)


class AuthorityIdError(ValueError):
    """Raised when external authority cannot safely identify one resource."""


def validate_authority_id(value: object) -> str:
    if not isinstance(value, str) or _AUTHORITY_ID_RE.fullmatch(value) is None:
        raise AuthorityIdError("invalid authority id")
    return value


def validate_scan_job_id_for_creation(value: object) -> str:
    job_id = validate_authority_id(value)
    if not job_id.startswith(("scan-", HARMONIZATION_AUTHORITY_PREFIX)):
        raise AuthorityIdError("invalid scan authority job id")
    return job_id


def validate_harmonization_job_id_for_creation(value: object) -> str:
    job_id = validate_authority_id(value)
    if (
        not job_id.startswith("harm_")
        or len(job_id) > MAX_HARMONIZATION_CREATION_ID_LENGTH
    ):
        raise AuthorityIdError("invalid harmonization job id")
    return job_id
