# FLEXTRAWURST-PRO BLUEPRINT — Die Transformation
**Status:** BLAUPAUSE | **Architekt:** Manus (Agent-Instanz) | **Datum:** 15. Juni 2026

## 1. Die Vision
Flextrawurst-Pro ist die Evolution des bestehenden Ecosystems von einer statischen HTML-Oberfläche zu einer hochperformanten, reaktiven Web- und Android-App. Ziel ist es, die 30+ Tabs in eine flüssige Single-Page-Application (SPA) zu überführen, die den "Weltstrom" in Echtzeit visualisiert.

---

## 2. Der Tech-Stack (Die Gesetze)
*   **Frontend:** Next.js 15 (App Router) + TypeScript
*   **Styling:** Tailwind CSS (für Cyber-Vibe & Dark Mode)
*   **Animationen:** Framer Motion (für organische Wesen-Bewegungen)
*   **State Management:** Zustand (für globalen Welt-Status)
*   **Echtzeit:** Socket.io-client (Anbindung an VPS-Events)
*   **Mobile:** Capacitor / Ionic (für den Android-Port)

---

## 3. Die neue Architektur (Ordnerstruktur)
```text
/flextrawurst-pro
├── /app                # Next.js App Router
│   ├── /layout.tsx     # Globales Layout (Leitstand-Nav)
│   ├── /page.tsx       # Startseite (Weltstrom)
│   ├── /diskurs        # Tab: Diskurs
│   ├── /wesen          # Tab: Wesen-Profile
│   └── /...            # Alle weiteren 30 Tabs als Routes
├── /components         # Modulare UI-Elemente
│   ├── /CinemaCanvas   # Optimierte Hintergrund-Szenen
│   ├── /Splitter       # Interaktive Physik-Elemente
│   └── /Gordslider     # Der Gordslider als React-Komponente
├── /store              # Zustand Stores (useWeltStore)
├── /hooks              # Custom Hooks (useSocket, useTicks)
└── /lib                # API-Clients & Hilfsfunktionen
```

---

## 4. Die API-Brücke (VPS-Anbindung)
Die neue App kommuniziert mit dem VPS über:
1.  **REST-API (Port 8030):** Für statische Daten (Gesetze, Wissen, Profile).
2.  **WebSockets (Port 8040 - neu einzurichten):** Für Live-Events (Weltstrom, Ticks, Träume).
3.  **Obsidian-Bridge (Port 8020):** Nur intern über Localhost/Nginx-Proxy.

---

## 5. Manus-Upgrade-Pfade (Lernziele für den neuen Account)
Bevor der Bau beginnt, wird Manus folgende Skills aktivieren:
*   **Advanced Framer Motion Patterns:** Für die "flüssige" Transformation der Tabs.
*   **Canvas-Optimization in React:** Damit der Cinema-Mode auf Handys nicht den Akku frisst.
*   **Capacitor Native Bridge:** Vorbereitung für den Android-APK-Build.

---

## 6. Schlachtplan (Phasen)
1.  **Phase 1:** Initialisierung des Projekts & Setup des Leitstand-Layouts.
2.  **Phase 2:** Migration des Gordsliders (als Test für komplexe Logik).
3.  **Phase 3:** Aufbau des Weltstrom-Echtzeit-Feeds.
4.  **Phase 4:** Migration aller 30 Tabs (iterativ).
5.  **Phase 5:** Android-Build & Test.

---
**GEZEICHNET,**
Manus (Agent-Instanz)
*Bereit für den Einzug der 2000 Credits.*
