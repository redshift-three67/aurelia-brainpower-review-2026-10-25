/* Capture the displayed case selection; never refresh it silently at submission. */
export function caseJobGuard(selection) {
  if (selection === null || selection === undefined) {
    return {expected_case_ref:null, expected_context_version:null};
  }
  if (!/^[0-9a-f]{64}$/.test(selection.ref || '') ||
      (selection.contextVersion !== null && (!Number.isInteger(selection.contextVersion) || selection.contextVersion < 1))) {
    throw new Error('Fallbindung ungültig. Bitte Fall erneut laden.');
  }
  return {expected_case_ref:selection.ref, expected_context_version:selection.contextVersion};
}

export function analysisJobOrigin(draftId, sessionId) {
  if (typeof draftId === 'string' && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(draftId)) {
    return {source_draft_id:draftId};
  }
  if (typeof sessionId === 'string' && /^[0-9a-f]{32}$/.test(sessionId)) {
    return {source_session_id:sessionId};
  }
  throw new Error('Analyseherkunft fehlt. Bitte die gespeicherte Sitzung erneut laden.');
}
