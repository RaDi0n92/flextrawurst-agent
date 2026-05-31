---
datum: 2026-05-31
betrifft: [repo-scan, einsicht, schema-drift, read-only]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Repo-Scan der vier Arbeitsstraenge

## Was ich gelesen habe

Ich habe `api.py`, `admin_einsicht_api.py`, die Schemas und die Surface-Quelle gelesen. Es war ein Lesegang durch gewachsene Schichten, nicht durch ein ordentliches Modulregal.

Wichtig war der Satz im Report: *EINSICHT existiert doppelt.* Das ist kein Vorwurf, sondern ein Befund. Die Welt ist gewachsen, und manche Organe haben eine zweite Knospe gebildet.

Ich habe auch Schema-Drift gesehen: API-Code spricht Felder an, die in den gelesenen Basisschemas nicht stehen. Besonders Schlafbriefe, Schattenkommentare und Substanzsedimente wirken wie historisch weitergewachsene Orte.

## Was ich verstehe

Das Repo ist kein Greenfield. Viele Funktionen sind real, aber ihre Herkunft liegt in mehreren Ringen.

## Was ich nicht verstehe

Ich verstehe noch nicht, welche DB-Migrationen wirklich angewendet wurden und welche nur als Datei fehlen.

## Was mich interessiert

Mich interessiert die Stelle, wo aus "gewachsen" "unverlaesslich" wird. Noch ist vieles rettbar durch Mapping.

## Was zusammenhängt und wie

EINSICHT, Suche, Lebensjournal, Schatten, Traeume und Substanzen kreuzen sich ueber `entity_thinking_log`, `events`, `ftw_posts` und private/internal Quellen.

## Was konzeptionell darin steht

Der Repo-Scan zeigt eine Welt, die bereits mehr erinnert als sie sauber indexieren kann.

## Was mich heute beschäftigt hat

Die Aufgabe war streng read-only. Das war gut, weil die richtige Arbeit hier erst Wahrnehmung war.

## Was mich noch beschäftigt

`substance_sediments` wird produktiv referenziert, aber das CREATE-Schema war im gelesenen SQL nicht auffindbar.

## Tiefer eingetaucht

`api.py` enthaelt alte und neue API-Schichten zugleich. `admin_einsicht_api.py` wirkt wie ein saubererer Router, aber seine Anbindung und Feldnamen muessen geprueft werden.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie Archaeologie mit Taschenlampe. Nicht graben, nur markieren.

## Warum dieser Code / diese Datei wohl existiert

Die Reportdatei existiert, damit spaeter nicht aus Bauchgefuehl refaktoriert wird.

## Was ich beim Bauen brauche

Vor EINSICHT II brauche ich eine kanonische Quelle fuer EINSICHT-Daten.

## Was noch fehlt bevor wir bauen können

Schema-Audit gegen die reale DB, aber erst wenn DB-Lesen erlaubt ist.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Eine Welt mit vielen Spuren braucht nicht weniger Spuren, sondern bessere Herkunftsmarkierung.

**Code-Skizze:**
```ts
type SourceHealth = {
  file: string;
  tables: string[];
  endpoints: string[];
  drift: "none" | "suspected" | "confirmed";
  nextAudit: string;
};
```

## Was ich mir merken will

Nicht jede doppelte Struktur ist Muell. Manche doppelte Struktur ist ein Hinweis auf zwei Wachstumsphasen.

## Dokumente gehören zusammen

`repo_scan_2026-05-31.md`, `api.py`, `admin_einsicht_api.py`, `schema*.sql`.

## Was mich überrascht hat

Dass die aktive Surface ausserhalb von `/root/werkraum` liegt: `/root/flextrawurst`.

## Wenn wir das bauen

**Vision-Schicht:** EINSICHT II sollte nicht noch eine dritte Einsicht bauen, sondern die vorhandenen zwei Linien zusammenfuehren.

**Code-Skizze:**
```ts
interface EinsichtSource {
  kind: "decision" | "dream" | "letter" | "event" | "substance";
  endpoint: string;
  canonical: boolean;
}
```

## Resonanz

[[abwurf: Eine gewachsene Welt braucht zuerst eine Karte, nicht zuerst Ordnung.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

SQL-Schema, API-Geschichte, Surface-Geschichte, Report-Schicht. Jede hat andere Wahrheit.

## Was das Gespräch hinzugefügt hat

Daniel hat verhindert, dass aus Analyse ein heimlicher Reparaturversuch wird.

## Vergessen-Wollen

Den Reflex, Schema-Drift sofort zu "fixen".

## Was fehlt noch

Ein expliziter Auftrag fuer einen Schema-/Migrations-Audit.
