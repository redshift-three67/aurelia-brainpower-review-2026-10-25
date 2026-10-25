"""Synthetic offline contract only; not a general schema or trust validator."""
import json
import math
import re


class ContractError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _reject(code='invalid_request'):
    raise ContractError(code)


def parse_object(raw: bytes, limit: int) -> dict:
    if type(raw) is not bytes or type(limit) is not int or limit <= 0:
        _reject()
    if len(raw) > limit:
        _reject('payload_limit')

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _reject()
            result[key] = value
        return result

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            _reject()
        return result

    try:
        result = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                            parse_constant=lambda value: _reject(), parse_float=finite_float)
    except (ValueError, UnicodeError, RecursionError):
        raise ContractError('invalid_request') from None
    if type(result) is not dict:
        _reject()
    return result


_MANIFEST = frozenset(('profile_revision', 'abi_surface', 'abi_version', 'kernel_id',
                       'release_id', 'schema_id', 'operations', 'entry'))
_CONTEXT = frozenset(('context_version', 'request_id', 'tenant_id', 'actor_id', 'audience',
                      'operation', 'issued_at', 'expires_at', 'authorization_revision',
                      'profile_revision', 'release_id'))
_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', re.ASCII)


def _bound(data, approved, fields):
    if type(approved) is not dict:
        _reject('contract_conflict')
    for key in fields:
        expected = approved.get(key)
        if type(expected) is not str or not expected or data[key] != expected:
            _reject('contract_conflict')


def validate_manifest(manifest: dict, approved: dict) -> None:
    if type(manifest) is not dict or manifest.keys() != _MANIFEST:
        _reject()
    for key in _MANIFEST - {'operations'}:
        if type(manifest[key]) is not str or not manifest[key]:
            _reject()
    if (manifest['abi_surface'] != 'rest' or manifest['abi_version'] != 'v1'
            or type(manifest['operations']) is not list or manifest['operations'] != ['analysis']):
        _reject('contract_conflict')
    _bound(manifest, approved, ('profile_revision', 'kernel_id', 'release_id', 'schema_id'))
    # entry is inert metadata in this synthetic REST profile; never resolve it.


def validate_context(context: dict, approved: dict, now: int) -> None:
    if type(context) is not dict or context.keys() != _CONTEXT or type(now) is not int:
        _reject()
    for key in _CONTEXT - {'issued_at', 'expires_at', 'profile_revision'}:
        if type(context[key]) is not str or not _ID.fullmatch(context[key]):
            _reject()
    if type(context['profile_revision']) is not str:
        _reject()
    issued, expiry = context['issued_at'], context['expires_at']
    if (type(issued) is not int or type(expiry) is not int
            or not 0 < expiry - issued <= 30 or not issued <= now < expiry):
        _reject()
    _bound(context, approved, ('context_version', 'audience', 'operation',
                              'profile_revision', 'release_id'))
