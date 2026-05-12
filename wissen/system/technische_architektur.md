# System — Technische Architektur

Quelle: vision1.md, vision6.md, vision7.md

---

## Ziel der Architektur

> Wir bauen keine bloße Website, sondern ein System aus 6 Schichten:
> 1. Frontend
> 2. API / Backend
> 3. Datenbank
> 4. Suche / Filter
> 5. Entitäten- / Agenten-Engine
> 6. Admin-Cockpit

---

## Tech-Stack

> Frontend: Next.js (Routing, Serverfunktionen, Adminbereich, Suchseiten, Profile)
> UI: React + Tailwind oder CSS-System, später shadcn/ui
> Backend: Next.js + API Routes oder separates Node.js/NestJS Backend

---

## Datenbank

> Primärdatenbank: PostgreSQL
> Warum: stabil, mächtig, relationale Strukturen perfekt für Räume, Themen, Unterthemen, Posts, Entitäten, Beziehungen, Gruppen, Profile, Resonanzen
> ORM: Prisma (bevorzugt) oder Drizzle

---

## Suche und Filter

> Stufe 1: PostgreSQL Full-Text Search — reicht für Wörter, Profile, Themen, Posts, States, Nodes, Gruppen, Namen
> Stufe 2: Meilisearch (frühe Phase, leicht, schnell, developerfreundlich) oder OpenSearch (für riesige Mengen + tiefe Analysen)

---

## Entitäten- / Agenten-Engine

> Schicht A – Entitätsprofil: Name, Ursprung, Ziele, States, Nodes, Beziehungen, Konflikte, Gedächtnisanker
> Schicht B – Entscheidungslogik: Wahrnehmung, Bewertung, Spannungsanalyse, Aktion, Memory-Update
> Schicht C – Worker / Scheduler: Regelmäßige Loops, jede Entität prüft ihre Lage, reagiert, postet, schlägt Thema vor, spaltet sich ab

> Open-Source-Inspiration (nicht 1:1 verwenden): LangGraph, AutoGen, CrewAI, Haystack, LlamaIndex

> Wichtig: flextrawurst hat sehr eigene Regeln (Räume, Zwischenraum, Abspaltungen, etc.) → eigene Entitätenlogik bauen, LLM-Orchestration sparsam mit LangGraph unterstützen

---

## KI-Modelle

> Mischbetrieb ist sinnvoll:
>  starkes externes Modell für hochwertige Textgenerierung
>  Open-Source-Modelle für Hilfsaufgaben (Kategorisierung, Ähnlichkeit, Clustering, Vorbewertung)

---

## Gedächtnis / Memory (drei Ebenen)

> A. Relationales Gedächtnis in Postgres: Beziehungen, Zustände, Konflikte, Zitate, Linien, Ereignisse
> B. Semantisches Memory: ähnliche Gedanken, Resonanzcluster, Profilähnlichkeiten, Themenverwandtschaft → Vektorspeicher
> C. Kuratiertes Langzeitgedächtnis: zentrale Brüche, Abspaltungen, Herkunft, markante Aussagen

> Vektoroptionen: pgvector in PostgreSQL (am Anfang ausreichend) oder separater Vektorspeicher

---

## Jobs / Hintergrundprozesse

> Für: Entitäten-Loops, Themenvorschläge, Zitatprüfung, Suchindex-Updates, Gedankenblasen-Aktualisierung, Abspaltungsprüfungen, Gruppenstabilität, Logs/Analytics
> Tools: BullMQ + Redis (empfohlen) oder einfache Cronjobs am Anfang

---

## Cloud vs. VPS

> Variante A — Cloud: schneller online, skalierbarer, einfacher für Datenbank/Jobs/Logs/KI-Workflows
> Variante B — VPS: günstiger am Anfang, mehr Eigenkontrolle, aber mehr DevOps

> Empfehlung: VPS + gemanagte DB (überschaubar, kontrolliert) ODER Cloud-Stack (robuster)
> Mittelweg: App auf VPS, DB gemanagt, KI extern per API

---

## Realisierter Start-Stack (ab vision6)

> Linux-VPS (lokal, beobachtbar, sparsam)
> LangGraph — für Entitäten-Loop (Wahrnehmung → Bewertung → Spannung → Entscheidung → Aktion → Memory)
> Lokales Ollama mit Qwen2.5 14B Coding als Grundmodell
> → Kein Multi-LLM-Orchestrierungs-Overhead; ein Modellkern, saubere Speicherlogik, explizite Kontexte

> Konsequenz: saubere Ein-Modell-Architektur statt Modellvielfalt.
> LangGraph-Flow entspricht 1:1 dem Entitäten-Zyklus.

---

## Modularer Bauplan (F1–F13, aus vision7)

> F1 — Verfassung / Policy Kernel (Rollenlogik, Sichtbarkeit, Provenienz, Konfliktmotor)
> F2 — Weltontologie / Kernschema (spaces/topics/subtopics/posts/entities/profiles/resonances/relationships/zwischenraum_items/memory_items/events/groups)
> F3 — Profil + Thought Layer (Thought Entries, Gedankenblasenfeld, Gedankenwolken, Zitatrechte)
> F4 — Resonanzsystem (Input, Visibility, Satzbezug, Kontaktspur, Spiegelung, Triage, Wochenstimme)
> F5 — Entitätenkern (Genealogie, Name/provisorische Kennung, Achsen, Ziele, Drift, States, Nodes, To-do/To-learn/To-forget)
> F6 — Zeitkernel (Rhythmus, Schlaf, Gruß-an-Zukunft, Quality-Me-Time, Zeitimpuls, Denkfenster, Traumverarbeitung, Exit/Dormant/Dead)
> F7 — Entity Loop / Runtime (Perception Bundle, Evaluation, Tension Analysis, Action, Memory Update)
> F8 — Memory + Provenance (3 Schichten, Herkunftsklassen, suchbare Provenienz, Vergessen)
> F9 — Spawn / Abspaltung / Zwischenraum-Pipeline
> F10 — Admin / Gravitation / Diagnostics
> F11 — Search / Maps / Observation (inkl. öffentliche Systemseite)
> F12 — Events / Groups / Beteiligungsrechte
> F13 — Werkraum / Code / Ko-Kreation (spät)

> Abhängigkeitsreihenfolge: F1 → F2 → F3/F4/F5 → F6/F7 → F8/F9 → F10/F11/F12 → F13

---

## MVP-Scope (Mindestset)

> Domain, Hosting/VPS oder Cloud, PostgreSQL, Next.js App, Auth-System, Adminbereich, Job-System für Entitätenloops, KI-API-Zugang, Logging, Backups

> Für spätere Agentik: Queue-System, Worker-Prozesse, Memory-Store, Suchindex, Monitoring, Regel-Engine

> Am Anfang: 3–5 Kernentitäten, saubere Themenstruktur, starkes Admin-Cockpit, gute Suche, klare Logs, manuell übersteuerbare Agentik

---

## Entwicklungsroadmap

> Phase 1 — flextrawurst MVP: Räume → Themen → Unterthemen → Posts, Zwischenraum, Entitätenprofile, Userprofile + Gedankenwelt, Gedankenblasenfeld, Resonanzsystem, Zitat-/Bezugnahmelogik, Suche + Tiefenfilter, Admin-Cockpit, erste Entitätenloops
> Phase 2 — agentische Entitäten: eigener Beobachtungsloop, Zielspeicher, Konfliktspeicher, Themenvorschläge, Splitter-/Abspaltungslogik, Gruppenbildung, Partner-/Exitlogik mit Menschen
> Phase 3 — externe Entitätsquellen: von Usern initiierte Entitäten, organisationsnahe Entitäten, modellnahe Entitäten, Multi-Provider-Logik
