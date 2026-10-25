# Phase 2 – Betriebsartentscheidung

**Entscheidung:** Variante A – lokaler Einoperator

**Zeitpunkt:** 2026-07-10

## Begründung

Der verifizierte aktuelle Betrieb ist lokal auf `127.0.0.1`; die vorhandenen Listener lagen auf Loopback (`8000`, `8090`). Ein OIDC-/SSO- und persistentes Mehrmandantensystem ohne bereitgestellten IdP, TLS-/Proxy-Grenze und Rollenmodell wäre keine belastbare Sicherheitsimplementierung.

## Verbindliche Grenze für die nächste Umsetzung

1. Der Standardbetrieb bleibt ausschließlich Loopback.
2. Nicht-Loopback-Bindings müssen explizit als unsicherer/noch nicht freigegebener Netzwerkmodus verweigert werden, bis Variante B mit IdP, TLS, zentraler Principal-Ableitung und Tenant-/Owner-Autorisierung umgesetzt ist.
3. Kein frei wählbarer Browserwert oder Environment-String wird als Ersatz für eine Benutzeridentität oder Multitenancy bezeichnet.
4. Die Projektkommunikation bleibt: lokaler Operator-Prototyp, nicht für externen Mehrbenutzerbetrieb freigegeben.

## Abgrenzung

Diese Entscheidung implementiert noch kein Pseudo-RBAC. Sie schafft zuerst eine ehrliche und fail-closed Deploymentgrenze. Variante B bleibt ein eigenständiges Architektur- und Integrationsgate.
