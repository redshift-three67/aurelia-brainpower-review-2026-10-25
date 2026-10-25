from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, Response
from uuid import uuid4
from datetime import datetime
import re
import base64
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List
from xml.sax.saxutils import escape as xml_escape
from ..schemas.resonance import (
    ResonanceAnalysisRequest, ResonanceAnalysisResponse,
    EMFStatusResponse, ResonanceSequenceResponse
)
from ..algorithms.resonance_engine import ResonanceMatrixEngine
from ..services.client_registry_service import ClientRegistryService
from ..services.report_manifest_service import ReportManifestService
from ..services.session_archive_service import SessionArchiveService
from ..services.safety_service import safety_block as _safety_block, DISCLAIMER_DE as _DISCLAIMER_DE
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

router = APIRouter()
# Initialisiere Engine beim Start
try:
    engine = ResonanceMatrixEngine(use_cuda=True)
except Exception as e:
    logger.warning(f"Could not initialize ResonanceMatrixEngine with CUDA: {e}. Fallback to CPU if possible.")
    engine = ResonanceMatrixEngine(use_cuda=False)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_IMPORT_DIR = PROJECT_ROOT / "db_import"
MAX_IMAGE_BYTES = 4 * 1024 * 1024
PDF_DIGIT_COLORS = {
    0: "#FFFFFF",
    1: "#FF0000",
    2: "#FF7F00",
    3: "#FFFF00",
    4: "#00FF00",
    5: "#00FFFF",
    6: "#0000FF",
    7: "#8B00FF",
    8: "#FF00FF",
    9: "#FFD700",
}


def _runtime_archive_root() -> Path:
    return PROJECT_ROOT / "data" / "runtime"


def _archive_services():
    archive_root = _runtime_archive_root()
    return (
        ClientRegistryService(archive_root / "clients.json"),
        SessionArchiveService(archive_root / "sessions.json"),
        ReportManifestService(archive_root / "artifacts.json"),
    )


def _client_data_from_registry_entry(entry) -> Dict[str, Any]:
    return {
        "first_name": entry.first_name,
        "last_names": list(entry.last_names),
        "birth_date": entry.birth_date,
        "birth_place": entry.birth_place,
        "planet": entry.planet,
    }


def _resolve_client_data_by_id(client_id: str) -> Dict[str, Any]:
    client_service, _, _ = _archive_services()
    entry = client_service.get_by_id(client_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"client_id nicht gefunden: {client_id}")
    return _client_data_from_registry_entry(entry)


def _mirror_api_session(request: ResonanceAnalysisRequest, client_data: Dict[str, Any], result: Dict[str, Any]):
    client_service, session_service, _ = _archive_services()

    if request.client_id:
        client_entry = client_service.get_by_id(request.client_id)
        if client_entry is None:
            raise HTTPException(status_code=404, detail=f"client_id nicht gefunden: {request.client_id}")
    else:
        client_entry = client_service.get_or_create(client_data)

    focus_sequence = _split_focus_sequence(request.focus) or [request.focus]
    last_names = client_data.get("last_names") or []
    if isinstance(last_names, list):
        suffix = " ".join(str(item).strip() for item in last_names if str(item).strip())
    else:
        suffix = str(last_names).strip()
    full_name = str(result.get("client_name") or f"{client_data.get('first_name', '')} {suffix}".strip() or "Unbekannt")

    return session_service.create_session(
        client_ref={"client_id": client_entry.client_id, "client_name": full_name},
        focus=focus_sequence[0],
        focus_sequence=focus_sequence,
        config={
            "mode": request.calculation_mode,
            "matrix_size": request.matrix_size,
            "focus_weight": request.focus_weight,
            "hrv_sim": request.hrv_sim,
            "use_planetary": request.use_planetary,
            "emf_compensate": request.emf_compensate,
            "amplifier": request.amplifier,
            "symmetry": request.symmetry,
            "palette": request.palette,
            "use_quantum": request.use_quantum,
            "use_cuda": request.use_cuda,
        },
        result_summary={
            "result_count": 1,
            "resonance_score": result.get("resonance_score"),
            "hardware": result.get("hardware") or result.get("hardware_acceleration"),
            "rates_string": result.get("rates_string"),
        },
        harmonization_status="not_requested",
    )


def _resolve_output_path(raw_path: str) -> Path:
    cleaned = str(raw_path or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="output_path ist leer.")
    candidate = Path(cleaned)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    return candidate


def _register_pdf_artifact(session_id: str, output_path: Path):
    _, session_service, report_service = _archive_services()
    session = session_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"session_id nicht gefunden: {session_id}")
    artifact = report_service.register_artifact(
        session_id=session_id,
        artifact_type="pdf",
        path=str(output_path),
        label=output_path.name,
    )
    session_service.attach_artifact(session_id, artifact.artifact_id)
    return artifact


def _split_focus_sequence(focus_raw: str):
    if not focus_raw:
        return []
    return [item.strip() for item in re.split(r"[;\r\n]+", focus_raw) if item.strip()]


def _contrast_text_color(hex_color: str) -> str:
    value = (hex_color or "").strip().lstrip("#")
    if len(value) != 6:
        return "#000000"
    try:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
    except ValueError:
        return "#000000"

    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#000000" if luminance > 140 else "#FFFFFF"


def _safe_pdf_filename(raw: str) -> str:
    base = (raw or "resonanzmatrix_bericht").strip()
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    base = base.strip("._")
    if not base:
        base = "resonanzmatrix_bericht"
    if not base.lower().endswith(".pdf"):
        base = f"{base}.pdf"
    return base


def _apply_request_amplifier(amplifier_name: str | None):
    previous_state = (engine.active_amplifier_id, engine.active_amplifier_data)
    requested = (amplifier_name or "").strip()
    if requested:
        result = engine.set_amplifier(requested)
        if not result:
            raise HTTPException(status_code=400, detail=f"Amplifier '{requested}' nicht gefunden.")
    else:
        engine.clear_amplifier()
    return previous_state


def _restore_request_amplifier(previous_state):
    prev_id, prev_data = previous_state
    engine.active_amplifier_id = prev_id
    engine.active_amplifier_data = prev_data


def _default_client_data() -> Dict[str, Any]:
    return {
        "first_name": "Standalone",
        "last_names": ["Client"],
        "birth_date": "1990-01-01",
        "birth_place": "Unknown",
    }


def _resolve_existing_path(raw_path: str) -> Path | None:
    cleaned = (raw_path or "").strip().strip('"').strip("'")
    if not cleaned:
        return None

    candidate = Path(cleaned)
    candidates: List[Path] = []
    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.append((PROJECT_ROOT / candidate).resolve())
        candidates.append((DB_IMPORT_DIR / candidate).resolve())

    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def _decode_image_base64_to_temp_file(image_base64: str) -> Path:
    payload = (image_base64 or "").strip()
    if not payload:
        raise HTTPException(status_code=400, detail="image_base64 ist leer.")

    if "," in payload and "base64" in payload.split(",", 1)[0].lower():
        payload = payload.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="image_base64 ist ungueltig.") from exc

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="image_base64 ist zu gross (max. 4 MB). Bitte image_path verwenden.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".img") as tmp:
        tmp.write(image_bytes)
        return Path(tmp.name)


def _build_response(request: ResonanceAnalysisRequest, result: Dict[str, Any]) -> ResonanceAnalysisResponse:
    return ResonanceAnalysisResponse(
        analysis_id=uuid4(),
        timestamp=datetime.utcnow(),
        client_name=result["client_name"],
        focus=request.focus,
        resonance_score=result["resonance_score"],
        matrix_12x12=result["matrix_12x12"],
        matrix_data=result.get("matrix_data", result["matrix_12x12"]),
        matrix_size=result.get("matrix_size", 12),
        matrix_colors=result["matrix_colors"],
        resonant_patterns=[],
        processing_time_ms=result["processing_time_ms"],
        hardware_acceleration=result["hardware"],
        emf_compensation=result.get("emf_compensation"),
        amplifier=result.get("amplifier"),
        amplifier_recommendations=result.get("amplifier_recommendations"),
        symmetry=result.get("symmetry", "none"),
        client_frequency_hz=result.get("client_signature", {}).get("frequency"),
        top_10=result.get("top_10"),
        safety=_safety_block(),  # R-7: kanonische Safety-Posture auf jeder Analyse-Response
    )


def _build_client_data(request: ResonanceAnalysisRequest) -> Dict[str, Any]:
    if request.client_data:
        return request.client_data.model_dump()
    if request.client_id:
        return _resolve_client_data_by_id(request.client_id)
    if request.group_members:
        return {
            "first_name": "Gruppe",
            "last_names": [f"{len(request.group_members)} Mitglieder"],
            "birth_date": "1990-01-01",
            "birth_place": "Group",
        }
    if request.geo_coords:
        return {
            "first_name": "Geo",
            "last_names": ["Resonanz"],
            "birth_date": "1990-01-01",
            "birth_place": "Geo",
        }
    if request.image_path or request.image_base64:
        return {
            "first_name": "Bild",
            "last_names": ["Resonanz"],
            "birth_date": "1990-01-01",
            "birth_place": "Image",
        }
    return _default_client_data()


def _requires_precomputed_signature(request: ResonanceAnalysisRequest) -> bool:
    return bool(
        request.group_members
        or request.geo_coords
        or request.image_path
        or request.image_base64
        or request.db_path
        or request.use_planetary
    )


def _prepare_precomputed_signature(request: ResonanceAnalysisRequest, client_data: Dict[str, Any]) -> Dict[str, Any]:
    from ..algorithms.client_signature import ClientSignatureGenerator

    sig_gen = ClientSignatureGenerator()
    temp_image_file: Path | None = None

    try:
        if request.group_members:
            client_sig = sig_gen.generate_group_signature(request.group_members)
            client_data["first_name"] = "Gruppe"
            client_data["last_names"] = [f"{len(request.group_members)} Mitglieder"]
        elif request.image_base64 or request.image_path:
            if request.image_base64:
                temp_image_file = _decode_image_base64_to_temp_file(request.image_base64)
                image_file = temp_image_file
            else:
                image_file = _resolve_existing_path(request.image_path or "")

            if not image_file:
                raise HTTPException(status_code=400, detail="Bild konnte nicht gefunden oder gelesen werden.")

            client_sig = sig_gen.generate_image_signature(str(image_file))
            label = client_sig.get("image_label") or image_file.stem
            client_data["first_name"] = label
            client_data["last_names"] = ["Bild"]
        else:
            client_sig = sig_gen.generate_signature(
                client_data,
                use_planetary=request.use_planetary,
                emf_compensator=engine.emf_compensator if engine.emf_active else None,
            )

        if request.geo_coords:
            coords = [part.strip() for part in request.geo_coords.split(",") if part.strip()]
            if len(coords) < 2:
                raise HTTPException(status_code=400, detail="geo_coords muss mindestens 'lat,lon' enthalten.")

            lat = float(coords[0])
            lon = float(coords[1])
            radius = float(coords[2]) if len(coords) > 2 else 0.0
            geo_freq = sig_gen.calculate_geo_frequency(lat, lon, radius_m=radius)

            base_freq = float(client_sig.get("frequency") or 0.0)
            client_sig["frequency"] = ((base_freq + geo_freq) / 2.0) if base_freq else geo_freq

            components = dict(client_sig.get("components") or {})
            components["geo_frequency_hz"] = geo_freq
            components["geo_coords"] = f"{lat:.6f},{lon:.6f},{radius:.2f}"
            client_sig["components"] = components

        if request.db_path:
            db_file = _resolve_existing_path(request.db_path)
            if not db_file:
                raise HTTPException(status_code=400, detail="db_path konnte nicht gefunden werden.")

            db_freq = sig_gen.vectorise_database_selection(str(db_file), request.focus)
            if db_freq > 0:
                base_freq = float(client_sig.get("frequency") or 0.0)
                client_sig["frequency"] = ((base_freq + db_freq) / 2.0) if base_freq else db_freq
                components = dict(client_sig.get("components") or {})
                components["db_frequency_hz"] = db_freq
                components["db_source"] = db_file.name
                client_sig["components"] = components

        return client_sig
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Ungueltige Vektor-Eingabe: {exc}") from exc
    finally:
        if temp_image_file and temp_image_file.exists():
            try:
                temp_image_file.unlink()
            except OSError:
                pass


def _list_db_files() -> List[Path]:
    if not DB_IMPORT_DIR.exists():
        return []
    return sorted([p for p in DB_IMPORT_DIR.rglob("*.txt") if p.is_file()])


def _read_db_entries(db_file: Path, max_entries: int = 50) -> List[str]:
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(db_file, "r", encoding=enc) as f:
                entries = [line.strip() for line in f if line.strip()]
            return entries[:max_entries]
        except UnicodeDecodeError:
            continue
        except Exception as exc:
            logger.warning(f"DB read failed ({db_file.name}, {enc}): {exc}")
            continue
    return []

@router.post("/analyze-matrix", response_model=ResonanceAnalysisResponse)
async def analyze_matrix_resonance(request: ResonanceAnalysisRequest, response: Response):
    """
    Führt eine hochfrequente 12x12 Matrix-Resonanz-Analyse durch (v1.5.0).
    Unterstützt: Einzelklient, Gruppen, Geo-Resonanz, DB-Vektorisierung, HRV-Simulation, Quantum-Toggle.
    Generiert Zahlenmuster und kohärente Farbmuster.
    """
    previous_amplifier_state = _apply_request_amplifier(request.amplifier)
    try:
        try:
            if not (
                request.client_data
                or request.client_id
                or request.group_members
                or request.geo_coords
                or request.image_path
                or request.image_base64
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Es fehlen Eingabedaten (Klient, Gruppe, Geo oder Bild).",
                )

            client_data = _build_client_data(request)
            precomputed_signature = None
            if _requires_precomputed_signature(request):
                precomputed_signature = _prepare_precomputed_signature(request, client_data)

            result = engine.calculate_resonance(
                client_data=client_data,
                focus=request.focus,
                matrix_size=request.matrix_size,
                focus_weight=request.focus_weight,
                calculation_mode=request.calculation_mode,
                hrv_sim=request.hrv_sim,
                palette=request.palette,
                emf_compensate=request.emf_compensate,
                symmetry=getattr(request, 'symmetry', 'none'),
                precomputed_signature=precomputed_signature,
            )
            session_entry = _mirror_api_session(request, client_data, result)
            if response is not None:
                response.headers["X-Session-ID"] = session_entry.session_id
                response.headers["X-Client-ID"] = session_entry.client_ref.client_id or ""

            return _build_response(request, result)
        finally:
            _restore_request_amplifier(previous_amplifier_state)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resonance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analyse-Fehler: {str(e)}")


@router.post("/analyze-sequence", response_model=ResonanceSequenceResponse)
async def analyze_matrix_sequence(request: ResonanceAnalysisRequest):
    """
    Fuehrt eine sequenzielle Mehrfach-Fokus-Analyse aus.
    Fokus-Items werden aus `focus` per Semikolon/Zeilenumbruch extrahiert.
    """
    focus_items = _split_focus_sequence(request.focus)
    if not focus_items:
        raise HTTPException(status_code=400, detail="Keine gueltigen Fokus-Eintraege gefunden.")

    try:
        sequence_results = []
        for focus in focus_items:
            single_request = request.copy(deep=True)
            single_request.focus = focus
            sequence_results.append(await analyze_matrix_resonance(single_request, Response()))

        return ResonanceSequenceResponse(
            count=len(sequence_results),
            focuses=focus_items,
            results=sequence_results,
            safety=_safety_block(),  # R-7: Safety-Posture auch auf der Sequenz-Antwort
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sequential resonance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sequenz-Analyse-Fehler: {str(e)}")


@router.post("/analyze-group", response_model=ResonanceAnalysisResponse)
async def analyze_group_resonance(request: ResonanceAnalysisRequest, response: Response):
    """
    Führt eine Gruppen-Resonanz-Analyse durch (v1.5.0).
    Nutzt Centroid-Berechnung aus mehreren Gruppenmitgliedern.
    """
    try:
        if not request.group_members:
            raise HTTPException(status_code=400, detail="group_members muss angegeben werden.")
        return await analyze_matrix_resonance(request, response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Group analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gruppen-Analyse-Fehler: {str(e)}")


@router.post("/analyze-geo", response_model=ResonanceAnalysisResponse)
async def analyze_geo_resonance(request: ResonanceAnalysisRequest, response: Response):
    """
    Führt eine Geo-Resonanz-Analyse durch (v1.5.0).
    Nutzt Geo-Koordinaten mit optionalem Radius.
    """
    try:
        if not request.geo_coords:
            raise HTTPException(status_code=400, detail="geo_coords (lat,lon) muss angegeben werden.")
        return await analyze_matrix_resonance(request, response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geo analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Geo-Analyse-Fehler: {str(e)}")


@router.get("/db/list")
async def list_databases():
    """Listet verfuegbare .txt Datenbanken aus db_import rekursiv auf."""
    db_files = _list_db_files()
    items = []
    for db in db_files:
        rel = db.relative_to(DB_IMPORT_DIR).as_posix() if DB_IMPORT_DIR in db.parents or db == DB_IMPORT_DIR else db.name
        items.append(
            {
                "name": db.name,
                "relative_path": rel,
                "absolute_path": str(db),
                "size_bytes": db.stat().st_size,
            }
        )

    return {"count": len(items), "root": str(DB_IMPORT_DIR), "items": items}


@router.post("/db/rank")
async def rank_databases(request: ResonanceAnalysisRequest, limit: int = Query(default=5, ge=1, le=10)):
    """Fuehrt ein zweiphasiges DB-Ranking analog zur CLI-Logik aus."""
    db_files = _list_db_files()
    if not db_files:
        return {"count": 0, "items": [], "message": "Keine DB-Dateien in db_import gefunden."}

    client_data = _build_client_data(request)
    if _requires_precomputed_signature(request):
        client_sig = _prepare_precomputed_signature(request, client_data)
    else:
        client_sig = engine.signature_gen.generate_signature(
            client_data,
            use_planetary=request.use_planetary,
            emf_compensator=engine.emf_compensator if engine.emf_active else None,
        )

    # Phase 1: Dateinamen-Vorfilter
    name_scores = []
    for db in db_files:
        db_name = db.stem
        try:
            res = engine.calculate_resonance(
                client_data,
                db_name,
                matrix_size=12,
                focus_weight=request.focus_weight,
                precomputed_signature=client_sig,
                calculation_mode="precision",
                emf_compensate=request.emf_compensate,
            )
            score = float(res["resonance_score"])
        except Exception:
            score = 0.0
        name_scores.append({"path": db, "name": db_name, "score": score})

    name_scores.sort(key=lambda x: x["score"], reverse=True)
    top30 = name_scores[:30]

    # Phase 2: Inhalts-Scan der Top-30
    ranked = []
    for cand in top30:
        entries = _read_db_entries(cand["path"], max_entries=50)
        if not entries:
            continue

        entry_scores = []
        for entry in entries:
            try:
                res = engine.calculate_resonance(
                    client_data,
                    entry,
                    matrix_size=12,
                    focus_weight=request.focus_weight,
                    precomputed_signature=client_sig,
                    calculation_mode="precision",
                    emf_compensate=request.emf_compensate,
                )
                entry_scores.append(float(res["resonance_score"]))
            except Exception as exc:
                logger.warning(f"DB rank entry skipped ({cand['path'].name}): {exc}")
                continue

        if not entry_scores:
            continue

        entry_scores.sort(reverse=True)
        avg_top5 = sum(entry_scores[:5]) / min(5, len(entry_scores))
        ranked.append(
            {
                "name": cand["path"].name,
                "relative_path": cand["path"].relative_to(DB_IMPORT_DIR).as_posix(),
                "absolute_path": str(cand["path"]),
                "avg_score": avg_top5,
                "name_score": cand["score"],
                "entries": len(entries),
            }
        )

    ranked.sort(key=lambda x: x["avg_score"], reverse=True)
    return {
        "count": min(limit, len(ranked)),
        "items": ranked[:limit],
        "scanned_files": len(db_files),
        "deep_scanned": len(ranked),
    }


@router.post("/db/scan")
async def scan_database(request: ResonanceAnalysisRequest, top_n: int = Query(default=21, ge=1, le=42)):
    """Scant eine DB gegen den aktuellen Vektor und liefert Top-N Fokuskandidaten."""
    if not request.db_path:
        raise HTTPException(status_code=400, detail="db_path ist fuer db/scan erforderlich.")

    db_file = _resolve_existing_path(request.db_path)
    if not db_file:
        raise HTTPException(status_code=400, detail="DB-Datei konnte nicht gefunden werden.")

    entries = _read_db_entries(db_file, max_entries=5000)
    if not entries:
        raise HTTPException(status_code=400, detail="DB-Datei ist leer oder nicht lesbar.")

    client_data = _build_client_data(request)
    if _requires_precomputed_signature(request):
        client_sig = _prepare_precomputed_signature(request, client_data)
    else:
        client_sig = engine.signature_gen.generate_signature(
            client_data,
            use_planetary=request.use_planetary,
            emf_compensator=engine.emf_compensator if engine.emf_active else None,
        )

    results = []
    for entry in entries:
        try:
            res = engine.calculate_resonance(
                client_data,
                entry,
                matrix_size=12,
                focus_weight=request.focus_weight,
                precomputed_signature=client_sig,
                calculation_mode="precision",
                emf_compensate=request.emf_compensate,
            )
            results.append({"entry": entry, "score": float(res["resonance_score"])})
        except Exception as exc:
            logger.warning(f"DB scan entry skipped ({db_file.name}): {exc}")
            continue

    if not results:
        raise HTTPException(status_code=400, detail="DB-Scan lieferte keine verwertbaren Ergebnisse.")

    results.sort(key=lambda x: x["score"], reverse=True)
    top = results[: min(top_n, len(results))]
    return {
        "db_name": db_file.name,
        "count": len(top),
        "items": top,
        "focus_string": ";".join(item["entry"] for item in top),
    }


@router.post("/export/pdf")
async def export_pdf_report(payload: Dict[str, Any]):
    """Erstellt einen PDF-Bericht aus Analyseergebnis + Workflow-Kontext."""
    result = payload.get("result") or {}
    context = payload.get("context") or {}

    if not isinstance(result, dict):
        raise HTTPException(status_code=400, detail="result muss ein Objekt sein.")

    matrix = result.get("matrix_data") or result.get("matrix_12x12")
    if not isinstance(matrix, list) or not matrix:
        raise HTTPException(status_code=400, detail="Matrix-Daten fehlen fuer den PDF-Export.")

    size = len(matrix)
    if not all(isinstance(row, list) and len(row) == size for row in matrix):
        raise HTTPException(status_code=400, detail="Matrix muss quadratisch sein.")

    try:
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise HTTPException(status_code=501, detail="reportlab ist nicht installiert.") from exc

    score = float(result.get("resonance_score") or 0.0)
    processing_ms = float(result.get("processing_time_ms") or 0.0)
    focus = str(result.get("focus") or context.get("focus") or "-")
    client_name = str(result.get("client_name") or context.get("client_name") or "-")
    matrix_size = int(result.get("matrix_size") or size)

    info_rows = [
        ["Erstellt", datetime.now().strftime("%d.%m.%Y %H:%M")],
        ["Klient", client_name],
        ["Vektor-Modus", str(context.get("vector_mode_label") or context.get("vector_mode") or "Klient")],
        ["Fokus", focus],
        ["Resonanz-Score", f"{score * 100:.2f}%"],
        ["Matrix", f"{matrix_size}x{matrix_size}"],
        ["Rechenzeit", f"{processing_ms:.0f} ms"],
        ["Hardware", str(result.get("hardware_acceleration") or "-")],
        ["Modus", str(context.get("calculation_mode") or "-")],
        ["Gewichtung", str(context.get("focus_weight") or "-")],
        ["Symmetrie", str(context.get("symmetry") or "-")],
        ["Palette", str(context.get("palette") or "Standard")],
        ["Amplifier", str(context.get("amplifier") or "Keiner")],
        ["Planetarisch", "Aktiv" if context.get("planetary_enabled") else "Aus"],
        ["EMF", "Aktiv" if context.get("emf_enabled") else "Aus"],
        ["HRV", "Aktiv" if context.get("hrv_enabled") else "Aus"],
    ]

    mode = str(context.get("vector_mode") or "client")
    if mode == "group":
        info_rows.append(["Gruppen-Mitglieder", str(context.get("group_count") or 0)])
    elif mode == "geo":
        info_rows.append([
            "Geo",
            f"{context.get('geo_lat', '-')}, {context.get('geo_lon', '-')} (r={context.get('geo_radius', '0')} m)",
        ])
    elif mode == "image":
        info_rows.append(["Bildquelle", str(context.get("image_source") or "-")])

    db_path = str(context.get("db_path") or "").strip()
    if db_path:
        info_rows.append(["DB", db_path])

    matrix_colors = result.get("matrix_colors")
    use_color_grid = (
        isinstance(matrix_colors, list)
        and len(matrix_colors) == size
        and all(isinstance(row, list) and len(row) == size for row in matrix_colors)
    )

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Resonanzmatrix Bericht", styles["Title"]))
    elements.append(Spacer(1, 10))

    info_table_data = [[xml_escape(str(k)), xml_escape(str(v))] for k, v in info_rows]
    info_table = Table(info_table_data, colWidths=[150, 360])
    info_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, rl_colors.HexColor("#C8D2CC")),
                ("BACKGROUND", (0, 0), (0, -1), rl_colors.HexColor("#F0F5F2")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    matrix_table_data = [[str(int(cell)) if isinstance(cell, (int, float)) else str(cell) for cell in row] for row in matrix]
    usable_width = A4[0] - doc.leftMargin - doc.rightMargin
    cell_size = min(22.0, usable_width / max(1, size))
    font_size = 8 if size <= 12 else 5 if size <= 24 else 4

    matrix_table = Table(
        matrix_table_data,
        colWidths=[cell_size] * size,
        rowHeights=[cell_size] * size,
    )

    matrix_style = [
        ("GRID", (0, 0), (-1, -1), 0.25, rl_colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]

    for r_idx, row in enumerate(matrix):
        for c_idx, cell in enumerate(row):
            if use_color_grid:
                cell_hex = str(matrix_colors[r_idx][c_idx])
            else:
                try:
                    cell_hex = PDF_DIGIT_COLORS.get(int(cell), "#FFFFFF")
                except Exception:
                    cell_hex = "#FFFFFF"

            matrix_style.append(("BACKGROUND", (c_idx, r_idx), (c_idx, r_idx), rl_colors.HexColor(cell_hex)))
            matrix_style.append(
                ("TEXTCOLOR", (c_idx, r_idx), (c_idx, r_idx), rl_colors.HexColor(_contrast_text_color(cell_hex)))
            )

    matrix_table.setStyle(TableStyle(matrix_style))
    elements.append(matrix_table)
    elements.append(Spacer(1, 14))

    rates_string = "".join(
        str(int(cell))
        for row in matrix
        for cell in row
        if isinstance(cell, (int, float))
    )
    rates_preview = rates_string if len(rates_string) <= 300 else f"{rates_string[:300]}..."
    elements.append(Paragraph(f"<b>Rates-String:</b> {xml_escape(rates_preview)}", styles["Normal"]))

    # R-7: kanonischer Nicht-Medizin-Disclaimer als PDF-Footer (kein Term-Block —
    # nur die Erklaerung; siehe app/services/safety_service.py). Vor doc.build().
    from reportlab.lib.styles import ParagraphStyle
    elements.append(Spacer(1, 18))
    disclaimer_style = ParagraphStyle(
        "R144Disclaimer",
        parent=styles["Normal"],
        fontSize=7,
        textColor=rl_colors.HexColor("#677E73"),
        leading=9,
    )
    elements.append(Paragraph(xml_escape(_DISCLAIMER_DE), disclaimer_style))

    doc.build(elements)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()

    session_id = str(payload.get("session_id") or "").strip()
    output_path_raw = str(payload.get("output_path") or "").strip()
    if session_id and not output_path_raw:
        raise HTTPException(status_code=400, detail="output_path ist erforderlich, wenn session_id mitgeliefert wird.")

    if output_path_raw:
        output_path = _resolve_output_path(output_path_raw)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(pdf_bytes)
        if session_id:
            artifact = _register_pdf_artifact(session_id, output_path)

    filename = _safe_pdf_filename(str(payload.get("filename") or "resonanzmatrix_bericht.pdf"))
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    if output_path_raw and session_id:
        headers["X-Artifact-ID"] = artifact.artifact_id
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers,
    )


# =========================================================================
# EMF COMPENSATION ENDPOINTS
# =========================================================================

@router.post("/emf/enable")
async def enable_emf_compensation(continuous: bool = False):
    """Aktiviert die EMF-Umfeld-Kompensation."""
    engine.enable_emf_compensation(continuous=continuous)
    return {"status": "enabled", "continuous": continuous}


@router.post("/emf/disable")
async def disable_emf_compensation():
    """Deaktiviert die EMF-Umfeld-Kompensation."""
    engine.disable_emf_compensation()
    return {"status": "disabled"}


@router.get("/emf/status")
async def get_emf_status():
    """Gibt den aktuellen EMF-Kompensationsstatus zurueck."""
    status = engine.get_emf_status()
    if not status:
        return {"active": False, "message": "EMF Compensator nicht aktiviert."}
    return status


@router.get("/emf/profile")
async def get_emf_profile():
    """Fuehrt eine aktuelle EMF-Umfeldmessung durch und gibt das Profil zurueck."""
    if not engine.emf_active or not engine.emf_compensator:
        raise HTTPException(status_code=400, detail="EMF Compensator nicht aktiviert. POST /emf/enable zuerst.")
    profile = engine.emf_compensator.profile_environment()
    recommendation = engine.emf_compensator.get_timing_recommendation()
    counters = engine.emf_compensator.get_counter_frequencies()
    return {
        "profile": profile,
        "recommendation": recommendation,
        "counter_frequencies": counters,
    }


@router.get("/emf/monitor", response_class=HTMLResponse)
async def emf_monitor_page():
    """Live-EMF-Monitor Dashboard (HTML + WebSocket Client)."""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>EMF Live-Monitor | 12x12 Resonance Engine v1.5.0</title>
    <style>
        :root{
          /* HEILSAMES DESIGN – gleiche kanonische Token-Quelle wie user_workflow.css
             (Salbeigrün · Sand · Terracotta). R-17: migriert von DARK hardcoded → LIGHT. */
          --bg: hsl(40 30% 97%); --bg2: hsl(40 25% 95%); --bg3: hsl(40 22% 92%); --bg4: hsl(40 20% 89%);
          --bd: hsl(145 15% 85%); --bd2: hsl(145 20% 72%);
          --primary: hsl(145 25% 36%); --primary-bg: hsl(145 30% 95%); --primary-glow: hsl(145 25% 36% / 0.12);
          --sand: hsl(35 35% 85%); --accent: hsl(18 45% 55%);
          --green: hsl(145 50% 40%); --amber: hsl(35 85% 55%); --red: hsl(0 65% 50%);
          --t: hsl(150 20% 15%); --td: hsl(150 10% 45%); --tm: hsl(150 8% 62%);
          --sans: 'Source Sans 3', system-ui, sans-serif; --mono: 'JetBrains Mono','Consolas',monospace;
          --r: 0.75rem; --rs: 0.625rem;
          --shadow-soft: 0 4px 20px -4px hsl(145 20% 30% / 0.08);
          --shadow-card: 0 8px 30px -8px hsl(145 20% 30% / 0.1);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: var(--sans); background: var(--bg); color: var(--t); padding: 20px; line-height: 1.55; }
        h1 { font-family: 'Playfair Display', Georgia, serif; color: var(--primary); margin-bottom: 8px; font-size: 1.6em; font-weight: 700; }
        .subtitle { color: var(--td); margin-bottom: 20px; font-size: 0.9em; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px; }
        .card { background: var(--bg2); border: 1px solid var(--bd); border-radius: var(--r); padding: 20px; box-shadow: var(--shadow-soft); }
        .card h3 { color: var(--primary); margin-bottom: 12px; font-size: 1em; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .metric .label { color: var(--td); }
        .metric .value { font-weight: bold; font-family: var(--mono); }
        .bar-bg { background: var(--bg4); border-radius: var(--rs); height: 10px; margin-top: 4px; }
        .bar-fill { height: 10px; border-radius: var(--rs); transition: width 0.5s ease; }
        .good { color: var(--green); } .warn { color: var(--amber); } .bad { color: var(--red); }
        .status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
        .freq-list { list-style: none; padding: 0; }
        .freq-list li { background: var(--bg3); border-radius: var(--rs); padding: 8px 12px; margin-bottom: 4px; display: flex; justify-content: space-between; font-size: 0.85em; border: 1px solid var(--bd); }
        .freq-list .hz { color: var(--primary); font-weight: bold; }
        #log { background: var(--bg3); border: 1px solid var(--bd); border-radius: var(--rs); padding: 12px; height: 120px; overflow-y: auto; font-family: var(--mono); font-size: 0.8em; color: var(--td); }
        .conn-status { padding: 6px 14px; border-radius: 20px; font-size: 0.8em; display: inline-block; }
        .conn-ok { background: hsl(145 50% 40% / 0.14); color: var(--green); border: 1px solid hsl(145 50% 40% / 0.3); }
        .conn-err { background: hsl(0 65% 50% / 0.14); color: var(--red); border: 1px solid hsl(0 65% 50% / 0.3); }
        .conn-wait { background: hsl(35 85% 55% / 0.14); color: var(--amber); border: 1px solid hsl(35 85% 55% / 0.3); }
    </style>
</head>
<body>
    <h1>EMF Live-Monitor</h1>
    <div class="subtitle">12x12 Resonance Matrix Engine v1.5.0 | Echtzeit-Umfeldanalyse
        <span id="connStatus" class="conn-status conn-wait" style="margin-left:12px;">Verbinde...</span>
    </div>
    <div class="grid">
        <div class="card">
            <h3>EMF Composite Index</h3>
            <div class="metric"><span class="label">Index</span><span class="value" id="emfIndex">--</span></div>
            <div class="bar-bg"><div class="bar-fill" id="emfBar" style="width:0%;background:var(--green);"></div></div>
            <div class="metric" style="margin-top:12px;"><span class="label">Entropy Score</span><span class="value" id="entropy">--</span></div>
            <div class="bar-bg"><div class="bar-fill" id="entBar" style="width:0%;background:var(--primary);"></div></div>
        </div>
        <div class="card">
            <h3>Sensoren</h3>
            <div class="metric"><span class="label">Timing Jitter</span><span class="value" id="jitter">-- ms</span></div>
            <div class="metric"><span class="label">GPU Noise</span><span class="value" id="gpuNoise">--</span></div>
            <div class="metric"><span class="label">System Load</span><span class="value" id="sysLoad">--</span></div>
            <div class="metric"><span class="label">Low-Noise Window</span><span class="value" id="lnw">--</span></div>
        </div>
        <div class="card">
            <h3>Timing Empfehlung</h3>
            <div class="metric"><span class="label">Status</span><span class="value" id="recStatus">--</span></div>
            <div class="metric"><span class="label">Konfidenz</span><span class="value" id="recConf">--</span></div>
            <div id="recMsg" style="margin-top:8px;font-size:0.85em;color:var(--tm);"></div>
        </div>
        <div class="card">
            <h3>Solfeggio Counter-Frequencies</h3>
            <ul class="freq-list" id="freqList"><li>Warte auf Daten...</li></ul>
        </div>
    </div>
    <h3 style="color:var(--primary);margin-bottom:8px;">Event Log</h3>
    <div id="log">Warte auf WebSocket-Verbindung...</div>
    <script>
        const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/api/v1/emf/ws';
        let ws, reconnectTimer;
        function connect() {
            document.getElementById('connStatus').className = 'conn-status conn-wait';
            document.getElementById('connStatus').textContent = 'Verbinde...';
            ws = new WebSocket(wsUrl);
            ws.onopen = () => {
                document.getElementById('connStatus').className = 'conn-status conn-ok';
                document.getElementById('connStatus').textContent = 'Verbunden';
                addLog('WebSocket verbunden: ' + wsUrl);
            };
            ws.onmessage = (evt) => {
                try { const d = JSON.parse(evt.data); updateUI(d); } catch(e) { addLog('Parse-Fehler: ' + e); }
            };
            ws.onclose = () => {
                document.getElementById('connStatus').className = 'conn-status conn-err';
                document.getElementById('connStatus').textContent = 'Getrennt';
                addLog('Verbindung getrennt. Reconnect in 5s...');
                reconnectTimer = setTimeout(connect, 5000);
            };
            ws.onerror = (e) => { addLog('WS Fehler: ' + e.type); };
        }
        function updateUI(d) {
            const emfIdx = d.emf_index || 0;
            document.getElementById('emfIndex').textContent = emfIdx.toFixed(4);
            document.getElementById('emfIndex').className = 'value ' + (emfIdx < 0.3 ? 'good' : emfIdx < 0.6 ? 'warn' : 'bad');
            document.getElementById('emfBar').style.width = (emfIdx * 100) + '%';
            document.getElementById('emfBar').style.background = emfIdx < 0.3 ? 'hsl(145 50% 40%)' : emfIdx < 0.6 ? 'hsl(35 85% 55%)' : 'hsl(0 65% 50%)';
            const ent = d.entropy_score || 0;
            document.getElementById('entropy').textContent = ent.toFixed(4);
            document.getElementById('entBar').style.width = (ent * 100) + '%';
            document.getElementById('jitter').textContent = (d.timing_jitter_ms || 0).toFixed(3) + ' ms';
            document.getElementById('gpuNoise').textContent = (d.gpu_noise || 0).toFixed(4);
            const sl = d.system_load || {};
            document.getElementById('sysLoad').textContent = ((sl.cpu_percent || 0) * 100).toFixed(0) + '% CPU / ' + ((sl.ram_percent || 0) * 100).toFixed(0) + '% RAM';
            document.getElementById('lnw').textContent = d.low_noise_window ? 'JA' : 'NEIN';
            document.getElementById('lnw').className = 'value ' + (d.low_noise_window ? 'good' : 'warn');
            const rec = d.recommendation || {};
            document.getElementById('recStatus').textContent = rec.recommendation || '--';
            document.getElementById('recStatus').className = 'value ' + (rec.recommendation === 'OPTIMAL' ? 'good' : rec.recommendation === 'AKZEPTABEL' ? 'warn' : 'bad');
            document.getElementById('recConf').textContent = ((rec.confidence || 0) * 100).toFixed(0) + '%';
            document.getElementById('recMsg').textContent = rec.message || '';
            const fl = document.getElementById('freqList');
            const cfs = d.counter_frequencies || [];
            if (cfs.length > 0) {
                fl.innerHTML = cfs.map(f => '<li><span class="hz">' + f.frequency_hz + ' Hz</span><span>' + f.description + '</span></li>').join('');
            }
            addLog('[' + (d.timestamp || new Date().toISOString()) + '] EMF=' + emfIdx.toFixed(3) + ' Ent=' + ent.toFixed(3));
        }
        function addLog(msg) {
            const el = document.getElementById('log');
            el.innerHTML += '<br>' + msg;
            el.scrollTop = el.scrollHeight;
        }
        connect();
    </script>
</body>
</html>
""")


@router.websocket("/emf/ws")
async def emf_websocket(websocket: WebSocket):
    """
    WebSocket fuer Echtzeit-EMF-Monitoring.
    Sendet alle 5 Sekunden ein aktualisiertes EMF-Profil an den Client.
    """
    await websocket.accept()
    logger.info("EMF WebSocket Client verbunden.")
    
    # Stelle sicher, dass EMF Compensator aktiv ist
    if not engine.emf_active:
        engine.enable_emf_compensation(continuous=False)
    
    try:
        while True:
            try:
                if engine.emf_compensator:
                    profile = engine.emf_compensator.profile_environment()
                    recommendation = engine.emf_compensator.get_timing_recommendation()
                    counters = engine.emf_compensator.get_counter_frequencies()
                    
                    payload = {
                        "type": "emf_update",
                        "timestamp": profile.get("timestamp"),
                        "emf_index": profile.get("composite_emf_index"),
                        "entropy_score": profile.get("entropy_score"),
                        "timing_jitter_ms": profile.get("timing_jitter_ms"),
                        "gpu_noise": profile.get("gpu_noise_factor"),
                        "low_noise_window": profile.get("low_noise_window"),
                        "system_load": profile.get("system_load"),
                        "recommendation": recommendation,
                        "counter_frequencies": counters,
                    }
                    
                    await websocket.send_text(json.dumps(payload, default=str))
                else:
                    await websocket.send_text(json.dumps({"type": "error", "message": "EMF Compensator nicht initialisiert"}))
            except Exception as inner_e:
                logger.error(f"EMF WebSocket Messfehler: {inner_e}")
                await websocket.send_text(json.dumps({"type": "error", "message": str(inner_e)}))
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("EMF WebSocket Client getrennt.")
    except Exception as e:
        logger.error(f"EMF WebSocket Fehler: {e}")


@router.websocket("/emf/client-sensor")
async def emf_client_sensor(websocket: WebSocket):
    """
    Remote Client Sensor Interface.
    Empfaengt Sensordaten vom Klienten-Geraet (Browser Audio API, GPS, HRV-Wearable)
    und integriert sie in die EMF-Kompensation auf dem Server.
    
    Client sendet JSON:
    {
        "type": "audio_spectrum" | "location" | "hrv" | "device_sensors",
        "data": { ... sensorspezifische Daten ... },
        "timestamp": "ISO-8601"
    }
    
    Server antwortet mit aktualisierten Kompensations-Empfehlungen.
    """
    await websocket.accept()
    logger.info("Client-Sensor WebSocket verbunden.")
    
    if not engine.emf_active:
        engine.enable_emf_compensation(continuous=False)
    
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                sensor_type = msg.get("type", "unknown")
                sensor_data = msg.get("data", {})
                
                response = {"type": "ack", "sensor": sensor_type}
                
                if sensor_type == "audio_spectrum" and engine.emf_compensator:
                    # Client sendet FFT-Spektrum seines Mikrofons
                    # Peak-Frequenzen deuten auf lokale EMF-Quellen hin
                    peaks = sensor_data.get("peak_frequencies", [])
                    noise_floor = sensor_data.get("noise_floor_db", -60)
                    
                    # Speichere als Remote-Messung im Compensator
                    if hasattr(engine.emf_compensator, '_remote_sensor_data'):
                        engine.emf_compensator._remote_sensor_data["audio"] = {
                            "peaks": peaks, "noise_floor": noise_floor,
                            "timestamp": msg.get("timestamp")
                        }
                    
                    response["message"] = f"Audio: {len(peaks)} Peaks empfangen"
                    
                elif sensor_type == "location":
                    # GPS-Position des Klienten fuer Geo-EMF-Korrelation
                    lat = sensor_data.get("lat", 0)
                    lon = sensor_data.get("lon", 0)
                    
                    if hasattr(engine.emf_compensator, '_remote_sensor_data'):
                        engine.emf_compensator._remote_sensor_data["location"] = {
                            "lat": lat, "lon": lon,
                            "timestamp": msg.get("timestamp")
                        }
                    
                    response["message"] = f"Location: {lat:.4f}, {lon:.4f}"
                    
                elif sensor_type == "hrv":
                    # HRV-Daten von Wearable (BLE Gateway)
                    rr_intervals = sensor_data.get("rr_intervals", [])
                    bpm = sensor_data.get("bpm", 0)
                    
                    if hasattr(engine.emf_compensator, '_remote_sensor_data'):
                        engine.emf_compensator._remote_sensor_data["hrv"] = {
                            "rr_intervals": rr_intervals, "bpm": bpm,
                            "timestamp": msg.get("timestamp")
                        }
                    
                    response["message"] = f"HRV: {bpm} BPM, {len(rr_intervals)} RR-Intervalle"
                
                elif sensor_type == "device_sensors":
                    # Geraete-Sensoren (Batterie, Bildschirmhelligkeit, Magnetometer)
                    if hasattr(engine.emf_compensator, '_remote_sensor_data'):
                        engine.emf_compensator._remote_sensor_data["device"] = {
                            **sensor_data,
                            "timestamp": msg.get("timestamp")
                        }
                    
                    response["message"] = "Device sensors empfangen"
                
                # Sende aktuelle Empfehlung zurueck
                if engine.emf_compensator:
                    response["recommendation"] = engine.emf_compensator.get_timing_recommendation()
                    response["emf_index"] = engine.emf_compensator.current_profile.get(
                        "composite_emf_index", 0) if engine.emf_compensator.current_profile else 0
                
                await websocket.send_text(json.dumps(response, default=str))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
            except Exception as inner_e:
                logger.error(f"Client-Sensor Verarbeitung: {inner_e}")
                await websocket.send_text(json.dumps({"type": "error", "message": str(inner_e)}))
    
    except WebSocketDisconnect:
        logger.info("Client-Sensor WebSocket getrennt.")
    except Exception as e:
        logger.error(f"Client-Sensor WebSocket Fehler: {e}")


# =========================================================================
# AMPLIFIER ENDPOINTS
# =========================================================================

@router.get("/amplifier/list")
async def list_amplifiers():
    """Listet alle verfuegbaren Resonanz-Verstaerker auf."""
    return {"amplifiers": engine.list_amplifiers(), "count": len(engine.amplifier_gen.amplifiers)}

@router.post("/amplifier/set/{amplifier_name}")
async def set_amplifier(amplifier_name: str):
    """Setzt den aktiven Amplifier fuer die Harmonisierung."""
    result = engine.set_amplifier(amplifier_name)
    if result:
        return {"status": "active", "amplifier": result["name"], "data": result}
    raise HTTPException(status_code=404, detail=f"Amplifier '{amplifier_name}' nicht gefunden")

@router.post("/amplifier/clear")
async def clear_amplifier():
    """Deaktiviert den aktiven Amplifier."""
    engine.clear_amplifier()
    return {"status": "cleared"}

@router.post("/amplifier/match")
async def match_amplifier(request: dict):
    """
    Berechnet die besten Amplifier fuer einen Klienten.
    
    Body: {"client_data": {...}, "focus": ["Heilung"], "top_n": 3}
    """
    client_data = request.get("client_data", {})
    focus_list = request.get("focus", [])
    top_n = request.get("top_n", 3)
    
    # Generiere Signatur
    sig = engine.signature_gen.generate_signature(client_data)
    matches = engine.get_amplifier_recommendation(sig, focus_list, top_n=top_n)
    
    return {"recommendations": matches, "client_frequency": sig.get("frequency")}

@router.post("/amplifier/add")
async def add_amplifier(request: dict):
    """
    Fuegt einen neuen Amplifier zur Registry hinzu.
    
    Body: {"id": "mein_stein", "data": {"name": "...", "category": "heilstein", "base_frequency_hz": 440}}
    """
    amp_id = request.get("id")
    amp_data = request.get("data", {})
    
    if not amp_id:
        raise HTTPException(status_code=400, detail="ID ist erforderlich")
    
    success = engine.amplifier_gen.add_amplifier(amp_id, amp_data)
    if success:
        return {"status": "added", "id": amp_id, "name": amp_data.get("name")}
    raise HTTPException(status_code=400, detail="Amplifier konnte nicht hinzugefuegt werden (Pflichtfelder pruefen)")
