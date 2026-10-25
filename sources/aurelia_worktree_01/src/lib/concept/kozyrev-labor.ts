export type LaborVorbereiten = "ja, Kern" | "ja, Labor" | "nein";
export type LaborLock = "gesetzt" | "gesperrt";
export type SchalterDefault = "an" | "aus" | "—";

export type LaborRow = {
  id: string;
  stueck: string;
  vorbereiten: LaborVorbereiten;
  destabilisiert: string;
  regel: string;
  lock: LaborLock;
  schalter: string;
  defaultOn: SchalterDefault;
  braucht: string;
};

/**
 * Recheck 2026-08-23 after operator lock of K1–K5.
 * Destabilisation = breaks C01/C03/D01/D20 or 20-client isolation.
 * Admin switches are AND-chain platform → tenant → session, fail-closed.
 */
export const KOZYREV_OPTIONAL: LaborRow[] = [
  {
    id: "K1",
    stueck: "kozyrev.padic.haar.v1 (p=2 Haar-DWT, optional Vladimirov)",
    vorbereiten: "ja, Kern",
    destabilisiert:
      "Nein. Lehrbuch-DSP, O(N), CPU für N≤2048, CUDA nur Batch im 16-GB-Pool. Abschalten entfernt nur den Katalogeintrag, nicht Radi144/Works.",
    regel: "D19, C09, D22. Dual-Modus. UI: Rechenmodell, kein Physikbeweis.",
    lock: "gesetzt",
    schalter: "kernel.kozyrev.padic.haar.v1",
    defaultOn: "an",
    braucht: "—",
  },
  {
    id: "K2",
    stueck: "kozyrev.reg.v1 (Rausch-/REG-Index)",
    vorbereiten: "ja, Labor",
    destabilisiert:
      "Nein, solange Default aus, Quelle immer simulated/derived und nie still mit Haar in einem Passport vermischt. CPU, kein Transformer.",
    regel: "C10, U05, D22. CopyGuard auf Text. Zwei Kernel-IDs, falls je zusammen gelistet.",
    lock: "gesetzt",
    schalter: "kernel.kozyrev.reg.v1",
    defaultOn: "aus",
    braucht: "Labor- oder Forschungsmandant",
  },
  {
    id: "K3",
    stueck: "Labor-ABI-Slot kozyrev.lab.* (executable: false, VRAM-Admit)",
    vorbereiten: "ja, Labor",
    destabilisiert:
      "Nein. Leere Verträge und Tests. Der Schalter öffnet keinen PyTorch-Worker — executable bleibt false, bis ein späteres Gate das ausdrücklich ändert.",
    regel: "D22, D23. Kein Image-Ballast. Labor-Quota kann 0 sein.",
    lock: "gesetzt",
    schalter: "capability.kozyrev.lab",
    defaultOn: "aus",
    braucht: "executable: false (hart)",
  },
  {
    id: "K4",
    stueck: "p=3/5-Filterbänke (eigene IDs, nicht Haar-v1)",
    vorbereiten: "ja, Labor",
    destabilisiert:
      "Nein. Weiter Filterbank, nicht Transformer. Eigene Kernel-IDs, eigenes Admit, Default aus. Schwerer als Haar, aber im selben Budget-Modell.",
    regel: "U04, D22. Haar bleibt das p-adische v1.",
    lock: "gesetzt",
    schalter: "kernel.kozyrev.padic.p3.v1 / p5.v1",
    defaultOn: "aus",
    braucht: "K1-Katalog darf unabhängig bleiben",
  },
  {
    id: "K5",
    stueck: "p-adische DSP auf HRV-RR (Ohrclip)",
    vorbereiten: "ja, Kern",
    destabilisiert:
      "Nein. 1D, kleine N, billig. Kein EEG. CopyGuard blockt Stress-/Schlaflesart. Läuft nicht, wenn K1 oder der Clip-Grant fehlt.",
    regel: "D21, D22. Quelle measured nur bei Clip-ACK, sonst derived/not-available.",
    lock: "gesetzt",
    schalter: "capability.kozyrev.padic.on_hrv_rr",
    defaultOn: "aus",
    braucht: "K1 an + Clip-Grant (D21)",
  },
  {
    id: "K6",
    stueck: "3-Tier: c2-Autoencoder + TRI-LSTM + Morphic-Transformer auf der Ada",
    vorbereiten: "nein",
    destabilisiert:
      "Ja. Frisst den 16-GB-Job-Pool, widerspricht C01, macht Analyse von 20 Klienten zur Restgröße. Auch „nur vorbereiten“ zieht Modelle in den Kern.",
    regel: "X05 bleibt Ihre Pause. Kein Kernel-ID, kein Schalter, kein Scaffold.",
    lock: "gesperrt",
    schalter: "— (existiert nicht)",
    defaultOn: "—",
    braucht: "nicht vorgesehen",
  },
  {
    id: "K7",
    stueck: "XGBoost-Heilmittel, Time-to-Zero, Meridian-Sequenzen als Outcome",
    vorbereiten: "nein",
    destabilisiert: "Ja, rechtlich. HWG/D01. Ein vorbereiteter Reportpfad leckt in die UI.",
    regel: "X07. Kein Schalter. CopyGuard würde blocken — nicht als Feature anbieten.",
    lock: "gesperrt",
    schalter: "— (existiert nicht)",
    defaultOn: "—",
    braucht: "nicht vorgesehen",
  },
  {
    id: "K8",
    stueck: "GPS-PPS als c2-Messung, Petrov, Weltenformel, RT-Core-Spiralen",
    vorbereiten: "nein",
    destabilisiert: "Ja. Falsche Quelle im Passport oder nutzloser VRAM. ID reservieren wäre schon ein Claim.",
    regel: "C11, X06/X08/X13. PPS bleibt Uhr. Kein Schalter.",
    lock: "gesperrt",
    schalter: "— (existiert nicht)",
    defaultOn: "—",
    braucht: "nicht vorgesehen",
  },
];

export const KOZYREV_GESETZT = KOZYREV_OPTIONAL.filter((r) => r.lock === "gesetzt");
export const KOZYREV_GESPERRT = KOZYREV_OPTIONAL.filter((r) => r.lock === "gesperrt");

export const KOZYREV_URTEIL = {
  kurz: "K1–K5 gesetzt, administrativ schaltbar. K6–K8 gesperrt, kein Schalter.",
  lang: "Zweite Prüfung: Haar-DSP, REG, leerer Labor-Slot, p=3/5 und Haar-auf-HRV destabilisieren den Kern nicht, wenn sie fail-closed schaltbar sind und Default nur bei K1 an ist. Autoencoder/LSTM/Transformer, Heilmittel-Ranking und PPS-als-c2 bleiben draußen — dafür gibt es bewusst keinen Schalter.",
};

export type SchalterRow = {
  id: string;
  key: string;
  defaultOn: SchalterDefault;
  kette: string;
  ausWirkung: string;
};

export const KOZYREV_SCHALTER: SchalterRow[] = [
  {
    id: "S0",
    key: "Kette",
    defaultOn: "—",
    kette: "platform AND tenant AND session, fehlendes Flag = aus, Audit wer/wann/scope",
    ausWirkung: "Admit weist kernel_id zurück. UI blendet den Eintrag aus. Kein stiller Fallback.",
  },
  {
    id: "K1",
    key: "kernel.kozyrev.padic.haar.v1",
    defaultOn: "an",
    kette: "Superadmin kann global aus. Mandant kann Praxis aus. Sitzung wählt den Kern oder nicht.",
    ausWirkung: "Haar nicht im Picker. Radi144/Works/Morphic unberührt. K5 folgt auf aus.",
  },
  {
    id: "K2",
    key: "kernel.kozyrev.reg.v1",
    defaultOn: "aus",
    kette: "Nur an, wenn Platform und Mandant Labor/Forschung erlauben.",
    ausWirkung: "REG nicht im Picker. Passport darf die ID nicht tragen.",
  },
  {
    id: "K3",
    key: "capability.kozyrev.lab",
    defaultOn: "aus",
    kette: "Labor-Mandant. executable bleibt false, bis ein späteres gesetztes Gate das ändert.",
    ausWirkung: "lab.* wird nicht admitted. Tests gegen Client-PDF bleiben grün.",
  },
  {
    id: "K4",
    key: "kernel.kozyrev.padic.p3.v1 / p5.v1",
    defaultOn: "aus",
    kette: "Eigene IDs. Haar-v1 bleibt unabhängig.",
    ausWirkung: "p≠2 nicht im Picker. Kein stilles Umdeuten auf Haar.",
  },
  {
    id: "K5",
    key: "capability.kozyrev.padic.on_hrv_rr",
    defaultOn: "aus",
    kette: "Braucht K1 an UND Clip-Grant (D21) UND dieses Flag.",
    ausWirkung: "RR-Reihe darf andere Kerne nutzen, nicht Haar. Keine Diagnose-Texte.",
  },
];
