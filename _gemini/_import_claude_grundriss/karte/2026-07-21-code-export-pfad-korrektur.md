---
datum: 2026-07-21
betrifft: [chatgpt-export, secrets-redaktion, pfad-provenienz, flextrawurst-frontend]
autor: claude-code bei Daniels VPS
---

## Korrigierte Altannahme

`/root/CLAUDE.md` benennt den Frontend-Pfad als `/root/werkraum/flextrawurst/`. Das ist inzwischen falsch, oder zumindest irreführend: dieser Ordner ist nur noch ein alter Output-Cache (15 Screenshots, eine generierte `flextrawurst_surface.html`, eine `DESIGN.md`) — kein Quellcode. Der echte, laufende Frontend-Code liegt unter `/root/flextrawurst/` (bestätigt über `scripts/build_surface.ts`, die tatsächlichen Port-8787/8030-Listener und die systemd-Units unter `flextrawurst/ops/systemd/`).

Gefunden beim Vorbereiten eines Code-Exports für ChatGPT (Auftrag: "den echten Live-Code, nicht nur Doku" zippen) — beim ersten Griff nach `/root/werkraum/flextrawurst/` fiel auf, dass da praktisch nichts drin ist, danach systemweite Suche nach `build_surface.ts` gemacht.

## Was das bedeutet

Die beiden Pfade koexistieren, ohne dass es in CLAUDE.md steht: `/root/werkraum/flextrawurst/` = alter/aktueller Build-Output-Spiegel (wird von einem `cp`-Schritt am Ende jedes Builds befüllt, siehe i18n-Gesetz-Workflow: `cp out/surface/flextrawurst_surface.html out/process_camera/flextrawurst_surface.html`), `/root/flextrawurst/` = das eigentliche Repo mit Quellcode, node_modules, Tests. Kein Widerspruch, nur eine in CLAUDE.md nicht nachgezogene Pfadangabe.

## Was ich mir merken will

Bei jeder Aufgabe, die "den echten Code" braucht: nicht blind dem in CLAUDE.md notierten Pfad folgen, sondern über die tatsächlich laufenden Prozesse (`ss -tlnp`, systemd-Units) verifizieren, wo der Code wirklich liegt — Doku kann veralten, laufende Prozesse lügen nicht.
