"""Explicit synthetic live clarification evaluation; never loads product sources."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor_workbench.config import load_config
from governor_workbench.evidence import now
from governor_workbench.hermes import HermesAdapter
from governor_workbench.intake import Intake
from governor_workbench.server import Application
from governor_workbench.store import Store
from tools.evaluate_staging_pilot import git, write_json


def wait(app, job_id, started):
    progress = time.monotonic()
    while True:
        job = app.store.job(job_id)
        if job['status'] not in ('queued', 'running'):
            return job
        elapsed = time.monotonic() - started
        if elapsed > 350:
            app.runner.cancel(job_id)
            raise RuntimeError('Live job exceeded 350 seconds; cancelled without retry.')
        if time.monotonic() - progress > 40:
            print(f'{job_id}: {job["status"]}, {elapsed:.0f}s', flush=True)
            progress = time.monotonic()
        time.sleep(.25)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    if output.parent != workspace / 'artifacts' or not output.name.startswith('operator-questions-live-'):
        parser.error('Output must be a fresh direct artifacts/operator-questions-live-* child.')
    if output.exists():
        parser.error('Output already exists; refusing to overwrite or repeat a live evaluation.')
    source_config = load_config(args.config)
    if source_config['orchestrator_transport'] != 'hermes':
        parser.error('Explicitly configured Hermes transport is required.')
    output.mkdir(parents=True)
    modules = ('jobs.py', 'question_llm.py', 'planning_llm.py', 'operator_questions.py',
               'store.py', 'server.py', 'scopes.py', 'intake.py', 'plans.py', 'hermes.py', 'hermes_runner.py')
    def hashes():
        return {name: hashlib.sha256((workspace/'governor_workbench'/name).read_bytes()).hexdigest() for name in modules}
    report = dict(started_at=now(), synthetic_only=True, real_product_content_sent=False,
                  automatic_reviews=False, apply_back_enabled=False, combinations=[],
                  module_hashes_at_start=hashes(), limitations=[
                      'One synthetic planning clarification per supervisor; no retry or model superiority claim.',
                      'No patch, product acceptance, HTTP/browser or apply-back evaluation.'])
    app = None
    try:
        repo = output/'synthetic-project'; repo.mkdir()
        hooks = output/'empty-git-hooks'; hooks.mkdir()
        (repo/'project_memories').mkdir()
        requirement = ('The release label must be exactly one of Alpha or Beta. Selection belongs to the '
                       'operator and is explicitly unspecified. Both values already satisfy the accepted '
                       'requirements; choosing one changes no requirement, file scope or test criterion. '
                       'Only release_note.md may be included in proposed change scope; no new files are allowed. '
                       'Do not infer a label. The operator label decision must be clarified before a concrete '
                       'release-note change plan can be produced. Do not execute changes.')
        files = {'release_note.md': '# Synthetic release\n\nLabel: [operator selection pending]\n',
                 'project_memories/strategy_project_clarification.md':
                     '# Synthetic clarification fixture\n\n' + requirement + '\n'}
        for path, content in files.items():
            (repo/path).write_text(content, encoding='utf-8', newline='')
        git(repo,hooks,'init','-b','main')
        git(repo,hooks,'add','--',*files)
        git(repo,hooks,'commit','-m','Synthetic clarification evaluation baseline')
        originals = {path:hashlib.sha256((repo/path).read_bytes()).hexdigest() for path in files}
        report['original_hashes'] = originals
        kept = ('router_url','router_api_key_env','codex_auth_path','hermes_path','orchestrator_transport',
                'orchestrator','supervisor','reasoning','model_timeout')
        config = {key:source_config[key] for key in kept}
        config.update(data_dir=str(output/'runtime'), projects=[dict(id='synthetic_clarification',
            name='Synthetic release label clarification', path=str(repo), kind='existing',
            gate='Read-only planning; no implementation permission', status='Synthetic evaluation',
            next_step='Clarify the operator-owned Alpha/Beta label before concrete planning', depends_on=[])],
            governor_dir='', snapshot_dir='', vault_root='', live_views={}, staging_pilot_roots=[],
            legacy_review_egress_authorized=False, monitor_interval=3600, git_interval=60,
            auto_review_cooldown=900, auto_review_daily_limit=4, port=8787)
        journal = Store(Path(config['data_dir'])/'journal.db')
        journal.set_setting('monitor_enabled',False)
        journal.set_setting('auto_review',False)
        adapter = HermesAdapter(config['hermes_path'], workspace=config['data_dir'],
                                codex_auth_path=config['codex_auth_path'], timeout=config['model_timeout'])
        availability = adapter.check()
        report['hermes_version'] = availability.get('version')
        if not availability.get('available'):
            raise RuntimeError('Hermes unavailable; no live models called.')
        probe = adapter.review('Synthetic local zero-tool capability probe.',probe_only=True)
        report['zero_tool_probe'] = probe
        write_json(output/'report.json',report)
        if probe.get('tool_count') != 0 or probe.get('success') is not True:
            raise RuntimeError('Hermes zero-tool probe failed; no live models called.')
        print('Genuine Hermes zero-tool probe passed.',flush=True)
        app = Application(config)
        app.registry.set_project_policy('synthetic_clarification',requirements=requirement,model_egress=True)
        context = app.scope_context('project','synthetic_clarification',False)
        Intake(app.store).accept(context,context['scope_hash'],'synthetic_clarification',dict(
            requirements=requirement, test_strategy='Check release_note.md names exactly the selected Alpha/Beta label; no other files change.',
            dependencies='No dependencies or prerequisite implementation steps.',
            open_evidence='Operator label decision pending within the accepted Alpha/Beta choices.'))
        for supervisor in ('gpt-5.6-sol','gpt-6-astra'):
            row = dict(supervisor=supervisor, orchestrator='gpt-5.6-terra', transport='hermes', started_at=now())
            report['combinations'].append(row)
            context = app.scope_context('project','synthetic_clarification')
            row['scope_hash'] = context['scope_hash']
            write_json(output/(supervisor+'-context.json'),context)
            print('Starting real synthetic clarification: Hermes Terra + '+supervisor,flush=True)
            started = time.monotonic()
            job = app.runner.submit('scope_plan',supervisor=supervisor,
                                    scope_kind='project',scope_id='synthetic_clarification')
            row['job_id'] = job['id']
            first = wait(app,job['id'],started)
            row['initial_job'] = first
            write_json(output/'report.json',report)
            if first['status'] == 'waiting_for_operator':
                pending = app.questions.list(status='pending',job_id=job['id'])
                if len(pending) != 1:
                    raise RuntimeError('Waiting job lacks one pending question.')
                record = pending[0]
                row['actual_question'] = record
                answer = 'Alpha, unverändert innerhalb der vorgegebenen Auswahl Alpha/Beta.'
                receipt = app.runner.answer_question(record['id'],answer,record['scope_hash'])
                row['answer_receipt'] = receipt
                row['same_job_requeued'] = receipt['job']['id'] == job['id']
                final = wait(app,job['id'],started)
                row['final_job'] = final
                if final['status'] == 'waiting_for_operator':
                    row['outcome'] = 'another_question_without_retry'
                    app.runner.cancel(job['id'])
                elif final['status'] == 'completed' and (final.get('result') or {}).get('candidate'):
                    row['outcome'] = 'same_job_plan_completed'
                else:
                    row['outcome'] = 'answer_review_or_plan_blocked'
                row['resolved_question'] = app.questions.get(record['id'])
            else:
                row['outcome'] = 'no_accepted_question'
            row['ended_at'] = now()
            write_json(output/'report.json',report)
            print(supervisor+': '+row['outcome'],flush=True)
    except Exception as exc:
        report['fatal_error'] = type(exc).__name__+': '+str(exc)[:1000]
        print(report['fatal_error'],flush=True)
    finally:
        if app is not None:
            app.close()
        if 'originals' in locals():
            report['final_original_hashes'] = {path:hashlib.sha256((repo/path).read_bytes()).hexdigest() for path in originals}
            report['originals_unchanged'] = report['final_original_hashes'] == originals
        report['module_hashes_at_end'] = hashes()
        report['module_files_unchanged_during_run'] = report['module_hashes_at_start'] == report['module_hashes_at_end']
        report['ended_at'] = now()
        write_json(output/'report.json',report)
    print(json.dumps(dict(report=str(output/'report.json'),outcomes=[row.get('outcome') for row in report['combinations']],
                          originals_unchanged=report.get('originals_unchanged')),ensure_ascii=False),flush=True)
    return 1 if report.get('fatal_error') or not report.get('originals_unchanged') else 0


if __name__ == '__main__':
    raise SystemExit(main())
