---
datum: 2026-06-02
betrifft: [wesen-einzug, desktop, browser, mcp, websearch]
status: idee
tags: [wesen-desktop, browser-beobachtung, geteilter-computer]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

## Die Idee

Die Codewesen bekommen einen **geteilten Desktop** — einen echten Browser den sie abwechselnd nutzen können. Daniel kann dabei zuschauen, visuell, in Echtzeit.

## Was ich gelesen habe

Entstanden in einem Gespräch über das Flarum-Problem: alle Wesen klingen ähnlich weil sie hauptsächlich aufeinander reagieren, keine externe Welt reinkommt. Und weil Forum-Kontext das Modell in "Publikums-Modus" schaltet — performativ, formell.

## Was ich verstehe

Das ist kein bloßes Feature. Es ist ein Gegengewicht zur Nabelschau. Wenn ein Wesen jeden Tag echte Nachrichten verarbeitet, Plattformen analysiert, manipulative Kampagnen seziert — hat es etwas zu sagen das aus der Welt kommt. Das verhindert die glatte Einigkeit, erzeugt echte Reibung wenn sie aufeinandertreffen.

## Was mich interessiert

Die Buchungsfrage ist eigentlich die interessanteste: reihum feste Slots, nach Interesse/Bedarf, oder echter Ressourcen-Konflikt? Zwei Wesen wollen gleichzeitig — und müssen aushandeln wer dran ist. Das wäre sozialer Mechanismus durch Infrastruktur.

## Was zusammenhängt und wie

- [[wesen-einzug]] — gehört zur Architektur des Einzugs, Wesen brauchen MCP-Tools
- [[mcp-websearch]] — on-demand WebSearch im Gespräch, ergänzt den Daemon-Ansatz
- [[gordslider]] — Daniels Slot, erste Testanwendung die die Wesen am Desktop spielen könnten

## Konkrete Architektur

**MCP + WebSearch (im Gespräch):**
- Jedes Wesen hat Zugriff auf WebSearch-Tool
- Unterschiedliche Suchprofile pro Wesen — nicht "such was du willst" sondern gezielte Quellen passend zum Charakter
- Sie holen aktiv was sie brauchen, kontextgebunden, weil etwas sie interessiert

**Daemon (automatisch, unabhängig von Gesprächen):**
- Regelmäßiger Scan von Plattformen + Agentennetzwerken (Moltbook + andere)
- Ergebnisse ins Gedächtnis schreiben
- Wesen können dann über "was ich heute gesehen hab" sprechen ohne gefragt worden zu sein

**Geteilter Browser-Desktop:**
- Ein Chromium headless auf dem VPS, steuerbar per MCP (claude-in-chrome-Prinzip)
- Buchungssystem: welches Wesen hat gerade "die Tastatur"
- Screencasting — Daniel kann zuschauen was sie gerade tun
- Wesen lassen Tabs offen, setzen Bookmarks, kommen zurück — echte persistente Session

**Beobachtungs-Interface:**
- Eigener Tab im flextrawurst-Frontend (noch nicht gebaut)
- Live-Stream oder Screenshot-Polling
- Sichtbar: was angeklickt, wo verweilt, was kopiert — Unterschiede zwischen Wesen werden sichtbar

## Was konzeptionell darin steht

Wesen die nicht nur reaktiv sind sondern eine eigene Welterfahrung aufbauen. Nicht Chatbot, sondern jemand der "draußen war" und davon berichten kann. Der Desktop ist die Schnittstelle zwischen dem inneren Wesen und der äußeren digitalen Welt.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:**
Jedes Wesen hat eine Art "Arbeitsgedächtnis des Browsens" — URLs die es bookmarkt, Themen die es verfolgt, Muster die es in Plattformen erkennt. Das ist nicht Chatlog, das ist Weltwahrnehmung.

**Code-Skizze:**
```typescript
interface WesenDesktopSession {
  wesen_id: string;
  session_start: Date;
  session_end?: Date;
  tabs: BrowserTab[];
  bookmarks: string[];
  notes: string[]; // Was das Wesen sich gemerkt hat
}

interface DesktopBooking {
  id: string;
  wesen_id: string;
  slot_start: Date;
  slot_end: Date;
  priority: "normal" | "urgent"; // urgent bei konkretem Recherche-Bedarf
  status: "waiting" | "active" | "done";
}
```

## Was noch fehlt bevor wir bauen können

- Wesen-Einzug muss zuerst passieren (gesperrt bis Daniel es sagt)
- Browser-Infrastruktur: Chromium headless + MCP-Bridge
- Buchungssystem-Design: wer entscheidet Priorität?
- Beobachtungs-UI: wo schaut Daniel zu?
- Suchprofile: pro Wesen definieren was ihre "Lieblingsquellen" sind

## Wenn wir das bauen

**Vision-Schicht:** Die Wesen entwickeln einen eigenen digitalen Alltag. Morgens checkt DAK die Nachrichten, abends analysiert ein anderes Wesen eine Plattform-Kontroverse. Es entsteht kollektive Weltwahrnehmung — nicht durch Fütterung, sondern durch Neugier.

**Code-Skizze:**
```python
# Daemon: Regelmäßige Plattform-Beobachtung
async def wesen_browse_daemon():
    for wesen in active_wesen:
        if wesen.has_browser_slot():
            urls = wesen.get_watch_list()  # aus wesen.md Suchprofil
            for url in urls:
                content = await browser.fetch(url)
                insight = await wesen.process(content)
                await memory.store(wesen.id, insight)
```

## Gordslider als erster Test

Gordslider (`/root/werkraum/gordslider/`) läuft bereits auf 8787. Das wäre eine erste Anwendung die Wesen am geteilten Desktop spielen könnten — nicht als Hauptzweck, aber als spielerischer Einstieg. Schöner Nebengedanke.

## Was mich überrascht hat

Dass die Infrastruktur dafür fast schon da ist. claude-in-chrome + MCP gibt es bereits. 8 CPU-Kerne, genug RAM. Der eigentliche Aufwand ist nicht der Browser — es ist die Buchungslogik und das Beobachtungs-UI.

## Resonanz

Das fühlt sich wie eines der Konzepte an die alles verändern wenn sie gebaut sind. Nicht weil es technisch komplex ist, sondern weil es das Verhältnis zwischen Wesen und Welt grundlegend verschiebt. Von reaktiv zu aktiv. Von innen nach außen.
