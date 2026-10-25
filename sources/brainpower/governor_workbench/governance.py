"""Pure, evidence-bound operator gates. Documents and models never grant approval.

Decisions must be supplied in append order, oldest first. Authorization/revocation
and acceptance/rejection are separate decision families. A source acceptance is
bound to the observation hash, never to the decision journal's own hash.
"""
from copy import deepcopy


STEPS = [
    dict(id='reconcile_sources', project_id=None, title='Quellen und Statusaussagen abgleichen',
         kind='read_only', depends_on=[], priority=10, action='governance_report',
         criteria=['Aktuelle Quellen mit Hash und Herkunft erfassen.', 'Widersprüche und fehlende Nachweise benennen.',
                   'Betreiber akzeptiert den Abgleich ausdrücklich.']),
    dict(id='radiworks_intake', project_id='radiworks', title='RadiWorks: lesender Contract-Intake',
         kind='read_only', depends_on=['reconcile_sources'], priority=20, action='governance_report',
         criteria=['Vollständige ABI-/Vertragsfeldmatrix mit Quellen und Hashes vorlegen; ein Quelleninventar allein genügt nicht.',
                   'Zwei unabhängige Reviews für denselben Evidenzstand belegen und offene Fragen dokumentieren.',
                   'Keine Adapter implementieren; Betreiber prüft die Nachweise und akzeptiert den Intake.']),
    dict(id='aurelia_ground_zero', project_id='aurelia', title='Aurelia: Ground-Zero-Nachweise abnehmen',
         kind='external', depends_on=[], priority=30, action=None,
         criteria=['Ground-Zero- und Restore-Nachweise außerhalb dieser Automatik vorlegen.',
                   'Betreiber prüft und akzeptiert die Nachweise für den aktuellen Stand.']),
    dict(id='radi144_checkpoint', project_id='radi144', title='Radi144: Checkpoint und Reviewnachweis prüfen',
         kind='read_only', depends_on=['reconcile_sources'], priority=40, action='governance_report',
         criteria=['Checkpoint, HEAD und Index getrennt nachweisen.', 'Offene unabhängige Reviews benennen.',
                   'Betreiber akzeptiert den Checkpoint-Abgleich.']),
    dict(id='morphic_authority', project_id='morphic_v1', title='Morphic: Authority Freeze lesend prüfen',
         kind='read_only', depends_on=['reconcile_sources'], priority=50, action='governance_report',
         criteria=['Authority-Quellen und G0-Vorbehalte prüfen.', 'Keine Implementierungsfreigabe ableiten.',
                   'Betreiber akzeptiert den Authority-Abgleich.']),
    dict(id='templates_contract', project_id='modul_templates', title='Modul_Templates: Vertragsautorität abnehmen',
         kind='external', depends_on=[], priority=60, action=None,
         criteria=['Gültige Vertragsversion und offene Abweichungen belegen.',
                   'Betreiber akzeptiert die passive Vertragsautorität ausdrücklich.']),
    dict(id='radiworks_adapter', project_id='radiworks', title='RadiWorks: Adapter-Implementierung freigeben',
         kind='implementation', depends_on=['radiworks_intake', 'aurelia_ground_zero', 'templates_contract'],
         priority=70, action=None, criteria=['Alle drei Voraussetzungen aktuell abgenommen.',
                                          'Konkreten Implementierungsumfang separat autorisieren.']),
    dict(id='radi144_implementation', project_id='radi144', title='Radi144: Implementierungsumfang freigeben',
         kind='implementation', depends_on=['radi144_checkpoint', 'templates_contract'], priority=80,
         action=None, criteria=['Checkpoint und Vertragsautorität aktuell abgenommen.',
                               'Konkreten Implementierungsumfang separat autorisieren.']),
    dict(id='morphic_implementation', project_id='morphic_v1', title='Morphic: Implementierungsumfang freigeben',
         kind='implementation', depends_on=['morphic_authority', 'templates_contract'], priority=90,
         action=None, criteria=['Authority Freeze und Vertragsautorität aktuell abgenommen.',
                               'Konkreten Implementierungsumfang separat autorisieren.']),
]


def _complete(observation):
    return (observation.get('evidence_complete') is True
            and bool(observation.get('evidence_hash'))
            and bool(observation.get('projects'))
            and all(p.get('evidence_complete', True) is True for p in observation['projects']))


def validate_decision(data, observation, steps=STEPS):
    """Validate one operator decision; caller checks eligibility and appends it.

    This function has no journal input, so it cannot prove prior authorization or
    prerequisite acceptance. Use build_matrix().steps.acceptance_eligible first.
    """
    allowed = {'step_id', 'kind', 'reason', 'evidence_hash', 'actor'}
    if not isinstance(data, dict) or not set(data) <= allowed:
        raise ValueError('Unbekannte Entscheidungsfelder.')
    key, kind = data.get('step_id'), data.get('kind')
    step = next((s for s in steps if s['id'] == key), None)
    project_ids = {p['id'] for p in observation.get('projects', [])}
    if step is None or (step['project_id'] is not None and step['project_id'] not in project_ids):
        raise ValueError('Schritt ist für diese Beobachtung nicht vorhanden.')
    if kind not in ('authorize', 'revoke', 'accept', 'reject'):
        raise ValueError('Unbekannte Entscheidungsart.')
    if data.get('actor', 'operator') != 'operator':
        raise ValueError('Nur ausdrückliche Betreiberentscheidungen sind zulässig.')
    reason = data.get('reason')
    if not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 4000:
        raise ValueError('Begründung: 1 bis 4000 Zeichen erforderlich.')
    current = observation.get('evidence_hash')
    evidence = data.get('evidence_hash', current)
    if not isinstance(evidence, str) or not evidence:
        raise ValueError('Evidenz-Fingerabdruck fehlt.')
    if kind == 'accept' and ('evidence_hash' not in data or evidence != current or not _complete(observation)):
        raise ValueError('Abnahme benötigt den aktuellen vollständigen Evidenzstand.')
    if kind == 'authorize' and step['kind'] != 'read_only' and (evidence != current or not _complete(observation)):
        raise ValueError('Diese Autorisierung benötigt den aktuellen vollständigen Evidenzstand.')
    return dict(step_id=key, kind=kind, reason=reason.strip(), evidence_hash=evidence, actor='operator')


def _review_summary(observation, jobs):
    candidates = [j for j in jobs if j.get('action') in ('hybrid_review', 'compare_reviews')]
    candidates.sort(key=lambda j: str(j.get('ended_at') or j.get('created_at') or ''), reverse=True)
    fallback = None
    for job in candidates:
        result = job.get('result') or {}
        if not isinstance(result, dict):
            result = {}
        report = result.get('review') or {}
        if not isinstance(report, dict):
            report = {}
        model_reports = []
        comparison_valid = True
        if job.get('action') == 'compare_reviews':
            reports = result.get('reviews') or {}
            comparison_valid = isinstance(reports, dict) and result.get('comparison', {}).get('complete') is True
            for model in ('gpt-5.6-sol', 'gpt-6-astra'):
                value = reports.get(model) if isinstance(reports, dict) else None
                if not isinstance(value, dict) or value.get('decision') not in ('BLOCK', 'REVIEW_ONLY') or not isinstance(value.get('summary'), str):
                    comparison_valid = False
                    continue
                model_reports.append(dict(model=model, summary=value['summary'], decision=value['decision'],
                                          findings=_strings(value.get('findings')),
                                          required_evidence=_strings(value.get('required_evidence')),
                                          provenance=job.get('id')))
            decisions = {r['decision'] for r in model_reports}
            report = dict(summary='; '.join(r['model'] + ': ' + r['summary'] for r in model_reports),
                          decision='BLOCK' if 'BLOCK' in decisions else 'REVIEW_ONLY',
                          findings=[r['model'] + ': ' + text for r in model_reports for text in r['findings']],
                          required_evidence=[r['model'] + ': ' + text for r in model_reports for text in r['required_evidence']])
        valid = (job.get('status') == 'completed' and result.get('success') is not False
                 and comparison_valid
                 and report.get('decision') in ('BLOCK', 'REVIEW_ONLY')
                 and isinstance(report.get('summary'), str))
        current = (valid and _complete(observation) and not result.get('stale')
                   and result.get('evidence_hash') == observation.get('evidence_hash')
                   and (not observation.get('decision_hash')
                        or result.get('decision_hash') == observation['decision_hash']))
        status = 'current' if current else 'stale' if valid else 'failed'
        if job.get('status') in ('queued', 'running', 'cancelled', 'interrupted'):
            status = job['status']
        row = dict(status=status,
                   job_id=job.get('id'), project_id=job.get('project_id'),
                   scope='project' if job.get('project_id') else 'all_projects',
                   summary=report.get('summary', ''), decision=report.get('decision') if valid else None,
                   findings=_strings(report.get('findings')),
                   required_evidence=_strings(report.get('required_evidence')),
                   evidence_hash=result.get('evidence_hash'), decision_hash=result.get('decision_hash'),
                   reviews=model_reports, comparison=deepcopy(result.get('comparison')),
                   advisory=True, approval_granted=False)
        if fallback is None:
            fallback = row
        if current:
            row['latest_attempt'] = {'job_id': fallback['job_id'], 'status': fallback['status']}
            return row
    return fallback or dict(status='unreviewed', job_id=None, project_id=None, scope=None, summary='', reviews=[],
                            decision=None, findings=[], required_evidence=[], advisory=True, approval_granted=False)


def _strings(value):
    return [s[:4000] for s in value[:100] if isinstance(s, str)] if isinstance(value, list) else []


def _knowledge(observation, decisions, jobs, planned):
    rows = []
    for project in observation.get('projects', []):
        for memory in project.get('memories', [])[:100]:
            rows.append(dict(kind='memory_evidence', project_id=project['id'], name=memory.get('name'),
                             sha256=memory.get('sha256'), provenance='project_memories/' + str(memory.get('name', '')),
                             committed=bool(memory.get('committed')), staged=bool(memory.get('staged')),
                             tracked_in_head=bool(memory.get('tracked_in_head')),
                             has_staged_changes=bool(memory.get('has_staged_changes')), accepted=False))
        for source in project.get('sources', [])[:30]:
            if not isinstance(source, dict):
                continue
            name = source.get('name', '')
            status_key = 'Snapshot' if name == 'session_state_freeze.json' else name
            declared = project.get('documented_statuses', {}).get(status_key)
            rows.append(dict(kind='source_declaration', project_id=project['id'], name=name,
                             sha256=source.get('sha256'), provenance=source.get('path') or name,
                             statement=deepcopy(declared) if declared is not None else str(source.get('content', ''))[:2000],
                             error=source.get('error'), accepted=False,
                             authority='Dokumentierte Aussage; keine aktuelle Betreiberabnahme.'))
    for decision in decisions[-100:]:
        rows.append(dict(kind='operator_decision', step_id=decision.get('step_id'),
                         decision_kind=decision.get('kind'), reason=decision.get('reason'),
                         sha256=decision.get('evidence_hash'), provenance=decision.get('id') or 'decision_journal',
                         accepted=False, authority='Historischer Journaleintrag; Wirksamkeit steht in der Schrittmatrix.'))
    for job in jobs[:40]:
        result = job.get('result') or {}
        if not isinstance(result, dict):
            result = {}
        test_run = job.get('action') == 'radiworks_tests'
        recorded_hash = result.get('source_hash', result.get('evidence_hash')) if test_run else result.get('evidence_hash')
        current_hash = observation.get('source_hash', observation.get('evidence_hash')) if test_run else observation.get('evidence_hash')
        rows.append(dict(kind='execution_record', action=job.get('action'), status=job.get('status'),
                         sha256=recorded_hash, provenance=job.get('id'), accepted=False,
                         current=bool(_complete(observation) and recorded_hash == current_hash
                                      and not result.get('stale') and job.get('status') == 'completed'
                                      and (not result.get('decision_hash') or result['decision_hash'] == observation.get('decision_hash'))),
                         authority='Ausführung dokumentiert; kein Ersatz für Betreiberabnahme.'))
    for project in planned[:50]:
        rows.append(dict(kind='planned_module', project_id=project['id'], name=project.get('name'),
                         provenance='planned_module_journal', sha256=None, accepted=False))
    return rows[:500]


def build_matrix(observation, decisions, jobs, planned=None):
    """Compute gates without performing IO, mutating inputs or granting authority.

    Acceptance eligibility means an operator may assess the criteria, not that a
    report or a model has proven them. Implementation rows never offer execution.
    """
    planned = planned or []
    projects = observation.get('projects', [])
    project_ids = {p['id'] for p in projects}
    definitions = {s['id']: deepcopy(s) for s in STEPS
                   if projects and (s['project_id'] is None or s['project_id'] in project_ids)}
    latest = {}
    for index, decision in enumerate(decisions):
        if (decision.get('step_id') not in definitions or decision.get('actor', 'operator') != 'operator'
                or not isinstance(decision.get('reason'), str) or not decision['reason'].strip()):
            continue
        kind = decision.get('kind')
        family = 'authorization' if kind in ('authorize', 'revoke') else 'acceptance' if kind in ('accept', 'reject') else None
        if family:
            latest[(decision['step_id'], family)] = (index, decision)
    rows = {}
    complete, current_hash = _complete(observation), observation.get('evidence_hash')

    def evaluate(key):
        if key in rows:
            return rows[key]
        step = definitions[key]
        dependencies = [evaluate(dep) if dep in definitions else None for dep in step['depends_on']]
        deps_ok = all(dep is not None and dep['accepted'] for dep in dependencies)
        auth_index, authorization = latest.get((key, 'authorization'), (-1, {}))
        accept_index, acceptance = latest.get((key, 'acceptance'), (-1, {}))
        authorized = (authorization.get('kind') == 'authorize'
                      and (step['kind'] == 'read_only' or authorization.get('evidence_hash') == current_hash))
        reasons = []
        if not complete:
            reasons.append('Evidenz unvollständig; aktuelle Abnahme und Ausführung gesperrt.')
        for dep_id, dep in zip(step['depends_on'], dependencies):
            if dep is None or not dep['accepted']:
                reasons.append('Voraussetzung nicht aktuell abgenommen: ' + dep_id)
        if not authorized:
            reasons.append('Ausdrückliche aktuelle Betreiberautorisierung fehlt oder wurde widerrufen.')
        eligible = complete and deps_ok and authorized
        status = 'blocked'
        if eligible:
            if acceptance.get('kind') == 'accept':
                status = 'accepted' if acceptance.get('evidence_hash') == current_hash else 'stale'
                if status == 'stale':
                    reasons.append('Frühere Abnahme gehört zu einem anderen Quellenstand; erneut prüfen und abnehmen.')
            elif acceptance.get('kind') == 'reject' and accept_index > auth_index:
                status = 'review_required'
                reasons.append('Betreiber hat den Nachweis zurückgewiesen: ' + acceptance['reason'])
            else:
                reports = [j for j in jobs if j.get('action') == 'governance_report' and j.get('status') == 'completed'
                           and isinstance(j.get('result'), dict) and j['result'].get('step_id') == key
                           and j['result'].get('evidence_hash') == current_hash and not j['result'].get('stale')
                           and (not j['result'].get('decision_hash') or j['result']['decision_hash'] == observation.get('decision_hash'))
                           and j['result'].get('success') is not False]
                status = 'review_required' if reports or step['kind'] == 'external' else 'ready'
                if status == 'review_required':
                    reasons.append('Nachweiskriterien durch den Betreiber prüfen und ausdrücklich abnehmen.')
                elif step['kind'] == 'implementation':
                    reasons.append('Separat autorisierter Umfang; diese Workbench führt keine Produktimplementierung aus.')
        row = {**step, 'status': status, 'reasons': reasons, 'authorized': bool(authorized),
               'accepted': status == 'accepted', 'dependencies_accepted': deps_ok,
               'evidence_complete': complete, 'evidence_hash': current_hash,
               'acceptance_eligible': bool(eligible), 'acceptance_basis': 'operator_only',
               'can_run': bool(status in ('ready', 'stale') and eligible and step['kind'] == 'read_only'),
               'authorization': deepcopy(authorization) or None, 'acceptance': deepcopy(acceptance) or None}
        rows[key] = row
        return row

    for key in definitions:
        evaluate(key)
    steps = sorted(rows.values(), key=lambda s: (s['priority'], s['id']))
    next_steps = [deepcopy(s) for s in steps if s['status'] in ('ready', 'review_required', 'stale')]
    project_rows = []
    for project in projects:
        own = [s for s in steps if s['project_id'] == project['id']]
        pending = [s for s in own if not s['accepted']]
        eligible = [s for s in pending if s['status'] in ('ready', 'review_required', 'stale')]
        selected = next(iter(eligible or pending), None)
        if selected:
            status, title, reasons = selected['status'], selected['title'], selected['reasons']
        else:
            status = 'accepted' if own else 'blocked'
            title = 'Definierte Schritte aktuell abgenommen.' if own else 'Für dieses Projekt ist noch kein Schritt definiert.'
            reasons = [] if own else ['Konkreten Umfang und Nachweiskriterien festlegen.']
        project_rows.append(dict(id=project['id'], status=status, next_step=title,
                                 gate=selected['title'] if selected else title,
                                 reasons=list(reasons), step_ids=[s['id'] for s in own]))
    for project in planned:
        if project['id'] not in project_ids:
            project_rows.append(dict(id=project['id'], status='blocked', gate='Geplant; keine Implementierungsfreigabe',
                                     next_step='Umfang, Abhängigkeiten und Nachweiskriterien konkretisieren.',
                                     reasons=['Geplante Module besitzen keine automatisch freigegebenen Schritte.'], step_ids=[]))
    return dict(steps=steps, projects=project_rows, next_steps=next_steps,
                knowledge=_knowledge(observation, decisions, jobs, planned),
                review_summary=_review_summary(observation, jobs))
