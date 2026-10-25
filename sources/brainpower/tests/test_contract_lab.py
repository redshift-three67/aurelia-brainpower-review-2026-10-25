"""Offline synthetic contract tests; no product/auth/transport claims."""
import copy
import json
import unittest
from unittest.mock import patch

from contract_lab.validation import ContractError, parse_object, validate_context, validate_manifest
from contract_lab.authority import TestAuthority
from contract_lab.lifecycle import TrialSlot, authorize_analysis
from contract_lab.errors import adapter_error


def approved():
    return dict(profile_revision='aurelia-rest/1.0-draft.1', kernel_id='synthetic',
                release_id='release-1', schema_id='schema-1', audience='synthetic',
                operation='analysis', context_version='synthetic-context-v1')


def context(**updates):
    value = dict(context_version='synthetic-context-v1', request_id='request-1',
                 tenant_id='A', actor_id='alice', audience='synthetic', operation='analysis',
                 issued_at=100, expires_at=130, authorization_revision='rev-1',
                 profile_revision='aurelia-rest/1.0-draft.1', release_id='release-1')
    value.update(updates)
    return value


def manifest(**updates):
    value = dict(profile_revision='aurelia-rest/1.0-draft.1', abi_surface='rest',
                 abi_version='v1', kernel_id='synthetic', release_id='release-1',
                 schema_id='schema-1', operations=['analysis'], entry='never_import:sentinel')
    value.update(updates)
    return value


class ParserTests(unittest.TestCase):
    def test_byte_boundary(self):
        raw = '{"text":"ä"}'.encode('utf-8')
        self.assertEqual(parse_object(raw, len(raw)), {'text': 'ä'})
        self.assertEqual(parse_object(raw, len(raw) + 1), {'text': 'ä'})
        with self.assertRaises(ContractError) as caught:
            parse_object(raw, len(raw) - 1)
        self.assertEqual(caught.exception.code, 'payload_limit')

    def test_bad_json_variants(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}', b'{"x":NaN}',
                    b'{"x":Infinity}', b'{"x":-Infinity}', b'[]', b'null',
                    b'{"x":"\xff"}', b'{', b'{} {}', b'{"x":1e999}'):
            with self.subTest(raw=repr(raw)), self.assertRaises(ContractError) as caught:
                parse_object(raw, 1024)
            self.assertEqual(caught.exception.code, 'invalid_request')

    def test_invalid_arguments(self):
        for raw, limit in [('{}', 2), (b'{}', True), (b'{}', 0), (b'{}', -1)]:
            with self.subTest(limit=limit, raw=raw), self.assertRaises(ContractError):
                parse_object(raw, limit)

    def test_nested_valid_input(self):
        self.assertEqual(parse_object(b'{"a":[1,true,null,{"b":2}]}', 100),
                         {'a': [1, True, None, {'b': 2}]})

    def test_error_does_not_echo_payload(self):
        with self.assertRaises(ContractError) as caught:
            parse_object(b'{SECRET_MARKER', 100)
        self.assertNotIn('SECRET_MARKER', str(caught.exception))


class ManifestTests(unittest.TestCase):
    def test_valid_entry_is_metadata_only(self):
        data = manifest(entry='module_that_does_not_exist:function')
        before = copy.deepcopy(data)
        self.assertIsNone(validate_manifest(data, approved()))
        self.assertEqual(data, before)

    def test_each_missing_or_wrong_type_field(self):
        for key in manifest():
            for variant in ('missing', 'type'):
                data = manifest()
                if variant == 'missing':
                    del data[key]
                else:
                    data[key] = None
                with self.subTest(key=key, variant=variant), self.assertRaises(ContractError):
                    validate_manifest(data, approved())

    def test_drift_variants(self):
        for key, value in [('profile_revision', 'v999'), ('release_id', 'release-2'),
                           ('schema_id', 'schema-2'), ('kernel_id', 'other'),
                           ('abi_surface', 'python'), ('abi_version', 'v2'),
                           ('operations', ['analysis', 'promote']), ('operations', ['other'])]:
            with self.subTest(key=key, value=value), self.assertRaises(ContractError):
                validate_manifest(manifest(**{key: value}), approved())

    def test_extra_field_and_incomplete_approval(self):
        with self.assertRaises(ContractError):
            validate_manifest(manifest(url='https://other.invalid'), approved())
        with self.assertRaises(ContractError):
            validate_manifest(manifest(), {})


class ContextTests(unittest.TestCase):
    def test_time_boundaries(self):
        for now in (100, 129):
            self.assertIsNone(validate_context(context(), approved(), now))
        for now in (99, 130, 131, True, '100'):
            with self.subTest(now=now), self.assertRaises(ContractError):
                validate_context(context(), approved(), now)

    def test_invalid_durations_and_types(self):
        for fields in [dict(expires_at=131), dict(expires_at=100), dict(expires_at=99),
                       dict(issued_at=True), dict(expires_at=130.0)]:
            with self.subTest(fields=fields), self.assertRaises(ContractError):
                validate_context(context(**fields), approved(), 100)

    def test_missing_extra_and_bad_ids(self):
        for key in context():
            data = context()
            del data[key]
            with self.subTest(missing=key), self.assertRaises(ContractError):
                validate_context(data, approved(), 100)
        for field in ('request_id', 'tenant_id', 'actor_id', 'authorization_revision'):
            for bad in ('', 'a b', 'ä', '../x', 'x' * 129, None, True):
                with self.subTest(field=field, bad=bad), self.assertRaises(ContractError):
                    validate_context(context(**{field: bad}), approved(), 100)
        with self.assertRaises(ContractError):
            validate_context(context(extra='x'), approved(), 100)

    def test_context_binding(self):
        for field in ('context_version', 'audience', 'operation', 'profile_revision', 'release_id'):
            with self.subTest(field=field), self.assertRaises(ContractError):
                validate_context(context(**{field: 'other'}), approved(), 100)

    def test_incomplete_approval(self):
        with self.assertRaises(ContractError):
            validate_context(context(), {}, 100)


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.grant = ('A', 'alice', 'synthetic', 'analysis', 'rev-1')
        self.authority = TestAuthority([self.grant])

    def test_explicit_grant_and_revocation(self):
        self.assertIsNone(authorize_analysis(context(), approved(), self.authority, 100))
        self.authority.revoke(*self.grant)
        with self.assertRaises(ContractError) as caught:
            authorize_analysis(context(), approved(), self.authority, 100)
        self.assertEqual(caught.exception.code, 'forbidden')

    def test_tenant_actor_revision_separation(self):
        for key, value in [('tenant_id', 'B'), ('actor_id', 'bob'), ('authorization_revision', 'rev-2')]:
            with self.subTest(key=key), self.assertRaises(ContractError):
                authorize_analysis(context(**{key: value}), approved(), self.authority, 100)
        self.assertTrue(self.authority.allows(*self.grant))

    def test_defensive_grant_copy(self):
        grants = [list(self.grant)]
        authority = TestAuthority(grants)
        grants[0][0] = 'B'
        grants.clear()
        self.assertTrue(authority.allows(*self.grant))
        self.assertFalse(authority.allows('B', *self.grant[1:]))

    def test_malformed_grants(self):
        for grant in [('A',), ('', 'alice', 'synthetic', 'analysis', 'rev-1'),
                      (True, 'alice', 'synthetic', 'analysis', 'rev-1')]:
            with self.subTest(grant=grant), self.assertRaises(ContractError):
                TestAuthority([grant])

    def test_exact_revocation_does_not_remove_other_tenant(self):
        other = ('B', 'bob', 'synthetic', 'analysis', 'rev-1')
        authority = TestAuthority([self.grant, other])
        authority.revoke(*self.grant)
        self.assertTrue(authority.allows(*other))

    def test_invalid_context_never_queries_authority(self):
        with patch.object(self.authority, 'allows') as lookup:
            with self.assertRaises(ContractError):
                authorize_analysis(context(), approved(), self.authority, 130)
            lookup.assert_not_called()


class LifecycleTests(unittest.TestCase):
    def test_normal_terminal_outcomes(self):
        for outcome in ('succeeded', 'failed', 'aborted'):
            slot = TrialSlot()
            slot.reserve('request-1')
            slot.start()
            slot.finish(outcome)
            self.assertEqual(slot.state, 'idle')
            self.assertEqual(slot.outcome, outcome)
            slot.reserve('request-2')
            self.assertIsNone(slot.outcome)

    def test_abort_holds_slot_until_completion(self):
        slot = TrialSlot()
        slot.reserve('request-1')
        slot.start()
        slot.request_abort()
        with self.assertRaises(ContractError):
            slot.reserve('request-2')
        with self.assertRaises(ContractError):
            slot.finish('succeeded')
        self.assertEqual(slot.state, 'abort_requested')
        slot.finish('aborted')
        self.assertEqual(slot.state, 'idle')

    def test_unknown_stays_blocked(self):
        for initial in ('reserved', 'running', 'abort_requested'):
            slot = TrialSlot()
            slot.reserve('request-1')
            if initial != 'reserved':
                slot.start()
            if initial == 'abort_requested':
                slot.request_abort()
            slot.lose_observation()
            for action in (lambda: slot.reserve('request-2'), slot.start,
                           slot.request_abort, lambda: slot.finish('aborted')):
                with self.subTest(initial=initial), self.assertRaises(ContractError):
                    action()
                self.assertEqual(slot.state, 'unknown')
                self.assertEqual(slot.request_id, 'request-1')

    def test_illegal_transition_preserves_state(self):
        slot = TrialSlot()
        for action in (slot.start, slot.request_abort, lambda: slot.finish('succeeded')):
            with self.assertRaises(ContractError):
                action()
            self.assertEqual(slot.state, 'idle')
        slot.reserve('request-1')
        for action in (slot.request_abort, lambda: slot.finish('failed'),
                       lambda: slot.reserve('request-2')):
            with self.assertRaises(ContractError):
                action()
            self.assertEqual(slot.state, 'reserved')

    def test_bad_reservation_id(self):
        for value in ('', None, True, '../x', 'x' * 129):
            slot = TrialSlot()
            with self.subTest(value=value), self.assertRaises(ContractError):
                slot.reserve(value)
            self.assertEqual(slot.state, 'idle')

    def test_unknown_outcome_preserves_running(self):
        slot = TrialSlot()
        slot.reserve('request-1')
        slot.start()
        with self.assertRaises(ContractError):
            slot.finish('SECRET_MARKER')
        self.assertEqual(slot.state, 'running')


class ErrorTests(unittest.TestCase):
    def test_exact_mapping_and_unknown_error(self):
        mapping = {'invalid_request': 400, 'forbidden': 403, 'contract_conflict': 409,
                   'state_conflict': 409, 'payload_limit': 413, 'busy': 503,
                   'recovery_required': 503}
        for code, status in mapping.items():
            with self.subTest(code=code):
                self.assertEqual(adapter_error(code), {'status': status, 'code': code})
        for unknown in ('SECRET_MARKER', None, [], True):
            self.assertEqual(adapter_error(unknown), {'status': 500, 'code': 'internal_error'})


if __name__ == '__main__':
    unittest.main()
