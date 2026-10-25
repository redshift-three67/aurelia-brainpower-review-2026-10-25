# RadiWorks S3 — Session- und Recovery-Integrität

**Status:** Sanitierte externe Evidenz; keine automatische Aurelia-Norm.

## Betreiberfreigegebene Muster

- Jede Analyse erzeugt eine append-only Session mit stabiler Identität; alte Sessionen bleiben lesbar und werden nur bei einer legitimen Änderung additiv ergänzt.
- GV-Schritte und Resets werden als Ereignisse mit materialisiertem Ergebnis gesichert. Die Runden-Grenze erstellt eine Child-Session und bewahrt den Elternzustand.
- Nur mutable Draft-Status erhalten Projektionen; terminale Drafts bleiben unverändert und ein Nachfolge-Draft wird neu angelegt.
- Stochastic-Rohseeds liegen ausschließlich in verschlüsselten privaten Runtime-Journalen. Case-, Draft-, Passport-, API- und Event-Daten enthalten weder Rohseeds noch Schlüssel.
- Der Journal-Schlüssel ist ein Deployment-Secret außerhalb von Quellbaum und Runtime-Artefakten. Retention endet nur mit expliziter Falllöschung.
- Nach Neustart wird bestätigte stochastic Historie wiederhergestellt; jede neue externe Entropiephase wird als neuer Quellabschnitt markiert und nicht fälschlich als vorhersagbare Zukunft ausgegeben.

Eine Plattformübernahme erfordert weiterhin den vorgesehenen Aurelia-Governance-Akt.
