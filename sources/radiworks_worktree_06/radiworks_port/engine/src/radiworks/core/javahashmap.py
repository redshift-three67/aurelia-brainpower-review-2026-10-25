"""Emulation der Java-HashMap-Iterationsreihenfolge für String-Schlüssel.

Das Original iteriert `ratesValues.keySet()` (HashMap<String, Integer>) in
Hash-Reihenfolge — nicht in Einfügereihenfolge. Da die Anreicherungsphase
rate für rate in dieser Reihenfolge erhöht, bestimmt die Reihenfolge, welcher
Rate welcher Ziehungswert zufließt. Für den bitidentischen Goldwert-Abgleich
wird die JDK-Reihenfolge hier exakt simuliert:

- String.hashCode: s[0]*31^(n-1) + ... (32-Bit, Overflow-Wrap)
- spread: h ^ (h >>> 16)
- Bucket: (cap - 1) & spread
- Default cap 16, Loadfaktor 0.75, Verdopplung bei size > threshold,
  Split in Low-/High-Bins unter Erhaltung der relativen Ordnung.

Annahme (wird geprüft): kein Bin erreicht TREEIFY_THRESHOLD (8) — bei
Goldwert-Größenordnungen (n <= ein paar hundert) erfüllt.
"""

from __future__ import annotations

LOAD_FACTOR = 0.75
TREEIFY_THRESHOLD = 8


def java_string_hash(value: str) -> int:
    """32-Bit-String.hashCode (Bitmuster als unsigned)."""
    h = 0
    for char in value:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h


def _spread(h: int) -> int:
    return h ^ (h >> 16)


def java_hashmap_string_order(insertion_order: list[str]) -> list[str]:
    """Iterationsreihenfolge einer HashMap<String,?> nach den Einfügungen."""
    capacity = 16
    threshold = int(capacity * LOAD_FACTOR)
    table: dict[int, list[str]] = {}
    size = 0
    seen: set[str] = set()

    def resize() -> None:
        nonlocal capacity, threshold, table
        old_capacity = capacity
        old_table = table
        capacity *= 2
        threshold = int(capacity * LOAD_FACTOR)
        table = {}
        for index, bucket in old_table.items():
            low: list[str] = []
            high: list[str] = []
            for key in bucket:
                spread = _spread(java_string_hash(key))
                if spread & (capacity - 1) == index:
                    low.append(key)
                else:
                    high.append(key)
            if low:
                table[index] = low
            if high:
                table[index + old_capacity] = high

    for key in insertion_order:
        if key in seen:
            continue  # put auf existierenden Schlüssel ändert die Ordnung nicht
        seen.add(key)
        spread = _spread(java_string_hash(key))
        bucket_index = spread & (capacity - 1)
        table.setdefault(bucket_index, []).append(key)
        size += 1
        if size > threshold:
            resize()

    ordered: list[str] = []
    for index in sorted(table):
        ordered.extend(table[index])
    max_bin = max((len(b) for b in table.values()), default=0)
    if max_bin >= TREEIFY_THRESHOLD:
        raise AssertionError(
            f"HashMap-Simulation: Bin mit {max_bin} Einträgen — Treeify würde greifen; "
            "Goldwert-Test mit kleinerer Ratezahl wiederholen."
        )
    return ordered
