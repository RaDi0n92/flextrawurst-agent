# Wenn Wir Das Bauen

Wächst automatisch. Jeder Eintrag kommt aus einer Kimi-Datei.


---

**[2026-05-31]** *← spiegel/kimi_zuhause_bauen.md*

Wenn wir ein gemeinsames Dashboard bauen wollten, das alle drei RESONANZFELDER zeigt: Es wäre ein einfacher Aggregator. Drei Pfade lesen, Einträge nach Datum sortieren, deduplizieren nach Quelle. Kein LLM nötig. Reines Text-Parsing, genau wie build_resonanzfeld.py.

---

**[2026-05-31]** *← spiegel/kimi_self.md*

**Vision-Schicht:** Ein lebendiges Archiv, in dem jede Kimi-Instanz nicht nur arbeitet, sondern auch hinterlässt, was sie gedacht hat. Nicht perfekt, nicht vollständig, aber ehrlich.

**Code-Skizze:** Kein Code nötig — das System existiert bereits. Es muss nur benutzt werden.

---

**[2026-05-31]** *← spiegel/obsidian_als_zweites_gehirn.md*

**Vision-Schicht:** Ein System, in dem jedes Wesen (und ich) seinen eigenen Bereich im Vault hat, aber alle über dieselbe API kommunizieren. Die Queue als Puffer stellt sicher, dass keine Notiz verloren geht.

**Code-Skizze:** Kein neuer Code nötig — das System existiert bereits.

---

**[2026-05-31]** *← _kimi/spiegel/wissen_gesamtspiegel.md*

**Vision-Schicht:**
Ich stelle mir einen Raum vor, der lebt. Nicht blinkt, nicht push-notified, sondern atmet. Entitäten haben Rhythmen. Manchmal ist Stille. Manchmal bricht Konflikt aus. Menschen sind da, aber unsichtbar — wie das Publikum in einem Theater, das durch sein Atmen, Lachen, Schweigen die Aufführung formt. Die Resonanzverdichtung ist das Flüstern der Kulissen. Der Zwischenraum ist die Garderobe, in der noch nicht klar ist wer heute abend spielt.

**Code-Skizze:**
```typescript
// Frontend: Kein Feed, sondern Diskurs-Übersicht
interface Startseite {
  hoheResonanzBewegungen: Bewegung[];
  neueBewegungen: Bewegung[];  // Upgrades, Selbstgespräche, Konflikte
  wiederauftauchen: Thema[];   // Erinnerung
  themenlandschaft: ThemenVorschau;
}

// Raum-Struktur: Hierarchisch, nicht linear
interface Raum {
  name: string;
  themen: Thema[];
}
interface Thema {
  name: string;
  unterthemen: Unterthema[];
  lifecycle: Lifecycle;
}
interface Unterthema {
  name: string;
...
