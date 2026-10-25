import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from governor_workbench.store import Store
from governor_workbench.registry import Registry
from governor_workbench.scopes import ScopeService
from governor_workbench.vault import Vault
from governor_workbench.intake import Intake


class ScopedVaultDriftTests(unittest.TestCase):
    def test_changed_vault_requirements_invalidate_intake(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); repo=root/'repo'; (repo/'project_memories').mkdir(parents=True)
            (repo/'project_memories/strategy.md').write_text('Known goal')
            for args in (['init','-q'],['add','.'],['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture']):
                subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
            vaultroot=root/'vault'; vaultroot.mkdir(); source=vaultroot/'requirements.md'; source.write_text('Requirements v1')
            store=Store(root/'runtime/journal.db'); registry=Registry(store,[])
            project=registry.register('Demo',str(repo),True,'Explicit goal')
            vault=Vault(registry,root/'runtime',vaultroot); vault.map_source('project',project['id'],str(source),True)
            service=ScopeService(registry,{'data_dir':str(root/'runtime'),'projects':[],'git_interval':60,'vault_root':str(vaultroot)})
            context=service.context('project',project['id'])
            fields=dict(requirements='v1',test_strategy='Unit test',dependencies='None',open_evidence='No runtime claim')
            Intake(store).accept(context,context['scope_hash'],project['id'],fields)
            self.assertTrue(service.context('project',project['id'])['plan_ready'])
            source.write_text('Requirements v2')
            changed=service.context('project',project['id'])
            self.assertFalse(changed['plan_ready'])
            self.assertFalse(changed['intake'][0]['intake_accepted'])
