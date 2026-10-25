"""
LLM-gestützte PDF-Analyse für Morphic Engine V1

Nutzt lokale LLMs über Ollama für:
- Intelligente Strukturerkennung
- Semantische Kategorisierung
- Kontextbewusste Gruppierung
- Automatische NLS-DB-Erstellung
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

# Ollama-Integration
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Ollama-Konfiguration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_DEFAULT_MODEL = "llama3.2"  # Oder: mistral, llama3, phi3
OLLAMA_TIMEOUT = 120  # Sekunden


@dataclass
class LLMAnalysisResult:
    """Ergebnis der LLM-Analyse"""
    groups: List[Dict] = field(default_factory=list)
    categories: Dict[str, int] = field(default_factory=dict)
    quality_score: float = 0.0
    model_used: str = ""
    tokens_used: int = 0
    confidence: float = 0.0
    raw_response: str = ""


def check_ollama_available() -> Dict:
    """Prüft ob Ollama verfügbar ist und welche Modelle installiert sind."""
    if not REQUESTS_AVAILABLE:
        return {'available': False, 'error': 'requests nicht installiert'}
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            return {
                'available': True,
                'models': models,
                'recommended': get_best_model(models)
            }
        return {'available': False, 'error': f'Status {response.status_code}'}
    except requests.exceptions.ConnectionError:
        return {'available': False, 'error': 'Ollama nicht erreichbar (localhost:11434)'}
    except Exception as e:
        return {'available': False, 'error': str(e)}


def get_best_model(models: List[str]) -> Optional[str]:
    """Wählt das beste verfügbare Modell."""
    # Präferenz-Reihenfolge
    preferred = [
        'llama3.2', 'llama3.1', 'llama3', 
        'mistral', 'mixtral',
        'phi3', 'phi',
        'gemma2', 'gemma',
        'qwen2', 'qwen'
    ]
    
    for pref in preferred:
        for model in models:
            if pref in model.lower():
                return model
    
    return models[0] if models else None


def call_ollama(
    prompt: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 4096
) -> Tuple[str, Dict]:
    """
    Ruft Ollama API auf.
    
    Returns:
        Tuple von (response_text, metadata)
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests nicht installiert")
    
    model = model or OLLAMA_DEFAULT_MODEL
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        return data['message']['content'], {
            'model': model,
            'total_duration': data.get('total_duration', 0),
            'eval_count': data.get('eval_count', 0)
        }
    except Exception as e:
        raise RuntimeError(f"Ollama-Aufruf fehlgeschlagen: {e}")


# System-Prompt für PDF-Analyse
PDF_ANALYSIS_SYSTEM_PROMPT = """Du bist ein Experte für medizinische und komplementärmedizinische Datenanalyse.
Deine Aufgabe ist es, Text aus PDF-Dokumenten zu analysieren und strukturierte Daten zu extrahieren.

Du identifizierst:
1. GRUPPEN: Thematische Kategorien (z.B. "Pathogene", "Toxine", "Organe", "Nährstoffe", "Remedies")
2. ITEMS: Einzelne Einträge innerhalb der Gruppen mit optionalen Werten
3. KATEGORIEN: pathogen, toxin, organ, nutrient, remedy, symptom, frequency, unknown

Antworte IMMER im folgenden JSON-Format:
{
  "groups": [
    {
      "name": "Gruppenname",
      "category": "kategorie",
      "confidence": 0.0-1.0,
      "items": [
        {"label": "Item-Name", "value": null oder Zahl, "category": "kategorie"}
      ]
    }
  ],
  "summary": "Kurze Zusammenfassung der Analyse"
}

Wichtig:
- Erkenne auch unvollständige oder fehlerhafte Schreibweisen
- Kategorisiere basierend auf Kontext, nicht nur Keywords
- Gruppiere zusammengehörige Items intelligent
- Gib realistische Konfidenz-Werte an"""


def analyze_text_with_llm(
    text: str,
    model: Optional[str] = None,
    context: Optional[str] = None
) -> LLMAnalysisResult:
    """
    Analysiert Text mit LLM.
    
    Args:
        text: Zu analysierender Text
        model: Ollama-Modell (optional)
        context: Zusätzlicher Kontext (optional)
    
    Returns:
        LLMAnalysisResult
    """
    # Text kürzen wenn zu lang
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [Text gekürzt]"
    
    prompt = f"""Analysiere den folgenden Text aus einem medizinischen/komplementärmedizinischen PDF-Dokument.
Extrahiere alle relevanten Gruppen und Items.

{f'Kontext: {context}' if context else ''}

TEXT:
{text}

Antworte im JSON-Format wie in den Instruktionen beschrieben."""

    try:
        response_text, metadata = call_ollama(
            prompt,
            model=model,
            system_prompt=PDF_ANALYSIS_SYSTEM_PROMPT,
            temperature=0.2
        )
        
        # JSON aus Response extrahieren
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                
                result = LLMAnalysisResult(
                    groups=parsed.get('groups', []),
                    model_used=metadata.get('model', ''),
                    tokens_used=metadata.get('eval_count', 0),
                    raw_response=response_text
                )
                
                # Kategorien zählen
                for group in result.groups:
                    cat = group.get('category', 'unknown')
                    result.categories[cat] = result.categories.get(cat, 0) + len(group.get('items', []))
                
                # Konfidenz berechnen
                if result.groups:
                    confidences = [g.get('confidence', 0.5) for g in result.groups]
                    result.confidence = sum(confidences) / len(confidences)
                
                # Qualitäts-Score
                total_items = sum(len(g.get('items', [])) for g in result.groups)
                categorized = sum(1 for g in result.groups for i in g.get('items', []) 
                                 if i.get('category', 'unknown') != 'unknown')
                result.quality_score = categorized / total_items if total_items > 0 else 0
                
                return result
                
            except json.JSONDecodeError:
                pass
        
        # Fallback wenn JSON-Parsing fehlschlägt
        return LLMAnalysisResult(
            raw_response=response_text,
            model_used=metadata.get('model', '')
        )
        
    except Exception as e:
        return LLMAnalysisResult(
            raw_response=f"Fehler: {e}"
        )


def llm_enhanced_pdf_import(pdf_path: str, model: Optional[str] = None) -> Dict:
    """
    Führt LLM-gestützte PDF-Analyse durch.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        model: Ollama-Modell (optional)
    
    Returns:
        Vollständiges Analyse-Ergebnis
    """
    try:
        import fitz
    except ImportError:
        raise ImportError("PyMuPDF nicht installiert")
    
    # PDF-Text extrahieren
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()
    
    # Prüfe Ollama
    ollama_status = check_ollama_available()
    if not ollama_status['available']:
        raise RuntimeError(f"Ollama nicht verfügbar: {ollama_status.get('error')}")
    
    # Modell wählen
    model = model or ollama_status.get('recommended')
    if not model:
        raise RuntimeError("Kein Ollama-Modell verfügbar")
    
    # LLM-Analyse
    result = analyze_text_with_llm(full_text, model=model)
    
    return {
        'source_file': pdf_path,
        'analyzed_at': datetime.now().isoformat(),
        'model_used': result.model_used,
        'tokens_used': result.tokens_used,
        'quality_score': result.quality_score,
        'confidence': result.confidence,
        'categories': result.categories,
        'groups': result.groups,
        'total_items': sum(len(g.get('items', [])) for g in result.groups)
    }


def compare_analysis_methods(pdf_path: str) -> Dict:
    """
    Vergleicht regelbasierte und LLM-basierte Analyse.
    """
    results = {
        'pdf_path': pdf_path,
        'comparison': {}
    }
    
    # Regelbasierte Analyse
    try:
        from core.pdf_advanced_import import advanced_pdf_import
        regex_result = advanced_pdf_import(pdf_path)
        results['comparison']['regex'] = {
            'groups': len(regex_result.groups),
            'items': sum(len(g.items) for g in regex_result.groups),
            'quality': regex_result.quality_score,
            'method': 'regex+keywords'
        }
    except Exception as e:
        results['comparison']['regex'] = {'error': str(e)}
    
    # LLM-Analyse
    try:
        llm_result = llm_enhanced_pdf_import(pdf_path)
        results['comparison']['llm'] = {
            'groups': len(llm_result.get('groups', [])),
            'items': llm_result.get('total_items', 0),
            'quality': llm_result.get('quality_score', 0),
            'confidence': llm_result.get('confidence', 0),
            'model': llm_result.get('model_used', ''),
            'method': 'llm'
        }
    except Exception as e:
        results['comparison']['llm'] = {'error': str(e)}
    
    # Empfehlung
    regex = results['comparison'].get('regex', {})
    llm = results['comparison'].get('llm', {})
    
    if 'error' not in llm and 'error' not in regex:
        if llm.get('quality', 0) > regex.get('quality', 0):
            results['recommendation'] = 'llm'
            results['reason'] = f"LLM hat höhere Qualität ({llm['quality']:.0%} vs {regex['quality']:.0%})"
        else:
            results['recommendation'] = 'regex'
            results['reason'] = f"Regex ist schneller bei vergleichbarer Qualität"
    elif 'error' in llm:
        results['recommendation'] = 'regex'
        results['reason'] = f"LLM nicht verfügbar: {llm['error']}"
    else:
        results['recommendation'] = 'llm'
        results['reason'] = f"Regex fehlgeschlagen: {regex['error']}"
    
    return results


def get_llm_status() -> Dict:
    """Gibt LLM-Status für CLI zurück."""
    status = check_ollama_available()
    status['base_url'] = OLLAMA_BASE_URL
    status['default_model'] = OLLAMA_DEFAULT_MODEL
    return status
