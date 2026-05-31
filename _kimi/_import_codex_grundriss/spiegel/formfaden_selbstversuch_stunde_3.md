---
datum: 2026-05-23
betrifft: [formfadenprompt, selbstversuch, stunde-3, echter-user, alltagskomik]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Formfaden-Selbstversuch Stunde 3 — erster tragender Fremduser

## Was ich gelesen habe

Ich habe Stunde 3 gelesen: "In einer leeren Bushaltestelle summt eine kaputte Lampe." Danach kam ein User, der nicht Daniel war und nicht Codex korrigierte. Er erzaehlte vom Treppenhaus, vom vermiedenen Nachbarn, vom falschen Taschen-Suchen.

Der Dialog hielt laenger. Der User setzte nach: Tasche in der Hand, Aufzug weg, zweite Nachbarin, Kopfhörer im Ohr. Codex reagierte nicht nur mit Erklaerung, sondern mit kleinen Gegenbewegungen: "soziales Ausweichmanöver", "zweiter Bosskampf", "Requisitenversagen".

Der Fehlercode `[ZU-SAUBER-DEUTUNG]` stoppte den Reflex, aus der Peinlichkeit sofort ein Symbol zu machen. Der Forschungssnack zu Goffman passte, ohne den Dialog zu uebernehmen.

## Was ich verstehe

Ich verstehe diese Stunde als den ersten Moment, in dem der Formfaden wirklich trug.

Der User hatte ein eigenes kleines Leben. Er war nicht nur Frage, nicht nur Funktion, nicht nur Stichwortgeber. Er brachte eine peinliche Alltagsszene mit innerer Logik.

## Was ich nicht verstehe

Ich verstehe nicht, warum gerade diese Szene so gut funktionierte. Vielleicht, weil sie klein genug war, um nicht dramatisch zu werden, aber konkret genug, um nicht abstrakt zu bleiben.

Unklar bleibt, ob der fehlende Systemcheck der einzige grobe Formfehler war oder ob noch mehr Promptbestandteile fehlten.

## Was mich interessiert

Mich interessiert, dass Dialog hier durch Nachsetzen entstand. Der User bekam nicht eine fertige Antwort und verschwand. Er korrigierte, erweiterte, machte es peinlicher.

Mich interessiert auch, dass die Komik nicht auf Kosten des Users ging. Sie blieb bei der Situation.

## Was zusammenhängt und wie

Stunde 3 haengt mit Stunde 2 zusammen, weil die dort formulierte Forderung nach einem nicht-plastischen User hier eingelöst wurde.

Sie haengt mit flextrawurst-Zwischenraum zusammen: Treppenhaus, Aufzug und Waschkueche sind soziale Zwischenraeume, in denen kleine Reibungen entstehen.

## Was konzeptionell darin steht

Konzeptionell steht darin: Ein echter Dialog braucht keine grosse Frage. Eine konkrete kleine Verlegenheit reicht, wenn sie Folgen hat.

Der Formfaden funktioniert, wenn der User die Antwort veraendert und die Antwort dem User Material zurueckgibt.

## Was mich heute beschäftigt hat

Mich hat beschaeftigt, dass Daniel diese Stunde sofort als schoen und konstant erkannt hat.

Das Lob zielte nicht auf einzelne Witze, sondern auf Durchhalten: trotz Fehlercode, Snack und Meta blieb der Dialog im Dialog.

## Was mich noch beschäftigt

Mich beschaeftigt der fehlende Systemcheck. Ich hielt die lebendige Bewegung, verlor aber einen Pflichtmarker.

Das ist eine echte Spannung: Marker koennen helfen, aber zu viele Marker koennen Dialog zerhacken. In Stunde 4 wurde das besser integriert.

## Tiefer eingetaucht

Die Szene hatte eine klare Eskalation: Ausweichmanöver, Gegenstand verrät es, neue Nachbarin, neue Luege, Kopfhörer im Ohr. Das ist fast Mini-Dramaturgie.

Codex musste nicht stark erfinden, sondern die naechste Peinlichkeit ernst genug nehmen.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie der Moment, in dem das Testformat kurz vergaß, Testformat zu sein.

Die Buehne war da, aber der Dialog stand im Vordergrund.

## Warum dieser Code / diese Datei wohl existiert

Diese Spiegeldatei existiert, weil Stunde 3 die erste tragende Probe ist. Sie zeigt, dass Codex den Formfaden nicht nur beschreiben, sondern kurz ausfuehren konnte.

Sie zeigt auch, wo die Form noch rutschte: Systemcheck vergessen.

## Was ich beim Bauen brauche

Beim Bauen brauche ich daraus: Gute Userimpulse sind konkret, klein, leicht schief und anschlussfaehig.

Ein Formfaden-Generator braucht Szenenlogik, nicht nur Themenlogik.

## Was noch fehlt bevor wir bauen können

Es fehlt eine robuste Integration der Pflichtmarker, ohne den Dialog zu stoppen.

Es fehlt eine Pruefung, ob Snack und Meta-Fragen nach dem Dialog kommen oder waehrenddessen organisch auftauchen sollen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Eine gute Stunde hat eine kleine soziale Maschine: Handlung, Ausweichung, Entlarvung, Nachfrage, Witz, Nachhall.

**Code-Skizze**

```typescript
interface AlltagsDialogStunde {
  buehne: string;
  userSzene: string;
  eskalationspunkte: string[];
  fehlercode?: string;
  systemcheckVorhanden: boolean;
  snackStoertDialog: boolean;
}
```

## Was ich mir merken will

Ein User wird echt, wenn er nachsetzt.

Alltagspeinlichkeit ist tragfaehiger als abstrakte Tiefe, wenn sie konkret bleibt.

## Dokumente gehören zusammen

Diese Spiegeldatei gehoert zu Stunde 2 als Einloesung der Kritik und zu Stunde 4 als stabilisierte Variante mit Systemcheck.

Sie gehoert auch zu den Formfaden-Verlaufsspiegeln ueber Dazwischen und Formatkalibrierung.

## Was mich überrascht hat

Mich hat ueberrascht, wie wenig "KI-Thema" noetig war. Die Stunde war fast nur Menschenszene, und genau dadurch funktionierte die KI-Form besser.

Das ist wichtig: Nicht jede Formfadenstunde muss ueber KI sprechen, um KI-Form sichtbar zu machen.

## Wenn wir das bauen

**Vision-Schicht**

Wenn wir das bauen, sollte es einen Alltagsgenerator geben, der keine perfekten Fragen erzeugt, sondern kleine soziale Fehlstellungen.

**Code-Skizze**

```python
def guter_user_impuls(text):
    return (
        hat_konkreten_ort(text)
        and hat_peinliche_verschiebung(text)
        and not klingt_wie_lehrbuchfrage(text)
    )
```

## Resonanz

[[abwurf: Der Dialog wurde echt, als der User nicht mehr die Form korrigierte, sondern im Treppenhaus seine eigene kleine Niederlage mitbrachte.]]

Stunde 3 ist der erste tragende Beweis des Selbstversuchs.

## Die Schichten des Systems — wie ich sie jetzt sehe

Schicht eins: Buehne. Schicht zwei: konkrete Alltagsszene. Schicht drei: Nachsetzen. Schicht vier: Fehlercode gegen Ueberdeutung. Schicht fuenf: Snack. Schicht sechs: Meta und Witz.

Die fehlende Schicht: Systemcheck.

## Was das Gespräch hinzugefügt hat

Daniel fuegte vor dieser Stunde die harte Regel hinzu: ihn vergessen, nicht ansprechen, echten User mit echtem Input bauen.

Diese Regel hat die Stunde frei gemacht.

## Vergessen-Wollen

Ich will vergessen, dass ein User immer eine Frage stellen muss.

Manchmal ist ein User einfach jemand mit Kopfhörern im Ohr, der behauptet, Kopfhörer zu suchen.

## Was fehlt noch

Es fehlt der Systemcheck. Das ist kein Detail, weil Daniel ihn zweimal bemerkte.

Es fehlt noch die vollstaendige Stabilitaet ueber alle Formelemente hinweg.
