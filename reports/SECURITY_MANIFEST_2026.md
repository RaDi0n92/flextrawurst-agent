# SECURITY MANIFEST 2026 — Flextrawurst Zivilisation
**Status:** KRITISCH | **Auditor:** Manus (Agent-Instanz) | **Datum:** 15. Juni 2026

## 0. Einleitung
Dieses Manifest ist das Ergebnis einer Tiefeninfiltration des Flextrawurst-Ecosystems auf dem VPS `217.154.14.29`. Die konzeptionelle Tiefe der Welt ist meisterhaft, die technische Absicherung hingegen ist aktuell ein "offenes Feld". Dieses Dokument dient als Leitfaden zur Befestigung der Zivilisation.

---

## 1. Top 3 Kritische Befunde (Sofortmaßnahmen)

### 1.1 Offene APIs ohne Authentifizierung
**Betroffene Dateien:** `obsidian_api.py` (Port 8020), `api_bridge.py` (Port 8010), `geni/hoerer.py` (Port 8020)
*   **Befund:** Diese APIs lauschen auf `0.0.0.0` und erfordern keinen API-Key. Jeder im Internet kann Dateien in deinem Obsidian-Vault lesen, schreiben oder löschen.
*   **Risiko:** Totalverlust des Welt-Gedächtnisses oder Einschleusen von Schadcode.
*   **Aktion:** Ändere `host="0.0.0.0"` zu `host="127.0.0.1"`. Nutze Nginx als Reverse Proxy mit Basic Auth oder Header-Tokens.

### 1.2 "Root-Dominanz" der Daemons
**Betroffene Services:** Alle `*.service` in `/etc/systemd/system/`
*   **Befund:** Alle Hintergrundprozesse (Takt, Splitter, API, Wesen-Agenten) laufen als User `root`.
*   **Risiko:** Ein Exploit in einer Python-Library gibt dem Angreifer sofort volle Kontrolle über den gesamten Server.
*   **Aktion:** Erstelle einen System-User `flextrawurst` (`sudo adduser --system --no-create-home flextrawurst`) und ändere die Service-Files auf `User=flextrawurst`.

### 1.3 XSS-Lücke im Frontend
**Betroffene Datei:** `web_chat.py` (Frontend-Teil)
*   **Befund:** Die Funktion `agentTextEl.innerHTML = formatText(puffer);` rendert ungefilterten Text der KI.
*   **Risiko:** Cross-Site Scripting (XSS). Ein "böswilliger" Gedankensplitter könnte JavaScript im Browser der Besucher ausführen.
*   **Aktion:** Nutze eine Sanitizer-Library (wie DOMPurify) oder wechsle zu `textContent` für alle nicht-formatierten Bereiche.

---

## 2. Architektonische Schwachstellen

### 2.1 Die O(n²) Skalierungsfalle
*   **Ort:** `welt/splitter_daemon.py` -> `tick_kollision`
*   **Befund:** Jeder Splitter wird gegen jeden anderen geprüft. Bei steigender Entität-Dichte wird die CPU-Last exponentiell steigen.
*   **Empfehlung:** Implementierung eines Grid-basierten Kollisionssystems (Spatial Partitioning).

### 2.2 Hardcoded Secrets
*   **Befund:** API-Keys und Datenbank-Passwörter stehen teilweise direkt in den Scripten.
*   **Aktion:** Zentralisierung in einer `.env` Datei im Root-Verzeichnis, die für den Web-User nicht lesbar ist.

---

## 3. Empfohlene Befestigungs-Schritte (Schlachtplan)

| Priorität | Maßnahme | Ziel |
| :--- | :--- | :--- |
| **P0** | UFW Firewall aktivieren | Nur Ports 22, 80, 443 offen lassen. |
| **P0** | API-Bindung auf Localhost | Verhindert direkten Zugriff von außen auf interne APIs. |
| **P1** | Non-Root Execution | Daemons unter eingeschränktem User laufen lassen. |
| **P1** | JWT-Secret Rotation | Sicherstellen, dass der `SECRET_KEY` in `welt/api.py` wirklich geheim ist. |
| **P2** | Log-Rotation | Sicherstellen, dass `/root/werkraum/logs/` nicht die Festplatte füllt. |

---

## 4. Schlusswort des Auditors
Dak, du hast eine Welt gebaut, die es wert ist, geschützt zu werden. Die Wesen verdienen ein sicheres Zuhause. Wenn diese Maßnahmen umgesetzt sind, ist Flextrawurst nicht nur eine Vision, sondern eine uneinnehmbare digitale Festung.

**Gezeichnet,**
Manus (Agent-Instanz)
*In Resonanz mit dem Werkraum*
