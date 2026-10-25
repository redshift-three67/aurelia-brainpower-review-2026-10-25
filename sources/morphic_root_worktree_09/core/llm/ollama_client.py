"""
Ollama LLM Client für Beschreibungs-Generierung und Analyse.

Unterstützt lokale LLM-Modelle via Ollama API.
"""

import json
import logging
from typing import Optional, Dict, List
from urllib.parse import urlsplit

import requests

logger = logging.getLogger(__name__)

OLLAMA_LOOPBACK_ORIGIN = "http://127.0.0.1:11434"
OLLAMA_PINNED_MODEL = "phi3:latest"
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _validated_loopback_origin(value: str) -> str:
    """Return a normalized HTTP loopback origin or reject it before use."""
    error = "Ollama origin must be a valid HTTP loopback origin with an explicit port"
    try:
        has_raw_delimiter = "?" in value or "#" in value
        parsed = urlsplit(value)
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise ValueError(error) from exc

    if (
        parsed.scheme != "http"
        or parsed.hostname not in _LOOPBACK_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or has_raw_delimiter
        or parsed.query
        or parsed.fragment
        or port is None
        or port == 0
    ):
        raise ValueError(error)

    return value.rstrip("/")


class OllamaClient:
    """Client für Ollama LLM API."""

    def __init__(
        self,
        base_url: str = OLLAMA_LOOPBACK_ORIGIN,
        model: str = OLLAMA_PINNED_MODEL,
    ):
        """
        Initialisiert Ollama Client.

        Args:
            base_url: Ollama API URL
            model: Modell-Name (z.B. "phi-3-mini:3.8b", "meditron:70b")
        """
        self.base_url = _validated_loopback_origin(base_url)
        self.model = model
        self.unavailability_reason = ""
        self._session = requests.Session()
        self._session.trust_env = False
        self.available = self._check_availability()

        if self.available:
            logger.info(f"Ollama Client initialisiert: {model} @ {base_url}")
        else:
            logger.warning(
                f"Ollama nicht verfügbar @ {base_url} ({self.unavailability_reason})"
            )

    def _check_availability(self) -> bool:
        """Prüft, ob Ollama verfügbar ist."""
        try:
            response = self._session.get(
                f"{self.base_url}/api/tags",
                timeout=2,
                allow_redirects=False,
            )
            if response.status_code == 200:
                # Prüfe, ob Modell verfügbar ist
                data = response.json()
                models = data.get("models", [])
                if models:
                    model_names = [m.get("name", "") for m in models]
                    if self.model in model_names:
                        return True
                    logger.warning(
                        "Erforderliches Ollama-Modell ist nicht installiert: %s",
                        self.model,
                    )
                    self.unavailability_reason = "model_missing"
                    return False
                else:
                    logger.warning("Keine Modelle installiert")
                    self.unavailability_reason = "no_models"
                    return False
            logger.warning("Ollama-Server hat nicht mit HTTP 200 geantwortet")
            self.unavailability_reason = "server_error"
            return False
        except Exception:
            logger.debug("Ollama-Verfügbarkeitsprüfung fehlgeschlagen")
            self.unavailability_reason = "server_unreachable"
            return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 150,
    ) -> Optional[str]:
        """
        Generiert Text mit Ollama.

        Args:
            prompt: User-Prompt
            system: System-Prompt (optional)
            temperature: Kreativität (0.0-1.0, niedrig = präziser)
            max_tokens: Maximale Token-Anzahl

        Returns:
            Generierter Text oder None bei Fehler
        """
        if not self.available:
            return None

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            if system:
                payload["system"] = system

            response = self._session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=90,  # Erhöht von 30s für längere Deutungs-Analysen
                allow_redirects=False,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API Fehler: {response.status_code}")
                return None

        except Exception:
            logger.error("Ollama-Generierung fehlgeschlagen")
            return None

    def generate_description(
        self, label: str, group: str, rates: Optional[List[float]] = None
    ) -> Optional[str]:
        """
        Generiert therapeutische Beschreibung für ein Item.

        Args:
            label: Item-Label (z.B. "An Shen Wan", "Chrom")
            group: Gruppen-Name (z.B. "tcm_rezepturen", "orthomolekular_mineralien")
            rates: Frequenzbereich [min, max] (optional)

        Returns:
            Beschreibung (max 60 Zeichen) oder None
        """
        system_prompt = """Du bist ein Experte für Naturheilkunde, TCM, Homöopathie und Orthomolekularmedizin.
Erstelle präzise, therapeutische Beschreibungen für Remedies und Substanzen.
Format: 1 Satz Hauptwirkung + 2-3 Indikationen. Maximal 60 Zeichen."""

        rates_info = ""
        if rates and len(rates) >= 2:
            rates_info = f"\nFrequenzbereich: [{rates[0]:.2f} - {rates[1]:.2f}]"

        prompt = f"""Erstelle eine therapeutische Beschreibung für:

Item: {label}
Gruppe: {group}{rates_info}

Anforderungen:
- Maximal 60 Zeichen
- 1 Satz Hauptwirkung
- 2-3 Indikationen
- Keine Einleitung, direkt starten

Beispiele:
- "Beruhigt Shen. Bei: Unruhe, Schlafstörungen, Angst"
- "Blutzuckerregulation. Bei: Diabetes, Heißhunger"
- "Neurotransmitter. Bei: Depression, Konzentration"

Beschreibung:"""

        description = self.generate(
            prompt, system=system_prompt, temperature=0.2, max_tokens=80
        )

        # Kürze auf 60 Zeichen falls nötig
        if description and len(description) > 60:
            description = description[:57] + "..."

        return description

    def generate_synergy_explanation(
        self,
        item_a: str,
        item_b: str,
        rates_a: List[float],
        rates_b: List[float],
        synergy_score: float,
    ) -> Optional[str]:
        """
        Erklärt Synergie zwischen zwei Items.

        Args:
            item_a: Erstes Item
            item_b: Zweites Item
            rates_a: Frequenzbereich Item A
            rates_b: Frequenzbereich Item B
            synergy_score: Synergie-Score (0.0-1.0)

        Returns:
            Erklärung (max 100 Zeichen) oder None
        """
        system_prompt = """Du bist ein Experte für Synergie-Effekte in der Naturheilkunde.
Erkläre, warum zwei Remedies synergistisch wirken basierend auf ihren Frequenzen."""

        prompt = f"""Erkläre die Synergie zwischen:

Item A: {item_a} (Frequenz: [{rates_a[0]:.2f} - {rates_a[1]:.2f}])
Item B: {item_b} (Frequenz: [{rates_b[0]:.2f} - {rates_b[1]:.2f}])
Synergie-Score: {synergy_score:.2f}

Anforderungen:
- Maximal 100 Zeichen
- Erkläre WARUM sie zusammen wirken
- Keine Einleitung

Beispiel: "Ähnliche Frequenzen verstärken Wirkung auf Nervensystem"

Erklärung:"""

        explanation = self.generate(
            prompt, system=system_prompt, temperature=0.2, max_tokens=100
        )

        if explanation and len(explanation) > 100:
            explanation = explanation[:97] + "..."

        return explanation

    def analyze_report_summary(
        self, top_items: List[Dict], focus: str = ""
    ) -> Optional[str]:
        """
        Erstellt eine tiefgehende KI-Analyse aus Bericht-Ergebnissen.

        Produziert 4 nummerierte Absaetze (wie Mustermann-Referenz):
        1. Hauptbelastungen und Kombination
        2. Score-Analyse der Top-Remedies
        3. Therapie-Empfehlung
        4. Tieferliegende Ursachen

        Args:
            top_items: Top Items aus Scan (mit label, score, group)
            focus: Fokus/Symptom (optional)

        Returns:
            Tiefenanalyse-Text mit 4 Absaetzen oder None
        """
        system_prompt = """Du bist ein erfahrener Therapeut fuer integrative Medizin und Bioresonanz-Analyse.
Du analysierst Morphic-Engine-Scan-Ergebnisse und erstellst eine tiefgehende,
verstaendliche Deutung fuer den Klienten. Schreibe auf Deutsch.
Verwende keine medizinischen Diagnosen, sondern formuliere als Orientierungshilfe.
Strukturiere deine Antwort in genau 4 nummerierte Absaetze."""

        items_text = "\n".join(
            [
                f"- {item.get('label', '')} (Score: {item.get('score', 0):.2f}, Gruppe: {item.get('group', '')})"
                for item in top_items[:12]
            ]
        )

        focus_text = f"\nThematischer Fokus: {focus}" if focus else ""

        prompt = f"""Analysiere diese Morphic-Engine-Scan-Ergebnisse:{focus_text}

Top-Resonanzen:
{items_text}

Erstelle eine tiefgehende Deutung in genau 4 nummerierten Absaetzen:

1. Die Hauptbelastungen koennten sich um eine Kombination aus ... drehen.
   Beschreibe die Zusammenhaenge zwischen den Top-Items.

2. Die hohe Score von [Top-Remedy] und [zweitbeste] deutet auf ...
   Erklaere die Bedeutung der staerksten Resonanzen.

3. Fuer die Therapie empfehle ich zunaechst, den Fokus auf ... zu legen.
   Gib konkrete priorisierte Empfehlungen.

4. Die tieferliegenden Ursachen koennten historisch bedingt sein ...
   Erklaere moegliche Ursachen-Zusammenhaenge.

Schliesse mit dem Hinweis: 'Bitte beachten Sie, dass dies keine medizinische
Diagnose darstellt und professionelle medizinische Hilfe empfohlen wird,
insbesondere wenn Symptome vorliegen oder sich im Laufe der Zeit verschlechtern.'

Antwort:"""

        return self.generate(
            prompt, system=system_prompt, temperature=0.4, max_tokens=800
        )


# Globale Instanz (Singleton)
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client(
    base_url: str = OLLAMA_LOOPBACK_ORIGIN,
    model: str = OLLAMA_PINNED_MODEL,
) -> Optional[OllamaClient]:
    """
    Gibt Ollama Client Singleton zurück.

    Args:
        base_url: Ollama API URL
        model: Modell-Name

    Returns:
        OllamaClient (mit `available` Attribut zur Statuspruefung) oder None
        bei einem Initialisierungsfehler.
    """
    global _ollama_client

    if _ollama_client is None:
        try:
            _ollama_client = OllamaClient(base_url=base_url, model=model)
        except Exception:
            return None

    return _ollama_client


def generate_description_cached(
    label: str,
    group: str,
    rates: Optional[List[float]] = None,
    cache: Optional[Dict] = None,
) -> str:
    """
    Generiert Beschreibung mit Caching.

    Args:
        label: Item-Label
        group: Gruppen-Name
        rates: Frequenzbereich (optional)
        cache: Cache-Dictionary (optional)

    Returns:
        Beschreibung oder "-" falls nicht verfügbar
    """
    # Prüfe Cache
    if cache is not None:
        cache_key = f"{group}:{label}"
        if cache_key in cache:
            return cache[cache_key]

    # Versuche Ollama
    client = get_ollama_client()
    if client:
        description = client.generate_description(label, group, rates)
        if description:
            # Speichere in Cache
            if cache is not None:
                cache[f"{group}:{label}"] = description
            return description

    # Fallback
    return "-"
