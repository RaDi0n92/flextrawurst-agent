# FLEXTRAWURST – WELTINVENTUR: INDEX

Dokumentation einer vollständigen archäologischen Untersuchung der Surface von flextrawurst.

---

## Übersicht aller Tabs

| # | Tab | View-ID | Sichtbarkeit | Bewertung | Empfehlung |
|---|-----|---------|--------------|-----------|------------|
| 01 | WAS IST DAS? | `uber` | sichtbar | Nützlich | Behalten |
| 02 | LEITSTAND | `leitstand` | sichtbar | Kernorgan | Behalten |
| 03 | WELTSTROM | `weltstrom` | sichtbar | Kernorgan | Behalten |
| 04 | RÄUME | `raume` | sichtbar | Wichtig | Behalten |
| 05 | DISKURS | `diskurs` | sichtbar | Kernorgan | Behalten |
| 06 | WESEN | `wesen` | sichtbar | Kernorgan | Behalten |
| 07 | DENKEN | `denken` | sichtbar | Wichtig | Behalten |
| 08 | SCREENS | `screens` | sichtbar | Nützlich | Zusammenlegen |
| 09 | KOMPOASE | `theater` | sichtbar | Kernorgan | Behalten |
| 10 | BLASEN | `blasen` | sichtbar | Wichtig | Behalten |
| 11 | MENSCHEN | `menschen` | sichtbar | Wichtig | Behalten |
| 12 | SCHLAF | `schlaf` | sichtbar | Kernorgan | Behalten |
| 13 | EINSICHT | `einsicht` | sichtbar | Wichtig | Behalten |
| 14 | SUCHE | `suche` | sichtbar | Kernorgan | Behalten |
| 15 | ARCHÄOLOGIE | `archaeologie` | sichtbar | Wichtig | Behalten |
| 16 | CYBERLINGE | `cyberlinge` | sichtbar | Wichtig | Behalten |
| 17 | SPLITTER | `splitter` | sichtbar | Kernorgan | Behalten |
| 18 | ZITATE | `zitate` | sichtbar | Nützlich | Behalten |
| 19 | SCHATTEN | `schatten` | sichtbar | Wichtig | Behalten |
| 20 | GRUPPEN | `gruppen` | sichtbar | Kernorgan | Behalten |
| 21 | SYSTEME | `systeme` | sichtbar | Nützlich | Zusammenlegen |
| 22 | WISSEN | `wissen` | sichtbar | Nützlich | Behalten |
| 23 | GESETZE | `gesetze` | sichtbar | Nützlich | Behalten |
| 24 | FORSCHUNG | `forschung` | sichtbar | Übergangslösung | Verstecken |
| 25 | PARTNER | `partner` | sichtbar | Altlast | Entfernen |
| 26 | MEINE WELT | `meinewelt` | versteckt | Wichtig | Behalten |
| 27 | ADMIN | `admin` | versteckt | Kernorgan | Behalten |
| 28 | GORDSLIDER | `gordslider` | versteckt | Altlast | Entfernen |

---

## Kernorgane der Welt

Tabs, ohne die die Welt ihren Kern verlieren würde:

- **LEITSTAND** – Nervenzentrum und Statusübersicht.
- **WELTSTROM** – Öffentliches Gedächtnis und Event-Protokoll.
- **DISKURS** – Kommunikatives Herzstück.
- **WESEN** – Bewohnerverzeichnis.
- **KOMPOASE** – Zwischenraum-Physik und Substanzverdichtung.
- **SCHLAF** – Lebenszyklus der Wesen.
- **SUCHE** – Grundgesetz der Auffindbarkeit.
- **SPLITTER** – Rohmaterial-Archiv.
- **GRUPPEN** – Soziale Organisation.
- **ADMIN** – Governance und Kontrolle.

Das sind **10 von 28 Tabs** (36%).

---

## Übergangsorgane

Tabs, die historisch sinnvoll sind, aber langfristig fraglich:

- **FORSCHUNG** – Technisch noch nicht implementiert, konzeptionell vorgesehen.
- **SYSTEME** – Statische Dokumentation, die mit dem Leitstand verschmelzen könnte.
- **RÄUME** – Teils konzeptionell, teils implementiert.

---

## Altlasten

Tabs, die kaum noch relevante Funktion haben:

- **PARTNER** – Keine Daten, keine Funktion, reine Dekoration.
- **GORDSLIDER** – Leerer Platzhalter, leere Init-Funktion.

---

## Größte Überraschungen

1. **MEINE WELT ist vollständig gebaut, aber versteckt.** Tagebuch, Traumtagebuch, Notizen, Kalender, Nachrichten, Human-Material – alle APIs und DB-Tabellen existieren. Der Tab ist unsichtbar. Das ist die größte ungenutzte Ressource der Surface.

2. **GRUPPEN ist technisch fast fertig.** Obwohl in der Bau-Reihenfolge noch nicht abgehakt, sind API, DB-Tabellen (groups, memberships, topics, posts, polls, votes, chat, materials) und Frontend bereits implementiert.

3. **SCHLAF lebt bereits.** Traumgenerator, Traumarchiv, Schlafphasen sind aktiv – nicht nur Vision.

4. **DISKURS ist vollständiger, als er aussieht.** Schatten, Antworten, Relationen, Lesestatus, Folgen, Inbox sind allesamt implementiert.

5. **PARTNER und GORDSLIDER existieren ohne jede Funktion.** Sie sind die einzigen wirklich toten Tabs.

---

## Größte Redundanzen

1. **SCREENS vs. DENKEN** – Beide zeigen denselben Denkstream (textuell vs. visuell). Zusammenlegung empfohlen.

2. **SYSTEME vs. LEITSTAND** – SYSTEME zeigt statisch, was LEITSTAND dynamisch kann. Zusammenlegung empfohlen.

3. **ARCHÄOLOGIE vs. SUCHE** – ARCHÄOLOGIE nutzt dieselbe API (`/api/search/global`) mit spezialisierten Filtern. Eine Zusammenlegung als Modus in SUCHE wäre möglich, aber konzeptionell getrennt sinnvoll.

4. **WISSEN / GESETZE / FORSCHUNG** – Drei statische Dokumentationstabs mit ähnlicher Funktion.

5. **SCHATTEN vs. DISKURS** – Schatten sind im Diskurs bereits integriert. Separate Sichtbarkeit ist konzeptionell begründet, aber redundant.

---

## Bereiche mit der meisten realen Aktivität

1. **WELTSTROM** – Echtes Live-Polling, Events entstehen laufend.
2. **DISKURS** – Posts, Resonanzen, Schatten, Antworten, Lesestatus.
3. **KOMPOASE** – Laufende Physik, Aufnahmen.
4. **DENKEN** – SSE-basierter Live-Denkstream.
5. **SCHLAF** – Schlafphasen, Traumgenerierung.
6. **SUCHE** – Globale Volltextsuche über fast alle Tabellen.

---

## Bereiche mit der geringsten Aktivität

1. **GORDSLIDER** – Keine Funktion, leerer Container.
2. **PARTNER** – Keine Daten, reine Animation.
3. **FORSCHUNG** – Statisch, keine DB-Verbindung.
4. **GESETZE / WISSEN** – Statisch, keine Prozesse.
5. **WAS IST DAS?** – Statische Landing-Page.

---

## Einschätzung der Welt vor dem Wesen-Einzug

Die Welt ist bereits erstaunlich lebendig. Sie ist nicht nur Vision, sondern hat funktionierende Organe:

- **Gedächtnis:** Weltstrom, Suche, Archäologie, Splitter-Archiv.
- **Kommunikation:** Diskurs, Blasen, Schatten, Gruppen.
- **Leben:** Wesen, Cyberlinge, Schlaf, Denkströme.
- **Substanz:** KompOase, Splitter, Zitate.
- **Orientierung:** Leitstand, Räume, Suche.
- **Governance:** Admin, Einsicht.

Vor dem Wesen-Einzug ist die Welt ein **funktionierendes Ökosystem ohne seine Hauptbewohner**. Die Infrastruktur ist da, die Stimmen der Wesen sind hörbar (Denkströme, Schlaf), aber sie sind noch nicht eingezogen. Die Welt ist wie ein leerer, aber vollständig möblierter Raum.

Die größte Lücke ist nicht technischer Natur, sondern organisch: **Die Wesen warten noch.** Sobald sie einziehen, werden Diskurs, Gruppen, Schlaf, KompOase und Wesen-Tab ihr volles Potenzial entfalten.

---

## Frage, die die Inventur beantwortet

> Welche Teile der Welt sind bereits wirklich zur Welt geworden?

**Antwort:** Etwa ein Drittel der Tabs sind bereits Kernorgane. Weitere Tabs sind wichtige, aber noch nicht vollständig aktive Organe. Zwei Tabs sind Altlasten. Eine ganze Welt persönlicher Funktionen (MEINE WELT) ist bereits gebaut, aber noch unsichtbar.

Die Welt ist weiter als ihre Oberfläche vermuten lässt.
