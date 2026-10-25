export function modeLabel(mode) { return mode === 'experimental' ? 'Experimentalvergleich' : 'Original'; }
export function resultRows(job) {
  return (job?.result?.results || []).map(row => {
    const source = job.originalSubset?.[row.originalIndex] || {};
    return {rate: row.rate, originalEW: source.energeticValue ?? null, originalGV: source.gv ?? null,
      score: row.score, intensity: row.intensity, originalIndex: (job.pageStart || 0) + row.originalIndex};
  });
}
const LABELS = {queued:'Wartet', running:'Berechnet', completed:'Abgeschlossen', failed:'Fehlgeschlagen', cancelled:'Abgebrochen', interrupted:'Unterbrochen'};
export function initExperimentalComparison(api, eventBus) {
  const get = id => document.getElementById('comparison-' + id);
  const mode=get('mode'), panel=get('panel'); if (!mode || !panel) return;
  const source=get('source'), page=get('page'), weight=get('weight'), start=get('start'), refresh=get('refresh');
  const status=get('status'), body=get('result-body'), history=get('history'), cancel=get('cancel'), retry=get('retry'), proof=get('proof'), reconcile=get('reconcile');
  let epoch=0, binding=null, sources=[], jobs=[], current=null, capability=null, pending=null, busy=false, timer=null;
  const timeout=()=>AbortSignal.timeout(10000);
  const pendingKey=caseId=>'radiworks.experimental.pending.v1.'+caseId;
  function savePending(){if(!binding)return;try{if(pending)sessionStorage.setItem(pendingKey(binding.caseId),JSON.stringify(pending));else sessionStorage.removeItem(pendingKey(binding.caseId));}catch(error){/* Server idempotency remains authoritative if browser storage is unavailable. */}}
  function restorePending(){try{const saved=JSON.parse(sessionStorage.getItem(pendingKey(binding.caseId)) || 'null');if(saved && ['start','cancel','retry'].includes(saved.kind) && /^[0-9a-f]{32}$/.test(saved.body?.request_id) && saved.caseId===binding.caseId){pending=saved;pending.body.expected_case_ref=binding.ref;}}catch(error){pending=null;}}
  const isActive=()=>mode.value==='experimental';
  const clearTimer=()=>{if(timer!==null)clearTimeout(timer);timer=null;};
  function controls() {
    const eligible=sources.find(s=>s.sessionId===source.value)?.eligible;
    start.disabled=busy || pending!==null || !capability?.configured || !binding || !eligible;
    source.disabled=busy || pending!==null;page.disabled=busy || pending!==null;weight.disabled=busy || pending!==null;refresh.disabled=busy;
    reconcile.hidden=pending===null;reconcile.disabled=busy;
    cancel.hidden=!current || !['queued','running'].includes(current.status);cancel.disabled=busy || pending!==null;
    retry.hidden=!current || !['failed','interrupted'].includes(current.status);retry.disabled=busy || pending!==null || !capability?.configured;
  }
  function pages() {
    const count=sources.find(s=>s.sessionId===source.value)?.rateCount || 0;
    page.replaceChildren();for(let i=0;i<count;i+=21){const o=new Option('Seite '+(i/21+1)+' · Raten '+(i+1)+'–'+Math.min(i+21,count),String(i));page.add(o);}
    controls();
  }
  function render(job) {
    current=job || null;body.replaceChildren();proof.textContent='';
    if(job){
      status.textContent=(LABELS[job.status] || 'Unbekannter Status')+' · eigener Auftrag '+job.id.slice(0,8)+(job.error?' · '+job.error.code:'');
      proof.textContent='Katalog: '+job.catalog.name+' · Seite '+(job.pageStart/21+1)+' · Gewichtung: '+job.weight+' · eigene Sitzung '+job.comparisonSessionId.slice(0,8)+' · eingefrorener Kontext '+job.contextDigest.slice(0,12)+' · '+job.formulaVersion;
      for(const row of resultRows(job)){
        const tr=document.createElement('tr');
        const values=[row.originalIndex+1,row.rate,row.originalEW ?? '—',row.originalGV ?? '—',Number.isFinite(row.score)?row.score.toFixed(6):'—',Number.isFinite(row.intensity)?row.intensity.toFixed(4):'—'];
        for(const value of values){const td=document.createElement('td');td.textContent=String(value);tr.append(td);}body.append(tr);
      }
    }
    history.replaceChildren();for(const item of jobs){const button=document.createElement('button');button.type='button';button.className='btn';button.textContent=(LABELS[item.status] || item.status)+' · '+item.id.slice(0,8);button.addEventListener('click',()=>{render(item);schedule();});history.append(button);}
    controls();
  }
  async function load(reset=false) {
    const token=++epoch;clearTimer();if(reset){mode.value='original';panel.hidden=true;binding=null;pending=null;current=null;jobs=[];render(null);}
    busy=true;controls();
    try {
      const active=await api.currentCaseWithRef(timeout());if(token!==epoch)return;
      if(!active.data?.caseId || !active.ref){binding=null;sources=[];jobs=[];status.textContent='Bitte zuerst einen Fall und eine neue Originalanalyse anlegen.';return;}
      const next={ref:active.ref,caseId:active.data.caseId};
      if(binding && binding.caseId!==next.caseId){mode.value='original';panel.hidden=true;current=null;pending=null;render(null);}
      binding=next;if(!pending)restorePending();else if(pending.caseId===binding.caseId){pending.body.expected_case_ref=binding.ref;savePending();}
      const values=await Promise.all([api.comparisonCapability(timeout()),api.comparisonSources(binding.ref,timeout()),api.comparisons(binding.ref,timeout())]);if(token!==epoch)return;
      capability=values[0];sources=values[1].sources;jobs=values[2].jobs;
      const previous=source.value;source.replaceChildren();for(const s of sources){const o=new Option('Originalsitzung '+(s.index+1)+(s.eligible?' · '+s.catalog:' · nicht vergleichbar'),s.sessionId);o.disabled=!s.eligible;source.add(o);}
      source.value=sources.some(s=>s.sessionId===previous && s.eligible)?previous:(sources.find(s=>s.eligible)?.sessionId || '');if(pending?.body.source_session_id)source.value=pending.body.source_session_id;pages();if(pending?.body.page_start!==undefined)page.value=String(pending.body.page_start);if(pending?.body.weight)weight.value=pending.body.weight;
      if(pending){const found=jobs.find(j=>j.requestId===pending.body.request_id);const cancelled=pending.kind==='cancel'?jobs.find(j=>j.id===pending.jobId && ['completed','failed','cancelled','interrupted'].includes(j.status)):null;if(found || cancelled){current=found || cancelled;pending=null;savePending();}}
      current=current?jobs.find(j=>j.id===current.id) || null:null;
      render(current);
      if(!current) status.textContent=!capability.configured?'Optionales CPU-Paket fehlt. Originalanalyse ist weiter nutzbar.':sources.some(s=>s.eligible)?'Quelle, Seite und Gewichtung wählen; Vergleich ausdrücklich starten.':'Keine belegte geeignete Quelle. Neue Originalanalyse mit vollständigem persönlichen Kontext verwenden.';
      if(pending)status.textContent='Annahme des Auftrags noch ungeklärt. Denselben Auftrag abgleichen; keine neue Request-ID verwenden.';
      schedule();
    } catch(error){if(token===epoch)status.textContent='Vergleichsstatus nicht erreichbar. Bitte aktualisieren; kein Auftrag wird automatisch wiederholt.';}
    finally{if(token===epoch){busy=false;controls();}}
  }
  function schedule() {
    clearTimer();if(!isActive() || !current || !['queued','running'].includes(current.status))return;
    const token=epoch, identifier=current.id, reference=binding.ref;
    timer=setTimeout(async()=>{try{const job=await api.comparison(identifier,reference,timeout());if(token!==epoch)return;const i=jobs.findIndex(j=>j.id===job.id);if(i>=0)jobs[i]=job;if(current?.id!==identifier)return;render(job);schedule();}catch(error){if(token===epoch)status.textContent='Statusabfrage unterbrochen. Aktualisieren gleicht den gespeicherten Auftrag ab.';}},1500);
  }
  async function command(kind) {
    if(busy || !binding)return;const token=epoch, reference=binding.ref;busy=true;controls();clearTimer();
    if(kind==='reconcile' && !pending){busy=false;controls();return;}
    if(kind!=='reconcile'){
      const requestId=crypto.randomUUID().replaceAll('-','');
      const payload={expected_case_ref:reference,request_id:requestId};
      if(kind==='start')Object.assign(payload,{source_session_id:source.value,page_start:Number(page.value),weight:weight.value});
      pending={kind,body:payload,jobId:current?.id || null,caseId:binding.caseId};savePending();
    }
    const outstanding=pending;
    try{
      let job;
      if(outstanding.kind==='start')job=await api.startComparison(outstanding.body,timeout());
      else if(outstanding.kind==='cancel')job=await api.cancelComparison(outstanding.jobId,outstanding.body,timeout());
      else job=await api.retryComparison(outstanding.jobId,outstanding.body,timeout());
      if(token!==epoch)return;pending=null;savePending();const i=jobs.findIndex(j=>j.id===job.id);if(i>=0)jobs[i]=job;else jobs.unshift(job);render(job);schedule();
    }catch(error){if(token===epoch){if(kind!=='reconcile' && [400,404,409,422,503].includes(error.status)){pending=null;savePending();}status.textContent='Antwort fehlt oder Auftrag abgelehnt. Bitte Status aktualisieren oder denselben Auftrag abgleichen; nicht neu starten.';}}
    finally{if(token===epoch){busy=false;controls();}}
  }
  mode.value='original';panel.hidden=true;
  mode.addEventListener('change',()=>{panel.hidden=!isActive();clearTimer();if(isActive())load();});
  source.addEventListener('change',pages);start.addEventListener('click',()=>command('start'));cancel.addEventListener('click',()=>command('cancel'));retry.addEventListener('click',()=>command('retry'));refresh.addEventListener('click',()=>load());reconcile.addEventListener('click',()=>command('reconcile'));
  eventBus.addEventListener('case.changed',()=>load(true));eventBus.addEventListener('analysis.context',()=>{if(isActive())load();});
  eventBus.addEventListener('server.restarted',()=>{if(isActive())load();});
  controls();
}
