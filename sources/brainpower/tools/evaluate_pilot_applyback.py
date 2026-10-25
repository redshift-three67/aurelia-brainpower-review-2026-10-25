"""Replay no models: apply/rollback genuine synthetic verified staging evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor_workbench.config import load_config
from governor_workbench.evidence import now
from governor_workbench.server import Application
from governor_workbench.store import Store
from tools.evaluate_staging_pilot import write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--source', choices=['staging-pilot-live-2026-09-12-r3','staging-pilot-live-2026-09-12-v04'], default='staging-pilot-live-2026-09-12-r3')
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[1]
    source = workspace/'artifacts'/args.source
    repo = source/'synthetic-project'
    output = Path(args.output).resolve()
    if output.parent != workspace/'artifacts' or not output.name.startswith('pilot-applyback-') or output.exists():
        parser.error('Output must be a fresh direct artifacts/pilot-applyback-* child.')
    if source.resolve() != source or repo.resolve() != repo or not (repo/'.git').is_dir():
        parser.error('Only the exact existing synthetic staging-r3 root is allowed.')
    original_report = json.loads((source/'report.json').read_text(encoding='utf-8'))
    if not original_report.get('synthetic_only') or not original_report.get('originals_unchanged'):
        parser.error('Original synthetic staging evidence is not intact.')
    files = original_report['original_hashes']
    if set(files) != {'calc.py','tests/test_calc.py','project_memories/strategy_project_pilot.md'}:
        parser.error('Unexpected synthetic original files.')
    def originals():
        return {p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in files}
    if originals() != files:
        parser.error('Synthetic original bytes drifted; no writes permitted.')
    tests = [r['test_job'] for r in original_report['combinations'] if r.get('outcome') == 'verified']
    if len(tests) != 2:
        parser.error('Two genuine verified staging test jobs required.')
    output.mkdir()
    runtime = output/'runtime'; runtime.mkdir()
    journal_path = source/'runtime'/'journal.db'
    before_journal = hashlib.sha256(journal_path.read_bytes()).hexdigest()
    with sqlite3.connect(journal_path.as_uri()+'?mode=ro',uri=True) as existing:
        with sqlite3.connect(runtime/'journal.db') as destination:
            existing.backup(destination)
    destination.close(); existing.close()
    shutil.copytree(source/'runtime'/'execution-staging',runtime/'execution-staging')
    config_source = load_config(args.config)
    kept = ('router_url','router_api_key_env','codex_auth_path','hermes_path','orchestrator_transport',
            'orchestrator','supervisor','reasoning','model_timeout')
    config = {key:config_source[key] for key in kept}
    config.update(data_dir=str(runtime), projects=[dict(id='synthetic_pilot',name='Synthetic isolated pilot',
        path=str(repo),kind='existing',gate='Isolated staging only; no apply-back',status='Synthetic evaluation',
        next_step='Change staged calc value to two and test',depends_on=[])],
        governor_dir='',snapshot_dir='',vault_root='',live_views={},staging_pilot_roots=[str(repo)],
        legacy_review_egress_authorized=False,monitor_interval=3600,git_interval=60,
        auto_review_cooldown=900,auto_review_daily_limit=4,port=8787)
    write_json(output/'config.json',{**config,'version':1,'port':8789})
    copied = Store(runtime/'journal.db')
    copied.set_setting('monitor_enabled',False); copied.set_setting('auto_review',False)
    report = dict(started_at=now(),source_evaluation=str(source),synthetic_only=True,model_calls=0,
        original_journal_sha256=before_journal,original_hashes=files,combinations=[],
        authorization='Explicit synthetic diagnostic apply and rollback only; no real products.',
        limitations=['Uses genuine earlier staging evidence; does not rerun model review or tests.',
                    'Original evaluation journal is read-only; new jobs and backups use a copied journal.'])
    app = None
    def execute(action, values):
        job = app.runner.submit_pilot(action,values)
        started = time.monotonic()
        while True:
            current = app.store.job(job['id'])
            if current['status'] not in ('queued','running'):
                write_json(output/(job['id']+'.json'),current)
                return current
            if time.monotonic()-started > 60:
                app.runner.cancel(job['id'])
                raise RuntimeError('Pilot action timeout; inspect durable transaction before any retry.')
            time.sleep(.1)
    try:
        app = Application(config)
        for test in tests:
            row = dict(verified_test_job_id=test['id']); report['combinations'].append(row)
            stage_id = test['result']['stage_id']
            manifest = json.loads((runtime/'execution-staging'/stage_id/'manifest.json').read_text(encoding='utf-8'))
            if Path(manifest['original_root']).resolve() != repo or {f['path'] for f in manifest['files']} != {'calc.py','tests/test_calc.py'}:
                raise RuntimeError('Manifest targets something other than the exact synthetic fixture.')
            row['before_hashes'] = originals()
            prepared = execute('pilot_prepare',dict(verified_test_job_id=test['id']))
            row['prepare_job'] = prepared
            if prepared['status'] != 'completed':
                row['outcome'] = 'prepare_blocked'; continue
            proposal = prepared['result']['apply_proposal']
            applied = execute('pilot_apply',dict(proposal_id=proposal['id'],proposal_hash=proposal['proposal_hash']))
            row['apply_job'] = applied
            row['applied_hashes'] = originals()
            if applied['status'] != 'completed':
                row['outcome'] = 'apply_failed'; break
            tx = applied['result']['pilot_transaction']
            row['matches_verified_stage'] = all(row['applied_hashes'][f['path']] == f['staged_sha256'] for f in manifest['files'])
            rolled = execute('pilot_rollback',dict(transaction_id=tx['id']))
            row['rollback_job'] = rolled
            row['restored_hashes'] = originals()
            row['outcome'] = ('applied_and_restored' if rolled['status']=='completed'
                              and row['restored_hashes']==files and row['matches_verified_stage'] else 'rollback_not_verified')
            write_json(output/'report.json',report)
            if row['outcome'] != 'applied_and_restored': break
    except Exception as exc:
        report['fatal_error'] = type(exc).__name__+': '+str(exc)[:1000]
    finally:
        if app is not None: app.close()
        report['final_original_hashes'] = originals()
        report['originals_restored'] = originals()==files
        report['original_journal_unchanged'] = hashlib.sha256(journal_path.read_bytes()).hexdigest()==before_journal
        report['ended_at'] = now()
        write_json(output/'report.json',report)
    print(json.dumps(dict(report=str(output/'report.json'),outcomes=[r.get('outcome') for r in report['combinations']],
                          originals_restored=report['originals_restored']),ensure_ascii=False),flush=True)
    return 0 if not report.get('fatal_error') and report['originals_restored'] and report['original_journal_unchanged'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
