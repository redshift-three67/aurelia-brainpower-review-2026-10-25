"""Scope-partitionierte Arbeitsbereiche für Case-, Draft- und Recovery-Daten."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from .core.cases import CaseStore
from .core.draft import DraftStore
from .persistence import RecoveryCoordinator
from .scope import ScopeContext


@dataclass
class WorkflowWorkspace:
    scope: ScopeContext
    case_store: CaseStore
    draft_store: DraftStore
    journal_dir: Path
    recovery: RecoveryCoordinator


class WorkflowRegistry:
    """Erzeugt je immutable ScopeContext einen isolierten Workflow-Workspace."""

    def __init__(self, base_dir: Path, cases_dir: Path, drafts_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._cases_dir = Path(cases_dir)
        self._drafts_dir = Path(drafts_dir)
        self._workspaces: dict[ScopeContext, WorkflowWorkspace] = {}
        self._lock = RLock()

    @staticmethod
    def _scope_root(root: Path, scope: ScopeContext) -> Path:
        return root / "scopes" / scope.tenant_id / scope.client_id / scope.job_id

    def workspace(self, scope: ScopeContext) -> WorkflowWorkspace:
        with self._lock:
            existing = self._workspaces.get(scope)
            if existing is not None:
                return existing
            cases = self._scope_root(self._cases_dir, scope)
            drafts = self._scope_root(self._drafts_dir, scope)
            journals = self._scope_root(self._base_dir / "entropy_journals", scope)
            recovery_root = self._scope_root(self._base_dir / "recovery", scope)
            workspace = WorkflowWorkspace(
                scope=scope,
                case_store=CaseStore(cases, scope=scope),
                draft_store=DraftStore(drafts, scope=scope),
                journal_dir=journals,
                recovery=RecoveryCoordinator(
                    recovery_root,
                    stores={"case": cases, "draft": drafts},
                ),
            )
            workspace.recovery.recover()
            self._workspaces[scope] = workspace
            return workspace
