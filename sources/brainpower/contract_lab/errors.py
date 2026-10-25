"""Sanitized synthetic adapter classification, not an HTTP endpoint."""
_STATUS = {'invalid_request': 400, 'forbidden': 403, 'contract_conflict': 409,
           'state_conflict': 409, 'payload_limit': 413, 'busy': 503,
           'recovery_required': 503, 'authorization_unavailable': 503}


def adapter_error(code):
    if type(code) is not str or code not in _STATUS:
        return {'status': 500, 'code': 'internal_error'}
    return {'status': _STATUS[code], 'code': code}
