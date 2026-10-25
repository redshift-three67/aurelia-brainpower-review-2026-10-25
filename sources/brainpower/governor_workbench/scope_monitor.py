"""One local scope observation per tick; no model calls or automatic planning.

The owner supplies a read-only observer callback. A separate tick lock prevents
overlapping callbacks; cached summaries remain readable while observation runs.
"""
import copy
import threading

from .evidence import now


MAX_SCOPES = 100
_ERROR = 'Beobachtung fehlgeschlagen; letzter bekannter Stand ist veraltet.'


class ScopeMonitor:
    def __init__(self, registry, observe_callback):
        if not callable(observe_callback):
            raise ValueError('Lesende Beobachtungsfunktion erforderlich.')
        self.registry = registry
        self.observe_callback = observe_callback
        self._tick_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._order = []
        self._rotation = []
        self._records = {}

    def _catalog(self):
        # A group remains scheduled when its members are archived or missing;
        # its observer must report incomplete evidence instead of omitting it.
        candidates = [('group', group['id']) for group in self.registry.list_groups()
                      if not group.get('archived')]
        candidates.extend(('project', project['id']) for project in self.registry.list_projects()
                          if not project.get('archived') and not project.get('group_id'))
        result = []
        seen = set()
        for kind, key in candidates:
            if not isinstance(key, str) or not 1 <= len(key) <= 64:
                raise ValueError('Ungültiger registrierter Scope.')
            if (kind, key) not in seen:
                result.append((kind, key))
                seen.add((kind, key))
                if len(result) == MAX_SCOPES:
                    break
        return result

    @staticmethod
    def _summary(context):
        if not isinstance(context, dict):
            raise ValueError('Beobachtung lieferte keinen Kontext.')
        source_hash = context.get('scope_hash')
        if not isinstance(source_hash, str) or not 1 <= len(source_hash) <= 128:
            raise ValueError('Beobachtung lieferte keinen begrenzten Quellenhash.')
        intake = context.get('intake')
        if not isinstance(intake, list) or len(intake) > 50 or type(context.get('plan_ready')) is not bool:
            raise ValueError('Beobachtung lieferte keine begrenzte Projektaufnahme.')
        summaries = []
        for item in intake:
            if not isinstance(item, dict) or not isinstance(item.get('project_id'), str):
                raise ValueError('Ungültige Projektaufnahme.')
            row = {'project_id': item['project_id'][:64]}
            for key in ('requirements_recorded', 'memories_present', 'evidence_complete', 'intake_accepted'):
                if key in item:
                    row[key] = item[key] is True
            warnings = item.get('missing_proofs', [])
            if not isinstance(warnings, list):
                raise ValueError('Ungültige Nachweisliste.')
            row['missing_proofs'] = [warning[:500] for warning in warnings[:20] if isinstance(warning, str)]
            row['missing_proofs_truncated'] = len(warnings) > 20
            summaries.append(row)
        return dict(scope_hash=source_hash, plan_ready=context['plan_ready'], intake=summaries)

    def tick(self):
        """Observe at most one scope; return its summary, or None if skipped."""
        if not self._tick_lock.acquire(blocking=False):
            return None
        try:
            try:
                order = self._catalog()
            except Exception:
                with self._state_lock:
                    for record in self._records.values():
                        record.update(error=_ERROR, stale=True, attempted_at=now())
                return None
            with self._state_lock:
                available = set(order)
                self._records = {key: value for key, value in self._records.items() if key in available}
                # Preserve the pending turn of surviving scopes. New scopes join
                # the rotation once, so changing membership cannot reset fairness.
                self._rotation = [key for key in self._rotation if key in available]
                queued = set(self._rotation)
                self._rotation.extend(key for key in order if key not in queued)
                self._order = order
                for kind, key in order:
                    self._records.setdefault((kind, key), dict(kind=kind, id=key,
                        observed_at=None, attempted_at=None, scope_hash=None,
                        plan_ready=False, intake=[], error=None, stale=True))
                if not self._rotation:
                    return None
                selected = self._rotation.pop(0)
                self._rotation.append(selected)
            # Neither source IO nor callback code runs under the summary lock.
            try:
                summary = self._summary(self.observe_callback(*selected))
            except Exception:
                summary = None
            checked_at = now()
            with self._state_lock:
                record = self._records[selected]
                if summary is None:
                    record.update(error=_ERROR, stale=True, attempted_at=checked_at)
                else:
                    record.update(summary, observed_at=checked_at, attempted_at=checked_at,
                                  error=None, stale=False)
                return copy.deepcopy(record)
        finally:
            self._tick_lock.release()

    def state(self):
        """Return only bounded cached data in registration order, without IO."""
        with self._state_lock:
            return [copy.deepcopy(self._records[key]) for key in self._order]
