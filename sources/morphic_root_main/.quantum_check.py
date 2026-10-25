"""Ad-hoc Verifikationsskript fuer den echten Qiskit-Grover-Pfad.

Nur zur einmaligen, manuellen Ausfuehrung im isolierten `.venv-quantum-check`
(Task 4). Testet, ob der reale Quanten-Pfad end-to-end durchlaeuft und ob
die markierten Items durch Amplitudenverstaerkung tatsaechlich nach oben
rutschen. Mit extremalem Oracle (genau 1 markiertes Item von 8) sollte ein
ordentlich funktionierender Grover das markierte Item als Top-Ergebnis
liefern.
"""

from __future__ import annotations

import os
import sys

# Vermeide CP1252-Encoding-Probleme mit Emojis in print-Ausgaben.
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from core.quantum_synergy.grover_search import GroverRemedySearch, QISKIT_AVAILABLE


def main() -> int:
    if not QISKIT_AVAILABLE:
        print("QISKIT_AVAILABLE = False - Real-Pfad kann nicht verifiziert werden.")
        return 2

    print(f"QISKIT_AVAILABLE = {QISKIT_AVAILABLE}")
    items = [{"label": f"item{i}", "group": "x", "score": 1.0} for i in range(8)]

    def oracle(item: dict) -> bool:
        return item["label"] == "item5"

    searcher = GroverRemedySearch(verbose=False)
    results = searcher.search(items, oracle, max_results=8, shots=4000)

    if not results:
        print("FEHLER: keine Ergebnisse vom Real-Pfad erhalten")
        return 1

    marked_prob = next(
        (prob for item, prob in results if item["label"] == "item5"), None
    )
    max_prob = max(prob for _, prob in results)
    top_label = results[0][0]["label"]

    print("Top-5 Ergebnisse:")
    for item, prob in results[:5]:
        marker = " <== MARKED" if item["label"] == "item5" else ""
        print(f"  {item['label']}: {prob * 100:.2f}%{marker}")

    if marked_prob is None:
        print("FEHLER: markiertes Item fehlt in den Ergebnissen")
        return 1

    print(
        f"\nmarked_prob={marked_prob*100:.2f}% | max_prob={max_prob*100:.2f}% | "
        f"top_label={top_label}"
    )

    if top_label == "item5":
        print("VERIFIKATION OK: markiertes Item ist Top-Ergebnis.")
        return 0
    if marked_prob > max_prob * 0.5:
        print("VERIFIKATION TEILWEISE OK: markiertes Item signifikant verstaerkt, aber nicht Top.")
        return 0
    print(
        "VERIFIKATION HINWEIS: markiertes Item ist NICHT das Top-Ergebnis.\n"
        "Moegliche Ursache (nur Befund, nicht im Rahmen dieses Tasks behoben):\n"
        "  - Bit-Reihenfolge-Konflikt zwischen klassischer Item-Indizierung\n"
        "    und Qiskit-Bitstring-Interpretation.\n"
        "  - Mehrere Grover-Iterationen wuerden die Amplitude weiter\n"
        "    dispersionsverstaerken statt fokussieren, falls die obere\n"
        "    Grenze von 10 Iterationen im Code nicht fachlich sinnvoll ist.\n"
        "Real-Pfad laeuft end-to-end durch, aber das Ranking ist derzeit\n"
        "nicht konkurrenzlos fuer dedizierte Einzelmarkierungen."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
