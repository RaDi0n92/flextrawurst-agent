# Z.ai / GLM API Anschlussnotiz

Stand: 2026-07-05.

## Was sicher ist

Z.ai dokumentiert GLM als OpenAI-kompatibel.

Normale Open-Platform-Beispiele nutzen:

```text
https://api.z.ai/api/paas/v4/
```

Coding-Plan-Beispiele nutzen:

```text
https://api.z.ai/api/coding/paas/v4
```

Anthropic-kompatibel fuer Coding-Plan:

```text
https://api.z.ai/api/anthropic
```

## Wichtig fuer diesen Werkraum

Keine API-Keys in Dateien schreiben.

Keine Konfiguration aendern, nur weil ein Modell mehr Kontext koennte. Daniel hat aktuell den freien Key / Free-Tier genannt und dort nur ca. 8000 Kontext beobachtet.

## GML-Konsequenz

Dieses Zuhause ist nicht auf grosses Kontextfenster angewiesen. Wenn spaeter ein groesseres Modell oder Coding-Plan aktiv wird, kann GML mehr lesen, aber die Startarchitektur bleibt trotzdem knapp.

