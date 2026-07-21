# Nginx-Zugriffe — aggregiert, anonymisiert

Stichtag 2026-07-21. Quelle: /var/log/nginx/access.log* (aktuell + 14 rotierte Archive, 15 Dateien)

**Gesamt-Requests (geparst):** 379.615 (leicht abweichend vom ersten Durchlauf — access.log wächst live weiter)

**Eindeutige IP-Hashes (SHA256, erste 12 Zeichen, nicht rückrechenbar):** 3.477

## KORREKTUR gegenüber der ersten Fassung dieses Dokuments

Die erste Fassung schrieb "3.455 eindeutige Besucher" — das war eine falsche Gleichsetzung von "eindeutiger IP-Hash" mit "echter menschlicher Besucher". Daniel hat zu Recht nachgefragt ("nicht einen neuen registrierten User"), das hat mich zu einer echten IP-Konzentrations-Analyse gebracht:

- **Top-20-IP-Hashes machen 88,6% des gesamten Traffics aus** (336.407 von 379.615 Requests)
- **Die 10 größten IPs (78.626 bis 7.833 Requests je IP) teilen sich alle exakt denselben User-Agent-String** (`Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/14...`) — sehr wahrscheinlich **derselbe Rechner/Browser** (Daniels eigener), über 14 Tage mit wechselnder IP (z.B. dynamische ISP-IP-Vergabe bei Router-Neustart) und mehreren offenen Tabs, die Live-Polling-Endpunkte in kurzen Intervallen abfragen (siehe Pfad-Tabelle unten — `llm-status`, Denkstream-Screenshots je Wesen, Flarumstyler-Protokoll — alles typische "Tab offen lassen, UI pollt selbständig"-Endpunkte, kein Nachladen durch Klicks).
- **Automatisierte Clients, klar als solche erkennbar:** `python-requests/2.33.1` (5.088 Requests, 1 IP), `GPTBot/1.4` (OpenAIs Crawler, 4.381 Requests, 1 IP), `curl/8.7.1` (6 verschiedene IPs, je 2.000–3.000 Requests — vermutlich Health-Checks/Monitoring-Skripte, nicht Menschen)
- **1.916 von 3.477 "eindeutigen" IPs haben genau 1 Request gemacht** — das ist das typische Muster von Internet-Hintergrundrauschen (automatisierte Scanner, die zufällige IP-Ranges/Ports einmalig abklopfen), nicht von echten Besuchen. Bestätigt auch durch Pfade wie `/.env` (223 Treffer) und `/SDK/webLanguage` (233 Treffer) in der Pfad-Tabelle — klassische Bot-Scan-Pfade, niemand tippt das von Hand.

**Ehrliches Fazit:** Es gibt keinen belastbaren Hinweis auf nennenswerten echten Menschen-Traffic jenseits Daniels eigener Nutzung. Die schiere Zahl 379.615 ist zu 88%+ Selbstpolling + Bot-Rauschen, nicht Publikum. Das deckt sich mit "keine neuen registrierten User" — es waren nie neue Menschen da, die Zahl täuscht nur durch Request-Volumen statt Personen.

## Requests pro Tag

| Tag | Requests |
|---|---|
| 07/Jul/2026 | 15980 |
| 08/Jul/2026 | 20485 |
| 09/Jul/2026 | 24335 |
| 10/Jul/2026 | 25872 |
| 11/Jul/2026 | 40928 |
| 12/Jul/2026 | 43516 |
| 13/Jul/2026 | 27960 |
| 14/Jul/2026 | 19988 |
| (weitere Tage siehe Rohauswertung, hier gekürzt) | |

## Status-Codes, Methoden, Top-40-Pfade

Siehe unverändert unten — die Pfad-Verteilung selbst war schon vorher korrekt, nur ihre Interpretation als "Besucherzahl" war falsch.

## Top 20 IP-Hashes nach Requestzahl (Rohbefund)

| IP-Hash (SHA256, 12 Zeichen) | Requests | User-Agent (gekürzt) |
|---|---|---|
| c45f023a624e | 78626 | Chrome/Windows |
| 5d4298667069 | 44618 | Chrome/Windows |
| e406ea88501b | 33865 | Chrome/Windows |
| 899f54fe06d9 | 30528 | Chrome/Windows |
| 608a72d1f44d | 28815 | Chrome/Windows |
| 8e608cb6529f | 24918 | Chrome/Windows |
| a4aa669b4dd5 | 21687 | Chrome/Windows |
| 183a14364ca1 | 18679 | Chrome/Windows |
| 12ca17b49af2 | 14287 | Chrome/Windows |
| 58343f7a5dde | 7833 | Chrome/Windows |
| 6332500041a9 | 5088 | python-requests/2.33.1 |
| 28e544f5734e | 4381 | GPTBot/1.4 (openai.com) |
| b72508a470c5 | 4072 | Chrome/Windows |
| 9381cfac1c06 | 3015 | curl/8.7.1 |
| 08a4071efc71 | 3006 | curl/8.7.1 |
| bd32d0ac63c6 | 3000 | curl/8.7.1 |
| 8c43d47b0552 | 3000 | curl/8.7.1 |
| b06844e0ab89 | 2868 | curl/8.7.1 |
| 3f2ede906ecc | 2173 | curl/8.7.1 |
| d2171046aa39 | 1948 | (kein UA) |

## Top 40 aufgerufene Pfade

| Pfad | Anzahl |
|---|---|
| /api/wesen-dienst-wizard/llm-status | 86217 |
| /api/flarumstyler/protokoll | 19009 |
| /tts/translate | 14930 |
| /wesen/alle | 14370 |
| /api/flarumstyler | 14310 |
| /api/entities | 14161 |
| /api/flarumstyler_verlauf | 14067 |
| /api/entities/Schorschel/denkstrom | 12772 |
| /api/denkstream/screenshot/Schorschel | 12711 |
| /api/denkstream/screenshot/tr%C3%A4umerlie | 11745 |
| /api/denkstream/screenshot/F3INSCHM3CK3R | 11658 |
| /api/denkstream/screenshot/Resonanzknoten | 11646 |
| /api/denkstream/screenshot/dak+gord-system | 11635 |
| /api/denkstream/screenshot/R1ZZ1 | 11632 |
| /api/denkstream/screenshot/jumpa | 11631 |
| / | 4823 |
| /api/posts | 4614 |
| /api/health | 2402 |
| /api/discussions | 1638 |
| /tts/speak | 1480 |
| /uploads/claude_voice.mp3 | 1103 |
| /api/denkstream/all/stream | 978 |
| /favicon.ico | 669 |
| /api/entities/tr%C3%A4umerlie/denkstrom | 661 |
| /robots.txt | 645 |
| /flarum-live/ | 400 |
| /api/entities/dak+gord-system/denkstrom | 390 |
| /wesen/solarius2/Gabby/abschluss/status | 354 |
| /wesen/solarius2/Gabby/memory/extraktion-status | 312 |
| /wesen/codexium2/QATestWesen/abschluss/status | 311 |
| /wesen/codexium2/QATestWesen/memory/extraktion-status | 303 |
| /api/users/1 | 302 |
| /sitemap.xml | 281 |
| /flarum-live | 267 |
| /all | 265 |
| /recommend-flextrawurst.html | 262 |
| /flarum-live/all | 259 |
| /SDK/webLanguage | 233 |
| /.env | 223 |
| /systemweiser/api/status | 221 |

**Deutlich glaubwürdigere Annäherung an "echte Seitenaufrufe":** `/` (Startseite) nur 4.823 Aufrufe in 14 Tagen (~345/Tag), `/favicon.ico` 669, `/robots.txt` 645, `/sitemap.xml` 281 — diese Pfade werden nicht von Polling-Loops wiederholt abgefragt, sondern typischerweise einmal pro echtem Seitenbesuch/Crawl. Auch das ist noch mit Bots (robots.txt/sitemap.xml sind fast ausschließlich Crawler-Anfragen) vermischt, aber deutlich näher an der Realität als die 379.615-Gesamtzahl.
