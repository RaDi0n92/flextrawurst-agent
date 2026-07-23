# Flextrawurst - Feature-Activation-System Explorations-Dokument

## Feature Activation Gate - Evaluierung

### Prinzip
**Gate System**: Bevor ein Feature aktiviert werden kann, wird es durch einen Gate evaluiert, der:
1. **Permissions** prüft (Wer darf was?)
2. **Blocker** prüft (Was blockiert das Feature?)
3. **Approvals** prüft (Wer muss explizit zustimmen?)
4. **Concept Readiness** prüft (Ist das Konzept bereit?)

### Evaluierungs-Logik

#### 1. Permissions-Check
```typescript
if (!hasPermission(actor, "feature.approve_activation")) {
  missingPermissions.push("feature.approve_activation");
}
```
- Nur User mit Permission "feature.approve_activation" können Features aktivieren

#### 2. can_enable_now Check
```typescript
if (!feature.can_enable_now) {
  blockers.push("can_enable_now_is_false");
}
```
- Features mit `can_enable_now = false` können nicht aktiviert werden
- Dies wird in der Feature Registry konfiguriert

#### 3. Daniel-Approval Check
```typescript
if (feature.requires_daniel_approval && actor.role !== "daniel_root") {
  blockers.push("requires_daniel_root_approval");
  requiredApprovals.push("daniel_root");
}

if (feature.requires_daniel_approval) {
  requiredApprovals.push("daniel_explicit_approval");
}
```
- Wenn `requires_daniel_approval = true`, muss Daniel (role: daniel_root) explizit zustimmen
- Andernfalls wird der Aktivierungsversuch blockiert

#### 4. Concept Readiness Check
```typescript
if (feature.requires_concept_readiness) {
  blockers.push("concept_readiness_required");
  notes.push("Konzept braucht Daniels Feinplanung.");
}
```
- Features mit `requires_concept_readiness = true` werden erst aktiviert, wenn das Konzept "bereit" ist
- Dieser Status wird wahrscheinlich extern definiert

### Ergebnis
Das Gate gibt zurück:
- `allowed: boolean` - Kann das Feature aktiviert werden?
- `blocked: boolean` - Wurde es blockiert?
- `missing_permissions: string[]` - Welche Rechte fehlen
- `blockers: string[]` - Was genau blockiert es
- `required_approvals: string[]` - Welche Zustimmungen nötig
- `notes: string[]` - Zusätzliche Hinweise

## Offene Fragen zu Features

1. **Warum Feature-Activation-System?**
   - Warum nicht einfach Features ein/ausschalten?
   - Was ist das Problem, das dieses System lösen soll?

2. **Concept Readiness**
   - Wem gehört die Verantwortung für "readiness"?
   - Wie wird "ready" bestimmt?
   - Ist das abhängig von Daniel's Planung?

3. **Blocker-System**
   - Warum `blockers: string[]` statt booleschem Flag?
   - Welche Arten von Blockern gibt es außer "concept_readiness_required"?
   - Können Blocker überwunden werden?

4. **Role-Basierte Permissions**
   - Welche Permissions gibt es außer "feature.approve_activation"?
   - Wie werden Permissions vergeben?
   - Kann Daniel Rollen verwalten?

5. **Feature-Lifecycle**
   - Was passiert nach "activation_blocked"?
   - Kann ein Feature deaktiviert werden?
   - Was ist der Unterschied zwischen "disabled" und "activation_blocked"?

6. **Konnektivität zu Ringen**
   - Sind Features und Ringe verbunden?
   - Aktiviert ein Ring ein Feature oder umgekehrt?
   - Welche Ringe haben welche Features?
