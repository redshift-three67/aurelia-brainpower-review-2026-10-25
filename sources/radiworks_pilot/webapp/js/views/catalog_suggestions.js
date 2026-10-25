/* Explicit lexical suggestions are a selection aid, never an analysis command. */
export function initCatalogSuggestions(api, eventBus, chooseConfirmed) {
  const topics = document.getElementById("db-suggestion-topics");
  const useFocus = document.getElementById("db-suggestion-use-focus");
  const start = document.getElementById("db-suggest-btn");
  const status = document.getElementById("db-suggestion-status");
  const list = document.getElementById("db-suggestion-list");
  const selected = document.getElementById("db-select");
  let revision = 0, controller = null, applying = false;
  function busy(value) {
    start.disabled = value;
    list.querySelectorAll("button").forEach((button) => { button.disabled = value; });
  }
  function invalidate() {
    if (applying) return;
    revision++;
    controller?.abort();
    list.replaceChildren(); list.hidden = true; busy(false);
    status.textContent = "Auswahl oder Suchkontext geändert. Bei Bedarf Vorschläge neu anfordern.";
  }
  topics.addEventListener("input", invalidate);
  useFocus.addEventListener("change", invalidate);
  selected.addEventListener("change", invalidate);
  eventBus.addEventListener("case.changed", invalidate);
  document.getElementById("db-search").addEventListener("input", invalidate);
  for (const button of document.querySelectorAll(".cat-btn, #db-search-clear, #db-focus-search")) {
    button.addEventListener("click", invalidate);
  }
  function begin() {
    controller?.abort(); controller = new AbortController();
    return {ticket: ++revision, signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15000)])};
  }
  function validProposal(result, body) {
    return result?.ruleVersion === "catalog-lexical-v1"
      && result.caseRef === body.expected_case_ref && result.contextVersion === body.expected_context_version
      && /^[0-9a-f]{64}$/.test(result.catalogSnapshotDigest)
      && Array.isArray(result.queryTerms) && result.queryTerms.length <= 12
      && result.queryTerms.every((term) => typeof term === "string")
      && Number.isInteger(result.catalogWarnings?.utf8ReplacementFiles) && result.catalogWarnings.utf8ReplacementFiles >= 0
      && Number.isInteger(result.totalMatches) && result.totalMatches >= 0
      && Array.isArray(result.suggestions) && result.suggestions.length <= 8
      && result.suggestions.every((item) => typeof item.name === "string"
        && /^catalog-[0-9a-f]{64}$/.test(item.catalogId) && /^catalog-[0-9a-f]{64}$/.test(item.exactId) && item.selector === item.exactId && !/[\\/]/.test(item.name)
        && [item.nameTerms,item.groupTerms,item.rateTerms].every((terms) => Array.isArray(terms)
          && terms.every((term) => result.queryTerms.includes(term)))
        && Number.isInteger(item.matchedRateCount) && item.matchedRateCount >= 0);
  }
  async function confirm(item, proposal, body) {
    const {ticket,signal} = begin(); busy(true);
    status.textContent = "Vorschlag und Katalog werden vor der Auswahl erneut geprüft …";
    try {
      const result = await api.confirmDatabaseSuggestion({...body,
        catalogSnapshotDigest: proposal.catalogSnapshotDigest, selector: item.selector}, signal);
      if (ticket !== revision) return;
      if (result.selector !== item.selector || result.catalogId !== item.catalogId || result.exactId !== item.exactId || result.name !== item.name
          || result.catalogSnapshotDigest !== proposal.catalogSnapshotDigest
          || result.ruleVersion !== proposal.ruleVersion) throw new Error("Vorschlagsbindung fehlt. Bitte neu anfordern.");
      applying = true;
      try { chooseConfirmed(result); } finally { applying = false; }
      list.replaceChildren(); list.hidden = true;
      status.textContent = "Einzeldatenbank „" + item.name + "“ gewählt. Eine Analyse startet erst mit „Analyse starten“.";
    } catch (error) {
      if (ticket !== revision) return;
      list.replaceChildren(); list.hidden = true;
      status.textContent = "Auswahl nicht übernommen: " + (error.name === "TimeoutError" ? "Zeitüberschreitung; bitte neu anfordern." : error.message);
    } finally { if (ticket === revision) busy(false); }
  }
  start.addEventListener("click", async () => {
    const {ticket,signal} = begin();
    const requestedTopics = topics.value, requestedFocus = useFocus.checked;
    list.replaceChildren(); list.hidden = true; busy(true);
    status.textContent = "Worttreffer im aktuellen Katalog werden geprüft …";
    try {
      const current = await api.currentCaseWithRef(signal);
      if (ticket !== revision) return;
      const body = {topics: requestedTopics, use_focus: requestedFocus,
        expected_case_ref: current.ref || null, expected_context_version: current.data.contextVersion || null, limit: 8};
      const result = await api.databaseSuggestions(body, signal);
      if (ticket !== revision) return;
      if (!validProposal(result,body)) throw new Error("Vorschlagsbindung fehlt. Bitte neu anfordern.");
      status.textContent = result.queryTerms.length
        ? result.totalMatches + " Datenbanken mit Worttreffern; höchstens acht Vorschläge. Suchwörter: " + result.queryTerms.join(", ") + "."
        : "Keine nutzbaren Suchwörter. Bitte Fokus speichern oder Themen eingeben.";
      if (result.catalogWarnings.utf8ReplacementFiles) {
        status.textContent += " Hinweis: " + result.catalogWarnings.utf8ReplacementFiles
          + " Datenbanken enthalten ersetzte UTF-8-Zeichen wie im Originalleser; einzelne Worttreffer können fehlen.";
      }
      for (const item of result.suggestions) {
        const row = document.createElement("li");
        const name = document.createElement("strong"); name.textContent = item.name;
        const reasons = document.createElement("p"); reasons.className = "hint";
        const parts = [];
        if (item.nameTerms.length) parts.push("Name: " + item.nameTerms.join(", "));
        if (item.groupTerms.length) parts.push("Gruppe: " + item.groupTerms.join(", "));
        if (item.rateTerms.length) parts.push("Rateninhalt: " + item.rateTerms.join(", ") + " (" + item.matchedRateCount + " Zeilen)");
        reasons.textContent = parts.join(" · ");
        const button = document.createElement("button"); button.type = "button"; button.className = "btn";
        button.textContent = "Datenbank wählen"; button.setAttribute("aria-label", "Datenbank wählen: " + item.name);
        button.dataset.selector = item.selector; button.addEventListener("click", () => confirm(item,result,body));
        row.append(name,reasons,button); list.append(row);
      }
      list.hidden = !result.suggestions.length;
    } catch (error) {
      if (ticket !== revision) return;
      status.textContent = "Vorschläge nicht verfügbar: " + (error.name === "TimeoutError" ? "Zeitüberschreitung; bitte erneut anfordern." : error.message)
        + " Die manuelle Namenssuche bleibt verfügbar.";
    } finally { if (ticket === revision) busy(false); }
  });
}
