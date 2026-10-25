"""VirtualEmitter — 1:1-Port der Hardware-Broadcast-Choreografie als Events.

Referenz: BroadCastService.broadcastNow (FUNKTIONSANALYSE §5.3, Java-Zeile
54-87). Der Original-Mechanismus wird vollstaendig in Software erhalten: die
Signatur wird Zeichen fuer Zeichen in Ziffern zerlegt, jede Ziffer beleuchtet
bestimmte LED-Gruppen (Clear-Modus: nur Ultraviolett), mit 25-ms-Blinkrhythmus
und Repeat-Zyklen. Der Kernel emittiert diese Choreografie als strukturierte
Events ueber den WebSocket-Fachkanal — **keine** physische Aktivierung
(isHardwareActivatable: false, Aurelia Hard Rules 4/10/11).

Ein spaeterer aurelia-emitterd-Connector kann diese Schritte 1:1 auf echte
Hardware abbilden (Lease -> Arming -> ACK); die Semantik ist identisch zur
Pi-LED-Ansteuerung des Originals.
"""

from __future__ import annotations

from dataclasses import dataclass

# BroadCastService-Konstruktor (Java-Zeile 26-46) — Zuordnung Ziffer -> LED-Gruppe.
# WICHTIG (exakte Original-Semantik): Die Liste "ultraviolet" [1,2,3,5,8] wird in
# broadcastNow NIEMALS gelesen (tote Daten im Original). Der Clear-Modus ruft
# blinkLED(data, n, this.infrared, AetherOnePins.ULTRAVIOLET) auf — also die
# ZAHLENLISTE 'infrared' [1,6] mit dem PIN ULTRAVIOLET.
LED_GROUPS: dict[str, tuple[int, ...]] = {
    "ultraviolet": (1, 2, 3, 5, 8),  # Original-Konstruktor, in broadcastNow ungenutzt
    "reds": (2, 5),
    "greens": (3, 7),
    "blues": (4, 8),
    "whites": (0, 9),
    "infrared": (1, 6),
}

# LED-Pins des Originals in Norm- und Clear-Modus
NORMAL_GROUPS = ("whites", "infrared", "reds", "greens", "blues")
CLEAR_PIN = "ultraviolet"
CLEAR_NUMBERS = LED_GROUPS["infrared"]  # Zahlenliste des Clear-Aufrufs

# BroadCastData-Defaults des Originals
DEFAULT_DELAY_MS = 25
DEFAULT_REPEAT = 1


def clean_signature(signature: str) -> str:
    """Java-Zeile 58: Entfernt '(', ')', '-', Leerzeichen."""
    for char in ("(", ")", "-", " "):
        signature = signature.replace(char, "")
    return signature.strip()


@dataclass
class EmitterStep:
    """Ein Zeichen-Schritt der Choreografie (Java-Zeile 60-83)."""

    position: int
    char: str
    digit_sequence: list[int]  # Ziffern von abs(ord(c) - 48), mehrstellig moeglich
    lit_groups: list[list[str]]  # LED-Gruppen je Teilschritt (parallel zu digit_sequence)
    delay_ms: int
    repeat: int

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "char": self.char,
            "digitSequence": self.digit_sequence,
            "litGroups": self.lit_groups,
            "delayMs": self.delay_ms,
            "repeat": self.repeat,
        }


def _groups_for_digit(digit: int, *, clear: bool) -> list[str]:
    """Java broadcastNow-Zeile 70-79 mit exakter Pin-/Zahlenlisten-Trennung."""
    if clear:
        # blinkLED(data, n, this.infrared, AetherOnePins.ULTRAVIOLET)
        return [CLEAR_PIN] if digit in CLEAR_NUMBERS else []
    return [group for group in NORMAL_GROUPS if digit in LED_GROUPS[group]]


def emitter_sequence(
    signature: str, *, clear: bool = False, delay_ms: int = DEFAULT_DELAY_MS, repeat: int = DEFAULT_REPEAT
) -> list[EmitterStep]:
    """Port von broadcastNow: repeat x Zeichen, je Zeichen abs(ord(c)-48).

    Mehrstellige Werte werden ziffernweise abgearbeitet (Java-Zeile 67-70:
    String.valueOf(i) -> je Zeichen parseInt).
    """
    cleaned = clean_signature(signature)
    steps: list[EmitterStep] = []
    for position, char in enumerate(cleaned):
        value = abs(ord(char) - 48)
        digits = [int(d) for d in str(value)]
        steps.append(
            EmitterStep(
                position=position,
                char=char,
                digit_sequence=digits,
                lit_groups=[_groups_for_digit(d, clear=clear) for d in digits],  # type: ignore[arg-type]
                delay_ms=delay_ms,
                repeat=repeat,
            )
        )
    return steps


def sequence_to_dict(steps: list[EmitterStep]) -> list[dict]:
    return [step.to_dict() for step in steps]
