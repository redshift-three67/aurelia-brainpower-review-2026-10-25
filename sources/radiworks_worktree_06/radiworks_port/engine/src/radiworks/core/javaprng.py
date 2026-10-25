"""Bitexakte Emulation von java.util.Random (LCG, Java-Spezifikation).

Der Original-Kern zieht ueberall `new Random(hotbit).nextInt(bound)` — die
zweite Stufe ist also die von der JLS/JDK-Spezifikation festgelegte 48-Bit-LCG.
Um den Python-Port bitidentisch zum Java-Original zu machen (Goldwert-Test),
wird genau dieser Generator hier emuliert — nicht Mersenne-Twister.

Spezifikation (java.util.Random):
    seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)
    next(bits): seed = (seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
                return seed >>> (48 - bits)      # als int der Breite `bits`
    nextInt(bound): siehe JDK-Quelltext (Potenz-2-Pfad + Reject-Schleife)
"""

from __future__ import annotations

MULTIPLIER = 0x5DEECE66D
ADDEND = 0xB
MASK_48 = (1 << 48) - 1


class JavaRandom:
    def __init__(self, seed: int) -> None:
        # Java: this.seed = (seed ^ MULTIPLIER) & mask — funktioniert mit
        # negativen Seeds identisch (Python-Zweierkomplement).
        self._seed = (seed ^ MULTIPLIER) & MASK_48

    def next_bits(self, bits: int) -> int:
        self._seed = (self._seed * MULTIPLIER + ADDEND) & MASK_48
        return self._seed >> (48 - bits)

    def next_int32(self) -> int:
        """Java nextInt() — vorzeichenbehaftet."""
        value = self.next_bits(32)
        return value - (1 << 32) if value >= (1 << 31) else value

    def next_int(self, bound: int) -> int:
        """Java nextInt(bound) — inklusive Potenz-2-Schnellpfad und Reject."""
        if bound <= 0:
            raise ValueError("bound must be positive")
        if bound & (bound - 1) == 0:  # Potenz von 2
            return (bound * self.next_bits(31)) >> 31
        while True:
            bits = self.next_bits(31)
            value = bits % bound
            if bits - value + (bound - 1) < (1 << 31):
                return value

    def next_boolean(self) -> bool:
        return self.next_bits(1) != 0
