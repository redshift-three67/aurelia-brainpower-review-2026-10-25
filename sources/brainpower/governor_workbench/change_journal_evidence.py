"""Integrity of archived S3 evidence, not operator authorization or test execution."""
import copy
import json

from .execution_workspace import _sha
from .plans import _hash, _id, _path
from .technical_completion import binding as technical_binding


def baseline(value):
    fields={'candidate_id','selection_id','step_ids','step_hashes','step_scopes','root',
            'root_identity','scope_hash','sources','adapter_hash'}
    if not isinstance(value,dict) or set(value)!=fields:
        raise ValueError('Vollständige Journalbindung erforderlich.')
    value=copy.deepcopy(value)
    for k in ('candidate_id','selection_id'):_id(value[k])
    for k in ('scope_hash','adapter_hash'):_hash(value[k])
    ids=value['step_ids']
    if not isinstance(ids,list) or len(ids)!=2 or any(not isinstance(k,str) for k in ids) or len(set(ids))!=2:
        raise ValueError('Genau zwei Schritte erforderlich.')
    for key in ids:_id(key)
    if (not isinstance(value['step_hashes'],dict) or set(value['step_hashes'])!=set(ids)
            or not isinstance(value['step_scopes'],dict) or set(value['step_scopes'])!=set(ids)):
        raise ValueError('Schrittbindung unvollständig.')
    paths=[];normalized=[]
    for key in ids:
        _hash(value['step_hashes'][key]);scope=value['step_scopes'][key]
        if not isinstance(scope,list) or not 1<=len(scope)<=20:
            raise ValueError('Begrenzte Schreibbereiche erforderlich.')
        for path in scope:
            _path(path);norm=path.casefold()
            if any(norm==p or norm.startswith(p+'/') or p.startswith(norm+'/') for p in normalized):
                raise ValueError('Schreibbereiche müssen disjunkt und eindeutig sein.')
            normalized.append(norm);paths.append(path)
    if not isinstance(value['sources'],dict) or set(value['sources'])!=set(paths):
        raise ValueError('Vollständiger expliziter Ausgangsstand erforderlich.')
    for sha in value['sources'].values():
        if sha is not None:_hash(sha)
    root=value['root_identity']
    if (not isinstance(value['root'],str) or not isinstance(root,dict) or set(root)!={'device','inode'}
            or any(type(v) is not int for v in root.values())):
        raise ValueError('Kanonische Wurzelidentität erforderlich.')
    return value


def transition(binding,files,scope,ordinal,evidence):
    """Validate snapshots already obtained by a trusted controller; never synthesize proof."""
    if not isinstance(evidence,dict) or set(evidence)!={'transaction','manifest','technical_receipt'}:
        raise ValueError('Versiegelte Übernahmebelege erforderlich.')
    if len(json.dumps(evidence,ensure_ascii=False).encode('utf-8'))>8*1024*1024:
        raise ValueError('Journalbeleg überschreitet Größenlimit.')
    if ordinal not in (0,1):raise ValueError('Nur zwei Übergänge zulässig.')
    key=binding['step_ids'][ordinal]
    tx=evidence['transaction'];manifest=evidence['manifest'];receipt=evidence['technical_receipt']
    proof=technical_binding(receipt['binding'])
    seal=_sha(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8'))
    if (tx['status']!='completed' or receipt['status']!='recorded'
            or receipt['kind']!='isolated_change_transfer_completion'
            or receipt['scope_observation_acknowledged'] is not True
            or receipt['execution_enabled'] is not False or receipt['product_gate_approved'] is not False
            or receipt['target_tests_executed'] is not False):
        raise ValueError('Abgeschlossene Übernahme und getrennter technischer Beleg erforderlich.')
    _id(receipt['id']);_id(tx['id'])
    expected=dict(transaction_id=tx['id'],stage_id=tx['stage_id'],manifest_hash=seal,
        candidate_id=binding['candidate_id'],selection_id=binding['selection_id'],step_id=key,
        step_hash=binding['step_hashes'][key],plan_scope_hash=scope)
    if (any(proof[k]!=v for k,v in expected.items()) or receipt['transaction_id']!=tx['id']
            or tx['manifest_hash']!=seal or tx['scope_hash']!=scope or manifest['id']!=tx['stage_id']
            or proof['observed_scope_hash']==scope):
        raise ValueError('Transaktion, Abschluss oder Quellenübergang falsch gebunden.')
    for item in (tx,manifest):
        if item['original_root']!=binding['root'] or item['root_identity']!=binding['root_identity']:
            raise ValueError('Belegwurzel stimmt nicht überein.')
    records=manifest['files'];paths=binding['step_scopes'][key]
    if not isinstance(records,list) or len(records)!=len(paths) or {r['path'] for r in records}!=set(paths):
        raise ValueError('Manifestumfang stimmt nicht überein.')
    after=dict(files);changed={}
    for record in records:
        path=record['path'];old=record['original_sha256'];new=record['staged_sha256'];_hash(new)
        if old!=files[path]:raise ValueError('Historischer Dateivorgänger stimmt nicht überein.')
        after[path]=new
        if old!=new:changed[path]=(old,new)
    if (not changed or not isinstance(tx['files'],list) or len(tx['files'])!=len(changed)
            or {r['path']:(r['before'],r['after']) for r in tx['files']}!=changed
            or any(r['written'] is not True or r['intent'] is not True for r in tx['files'])):
        raise ValueError('Abgeschlossene Transaktionsdateien stimmen nicht überein.')
    return after,proof['observed_scope_hash']


def rollback_transaction(original,restored):
    if not isinstance(restored,dict) or restored.get('status')!='rolled_back':
        raise ValueError('Abgeschlossene Rücknahme erforderlich.')
    for field in ('id','stage_id','manifest_hash','scope_hash','original_root','root_identity','files'):
        if restored.get(field)!=original[field]:
            raise ValueError('Rücknahme gehört nicht zur ursprünglichen Transaktion.')
