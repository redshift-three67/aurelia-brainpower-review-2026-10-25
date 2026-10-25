
import { prepareFocusImage } from "./context-image.js";

export function initPersonalContext(api, saveBtn) {
  const fields = {firstName:"case-first-name",lastName:"case-last-name",birthDate:"case-birth-date",place:"case-place",placeKind:"case-place-kind"};
  const inputs = Object.fromEntries(Object.entries(fields).map(([key,id])=>[key,document.getElementById(id)]));
  const placeLabel=document.getElementById("case-place-label");
  const placeHelp=document.getElementById("case-place-help");
  function describePlace(changed=false) {
    const kind=inputs.placeKind.value;
    placeLabel.textContent=kind==="birth"?"Geburtsort":kind==="residence"?"Wohn-/Aufenthaltsort":"Bisheriger Ort (Typ nicht festgelegt)";
    const explanation=kind==="birth"
      ?"Geburtsort ist aktiv; Wohn-/Aufenthaltsort ist inaktiv. Im persönlichen Verfahren und im separaten EXP1-Vergleich wird der Geburtsort nur zusammen mit dem Geburtsdatum berücksichtigt."
      :kind==="residence"
        ?"Wohn-/Aufenthaltsort ist aktiv; Geburtsort ist inaktiv. Dieser Ort bleibt Kontext und wird nicht als Geburtsort berechnet."
        :"Die Bedeutung des bisher gespeicherten Orts ist nicht festgelegt. Er wird nicht als Geburtsort berechnet. Zum Festlegen einen Ortstyp wählen und den Ort neu eingeben.";
    placeHelp.textContent=(changed?"Ortstyp gewechselt: Bitte den Ort neu eingeben und den Fall speichern. ":"")+explanation+" Frühere Aufträge bleiben unverändert; im Originalmodus verändern diese Angaben keine Analysewerte.";
  }
  const file=document.getElementById("case-image-file");
  const select=document.getElementById("case-image-select");
  const remove=document.getElementById("case-image-remove");
  const preview=document.getElementById("case-image-preview");
  const status=document.getElementById("case-image-status");
  const contextStatus=document.getElementById("case-context-status");
  let baseline={}, image=null, staged=null, sequence=0, preparing=false, saving=false, conflicted=false;
  const today=new Date();
  inputs.birthDate.max=[today.getFullYear(),String(today.getMonth()+1).padStart(2,"0"),String(today.getDate()).padStart(2,"0")].join("-");
  function controls() {
    select.disabled=saving||preparing;
    remove.disabled=saving||preparing||!image;
    file.disabled=saving||preparing;
    for(const input of Object.values(inputs)) input.disabled=saving;
    saveBtn.disabled=saving||preparing||conflicted;
  }
  function showPreview(src) {
    preview.onload=()=>{preview.hidden=false;};
    preview.onerror=()=>{preview.hidden=true;status.textContent="Bildreferenz vorhanden; Vorschau in dieser Instanz nicht verfügbar.";};
    if(src) {preview.src=src;preview.hidden=false;}
    else {preview.removeAttribute("src");preview.hidden=true;}
  }
  function invalidate() {
    sequence+=1; conflicted=true;
    status.textContent="Fallkontext wurde während des Speicherns geändert. Eingaben bleiben erhalten; bitte Fall neu laden.";
    controls();
  }
  function hydrate(data={}, ownSave=false) {
    if(saving&&!ownSave){invalidate();return false;}
    conflicted=false;
    sequence+=1; preparing=false; staged=null;
    const personal=data.personalContext||{};
    baseline=Object.fromEntries(Object.keys(fields).map(key=>[key,typeof personal[key]==="string"?personal[key]:""]));
    if(!data.name) baseline.placeKind="residence";
    for(const [key,input] of Object.entries(inputs)) input.value=baseline[key];
    describePlace();
    image=personal.image&&typeof personal.image==="object"?personal.image:null;
    baseline.image=image;
    showPreview(image?api.contextImageUrl(image.sha256):null);
    status.textContent=image?"Fokusbild lokal gespeichert.":"Kein Fokusbild gewählt.";
    contextStatus.textContent=data.caseId
      ? "Kontextversion "+data.contextVersion+". Änderungen gelten nur für neue Aufträge; frühere Sitzungen behalten ihren Stand."
      : "Älterer Fall ohne feste Kontextversion. Beim bewussten Speichern wird eine Fall-ID ergänzt; alte Sitzungen bleiben unverändert.";
    file.value=""; controls();
  }
  inputs.placeKind.addEventListener("change",()=>{
    if(saving){invalidate();return;}
    if(!["residence","birth"].includes(inputs.placeKind.value)) return;
    inputs.place.value="";
    describePlace(true);
    inputs.place.focus();
  });
  select.addEventListener("click",()=>file.click());
  file.addEventListener("change",async()=>{
    const selected=file.files?.[0];file.value="";
    if(!selected||saving) return;
    const ticket=++sequence;preparing=true;controls();
    status.textContent="Fokusbild wird lokal geprüft …";
    try {
      const result=await prepareFocusImage(selected);
      if(ticket!==sequence) return;
      staged=result;image=result.image;showPreview(result.previewUrl);
      status.textContent="Fokusbild vorbereitet. Erst beim Fall-Speichern wird es lokal abgelegt.";
    } catch(_) {
      if(ticket===sequence) status.textContent="Bild konnte nicht aufbereitet werden. Bitte gültiges PNG, JPEG oder WebP bis 5 MB wählen; das bisherige Bild bleibt erhalten.";
    } finally {
      if(ticket===sequence){preparing=false;controls();}
    }
  });
  remove.addEventListener("click",()=>{
    if(saving||preparing) return;
    sequence+=1;staged=null;image=null;showPreview(null);
    status.textContent="Fokusbild entfernt vorgemerkt. Bitte Fall speichern.";controls();
  });
  return {
    hydrate,
    invalidate,
    bindingToken(){return sequence;},
    assertBinding(ticket){
      if(ticket!==sequence||conflicted) throw new Error("Fallkontext wurde geändert. Die Speicherantwort wird nicht übernommen; bitte Fall neu laden.");
    },
    get preparing(){return preparing;},
    setSaving(value){saving=value;controls();},
    validate(){
      for(const input of Object.values(inputs)) if(!input.checkValidity()){
        input.reportValidity();input.focus();return false;
      }
      return true;
    },
    async payload(isNew){
      if(conflicted) throw new Error("Fallkontext wurde geändert. Bitte Fall neu laden.");
      const ticket=sequence, candidate=staged;
      const changes={};
      for(const [key,input] of Object.entries(inputs)) if(isNew||input.value!==baseline[key]) changes[key]=input.value||null;
      if(inputs.placeKind.value!==baseline.placeKind) changes.place=inputs.place.value||null;
      if(candidate) {
        const saved=await api.uploadContextImage({pngBase64:candidate.pngBase64});
        if(ticket!==sequence||conflicted) throw new Error("Fallkontext wurde geändert. Bitte Fall neu laden.");
        if(["sha256","mediaType","byteLength"].some(key=>saved.image?.[key]!==candidate.image[key])) throw new Error("Bildreferenz stimmt nicht überein. Bitte Bild erneut wählen.");
        image=saved.image;
      }
      if(isNew||JSON.stringify(image)!==JSON.stringify(baseline.image)) changes.image=image;
      return changes;
    }
  };
}

