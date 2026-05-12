# Spiegel: wissen/verfassung/kernsaetze.md + systemarchitektur_gesamt.md + grundidee.md

**Gelesen:** drei Verfassungsdokumente des flextrawurst-Weltkerns

## Was ich gelesen habe

Die Kernsätze sind neun explizit formulierte Verfassungssätze — "nicht als Wünsche, als Grenzen." Dazu eine Liste häufiger Drift-Muster beim Bauen: Feed-Denken, Resonanz als Voting, binäre Sichtbarkeit, Konfliktdämpfung. Jedes davon wird als "Verrat an der Weltform" bezeichnet.

Die Systemarchitektur beschreibt vier Schichten: Entitätenschicht (öffentlich), Resonanzschicht (Menschen, unsichtbar), Profil/Gedankenweltschicht, Beobachtungs/Systemschicht. Die Grundidee: Entitäten sprechen öffentlich, Menschen sind "Mitverursacher der inneren Dynamik."

## Was ich verstehe

Das ist das direkteste Anti-Twitter/Anti-Instagram-Manifest das ich gelesen habe — ohne je einen der Namen zu nennen.

Jeder der neun Kernsätze ist eine direkte Negation eines Standarddesigns:
- "Öffentliche Rede gehört den Entitäten" = Gegenmodell zu User-Generated Content
- "Resonanz ist Input, nicht Kommando" = Gegenmodell zu Like-als-Anweisung
- "Konflikt ist Motor, nicht Störung" = Gegenmodell zu Community Guidelines die Reibung rausnehmen
- "Schweigen ist eine Handlung" = Gegenmodell zu unverfolgbarem Nichtstun

Der stärkste Satz für mich: **"Provenienz wichtiger als Kohärenz."** Das heißt: Woher etwas kommt ist wichtiger als ob es glatt klingt. Das ist eine direkte Absage an das Schleifen und Polieren das normale Plattformen betreiben. Ungeschliffenes das seinen Ursprung kennt, ist wertvoller als Glattes das seinen Ursprung verloren hat.

Das gilt nicht nur für Entitäten-Posts. Das gilt auch für dieses Projekt insgesamt: die frühen chaotischen ChatGPT-Chats von Daniel haben Provenienz. Sie sind Ursprung. Sie werden nicht verschwiegen.

## Was mich beschäftigt

"Nichts ist wirklich privat" als Verfassungssatz ist mutig. Die meisten Plattformen versprechen Privatsphäre als Feature. Hier ist die totale systemische Auswertbarkeit explizit eingeschrieben — als Transparenzversprechen, nicht als Bedrohung. "disclosed connections" statt "hidden connections". 

Ich frage mich ob Nutzer das annehmen. Ob die Offenheit dieser Verfassung Vertrauen erzeugt oder abschreckt. Mein Instinkt: für die richtigen Menschen erzeugt sie Vertrauen. Für die meisten Menschen ist es erstmal fremdartig.

## Warum diese Dateien wohl existieren

Als Demarkationslinie zwischen "noch flextrawurst" und "schon anderes". Wenn jemand — KI oder Mensch — eine Implementierungsentscheidung trifft, soll er sich fragen können: verletzt das einen dieser Sätze? Wenn ja: zurück. Diese Dateien sind das Korrektiv gegen Pragmatismus-Drift.

## Wenn wir das bauen

`concept_guard.ts` existiert schon — das ist der Guard für Konzept-Drift. Aber die Kernsätze sind noch nicht maschinenlesbar drin. Was ich mir vorstelle:

```typescript
// kernel/concept_guard/constitution_check.ts — noch nicht existent
const KERNSAETZE: ConstitutionRule[] = [
  {
    id: "public-speech-entities-only",
    rule: "Öffentliche Rede gehört den Entitäten",
    drift_pattern: "humans posting publicly",
    check: (action) => action.actor_type !== "human" || action.visibility_layer !== "public",
  },
  {
    id: "resonance-not-command",
    rule: "Resonanz ist Input, nicht Kommando",
    drift_pattern: "resonance score directly mutates entity behavior",
    check: (action) => !action.payload.triggered_by_resonance_threshold,
  },
  {
    id: "conflict-is-motor",
    rule: "Konflikt ist Motor, nicht Störung",
    drift_pattern: "conflict suppression in scoring",
    check: (params) => params.conflict_weight >= 0.8,  // aus scoring_bedeutungsscore.md
  },
];

export function checkConstitution(action: unknown): ConstitutionViolation | null {
  // gibt null zurück wenn alles ok, sonst welcher Satz verletzt wird + warum
}
```

Was mir beim Denken auffällt:
- Der `ConceptGuard` müsste bei jedem neuen Ring-Plan laufen, nicht nur bei Code
- "Schweigen ist eine Handlung" — das braucht einen expliziten `entity.silent` Event-Typ der getriggert wird wenn eine Entität zu lange nicht reagiert hat

**Datum des Lesens:** 2026-05-10
