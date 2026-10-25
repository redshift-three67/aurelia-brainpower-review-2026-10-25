"""Explicit synthetic grants; no real session or database authorization."""
from .validation import ContractError, _ID


class TestAuthority:
    def __init__(self, grants):
        self._grants = set()
        for grant in grants:
            if (type(grant) not in (tuple, list) or len(grant) != 5
                    or any(type(value) is not str or not _ID.fullmatch(value) for value in grant)):
                raise ContractError('invalid_request')
            self._grants.add(tuple(grant))

    def allows(self, tenant, actor, audience, operation, revision):
        values = (tenant, actor, audience, operation, revision)
        if any(type(value) is not str for value in values):
            return False
        return values in self._grants

    def revoke(self, tenant, actor, audience, operation, revision):
        values = (tenant, actor, audience, operation, revision)
        if any(type(value) is not str for value in values):
            raise ContractError('invalid_request')
        self._grants.discard(values)
