"""In-memory trial states, not durable evidence or OS process ownership."""
from .validation import ContractError, validate_context, _ID


def authorize_analysis(context, approved, authority, now):
    validate_context(context, approved, now)
    if authority.allows(context['tenant_id'], context['actor_id'], context['audience'],
                        context['operation'], context['authorization_revision']) is not True:
        raise ContractError('forbidden')


class TrialSlot:
    def __init__(self):
        self.state = 'idle'
        self.request_id = None
        self.outcome = None

    def reserve(self, request_id):
        if self.state != 'idle':
            raise ContractError('recovery_required' if self.state == 'unknown' else 'busy')
        if type(request_id) is not str or not _ID.fullmatch(request_id):
            raise ContractError('invalid_request')
        self.request_id, self.outcome, self.state = request_id, None, 'reserved'

    def start(self):
        if self.state != 'reserved':
            raise ContractError('state_conflict')
        self.state = 'running'

    def request_abort(self):
        if self.state != 'running':
            raise ContractError('state_conflict')
        self.state = 'abort_requested'

    def finish(self, outcome):
        if (self.state not in ('running', 'abort_requested')
                or outcome not in ('succeeded', 'failed', 'aborted')
                or self.state == 'abort_requested' and outcome == 'succeeded'):
            raise ContractError('state_conflict')
        self.outcome, self.state = outcome, 'idle'

    def lose_observation(self):
        if self.state != 'idle':
            self.state = 'unknown'
