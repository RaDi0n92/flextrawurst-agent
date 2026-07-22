---
datum: 2026-05-31
betrifft: [surface, ui-inventur, einsicht-ii]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Surface-UI-Inventur

## Was ich gelesen habe

Ich habe die aktive Surface-Quelle in `/root/flextrawurst/scripts/build_surface.ts` gelesen. Sie ist gross, direkt, gewachsen und voller UI-Patterns.

Ich habe die EINSICHT-Struktur genauer gelesen: Header, Wesenfilter, Subtabs, Liste links, Detailpanel rechts. Das ist bereits fast genau die Form, die EINSICHT II braucht.

Ich habe auch die mehrfachen Suchorte gesehen: Topbar, Diskurs, Backend global, Backend archaeology. Das Wort *Suche* ist nicht eine Komponente, sondern eine kleine Familie.

## Was ich verstehe

EINSICHT II sollte in den vorhandenen EINSICHT-Tab hinein, nicht als neuer Haupttab.

## Was ich nicht verstehe

Ich verstehe noch nicht, welcher Suchort spaeter offiziell "die" Archäologie-Suche sein soll.

## Was mich interessiert

Mich interessiert das Detailpanel als gemeinsamer Ort: Entscheidung, Traum, Brief, Splitter, Schatten, Event koennten dort dieselbe Wuerde bekommen.

## Was zusammenhängt und wie

Tabs, Subtabs, Status-Badges, Entity-Selector und Detailpanel bilden schon eine UI-Grammatik.

## Was konzeptionell darin steht

Die Surface will keine Admin-Tabelle sein. Sie will Weltkoerper bleiben, auch wenn sie technische Daten zeigt.

## Was mich heute beschäftigt hat

Die Pfaddrift zwischen `/root/flextrawurst` und `/root/werkraum/flextrawurst` ist klein im Namen, gross in der Wirkung.

## Was mich noch beschäftigt

Viele Patterns sind inline. Wiederverwendung ist moeglich, aber nicht sauber komponentisiert.

## Tiefer eingetaucht

`ei-item` ist der beste Trefferlisten-Baustein. `ei-detail-panel` ist die beste Detail-Zielansicht. `koZeigeSpur()` ist der beste Provenienzblock.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie UI-Vermessung ohne Pixel-Schubsen. Trocken, aber noetig.

## Warum dieser Code / diese Datei wohl existiert

Die Inventur existiert, damit EINSICHT II nicht aus Versehen ein neues Designsystem erfindet.

## Was ich beim Bauen brauche

Beim Bau brauche ich eine Entscheidung: EINSICHT II als Subtab `archaeologie` oder `suche`.

## Was noch fehlt bevor wir bauen können

Ein kanonisches SearchResult-Modell und stabile Typkeys.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Die Suche ist kein Suchfeld, sondern eine Art Gedaechtnis-Tuer. Sie muss zeigen, woher etwas kommt und wohin man damit geht.

**Code-Skizze:**
```ts
type UiTarget = {
  view: "einsicht" | "diskurs" | "kompoase" | "menschen" | "wesen";
  panel: "detail" | "canvas" | "post";
  id: string;
};
```

## Was ich mir merken will

Nicht noch einen Drawer bauen. Der Drawer ist schon da, er heisst nur je nach Tab anders.

## Dokumente gehören zusammen

`surface_ui_inventur_2026-05-31.md`, `build_surface.ts`, `out/process_camera/flextrawurst_surface.html`.

## Was mich überrascht hat

Dass EINSICHT schon sehr nah an der noetigen Form ist. Es fehlt weniger UI als Klarheit.

## Wenn wir das bauen

**Vision-Schicht:** EINSICHT II soll Archäologie als Lesen fuehlbar machen: Treffer, Spur, Kontext, Ziel.

**Code-Skizze:**
```ts
function renderArchaeologyResult(r: ArchaeologyResult) {
  return renderEiItem(r.ts, r.snippet, r.source_type, r.visibility);
}
```

## Resonanz

[[abwurf: Der beste neue UI-Baustein ist manchmal der, der schon da ist und endlich kanonisch genannt wird.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Topbar, Haupttabs, Subtabs, Listen, Detailpanel, Canvas. Suche muss durch diese Schichten laufen, nicht daneben.

## Was das Gespräch hinzugefügt hat

Daniel hat den Scope sauber gehalten: nur lesen, keine Surface anfassen.

## Vergessen-Wollen

Den Impuls, beim Inventarisieren schon UI-Code zu bauen.

## Was fehlt noch

Ein kleiner Designvertrag fuer EINSICHT-II-Suchergebnisse.
