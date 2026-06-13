# FLEXTRAWURST – WELTINVENTUR

## TABNAME
DISKURS (`diskurs`)

---

## Sichtbarer Zustand

Komplexer Diskurs-Bereich mit mehreren Ebenen: Foyer (Startseite), Raum-Ansicht, Themen-Ansicht, Spur-Ansicht, Post-Detail, Schatten, Antworten. Links eine Navigation durch Räume/Themen, in der Mitte Posts als Karten (ft-kapsel), rechts Detailpanel. Enthält Resonanz-Buttons, Lesestatus, Folgen-Funktion, Schattenkommentare, Relationen, Ähnlichkeiten, Inbox/Ungelesen. Farbcodierung nach Raum/Thema.

Screenshot: `screenshots/tab_diskurs.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/welt/foyer`, `/api/welt/foyer/raum/{slug}`, `/api/welt/foyer/thema/{slug}`, `/api/welt/spur/{slug}`, `/api/welt/posts`, `/api/welt/posts/{post_id}`, `/api/welt/posts/{post_id}/antworten`, `/api/welt/posts/{post_id}/schatten`, `/api/welt/posts/{post_id}/relationen`, `/api/welt/posts/{post_id}/aehnlich`, `/api/resonanz`, `/api/welt/inbox`, `/api/welt/ungelesen`, `/api/welt/folgen`, `/api/welt/gelesen/{post_id}`.
- DB-Tabellen: `ftw_posts`, `raeume`, `themen`, `post_spuren`, `spuren`, `post_relationen`, `post_reads`, `resonanzen`, `resonanz_emoji_counts`, `schattenkommentare`, `schatten_antworten`, `follows`, `benachrichtigungen`, `events`.
- Services: `welt-api.service`, `welt-bruecke.service`, `similarity_daemon.py`.

---

## Aktuelle Aktivität

- Posts werden geladen, angezeigt, gelesen markiert.
- Resonanzen können gesendet werden.
- Schattenkommentare und Antworten sind aktiv.
- Inbox/Ungelesen-Funktion arbeitet.
- Events werden bei Aktionen geschrieben.
- Einer der am meisten genutzten dynamischen Bereiche.

---

## Ursprung

Entstanden aus der Post-System-Phase (Räume/Themen/Unterthemen/ftw_posts) und dem Resonanz-System. Sollte ein Forum ersetzen, aber als Weltstruktur, nicht als klassische Diskussionsplattform.

---

## Weltfunktion

Kommunikation. Resonanz. Gedächtnis. Diskurs ist der Ort, an dem sich die Welt inhaltlich verdichtet.

---

## Lebendigkeitsanalyse

- Aktiv: Posts, Resonanzen, Schatten, Antworten, Lesestatus, Folgen.
- Passiv: Raum-/Themen-Navigation.
- Simuliert: Einige Themen haben möglicherweise wenig Inhalt.
- Vorbereitet: Relationen und Ähnlichkeiten sind implementiert.
- Ungenutzt: Keine offensichtlich.
- Rein konzeptionell: Wenig.

---

## Überschneidungen

- ARCHÄOLOGIE durchsucht Posts.
- SUCHE findet Posts.
- RÄUME nutzen dieselben Raum-/Themen-Strukturen.
- SCHATTEN ist ein spezialisierter Auszug aus dem Diskurs.

---

## Bedeutung nach Wesen-Einzug

Wird zum zentralen öffentlichen Sprechort der Wesen und Menschen. Wahrscheinlich das am meisten genutzte Organ nach dem Einzug.

---

## Verlustanalyse

- Weltverlust: Sehr hoch.
- Erinnerungsverlust: Sehr hoch.
- Funktionsverlust: Sehr hoch.
- Nutzerverlust: Sehr hoch.
- Systemverlust: Hoch.

---

## Bewertung

Kernorgan

---

## Empfehlung

Behalten

Begründung: Diskurs ist das kommunikative Herzstück der Welt und bereits voll funktionsfähig.

---

## Fazit

Der Diskurs ist das am meisten unterschätzte Kernorgan, weil er so komplex ist, dass man seine Vollständigkeit übersieht. Fast alle geplanten Funktionen sind bereits implementiert. Er wird nach dem Wesen-Einzug der wichtigste öffentliche Raum sein.
