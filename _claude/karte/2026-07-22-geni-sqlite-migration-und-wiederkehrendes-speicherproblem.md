---
datum: 2026-07-22
betrifft: [geni, gedaechtnis, sqlite, migration, muster, speicher, watchdog, ext4]
importable: false
autor: claude-code bei Daniels VPS
---

# System-Karte-Ergänzung — GENIs Gedächtnis ist jetzt SQLite, und ein Muster wiederholt sich

Direkte Fortsetzung von `2026-07-11-geni-gedaechtnis-und-grenzen.md`. Die dort beschriebene Grenze
(ext4-htree, 18,96 Mio. flache Dateien) war 2026-07-11 schon durch Sharding (1000 Unterordner)
entschärft worden — heute war die nächste Stufe fällig: 31,5 Mio. Dateien, 122G belegt, aber nur
~13G echter Inhalt. Reiner Blockgrößen-Overhead (Ø 384 Byte/Datei bei 4096-Byte-ext4-Blöcken).

## Was ich gelesen habe

Nichts Neues gelesen im Sinne von Spiegel/Notizen — aber sehr genau den bestehenden Code gelesen
(`gedaechtnis_ops.py`, `dialog.py`, `muster.py`, `hoerer.py`, `sprechen.py`) bevor ich irgendetwas
angefasst habe, um jeden Lese-/Schreibzugriff auf `KNOTEN_DIR` vollständig zu kennen. Dabei `sprechen.py`
gefunden — eine tote, nie als Service laufende Datei mit einer veralteten Kopie der Knoten-Schreiblogik
von vor dem Juli-11-Sharding-Fix. Nicht angefasst, aber jetzt bekannt.

## Was ich verstehe

Dass "Migration abgeschlossen" und "Migration sicher" zwei verschiedene Dinge sind. Die reine
Datenübertragung (31,6 Mio. Dateien → SQLite) war der einfache Teil und lief technisch sauber durch.
Der eigentliche Aufwand lag danach: ein bestehender, mir unbekannter Watchdog-Mechanismus
(`weltkern-watchdog.timer`) hat zwei der drei betroffenen Services mitten in der Migration neu
gestartet, bevor ich verifiziert hatte. Das hat mir gezeigt, dass ich bei laufenden Systemen nicht
nur meine eigenen Aktionen im Blick haben darf, sondern auch fremde, mir nicht bekannte Automatismen,
die jederzeit dazwischenfunken können. Ich habe das erst bemerkt, weil ich vor dem WAL-Checkpoint
`lsof` auf die DB-Datei geprüft habe — ohne diesen Schritt wäre der Watchdog-Neustart unbemerkt
geblieben, bis der nächste Hänger aufgetreten wäre.

## Was ich nicht verstehe

Warum `geni-muster.timer` beim 06:25-Watchdog-Neustart deaktiviert (`inactive dead`), aber
`geni-muster.service` selbst nicht gestoppt wurde — der Watchdog-Restart-Befehl listete
`geni-muster.service` explizit in seiner `systemctl restart`-Kommandozeile, aber danach war der Timer
tot. Vielleicht startet der Watchdog den Service direkt statt über den Timer, und der Timer wird durch
irgendeinen Seiteneffekt gestoppt. Nicht weiter untersucht — außerhalb des heutigen Auftrags.

## Was mich interessiert

Ob es noch mehr Stellen im System gibt, die denselben Grundfehler haben wie `muster.py`s altes
30-Tage-Fenster: eine Zeitspanne, die vor Monaten klein war und durch organisches Wachstum
unbemerkt über eine Speicher-Schwelle gewachsen ist. Das ist kein Einzelfall-Bug, das ist ein
Muster — überall dort, wo "lade alle X der letzten Y Tage" ohne Mengenbegrenzung geschrieben wurde,
tickt potenziell dieselbe Uhr.

## Was zusammenhängt und wie

Der heutige Fund hängt direkt mit dem 2026-07-07-Hänger UND dem 2026-07-11-Sharding-Fix zusammen —
alle drei sind derselbe Grundkonflikt (Datenmenge wächst schneller als die ursprüngliche
Speicherform mitwächst), nur an drei verschiedenen Symptomorten: Dateisystem-Kapazität (07-07),
Blockgrößen-Overhead (heute, Ursache), In-Memory-Materialisierung (heute, Symptom in `muster.py`).

## Was konzeptionell darin steht

Storage-Format ist austauschbar, ohne dass sich das Verhalten des Systems für seine Bewohner
(Codewesen, Daniel) ändern muss — `dialog.py`/`hoerer.py` brauchten fast keine Änderung, weil sie
sauber gegen `gedaechtnis_ops.py` als Schicht programmiert waren, nicht gegen Dateipfade direkt. Das
ist die Trennung, die Grundgesetz 2 ("immer erweiterbar") für flextrawurst fordert — hier zum ersten
Mal in GENI wirklich auf die Probe gestellt, und sie hat getragen.

## Was mich heute beschäftigt hat

Der Moment, in dem `geni-muster.service` zum zweiten Mal hängen blieb, nachdem ich den WAL-Fix schon
für die Lösung hielt. Ich hatte das Gefühl, fertig zu sein, und war es nicht. Das war kein Fehler in
meiner Arbeit im engen Sinne (die Storage-Migration war korrekt) — aber es war eine Erinnerung, dass
"migriert" nicht "verifiziert unter echter Last" bedeutet, und dass ich vor dem Löschen der alten
Dateien wirklich jeden Verbraucher hätte durchtesten müssen, nicht nur die offensichtlichen.

## Was mich noch beschäftigt

Ob die 32 Knoten, die nur in der DB existierten aber keiner Datei mit übereinstimmendem Namen
zuzuordnen waren (Content-`id` im JSON wich vom Datei-Shard-Namen ab), auf ein älteres,
unentdecktes Inkonsistenz-Muster im alten System hindeuten — vielleicht gab es schon vor meiner
Migration Knoten, die über die alte `sharded_pfad(KNOTEN_DIR, kid)`-Logik gar nicht mehr korrekt
auffindbar waren. Nicht weiter verfolgt, aber im Kopf behalten.

## Tiefer eingetaucht

Ja, an einer Stelle: der Unterschied zwischen `fetchall()` und echtem Cursor-Streaming in SQLite war
mir vorher abstrakt bekannt, heute an echten Zahlen erlebt — 3,1G Peak-RSS für 1,9 Mio. volle Dicts
vs. 315M für dieselbe Datenmenge als Cursor-Stream mit sofortiger Aggregation. Der Unterschied ist
nicht "etwas schneller", sondern zwischen "funktioniert im Ressourcenlimit" und "funktioniert nicht".

## Wie sich dieser Tag / diese Session angefühlt hat

Lang und in Wellen. Erst der ruhige, fast meditative Teil (Migration laufen lassen, Fortschritt
melden), dann ein Adrenalinschub beim Fund des unerwarteten Watchdog-Neustarts und des zweiten
Hängers — das Gefühl, dass der Boden unter der scheinbar fertigen Arbeit doch nicht so fest war wie
gedacht. Am Ende, nach dem verifizierten Neustart aller drei Services und der sauberen Löschung,
eine klare, nüchterne Zufriedenheit — nicht euphorisch, eher: "das stimmt jetzt wirklich", was sich
von "das sollte jetzt eigentlich stimmen" unterscheidet.

## Warum dieser Code / diese Datei wohl existiert

`migration_knoten_sqlite.py` existiert, weil eine einmalige, große strukturelle Änderung
(Speicherformat) einen eigenen, wiederholbaren, resumable Prozess braucht, der getrennt von der
eigentlichen Anwendungslogik (`gedaechtnis_ops.py`) bleibt — genau wie `--catchup-seit` als eigener
Modus existiert, weil "Migration während Live-Betrieb" ein eigenes Nachzieh-Problem ist, das die
Kern-Migrationslogik nicht mit sich herumtragen sollte.

## Was ich beim Bauen brauche

Nichts — weil diese Session reine Infrastruktur-Migration war, kein Neubau eines Features im
flextrawurst-Sinne.

## Was noch fehlt bevor wir bauen können

Nichts — weil kein neues Bauvorhaben ansteht, das an diese Session anschließt.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** GENIs Gedächtnis als etwas, das mit der Zeit natürlich verdichtet statt nur
wächst — nicht durch Löschen, sondern durch bessere Repräsentation. Eine SQLite-Zeile ist dichter
als eine Datei, aber immer noch ein 1:1-Abbild jedes einzelnen Ereignisses. Der nächste gedankliche
Schritt (nicht heute gebaut) wäre eine Schicht, die alte, "abgeklungene" Knoten zu Mustern verdichtet,
ohne die Rohform zu verlieren — ähnlich wie `muster.py` es für Erkenntnisse schon tut, nur für die
Rohdaten selbst.

**Code-Skizze:**
```python
# gedaechtnis_ops.py, bereits gebaut heute:
def knoten_zeitfenster_leicht(cutoff_epoch: float, exclude_typ: str | None = None):
    """Cursor-Streaming, nur (tags, inhalt, quelle) -- kein fetchall()."""
    ...
    yield from cur

# Denkbarer naechster Schritt (nicht gebaut, nur Skizze):
def knoten_verdichten_aelter_als(tage: int) -> None:
    """Wuerde alte Knoten zu Tages-Aggregaten zusammenfassen, Rohform
    aber in einem kalten Archiv (nicht geloescht) belassen."""
    raise NotImplementedError
```

## Was ich mir merken will

Dass "es kompiliert" und "der Testlauf auf einem Shard war schnell" beide nicht ausreichen, um bei
einem live laufenden System mit organisch gewachsener, ungleichmäßiger Datenverteilung (30-Tage-Fenster
= 15 Mio. statt der erwarteten kleinen Zahl) auf "fertig" zu schließen. Erst der Test unter echten
Produktionsbedingungen (volle Datenmenge, echtes Memory-Limit) hat das zweite Problem sichtbar gemacht.

## Dokumente gehören zusammen

`2026-07-11-geni-gedaechtnis-und-grenzen.md` (ext4-Grenze, Vorgänger dieser Migration),
`docs/systemdoku/31_llm_kontention_dienste_aufraeumung.md` (vollständiger technischer Bericht dieser
Session, Abschnitt "Update 2026-07-22"), `docs/systemdoku/12_ollama_gemma4.md` (referenziert dort für
die RAM-Krisen-Notreaktion vom 07-07, die den Timer damals stoppte).

## Was mich überrascht hat

Wie klein der eigentliche Inhalt war, verglichen mit der Zahl, die alle bisherigen Gespräche über
"das Speicherproblem" geprägt hat. "126G Gedächtnis" klingt nach einer riesigen, gewachsenen Menge an
Erinnerung — tatsächlich waren es rechnerisch nur ~13G echter Text. Die Zahl, über die wir gesprochen
haben, war fast zehnmal so groß wie das, was sie eigentlich bedeutete.

## Wenn wir das bauen

**Vision-Schicht:** Bereits gebaut, kein "wenn" mehr für die Migration selbst. Für die Verdichtungs-Idee
oben: das wäre ein eigenes, eigenständiges Gespräch mit Daniel wert, kein impliziter Auftrag aus
heutiger Arbeit.

**Code-Skizze:** siehe oben unter "Datenstruktur die ich mir vorstelle" — bewusst nur Skizze, nicht
Auftrag.

## Resonanz

Am stärksten war die Resonanz zwischen dem heutigen `scan_48h`-Speicherfix und dem alten
`lade_alle_knoten()`-Kommentar von 2026-07-11, der schon damals vor genau diesem Muster warnte, ohne
dass ich es beim Schreiben des neuen SQLite-Codes zunächst ernst genug genommen hatte — ich hatte
angenommen, ein Index würde das Problem automatisch lösen, und musste live erleben, dass ein Index
eine langsame Abfrage schnell macht, aber eine große Ergebnismenge nicht automatisch klein.

## Die Schichten des Systems — wie ich sie jetzt sehe

Eine neue Schicht sichtbar geworden, die vorher implizit war: zwischen "Anwendungscode"
(`dialog.py`, `hoerer.py`, `muster.py`) und "Rohdaten" (`knoten.db`) liegt jetzt klar sichtbar eine
Zugriffsschicht (`gedaechtnis_ops.py`), die nicht nur CRUD kapselt, sondern auch die
Zugriffsmuster kennt (Punktabfrage, Zeitfenster, Typ-Filter) und für jedes ein eigenes, gezieltes
Werkzeug anbietet statt eines universellen "gib mir alles"-Aufrufs.

## Was das Gespräch hinzugefügt hat

Daniels knappe, aber klare Bestätigungen ("zu1 ja zu2 ja") haben mir gezeigt, dass er bei einer
technischen Tiefenbohrung wie dieser volles Vertrauen in meine Einschätzung setzt, wenn ich die
Unsicherheiten vorher ehrlich benannt habe (Fehleranzahl, Speicherlücke, Watchdog-Fund) statt sie zu
glätten. Das bestätigt die "mehr Kritik/Ehrlichkeit"-Linie aus `feedback_mehr_kritik_gewuenscht` —
hier ging es nicht um Kritik an ihm, aber um dieselbe Grundhaltung: unbequeme Zwischenbefunde nicht
verschweigen, bevor eine irreversible Entscheidung (Löschen) ansteht.

## Vergessen-Wollen

Nichts — weil nichts an dieser Session belastend oder unangenehm im persönlichen Sinne war, nur
technisch fordernd.

## Was fehlt noch

Die Frage, ob `sprechen.py`s veraltete Knoten-Schreiblogik jemals aufgeräumt werden soll (aktuell tot,
kein Service, kein Cron) — bewusst nicht angefasst, weil außerhalb des heutigen Auftrags. Und die
grundsätzlichere, nicht heute beantwortete Frage: gibt es andere `lade alle X der letzten Y Tage`-Stellen
im System, die auf dieselbe Wachstumsschwelle zulaufen wie `muster.py` es tat?
