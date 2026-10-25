# Sicherheitsvermerk — nicht extern freigeben

Die unveränderten V3-Quelldateien enthalten mindestens ein im Klartext
wiedergegebenes Datenbankgeheimnis und konkrete interne Betriebsdetails.

Daraus folgen zwingend:

1. Der Ordner `source/` bleibt lokal und vertraulich.
2. Er darf weder nach GitHub übertragen noch an ein externes LLM, einen
   Reviewer oder einen Dritten weitergegeben werden.
3. Vor jeder späteren Veröffentlichung ist eine separate, überprüfte
   Sanitierung erforderlich.
4. Das betroffene Datenbankgeheimnis ist als offengelegt zu behandeln und in
   einem separat freigegebenen Wartungsfenster zu rotieren.
5. Die sanitierte Codex-Verifikation wiederholt den geheimen Wert bewusst
   nicht.

Dieser Vermerk ersetzt keine Geheimnisrotation und keine Zugriffskontrolle.
Die vollständige Originalquelle wurde ausschließlich zur geforderten lokalen
Provenienz erhalten.
