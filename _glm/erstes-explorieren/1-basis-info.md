# Flextrawurst - Erstes Explorations-Dokument

## Historische Erkenntnisse

### Projekt-Identität
- **Autor:** Daniel (VPS-Besitzer)
- **Typ:** Eigenwilliges, tiefgründiges Systemprojekt, nicht von KI entwickelt
- **Status:** VPS-basiert, Preview Server läuft auf localhost:8787
- **Technologie:** Node.js mit TypeScript (module type), benutzt `--experimental-strip-types` für Tests

### Architektur-Highlights
- **Kernel-Struktur:** 45+ Unterverzeichnisse
- **Schicht-System:** Weltlauf mit Ringen 1-23+
- **Verschiedene Zustände:** Runtime, Governance, Preview, Process-Camera
- **Globale Komponenten:** Audit, Gate, Lock, Matrix-Systeme

---

## Zentrale Komponenten

### 1. Weltengine (world_engine)
- Tick-System zur Zyklischen Ausführung
- Presence Pulse für Entitäts-Aktivierung
- State Transitions für Zustandsänderungen
- Laufzeit-Pipeline für Welt-Updates

### 2. Weltlauf (worldrun)
- Command Handling mit Bridge zu Governance
- Audit-System für alle Operationen
- Snapshot-Fähigkeit für Wiederherstellung
- Transition-System für Zustandswechsel
- Gate-System zur validierung von Operationen

### 3. Governance-System
- **global_lock:** Globaler Zustands-Blockierer
- **governance_matrix:** Strukturierte Entscheidungsfindung
- **approval_levels:** Mehrstufige Genehmigungen
- **governance_gate:** Validierung von Operationen
- **governance_intent_bridge:** Verbindung zu Admin-Intents
- **governance_ledger_bridge:** Buchführungs-System

### 4. Admin-System
- Rollen: daniel_root, operator, observer, system_process
- Command Intents für Features, Import, Weltlauf-Steuerung
- Permissions für Activation, Pause, Resume, Freeze, Stop

### 5. Sicherheits-Komponenten (historisch gelöst)
- **concept_guard:** Konzept-Validierung
- **integrity:** Integritäts-System
- **provenance:** Herkunftsnachweis
- **replay:** Wiederholbarkeit von Zuständen
- **audit:** Komplette Operation-Audit-Spur

### 6. Weitere interessante Bereiche
- **worldblick:** Static Preview der Welt
- **process_camera:** Kindliche, erdachte Prozess-Kamera
- **organ_dock:** Blueprint-Systeme
- **world_camera:** Visuelle Sicht auf die Welt
- **concepts:** Future Concepts
- **slots:** Zustands-Slots für temporäre Werte

---

## Historische Sicherheitsprobleme (wurden gelöst)

### Probleme (2026-05-30)
- 10+ Secrets in world-readable Systemdateien
- Kein Rate Limiting
- Veraltete TLS-Versionen
- Fehlende Security Headers

### Lösungen
- Audit- und Gate-Systeme implementiert
- Konzepte mit concept_guard, integrity, provenance
- Governance-Matrix mit approval_levels und global_locks

---

## Server-Status
- **Server:** Preview Server
- **Port:** 8787 (localhost)
- **Zugriff:** http://localhost:8787/, http://127.0.0.1:8787/
- **Wichtig:** Externe Erreichbarkeit erfordert Port/Firewall/SSH-Tunnel Konfiguration
- **Script:** `npm run worldblick` für Preview-Build, `npm run process-camera` für Process-Camera

---

## Offene Fragen
1. Wie entstehen die Ringe?
2. Was ist der Unterschied zwischen Runtime-Ring und Governance-Ring?
3. Welches Problem soll das System lösen?
4. Ist es ein Gedankenexperiment, Gedächtnis-System, Simulation oder was anderes?
