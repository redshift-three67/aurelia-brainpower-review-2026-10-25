"""Explicit paid synthetic Hermes/Sol/Astra staging evaluation; no product inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor_workbench.config import load_config
from governor_workbench.evidence import now
from governor_workbench.hermes import HermesAdapter
from governor_workbench.intake import Intake
from governor_workbench.plans import PlanBook
from governor_workbench.server import Application
from governor_workbench.store import Store


def write_json(path, value):
    encoded = json.dumps(value, ensure_ascii=False, indent=2)
    if len(encoded) > 2_000_000:
        raise ValueError('Evaluation artifact exceeds its bounded report size.')
    path.write_text(encoded, encoding='utf-8')


def git(repo, hooks, *args):
    result = subprocess.run(['git', '-c', 'core.hooksPath='+str(hooks), '-c', 'commit.gpgsign=false',
        '-c', 'user.name=Governor synthetic evaluation', '-c', 'user.email=synthetic@invalid.local',
        '-c', 'core.autocrlf=false', '-c', 'init.templateDir=', *args],
        cwd=repo, capture_output=True, timeout=30,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        raise RuntimeError('Synthetic Git setup failed; command output withheld.')


def wait_job(app, job, report, target):
    started = time.monotonic()
    progress = started
    while True:
        current = app.store.job(job['id'])
        if current['status'] not in ('queued', 'running'):
            print(f"{current['action']}: {current['status']} ({time.monotonic()-started:.1f}s)", flush=True)
            write_json(target/(current['id']+'.json'), current)
            return current
        if time.monotonic()-started > 350:
            app.runner.cancel(job['id'])
            deadline = time.monotonic()+20
            while time.monotonic() < deadline:
                current = app.store.job(job['id'])
                if current['status'] not in ('queued', 'running'):
                    break
                time.sleep(.2)
            write_json(target/(current['id']+'.json'), current)
            raise RuntimeError('Evaluation job exceeded 350 seconds; cancelled without retry.')
        if time.monotonic()-progress >= 45:
            print(f"{current['action']}: {current['status']}, elapsed {time.monotonic()-started:.0f}s", flush=True)
            progress = time.monotonic()
            report['progress'] = {'job_id': current['id'], 'action':current['action'], 'elapsed_seconds':round(progress-started)}
            write_json(target/'report.json', report)
        time.sleep(.25)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    if output.parent != workspace/'artifacts' or not output.name.startswith('staging-pilot-live-'):
        parser.error('Output must be a fresh direct artifacts/staging-pilot-live-* child directory.')
    if output.exists():
        parser.error('Evaluation output already exists; refusing to overwrite or retry a live run.')
    source_config = load_config(args.config)
    if source_config['orchestrator_transport'] != 'hermes':
        parser.error('This evaluation requires the explicitly configured Hermes transport.')
    output.mkdir(parents=True)
    report = {'started_at':now(), 'synthetic_only':True, 'real_product_content_sent':False,
              'automatic_reviews':False, 'combinations':[], 'apply_back_enabled':False,
              'limitations':['One small synthetic fixture; not product acceptance or model superiority evidence.',
                            'Restricted Python unittest runner is not an OS sandbox.']}
    evaluated_modules = ('jobs.py','execution_policy.py','patch_llm.py','post_test_review.py',
                         'execution_workspace.py','staged_tests.py','restricted_test_runner.py',
                         'scopes.py','intake.py','plans.py')
    report['module_hashes_at_start'] = {name:hashlib.sha256((workspace/'governor_workbench'/name).read_bytes()).hexdigest()
                                      for name in evaluated_modules}
    app = None
    try:
        repo = output/'synthetic-project'; repo.mkdir()
        hooks = output/'empty-git-hooks'; hooks.mkdir()
        (repo/'tests').mkdir(); (repo/'project_memories').mkdir()
        files = {'calc.py':'def value():\n    return 1\n',
                 'tests/test_calc.py':'import unittest\nfrom calc import value\n\nclass TestValue(unittest.TestCase):\n    def test_value(self):\n        self.assertEqual(value(), 2)\n',
                 'project_memories/strategy_project_pilot.md':
                     '# Synthetic isolated pilot\n\nRequirement: calc.value() returns integer 2.\n'
                     'Keep the existing unittest assertion unchanged. No dependencies, secrets or product data.\n'
                     'Only calc.py should need a behavior change; tests/test_calc.py is included for isolated tests.\n'
                     'This evaluation permits staging copies and local tests only. Original bytes must stay unchanged.\n'}
        for path, content in files.items():
            (repo/path).write_text(content, encoding='utf-8', newline='')
        git(repo,hooks,'init','-b','main')
        git(repo,hooks,'add','--',*files)
        git(repo,hooks,'commit','-m','Synthetic staging evaluation baseline')
        originals = {path:hashlib.sha256((repo/path).read_bytes()).hexdigest() for path in files}
        report['original_hashes'] = originals
        kept = ('router_url','router_api_key_env','codex_auth_path','hermes_path','orchestrator_transport',
                'orchestrator','supervisor','reasoning','model_timeout')
        config = {key:source_config[key] for key in kept}
        config.update(data_dir=str(output/'runtime'), projects=[{'id':'synthetic_pilot','name':'Synthetic isolated pilot',
            'path':str(repo), 'kind':'existing','gate':'Isolated staging only; no apply-back',
            'status':'Synthetic evaluation','next_step':'Change staged calc value to two and test','depends_on':[]}],
            governor_dir='',snapshot_dir='',vault_root='',live_views={},staging_pilot_roots=[str(repo)],
            legacy_review_egress_authorized=False,monitor_interval=3600,git_interval=60,
            auto_review_cooldown=900,auto_review_daily_limit=4,port=8787)
        journal = Store(Path(config['data_dir'])/'journal.db')
        journal.set_setting('monitor_enabled',False)
        journal.set_setting('auto_review',False)
        adapter = HermesAdapter(config['hermes_path'],workspace=config['data_dir'],
                                codex_auth_path=config['codex_auth_path'],timeout=config['model_timeout'])
        availability = adapter.check()
        report['hermes_version'] = availability.get('version')
        if not availability.get('available'):
            raise RuntimeError('Hermes availability probe failed; no model calls attempted.')
        probe = adapter.review('Synthetic local zero-tool capability probe.',probe_only=True)
        report['zero_tool_probe'] = probe
        write_json(output/'report.json',report)
        if probe.get('tool_count') != 0 or probe.get('success') is not True:
            raise RuntimeError('Zero-tool probe failed; no model calls attempted.')
        print('Genuine Hermes zero-tool probe passed.',flush=True)
        app = Application(config)
        app.registry.set_project_policy('synthetic_pilot',requirements='calc.value returns integer 2; preserve existing test assertion.',model_egress=True)
        context = app.scope_context('project','synthetic_pilot',False)
        Intake(app.store).accept(context,context['scope_hash'],'synthetic_pilot',{
            'requirements':'calc.value must return integer 2; do not weaken tests.',
            'test_strategy':'Run unchanged stdlib unittest test_value against staged calc.py.',
            'dependencies':'No external dependencies or prerequisite steps.',
            'open_evidence':'Staged test execution and independent post-test review are pending.'})
        context = app.scope_context('project','synthetic_pilot')
        proposal = {'summary':'Synthetic isolated staging evaluation','steps':[{
            'id':'fix_value','title':'Return two in staged fixture','project_id':'synthetic_pilot',
            'priority':1,'depends_on':[],'rationale':'Operator-defined synthetic fixture; no product inputs.',
            'scope':['calc.py','tests/test_calc.py'],'tests':['Run unchanged TestValue.test_value using stdlib unittest.'],
            'action':'change'}]}
        # The operator-defined fixture plan is not reported as an evaluated model plan.
        operator_review = {'summary':'Operator fixture plan reviewed for this explicit synthetic evaluation only.',
                           'decision':'REVIEW_ONLY','findings':[],'required_evidence':[]}
        book = PlanBook(app.store)
        candidate = book.save_candidate(context,proposal,operator_review,'operator-synthetic-fixture')
        book.approve(candidate['id'],context['scope_hash'],context,['fix_value'])
        report['plan_provenance'] = 'Operator-defined fixed evaluation plan; not a model-generated or model-reviewed plan.'
        for supervisor in ('gpt-5.6-sol','gpt-6-astra'):
            row = {'supervisor':supervisor, 'orchestrator':'gpt-5.6-terra','transport':'hermes','started_at':now()}
            report['combinations'].append(row)
            write_json(output/'report.json',report)
            print('Starting live synthetic combination: Hermes Terra + '+supervisor,flush=True)
            patch_job = app.runner.submit('scope_patch',supervisor=supervisor,scope_kind='project',scope_id='synthetic_pilot',
                                          candidate_id=candidate['id'],step_id='fix_value')
            patched = wait_job(app,patch_job,report,output)
            row['patch_job'] = patched
            if patched['status']=='completed' and (patched.get('result') or {}).get('stage') and not patched['result'].get('stale'):
                tested = wait_job(app,app.runner.submit('stage_test',supervisor=supervisor,stage_job_id=patched['id']),report,output)
                row['test_job'] = tested
                row['outcome'] = 'verified' if tested['status']=='completed' and tested['result'].get('verified') else 'not_verified'
            else:
                row['outcome'] = 'blocked_or_failed_without_tests'
            row['ended_at'] = now()
            write_json(output/'report.json',report)
    except Exception as exc:
        report['fatal_error'] = type(exc).__name__+': '+str(exc)[:1000]
        print(report['fatal_error'],flush=True)
    finally:
        if app is not None:
            app.close()
        if 'originals' in locals():
            observed = {path:hashlib.sha256((repo/path).read_bytes()).hexdigest() for path in originals}
            report['final_original_hashes'] = observed
            report['originals_unchanged'] = observed == originals
        report.pop('progress',None)
        report['module_hashes_at_end'] = {name:hashlib.sha256((workspace/'governor_workbench'/name).read_bytes()).hexdigest()
                                        for name in evaluated_modules}
        report['module_files_unchanged_during_run'] = report['module_hashes_at_start'] == report['module_hashes_at_end']
        report['ended_at'] = now()
        write_json(output/'report.json',report)
    print(json.dumps({'report':str(output/'report.json'),'outcomes':[row.get('outcome') for row in report['combinations']],
                      'originals_unchanged':report.get('originals_unchanged')},ensure_ascii=False),flush=True)
    return 1 if report.get('fatal_error') or not report.get('originals_unchanged') else 0


if __name__ == '__main__':
    raise SystemExit(main())
