"""Bounded, explicitly selected review contexts for registry projects and groups."""
import copy
from pathlib import Path
from .evidence import Observer, fingerprint
from .memory_registry import _check_root


class ScopeService:
    def __init__(self,registry,config,stop_event=None):
        self.registry=registry
        self.config=config
        self.stop_event=stop_event
        self.observers={}

    def members(self,kind,key):
        projects=self.registry.list_projects()
        if kind=='project':
            selected=[p for p in projects if p['id']==key]
        elif kind=='group':
            if not any(g['id']==key for g in self.registry.list_groups()):
                raise ValueError('Gruppe nicht gefunden.')
            selected=[p for p in projects if p['group_id']==key]
        else: raise ValueError('Geltungsbereich muss project oder group sein.')
        if not selected: raise ValueError('Keine Projekte im Geltungsbereich.')
        if any(p['archived'] for p in selected):
            raise ValueError('Ein Mitglied ist archiviert; Gruppenaufnahme bleibt unvollständig.')
        return selected

    def context(self,kind,key,require_egress=True,force_git=True):
        selected=self.members(kind,key)
        if require_egress and any(not p['model_egress'] for p in selected):
            raise ValueError('Explizite Modellübermittlung ist nicht für alle Mitglieder freigegeben.')
        cfg=copy.deepcopy(self.config)
        cfg['projects']=[]
        # Only the historical integration group owns these central documents.
        legacy=kind=='group' and key=='aurelia-integration'
        if not legacy: cfg.update(governor_dir='',snapshot_dir='')
        for p in selected:
            _check_root(Path(p['path']))
            original=p['source_config']
            cfg['projects'].append({**original,'id':p['id'],'name':p['name'],'path':p['path'],
                'kind':'existing','gate':original.get('gate','Aufnahme offen'),
                'status':original.get('status','Prüfung offen'),
                'next_step':original.get('next_step','Anforderungen und Nachweise erfassen.'),
                'depends_on':original.get('depends_on',[])})
        signature=fingerprint(cfg)
        observer=self.observers.get(signature)
        if observer is None:
            if len(self.observers)>=100: self.observers.clear()
            observer=Observer(cfg,self.stop_event); self.observers[signature]=observer
        observation=observer.scan(force_git=force_git)
        context=observer.context(observation)
        metadata=[{k:p[k] for k in ('id','name','path','requirements','group_id','role','model_egress','archived')} for p in selected]
        context['registry_projects']=metadata
        for row,meta in zip(context['projects'],metadata):
            row['evidence_hash']=fingerprint({'observed':row['evidence_hash'],'registration':meta})
        context['review_scope']={'kind':kind,'id':key}
        if kind=='project' and selected[0]['group_id']:
            context['group_boundary']={'group_id':selected[0]['group_id'],'role':selected[0]['role'],
                'shared_gates_remain_binding':True,'group_prerequisites_verified':False,
                'instruction':'Einzelreview ersetzt keine gruppenweite Prüfung gemeinsamer Voraussetzungen.'}
        decisions=[]; matrix={'steps':[],'projects':[],'next_steps':[]}
        if legacy:
            from .governance import STEPS,build_matrix
            ids={p['id'] for p in selected}
            applicable={s['id'] for s in STEPS if s['project_id'] in ids or s['project_id'] is None}
            decisions=[d for d in self.registry.store.decisions() if d['step_id'] in applicable]
            # Preserve existing journal fingerprint semantics; do not rewrite approvals.
            observation['source_hash']=fingerprint({'sources':observation['evidence_hash'],'planned_projects':self.registry.store.planned()})
            observation['evidence_hash']=fingerprint({'sources':observation['source_hash'],'rules':STEPS})
            observation['decision_hash']=fingerprint(decisions)
            derived=build_matrix(observation,decisions,self.registry.store.jobs(200),self.registry.store.planned())
            matrix={k:derived[k] for k in ('steps','projects','next_steps')}
            matrix['steps']=[s for s in matrix['steps'] if s['id'] in applicable]
        context['operator_decisions']=decisions
        context['decision_hash']=fingerprint(decisions)
        context['governor_matrix']=matrix
        context['current_request']={'authorized':require_egress,'scope':'read_only_advisory',
            'product_implementation_authorized':False,'historical_pause_superseded_for_this_review':require_egress}
        context['scope_hash']=fingerprint({'observation':observation['evidence_hash'],
            'registry':metadata,'decisions':decisions,'matrix':matrix})
        from .vault import Vault
        vault=Vault(self.registry,self.config.get('data_dir','runtime'),self.config.get('vault_root') or None)
        scopes=[(kind,key)]+([('project',p['id']) for p in selected] if kind=='group' else [])
        vault_sources=[]
        for source_kind,source_key in scopes:
            mappings=vault.list_sources(source_kind,source_key)
            if mappings:
                permissions={m['id']:m['model_egress'] for m in mappings}
                vault_sources.extend({**s,'scope_kind':source_kind,'scope_id':source_key,'model_egress':permissions[s['id']]}
                    for s in vault.context(source_kind,source_key,require_egress)['sources'])
        context['vault_sources']=vault_sources
        for row in context['projects']:
            applicable_vault=[s for s in vault_sources if s['scope_kind']=='group' or s['scope_id']==row['id']]
            row['evidence_hash']=fingerprint({'project':row['evidence_hash'],'vault':applicable_vault})
        context['intake']=[{'project_id':p['id'],'requirements_recorded':bool(p['requirements'].strip()),
            'memories_present':bool(o['memories']),'evidence_complete':o['evidence_complete'],
            'intake_accepted':False,'missing_proofs':o['warnings']} for p,o in zip(selected,observation['projects'])]
        # A template or successful scan is not an assessed requirements/test/dependency intake.
        context['plan_ready']=False
        # Intake confirmations change the planning hash, but do not invalidate
        # other drafts prepared from the same group sources and decisions.
        context['intake_source_hash']=fingerprint({'scope':context['scope_hash'],'vault':vault_sources})
        from .intake import Intake
        book=Intake(self.registry.store)
        records=book.records([p['id'] for p in selected])
        context['intake_records']=records
        for item,row in zip(context['intake'],context['projects']):
            item['intake_accepted']=book.accepted(item['project_id'],row['evidence_hash'])
            item['requirements_recorded']=item['requirements_recorded'] or item['intake_accepted']
        context['plan_ready']=all(i['intake_accepted'] and i['evidence_complete'] and i['memories_present'] for i in context['intake'])
        context['scope_hash']=fingerprint({'base':context['scope_hash'],'intake_records':records})
        context['scope_hash']=fingerprint({'base':context['scope_hash'],'vault_sources':vault_sources})
        # Unconfirmed source-bound suggestions are review reference material,
        # never operator decisions or assessed intake. Resolve them against the
        # stable intake source hash before extending only the review fingerprint.
        from .intake_drafts import IntakeDrafts
        accepted={item['project_id'] for item in context['intake'] if item['intake_accepted']}
        context['intake_proposals']=[
            {**{key:draft[key] for key in ('id','project_id','source_hash','fields')},
             'status':'unconfirmed_draft'}
            for draft in IntakeDrafts(self.registry.store).list(context)
            if draft['current'] and draft['project_id'] not in accepted]
        if context['intake_proposals']:
            context['scope_hash']=fingerprint({'base':context['scope_hash'],
                'intake_proposals':context['intake_proposals']})
        return context
