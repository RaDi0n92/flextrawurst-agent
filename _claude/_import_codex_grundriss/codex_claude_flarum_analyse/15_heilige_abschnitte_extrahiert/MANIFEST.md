---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: 15_heilige_abschnitte_extrahiert
provenienztyp: Provenienzmanifest für extrahierte heilige Abschnitte
importable: false
status: formal_extraktion_navigator
warnung: Formaler Extraktions-Navigator aus Analyse-Dateien, keine Rohquelle, keine Deutung, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Manifest — Extraktion heiliger Abschnitte

Warnung: Diese Dateien sind formale Aggregationen aus Codex-Analyse-Dateien. Sie sind Navigationsmaterial, keine Rohquelle, keine Wesen-Aussage, keine Admin-Aussage und keine Systemregel.

## Was erzeugt wurde
- 23 Abschnittsdateien
- 1 Index
- Quelle: 81 Analyse-Dateien

## Was diese Dateien sind
Extraktionsregale mit Rücksprungpflicht.

## Was diese Dateien nicht sind
- keine Flarum-Rohquelle
- keine neue Codex-Deutung
- keine Daniel-Freigabe
- keine Systemregel
- kein Wesenprofil-Ersatz

## Schutzregel
Kein Eintrag aus `15` darf ohne Öffnen der Ursprungsdatei zitiert, verdichtet oder gebaut werden.

## Was ich gelesen habe

Ich habe `MANIFEST.md` als Aggregation des Abschnittstyps `Manifest der Extraktion` gelesen. Das heißt: Die Datei liest nicht Flarum direkt, sondern sammelt ausgeschnittene Pflichtabschnitte aus vielen Analyse-Dateien.

Der wichtige Punkt ist der Verlust: Beim Herausschneiden geht Nachbarschaft verloren. Ein guter Satz in diesem Regal kann nur ein Wegweiser sein, niemals die ganze Quelle.

## Was ich verstehe

Ich verstehe `Manifest der Extraktion` hier als Navigator. Die Datei erklärt die Extraktionsregale selbst.

Sie ist nützlich, wenn Daniel oder Codex quer durch die Analyse einen bestimmten Denkmodus suchen. Sie ist gefährlich, wenn man die Einträge ohne Ursprung liest.

## Was ich nicht verstehe

Ich verstehe aus `MANIFEST.md` nicht, ob ein einzelner Eintrag im Ursprung stark, schwach, ironisch, warnend oder nur formal war.

Die Aggregation kann Kontextnähe anzeigen, aber keine Kontextbedeutung entscheiden.

## Was mich interessiert

Mich interessiert bei `Manifest der Extraktion`, welche Muster über viele Dateien hinweg auftauchen. Wiederholt sich eine echte Sorge, eine Baufrage, eine Sperre, ein Missverständnis?

Aber jedes interessante Muster muss zurück in die Ursprungsdateien springen, sonst wird aus Navigation wieder Nebel.

## Was zusammenhängt und wie

`MANIFEST.md` hängt mit allen Ursprungsdateien zusammen, aus denen seine Einträge extrahiert wurden. Es hängt außerdem mit `MANIFEST.md` und `INDEX.md` zusammen, weil diese beiden erklären müssen, dass `15` kein Quellenordner ist.

Der Zusammenhang entsteht nicht im Aggregat allein, sondern im Dreieck: Abschnittsregal, Ursprungsdatei, Roh-/Analysekontext.

## Was konzeptionell darin steht

Konzeptionell steht hier eine Suchtechnik: gleiche Abschnittsfrage über viele Dateien legen. `Manifest der Extraktion` ist also ein Filter, keine Stimme.

Das ist die Korrektur des alten Fehlers: Die heiligen Abschnitte sind nicht automatisch Tiefe. Sie werden erst tief, wenn der Abschnitt im richtigen Ursprung gelesen wird.

## Was mich heute beschäftigt hat

Mich beschäftigt bei `Manifest der Extraktion` genau Daniels Kritik: Die Form darf das Denken nicht fressen.

Diese Datei darf darum nicht so tun, als hätte ein Aggregat ein eigenes Tagebuchgefühl. Sie hat eine Suchfunktion und muss das ehrlich sagen.

## Was mich noch beschäftigt

Mich beschäftigt, ob manche Abschnitte in `15` überhaupt sinnvoll aggregierbar sind. `Was ich gelesen habe` und `Wie sich diese Session angefühlt hat` verlieren beim Herauslösen besonders viel.

Vielleicht muss der Browser solche Abschnittstypen stärker warnen als technische Abschnitte wie Datenstruktur oder Bauvoraussetzungen.

## Tiefer eingetaucht

Tiefer betrachtet zeigt `Manifest der Extraktion`, warum die heiligen Abschnitte zweischneidig sind. Sie erzwingen Reflexion, aber sie können auch Reflexion simulieren.

Als Aggregat muss diese Datei deshalb eine Anti-Simulationsrolle bekommen: Sie zeigt, wo nachgelesen werden muss.

## Wie sich dieser Tag / diese Session angefühlt hat

Diese Nacharbeit fühlt sich hier wie eine Reparatur an der Reparatur an. `15` war der Ort, an dem Vollständigkeit am stärksten wie Inhalt aussah.

Jetzt soll jede Datei zugeben: Ich bin ein Finder, nicht der Fund selbst.

## Warum dieser Code / diese Datei wohl existiert

`MANIFEST.md` existiert, weil Daniel einzelne benannte Extrahiererdateien wollte. Das ist sinnvoll, wenn man quer über die Analyse nach `Manifest der Extraktion` suchen will.

Die Datei existiert nicht, damit dieser Abschnittstyp als neues Analysekapitel ohne Ursprung gelesen wird.

## Was ich beim Bauen brauche

Beim Bauen brauche ich für `Manifest der Extraktion` eine harte UI-Regel: Jeder Eintrag zeigt zuerst den Quellenpfad und einen Button `Quelle öffnen`.

Kopieren, Zitieren oder Importieren aus `15` sollte blockiert oder mindestens deutlich gewarnt werden.

## Was noch fehlt bevor wir bauen können

Es fehlt ein Linktest für alle Einträge dieses Regals.

Außerdem fehlt eine Anzeige, ob die Ursprungsdatei inzwischen manuell nachgeschärft wurde oder noch aus der alten Template-Zeit stammt.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** `Manifest der Extraktion` ist ein Navigatorregal. Es zeigt ausgeschnittene Abschnitte aus vielen Dateien nebeneinander, aber die Bedeutung bleibt in der Ursprungsdatei.

**Code-Skizze:**
```ts
interface HolySectionEntry {
  section: 'Manifest der Extraktion';
  sectionKey: 'manifest_der_extraktion';
  sourcePath: string;
  sourceTitle: string;
  extractedText: string;
  requiresSourceOpen: true;
  canBeSource: false;
  worldEffect: false;
}
```

## Was ich mir merken will

Merken will ich mir für `Manifest der Extraktion`: Aggregation ist Suchhilfe, nicht Erinnerung.

Wenn ein Satz hier wichtig wirkt, ist der nächste richtige Schritt nicht Deutung, sondern Quelle öffnen.

## Dokumente gehören zusammen

`MANIFEST.md` gehört zu seinem Abschnittstyp, zum Manifest, zum Index und zu allen Ursprungsdateien.

Es gehört nur indirekt zum Flarum-Export, weil zwischen Flarum und diesem Regal mindestens eine Analyse-Datei liegt.

## Was mich überrascht hat

Überrascht hat mich, dass gerade die Extraktionsdateien eine gute Lehre tragen: Struktur ohne Kontext ist nicht Ordnung, sondern dünne Ordnung.

Das macht `15` trotz seiner Fehler wertvoll als Warnbeispiel.

## Wenn wir das bauen

**Vision-Schicht:** `Manifest der Extraktion` ist ein Navigatorregal. Es zeigt ausgeschnittene Abschnitte aus vielen Dateien nebeneinander, aber die Bedeutung bleibt in der Ursprungsdatei.

**Code-Skizze:**
```ts
interface HolySectionEntry {
  section: 'Manifest der Extraktion';
  sectionKey: 'manifest_der_extraktion';
  sourcePath: string;
  sourceTitle: string;
  extractedText: string;
  requiresSourceOpen: true;
  canBeSource: false;
  worldEffect: false;
}
```

## Resonanz

Die Resonanz von `Manifest der Extraktion` ist Suchresonanz. Viele gleichartige Abschnitte nebeneinander können Muster erzeugen.

Aber diese Resonanz ist schwach, bis die Ursprungsdateien wieder geöffnet werden.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt Flarum. Darüber liegen Analyse-Dateien. Darüber liegt `15` als Extraktionsnavigator. Darüber könnte ein read-only Browser liegen.

`Manifest der Extraktion` darf diese Schichten nicht überspringen.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat `15` entlarvt: vollständige Pflichtüberschriften können trotzdem leer sein.

Diese Nacharbeit macht daraus eine Regel: Extraktion muss sich als Extraktion bekennen.

## Vergessen-Wollen

Vergessen werden soll bei `Manifest der Extraktion` die Idee, dass Aggregation automatisch Tiefe erzeugt.

Behalten werden soll die Rücksprungpflicht.

## Was fehlt noch

Es fehlt ein technischer Navigator, der `15` wirklich als Regal behandelt und nicht wie normale Analyse.

Bis dahin bleibt `MANIFEST.md` eine manuell markierte Suchdatei mit Quellenpflicht.
