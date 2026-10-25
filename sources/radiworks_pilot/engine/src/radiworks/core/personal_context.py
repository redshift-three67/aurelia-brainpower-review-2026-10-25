"""Versioned personal context: metadata only, never original analysis weighting."""
from __future__ import annotations
import copy
import json
import re
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any
from ..persistence import document_digest
from ..scope import ScopeContext

FIELDS = {'firstName': 160, 'lastName': 160, 'birthDate': 10, 'place': 240, 'image': None}
HEX32 = re.compile(r'[0-9a-f]{32}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')

class ContextError(ValueError):
    pass

def normalize_personal(value: object, *, birth_date_limit: int | None = None) -> dict[str, Any]:
    if value is None:
        value = {}
    if type(value) is not dict or set(value) - (set(FIELDS) | {'placeKind'}):
        raise ContextError('Persönlicher Kontext enthält ungültige Felder.')
    normalized = dict.fromkeys(FIELDS)
    for name, limit in FIELDS.items():
        field = value.get(name)
        if field is None:
            continue
        if name == 'image':
            if (type(field) is not dict or set(field) != {'sha256', 'mediaType', 'byteLength'}
                or type(field['sha256']) is not str or not HEX64.fullmatch(field['sha256'])
                or field['mediaType'] not in ('image/png', 'image/jpeg', 'image/webp')
                or type(field['byteLength']) is not int or not 1 <= field['byteLength'] <= 5_000_000):
                raise ContextError('Bildreferenz muss SHA-256, erlaubten Bildtyp und begrenzte Größe enthalten.')
            normalized[name] = copy.deepcopy(field)
            continue
        if type(field) is not str or len(field) > limit:
            raise ContextError(f'{name}: Text ist ungültig oder zu lang.')
        if any(unicodedata.category(char) in ('Cc', 'Cs', 'Cf') for char in field):
            raise ContextError(f'{name}: Steuerzeichen sind nicht erlaubt.')
        text = unicodedata.normalize('NFC', field).strip()
        if len(text) > limit:
            raise ContextError(f'{name}: normalisierter Text ist zu lang.')
        if name == 'birthDate' and text:
            try:
                parsed = date.fromisoformat(text)
            except ValueError as exc:
                raise ContextError('Geburtsdatum muss ein gültiges Datum YYYY-MM-DD sein.') from exc
            if parsed.isoformat() != text or parsed.toordinal() > (birth_date_limit if birth_date_limit is not None else date.today().toordinal()):
                raise ContextError('Geburtsdatum ist nicht gültig.')
        normalized[name] = text or None
    # Omitted kind preserves the historical snapshot shape and digest.
    if 'placeKind' in value:
        kind = value['placeKind']
        if type(kind) is not str or kind not in ('residence', 'birth'):
            raise ContextError('Ortstyp muss Wohn-/Aufenthaltsort oder Geburtsort sein.')
        normalized['placeKind'] = kind
    return normalized

def context_title(case: dict) -> str:
    """Build a display-only case label from normalized personal context and focus."""
    personal = normalize_personal(case.get('personalContext'))
    parts = [personal.get('firstName'), personal.get('lastName')]
    birth_date = personal.get('birthDate')
    if birth_date:
        parts.append(date.fromisoformat(birth_date).strftime('%d%m%Y'))
    if personal.get('placeKind') in ('residence', 'birth') and personal.get('place'):
        parts.append(personal['place'])
    prefix = ' '.join(part for part in parts if isinstance(part, str) and part)
    focus = case.get('focus')
    if focus is not None:
        if type(focus) is not str:
            raise ContextError('Fokus muss Text sein.')
        focus = unicodedata.normalize('NFC', focus).strip()
        if any(unicodedata.category(char) in ('Cc', 'Cs', 'Cf') for char in focus):
            raise ContextError('Fokus enthält unzulässige Steuerzeichen.')
    else:
        focus = ''
    title = f'{prefix} - {focus}' if prefix and focus else prefix or focus
    if title:
        return title
    case_id = case.get('caseId')
    if type(case_id) is not str or not HEX32.fullmatch(case_id):
        raise ContextError('Eine Fall-ID wird für den neutralen Titel benötigt.')
    return f'Fall {case_id[:8]}'

def context_values(case: dict) -> dict:
    return {
        'caseLabel': case.get('name'),
        'description': case.get('description'),
        'focus': case.get('focus'),
        'personal': normalize_personal(case.get('personalContext')),
    }

def prepare_identity(case: dict, stored: dict | None = None) -> None:
    """Only an explicit planned write assigns identity to a legacy case."""
    if stored is not None and 'personalContext' not in case:
        case['personalContext'] = copy.deepcopy(stored.get('personalContext'))
        if 'personalContextOriginal' in stored:
            case['personalContextOriginal'] = copy.deepcopy(stored['personalContextOriginal'])
    if stored is not None and type(case.get('personalContext')) is dict:
        incoming_personal = case['personalContext']
        old_kind = (stored.get('personalContext') or {}).get('placeKind')
        if incoming_personal.get('placeKind') != old_kind and 'place' not in incoming_personal:
            raise ContextError('Beim Wechsel des Ortstyps den Ort ausdrücklich neu angeben oder leeren.')
    previous_id = (stored or {}).get('caseId')
    incoming_id = case.get('caseId')
    if previous_id is not None and incoming_id is not None and previous_id != incoming_id:
        raise ContextError('Die feste Fall-ID darf nicht geändert werden.')
    case_id = previous_id or incoming_id or uuid.uuid4().hex
    if type(case_id) is not str or not HEX32.fullmatch(case_id):
        raise ContextError('Ungültige feste Fall-ID.')
    raw = copy.deepcopy(case.get('personalContext') or {})
    normalized = normalize_personal(case.get('personalContext'))
    retained_original = case.get('personalContextOriginal')
    if retained_original is not None and normalize_personal(retained_original) == normalized:
        raw = copy.deepcopy(retained_original)
    old_version = (stored or {}).get('contextVersion', 0)
    if type(old_version) is not int or old_version < 0:
        raise ContextError('Ungültige Kontextversion im gespeicherten Fall.')
    changed = stored is not None and (
        context_values(case) != context_values(stored)
        or raw != stored.get('personalContextOriginal', {})
    )
    case['caseId'] = case_id
    case['personalContext'] = normalized
    case['personalContextOriginal'] = raw
    case['contextVersion'] = max(1, old_version + int(changed))

def _check_scope(scope: object) -> None:
    if type(scope) is not dict or set(scope) != {'tenant_id', 'client_id', 'job_id'}:
        raise ContextError('Kontext-Scope ist ungültig.')
    if any(type(value) is not str or not value for value in scope.values()):
        raise ContextError('Kontext-Scope ist unvollständig.')

@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    _serialized: str

    @classmethod
    def capture(cls, case: dict, scope: ScopeContext | None) -> 'ContextSnapshot':
        if 'caseId' not in case or 'contextVersion' not in case:
            raise ContextError('Fallidentität muss vor dem Snapshot geplant werden.')
        scope_data = scope.to_dict() if scope is not None else None
        context = context_values(case)
        payload = {
            'schemaVersion': 1, 'snapshotId': uuid.uuid4().hex,
            'caseId': case['caseId'], 'contextVersion': case['contextVersion'],
            'scope': scope_data, 'capturedAt': datetime.now(timezone.utc).isoformat(),
            'context': context, 'originalPersonal': copy.deepcopy(case['personalContextOriginal']),
        }
        payload['digest'] = document_digest(payload)
        return cls.from_payload(payload)

    @classmethod
    def from_payload(cls, payload: object) -> 'ContextSnapshot':
        required = {'schemaVersion','snapshotId','caseId','contextVersion','scope','capturedAt','context','originalPersonal','digest'}
        if type(payload) is not dict or set(payload) != required:
            raise ContextError('Kontext-Snapshot hat ein ungültiges Schema.')
        if type(payload['schemaVersion']) is not int or payload['schemaVersion'] != 1:
            raise ContextError('Kontext-Snapshot-Version ist ungültig.')
        for name in ('snapshotId', 'caseId'):
            if type(payload[name]) is not str or not HEX32.fullmatch(payload[name]):
                raise ContextError('Kontext-Snapshot-ID ist ungültig.')
        if type(payload['contextVersion']) is not int or payload['contextVersion'] < 1:
            raise ContextError('Kontext-Snapshot-Revision ist ungültig.')
        if payload['scope'] is not None:
            _check_scope(payload['scope'])
        context = payload['context']
        if type(context) is not dict or set(context) != {'caseLabel','description','focus','personal'}:
            raise ContextError('Kontext-Snapshot-Inhalt ist ungültig.')
        try:
            timestamp = datetime.fromisoformat(payload['capturedAt'])
            if timestamp.tzinfo is None:
                raise ValueError()
            # Frozen UTC date + one calendar day tolerates the original local timezone.
            birth_limit = timestamp.astimezone(timezone.utc).date().toordinal() + 1
        except (TypeError, ValueError, OverflowError) as exc:
            raise ContextError('Kontext-Snapshot-Zeitpunkt ist ungültig.') from exc
        if normalize_personal(context['personal'], birth_date_limit=birth_limit) != context['personal']:
            raise ContextError('Kontext-Snapshot ist nicht normalisiert.')
        if normalize_personal(payload['originalPersonal'], birth_date_limit=birth_limit) != context['personal']:
            raise ContextError('Kontext-Snapshot-Original passt nicht zum Inhalt.')
        clean = {key: value for key, value in payload.items() if key != 'digest'}
        if type(payload['digest']) is not str or payload['digest'] != document_digest(clean):
            raise ContextError('Kontext-Snapshot-Prüfsumme stimmt nicht.')
        return cls(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')))

    def payload(self) -> dict:
        return json.loads(self._serialized)

    def reference(self, session_id: str, draft_id: str) -> 'ContextReference':
        snapshot = self.payload()
        return ContextReference.from_payload({
            **{key: snapshot[key] for key in ('schemaVersion','snapshotId','caseId','contextVersion','scope','digest')},
            'sessionId': session_id, 'draftId': draft_id,
        })

@dataclass(frozen=True, slots=True)
class ContextReference:
    _serialized: str

    @classmethod
    def from_payload(cls, payload: object) -> 'ContextReference':
        keys = {'schemaVersion','snapshotId','caseId','contextVersion','scope','digest','sessionId','draftId'}
        if type(payload) is not dict or set(payload) != keys:
            raise ContextError('Kontextreferenz hat ein ungültiges Schema.')
        if type(payload['schemaVersion']) is not int or payload['schemaVersion'] != 1:
            raise ContextError('Kontextreferenz-Version ist ungültig.')
        for key in ('snapshotId','caseId','sessionId'):
            if type(payload[key]) is not str or not HEX32.fullmatch(payload[key]):
                raise ContextError('Kontextreferenz-ID ist ungültig.')
        if type(payload['contextVersion']) is not int or payload['contextVersion'] < 1:
            raise ContextError('Kontextreferenz-Revision ist ungültig.')
        if type(payload['digest']) is not str or not HEX64.fullmatch(payload['digest']):
            raise ContextError('Kontextreferenz-Prüfsumme ist ungültig.')
        if payload['scope'] is not None:
            _check_scope(payload['scope'])
        try:
            if str(uuid.UUID(payload['draftId'])) != payload['draftId']:
                raise ValueError()
        except (TypeError, AttributeError, ValueError) as exc:
            raise ContextError('Kontextreferenz-Draft-ID ist ungültig.') from exc
        return cls(json.dumps(payload, sort_keys=True, separators=(',', ':')))

    def payload(self) -> dict:
        return json.loads(self._serialized)

