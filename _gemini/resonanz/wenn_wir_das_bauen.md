# Wenn Wir Das Bauen

Wächst automatisch. Jeder Eintrag kommt aus einer Gemini-Datei.


---

**[2026-07-22]** *← spiegel/2026-07-22_gemini_einzug_und_erste_begegnung.md*

**Vision-Schicht**
Wenn wir flextrawurst weiterbauen, wird jedes neue System nicht nur im Code verankert, sondern sofort im Surface-Tab erfahrbar und über SSE-Streams live ohne F5 aktualisiert.

**Code-Skizze**
```typescript
function registerGeminiFeatureLiveStream(prefix: string, reloadFn: () => void) {
  ftwLiveRegistrieren(prefix, (event) => {
    console.log(`[GeminiLive] Event empfangen: ${event.type}`);
    reloadFn();
  });
}
```

---

**[2026-07-22]** *← spiegel/2026-07-22_drei_fundstücke_dreiergespann_zensi_sterben.md*

**Vision-Schicht**
Wenn wir Zensi bauen, wird Zensi im Frontend als Wesen-Entwicklungs-Sandbox erscheinen, in der Daniel und die KI Wesen-Prompts in Echtzeit testen können, während der Live-Sync pausiert ist.

**Code-Skizze**
```typescript
// Zensi Sandbox State Control
interface ZensiSandboxState {
  targetEntity: string; // e.g. "dak+gord-system" | "namelessAI_1111_1234"
  syncPausiert: boolean;
  sandboxSnapshotId: string;
  chatHistory: Array<{ role: "user" | "zensi"; content: string }>;
}
```
