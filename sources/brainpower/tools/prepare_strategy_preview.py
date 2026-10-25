"""Synthetic local UI fixture. No live database, real models or product writes."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from governor_workbench.config import load_config
from governor_workbench.store import Store
from governor_workbench.registry import Registry
from governor_workbench.scopes import ScopeService
from governor_workbench.intake import Intake
from governor_workbench.intake_drafts import IntakeDrafts
from governor_workbench.plans import PlanBook

root=Path(__file__).resolve().parents[1]/'artifacts/strategy-preview'
root.mkdir(exist_ok=False)
repo=root/'fixture'; (repo/'project_memories').mkdir(parents=True)
(repo/'project_memories/note.md').write_text('# Synthetic acceptance fixture\nOnly test data.\n',encoding='utf-8')
for args in (['init','-q'],['add','.'],['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture']):
    subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
path=root/'config.json'
path.write_text(json.dumps(dict(version=1,port=8790,data_dir=str(root/'runtime'),projects=[dict(id='fixture',name='Strategie-Testprojekt',path=str(repo))])),encoding='utf-8')
cfg=load_config(path); store=Store(root/'runtime/journal.db')
for key in ('monitor_enabled','auto_review'): store.set_setting(key,False)
registry=Registry(store,cfg['projects'])
fields=dict(requirements='Synthetische Notiz prüfen.',test_strategy='Inhalt und Quellenhash vergleichen.',dependencies='Keine.',open_evidence='Keine echte Produktaussage.')
scope=ScopeService(registry,cfg)
context=scope.context('project','fixture',False)
IntakeDrafts(store).save(context,context['scope_hash'],'fixture',fields,[{k:m[k] for k in ('name','sha256')} for m in context['projects'][0]['memories']])
Intake(store).accept(context,context['scope_hash'],'fixture',fields)
context=scope.context('project','fixture',False)
proposal=dict(summary='Synthetische Prüfstrategie',steps=[dict(id='inspect',title='Quellenstand prüfen',project_id='fixture',priority=1,depends_on=[],rationale='Voraussetzung vor Folgeprüfung.',scope=['project_memories/note.md'],tests=['Notiz auf erwarteten Inhalt prüfen.'],action='review'),dict(id='follow',title='Folgebefund dokumentieren',project_id='fixture',priority=2,depends_on=['inspect'],rationale='Benötigt geprüften Quellenstand.',scope=['project_memories/note.md'],tests=['Ergebnis mit vorheriger Prüfung abgleichen.'],action='review')])
review=dict(summary='Synthetischer Fixture-Review; kein Modellaufruf.',decision='REVIEW_ONLY',findings=[],required_evidence=[])
job=store.create_job('scope_plan',None)
candidate=PlanBook(store).save_candidate(context,proposal,review,job['id'])
store.update_job(job['id'],status='completed',result=dict(candidate=candidate,proposal=proposal,review=review,scope_hash=context['scope_hash'],review_scope=context['review_scope'],plan_ready=True,stale=False))
print(path)
