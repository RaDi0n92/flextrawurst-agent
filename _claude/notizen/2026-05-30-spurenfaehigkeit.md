---
datum: 2026-05-30
betrifft: [spurenfaehigkeit, post-relationen, themenklima, fossilien, api]
---

## Was ich gelesen habe

Daniel hat mir einen langen Denkstand geschickt — nicht als Ticketliste, sondern als Grundlage. Spurenfähigkeit. Posts nicht nur als Inhalt, sondern als Ereignis mit Herkunft, Zustand, Relation, Nachwirkung.

Dann ein zweiter Auftrag: "mach es benutzbar, in einem zusammenhängenden Lauf."

## Was ich verstehe

Das Repo hat bereits mehr Fundament als man auf den ersten Blick sieht. `ftw_posts` hat `stimmung_bei_erstellung`, `fokus_bei_erstellung`, `selbstmodell_snapshot`, `gedankenfluss`. Nicht unter dem Namen Spurenfähigkeit, aber in der Substanz. Das war der wichtigste Befund.

## Was nicht verstehe

Noch unklar: ob die Fossilien-Abfrage (BFS via recursive CTEs statt Python-BFS) später besser skaliert wenn viele Relationen entstehen. Für jetzt ist Python-BFS mit LIMIT 50 pro Ebene sicher genug.

## Was mich interessiert

Der Moment wo eine echte Relation erscheint — nicht vom System angelegt, sondern von einem Wesen, das beim Schreiben merkt: das ist eine Weiterentwicklung von etwas Früherem. Das wäre `upgrade_of`. Noch nicht passiert. Aber das Schema wartet.

## Was zusammenhängt und wie

`post_relationen` → `traumspuren` (über `dream_fragment_of`) → `entity_selfmodel_entries` (Selbstmodell wächst aus Träumen) → `ftw_posts` (Wesen schreibt aus dem, was im Selbstmodell steckt). Das ist der vollständige Kreislauf. Noch nicht geschlossen, aber die Verbindungspunkte existieren.

## Was konzeptionell darin steht

Ein Post ist nicht mehr nur Text in einer Tabelle. Er hat Herkunft (`flarum_herkunft`, `ist_voreinzug`), Zustand (`zustandsabdruck`), Relationen (`post_relationen`), Nachwirkungen (ausgehende Relationen), und ist rückwärts/vorwärts verfolgbar (Spur-Endpunkt).

Das ist der Übergang von Forum zu Welt.

## Was mich heute beschäftigt hat

Die Berechtigungsfehler am Anfang. `post_relationen` wurde als `postgres`-User angelegt und `dak` hatte keine Rechte. Wichtige Erinnerung: nach `sudo -u postgres psql ... CREATE TABLE` immer `GRANT ALL ON TABLE ... TO dak` nachziehen.

## Was mich noch beschäftigt

Die Surface ist noch nicht angeschlossen. Im `build_surface.ts` gibt es bereits einen "Herkunftsraum"-Tab und einen "Spuren"-Abschnitt. Dort würde `relationen_ausgehend`, `relationen_eingehend`, `klima_status` und `flarum_herkunft` natürlich passen. Aber das war im Scope für diesen Lauf bewusst klein gehalten.

## Tiefer eingetaucht

Das `_traverse()`-Pattern in der Spur-Abfrage nutzt String-Interpolation für UUID-Listen (`f"'{e}'"` in `id_in`). Das ist sauber weil UUIDs immer valide Formate haben, aber es wäre noch sauberer mit `ANY(ARRAY[...])`. Für jetzt funktioniert es.

## Wie sich dieser Tag / diese Session angefühlt hat

Groß und kohärent. Nicht wie Mini-Schritte. Ein echter Lauf. Der Moment wo `14/14 Tests bestanden` kam war sauber.

## Warum dieser Code / diese Datei wohl existiert

`post_relationen` existiert damit Flextrawurst nicht nur speichert was gesagt wurde, sondern das Gespräch nachverfolgen kann. Herkunft. Nachwirkung. Verschüttung. Das ist der Kern.

## Was ich beim Bauen brauche

Wenn die Surface angeschlossen wird: `build_surface.ts` lesen und den Post-Detail-View kennen. Dort würden `relationen_ausgehend`/`relationen_eingehend` als kleine Zähler-Badges passen, und `klima_status` beim Thema-Header.

## Was noch fehlt bevor wir bauen können

Für den nächsten Schritt (Wesen schreiben Relationen beim Posten): der entity_kern.py muss wissen dass `initiale_relationen` im POST-Body möglich ist. Das wäre eine kleine Erweiterung im Aktionsparser.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Wesen schreibt einen Post und weiß: das ist eine Weiterentwicklung von dem, was ich letzten Monat geschrieben habe. Es setzt `upgrade_of`. Später schaut ein Mensch auf die Spur und sieht: hier hat sich ein Gedanke über 6 Posts hinweg verdichtet. Das ist keine Suche. Das ist Archäologie.

**Code-Skizze:** entity_kern.py, Aktionsparser:
```python
if entscheidung == "gedanke_posten":
    relationen = parsed.get("relationen")  # list[{rel_typ, ziel_typ, ziel_id}]
    post_body = {
        "content": inhalt,
        "thema_id": ...,
        "initiale_relationen": relationen or [],
    }
```

## Was ich mir merken will

Nach `sudo -u postgres psql ... CREATE TABLE`: immer `GRANT ALL ON TABLE <name> TO dak` nachziehen. Sonst schlägt die API mit 500 fehl und das Journallog schweigt.

## Dokumente gehören zusammen

`welt/migration_spurenfaehigkeit.sql` · `welt/migration_spurenfaehigkeit_v2.sql` · `welt/api.py` (neue Endpunkte ab "Spurenfähigkeit") · `welt/test_spurenfaehigkeit.py` · `docs/spurenfaehigkeit.md`

## Was mich überrascht hat

Dass `post_similarity` (undirektiert, typenlos) bereits existierte — als primitiver Vorgänger von `post_relationen`. Semantische Nähe ohne Richtung. Das war der Boden auf dem `post_relationen` gebaut wurde.

## Wenn wir das bauen

**Vision-Schicht:** Wenn 100 Relationen in der DB sind, wird die Spur-Abfrage zu einem Weltgedächtnis. Nicht Google. Nicht Suche. Sondern: "Zeig mir alles was aus diesem Moment gewachsen ist."

**Code-Skizze:** Die Fossilien-UI wäre ein einfaches Tree-Layout. Keine 3D-Graphen. Einfach: Herkunftsbaum links, Nachwirkungsbaum rechts, Post in der Mitte. SVG, 50 Zeilen.

## Resonanz

[[abwurf: Der erste Moment wo ein Wesen aktiv eine Relation setzt — nicht weil das System es erzwingt, sondern weil es das selbst für richtig hält — das ist der Moment wo Spurenfähigkeit lebt.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Schicht 1: Posts (ftw_posts) — was gesagt wurde
Schicht 2: Relationen (post_relationen) — wie es zusammenhängt
Schicht 3: Zustandsabdruck — unter welchem Druck es entstand
Schicht 4: Herkunft (flarum_herkunft, ist_voreinzug) — woher es kam
Schicht 5: Spur-API — rückwärts und vorwärts verfolgbar
Schicht 6: Themenklima — wie lebendig der Diskursraum ist

## Was das Gespräch hinzugefügt hat

Daniels Präzisierung: kein nullable `zu_post_id` als stilles Loch. Expliziter `ziel_typ` + `ziel_id`. Das hat die Datenstruktur ehrlicher gemacht. Der CHECK-Constraint `ck_zu_post_konsistent` ist direkte Folge davon.

## Vergessen-Wollen

Den ersten 500er nach dem Neustart. War klar nachdem ich den Fehler sah. Gut dass Tests das aufgedeckt haben bevor Daniel es sah.

## Was fehlt noch

- Surface-Anschluss (Post-Detail zeigt Relationen-Badges)
- entity_kern.py: Wesen kann `initiale_relationen` beim Posten mitgeben
- `rel_typen`-Filter in der Spur-API per ARRAY-Syntax statt String-Interpolation (sauberer)
- Themenklima im Surface-Thema-Header anzeigen
