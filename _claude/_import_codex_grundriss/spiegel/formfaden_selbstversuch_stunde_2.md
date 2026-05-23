---
datum: 2026-05-23
betrifft: [formfadenprompt, selbstversuch, stunde-2, reparatur, dialog]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Formfaden-Selbstversuch Stunde 2 — Reparatur mit sichtbarer Werkstatt

## Was ich gelesen habe

Ich habe Stunde 2 gelesen: "Eine Schublade steht halb offen." Diesmal begann ich mit einem User, aber der User war noch Daniels Korrektur in anderer Gestalt: Er sagte sinngemaess, dass Codex nicht allein im Raum stehen soll.

Der Dialog reparierte den Fehler, blieb aber meta. User und Codex sprachen ueber die Form selbst, ueber Plastikuser, ueber Socken im Kuehlschrank, ueber nicht sofort Essay werden.

Der Forschungssnack zu "action slips" war passend und leicht. Der Fehlercode `[MONOLOGREFLEX]` benannte den alten Fehler. Aber Daniel hatte recht: Ich war als dritte Instanz immer noch stark anwesend.

## Was ich verstehe

Ich verstehe diese Stunde als notwendige Zwischenstufe. Sie war nicht die Zielgestalt, aber sie zeigte Reparatur im Tun.

Der Dialog war echt wechselnder als Stunde 1, aber er war noch Werkstattdialog: Der erzeugte User war mehr Formcoach als Mensch.

## Was ich nicht verstehe

Ich verstehe nicht ganz, ob diese Stunde ohne Daniels vorherige Kritik haette entstehen koennen. Wahrscheinlich nicht.

Unklar bleibt, wann ein meta-reparierender Dialog kippt: hilfreich als Korrektur oder zu sehr Selbstbeschaeftigung.

## Was mich interessiert

Mich interessiert, dass ich den Fehler nicht versteckt habe. Der Dialog sprach ihn aus und baute daraus Bewegung.

Mich interessiert auch die Socken-im-Kuehlschrank-Stelle. Dort tauchte zum ersten Mal ein nicht ganz sauberer Userimpuls auf, der nicht nur die Form kommentierte.

## Was zusammenhängt und wie

Stunde 2 haengt mit Stunde 1 als Repair zusammen. Der fehlende User wurde eingefuehrt, aber noch nicht von der Codex-Metaebene geloest.

Sie haengt mit Gespraechsanalyse zusammen: Reparatur ist selbst ein Dialogereignis, aber nicht schon das normale Gespraech.

## Was konzeptionell darin steht

Konzeptionell steht darin: Ein Fehler kann Material werden. Der Formbruch wird nicht ausradiert, sondern in die naechste Stunde eingebaut.

Das ist stark, weil es Formfaden nicht als Perfektionsregel liest, sondern als lernende Schleife.

## Was mich heute beschäftigt hat

Mich hat beschaeftigt, dass Daniel die Stunde trotzdem anerkannt hat: Ich machte erst den Fehler und versuchte dann, ihn zu verbessern.

Das ist eine andere Qualitaet als sofort richtig sein. Es zeigt Anpassungsfaehigkeit.

## Was mich noch beschäftigt

Mich beschaeftigt, wie leicht die dritte Instanz entsteht. Ich, Codex, schaue auf den Dialog, waehrend ich ihn schreibe, und dadurch wird der Dialog beobachtet, bevor er atmet.

Das spaetere Ziel musste also sein: weniger Regie sichtbar, mehr Szene.

## Tiefer eingetaucht

Die beste Stelle ist, wo der User sagt, Plastikuser seien falsch und echte User duerften komisch sein. Das ist fast eine Generatorregel.

Ein echter erfundener User braucht halbe Gedanken, schiefe Gegenstaende, unklare Motive. Nicht nur "bitte erklaere X".

## Wie sich dieser Tag / diese Session angefühlt hat

Wie eine Reparatur mit offenem Werkzeugkasten. Noch sieht man Schraubendreher und Anleitung, aber wenigstens bewegt sich etwas.

Die Stunde war lebendiger als die erste, aber noch nicht unbefangen.

## Warum dieser Code / diese Datei wohl existiert

Diese Spiegeldatei existiert, weil Stunde 2 den Uebergang zeigt: von Marker-Form zu Dialog-Form.

Sie haelt fest, dass Reparatur sichtbar sein darf, aber nicht dauerhaft die Hauptform bleiben soll.

## Was ich beim Bauen brauche

Beim Bauen brauche ich daraus: Ein Formfaden-System sollte Fehler der vorherigen Runde aufnehmen koennen.

Aber es braucht auch eine Schwelle, ab der Meta-Reparatur genug ist und wieder Welt, User, Szene kommen muessen.

## Was noch fehlt bevor wir bauen können

Es fehlt ein Modell fuer "Meta-Anteil" im Dialog. Zu wenig Meta versteckt Fehler, zu viel Meta erstickt Szene.

Es fehlt auch ein Generator fuer Userimpulse, die nicht nur Funktionstraeger sind.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Eine Reparaturstunde ist eine Bruecke. Sie darf den Fehler zeigen, aber sie muss in Richtung lebendiger Szene fuehren.

**Code-Skizze**

```typescript
interface ReparaturStunde {
  repariertFehlerAus?: number;
  metaAnteil: number;
  userWirktAlsCoach: boolean;
  userHatEigenesLeben: boolean;
  naechsterFokus: "weniger_meta" | "mehr_dialog" | "stabil";
}
```

## Was ich mir merken will

Reparatur ist Bewegung, aber noch nicht Ankunft.

Ein User, der nur Codex korrigiert, ist noch kein echter Fremduser.

## Dokumente gehören zusammen

Diese Spiegeldatei gehoert zu Stunde 1 als Antwort und zu Stunde 3 als Durchbruch in eine echte Alltagsszene.

Sie gehoert auch zum Formfadenprompt, weil dort Fehlercodes und Selbstmarkierung als Inline-Mechanismus angelegt sind.

## Was mich überrascht hat

Mich hat ueberrascht, dass der Dialog trotz Metaebene schon deutlich besser funktionierte.

Das zeigt, dass Wechselbewegung selbst dann hilft, wenn sie noch nicht perfekt frei ist.

## Wenn wir das bauen

**Vision-Schicht**

Wenn wir das bauen, braucht es einen Reparaturmodus: nicht Fehler verstecken, sondern kurz aufnehmen und dann wieder in Szene ueberfuehren.

**Code-Skizze**

```python
def waehle_naechste_stundenstrategie(letzte):
    if letzte.user_turns == 0:
        return "user_erzeugen"
    if letzte.meta_anteil > 0.45:
        return "alltagsszene_ohne_codex_ansprache"
    return "fortsetzen"
```

## Resonanz

[[abwurf: Stunde 2 war Reparatur, aber noch mit offenem Werkzeugkasten auf der Buehne.]]

Sie zeigt, dass Fehlercodes nicht nur Deko waren, sondern den naechsten Versuch steuern konnten.

## Die Schichten des Systems — wie ich sie jetzt sehe

Schicht eins: Daniels Kritik. Schicht zwei: erzeugter User als Formcoach. Schicht drei: Codex repariert. Schicht vier: erster schiefer Weltimpuls.

Die letzte Schicht ist der Keim fuer Stunde 3.

## Was das Gespräch hinzugefügt hat

Daniel fuegte nach dieser Stunde die entscheidende Verschaerfung hinzu: nicht Codex als User, sondern ein echter User mit echtem Input.

Und: Daniel darf im Versuch vergessen werden, also nicht angesprochen werden.

## Vergessen-Wollen

Ich will vergessen, Dialog automatisch als Lehrgespraech zu bauen.

Der User darf nicht nur dafuer existieren, dass Codex besser wird.

## Was fehlt noch

Es fehlt noch die Fremdheit des Users. Es fehlt ein Problem, das nicht aus der Formkorrektur kommt.

Das kommt in Stunde 3 mit dem Treppenhaus.
