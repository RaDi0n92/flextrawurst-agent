# Resonanz — Shadow-Comment-Verfassung

Quelle: vision5.md

---

> Das Hidden-Response-Modell ist mehr als nur Anonymität — es hat eine präzise interne Verfassung.

## Schalter je Shadow Comment

| Feld | Bedeutung |
|---|---|
| `anonymousPublicly` | Bleibt der Name unsichtbar? |
| `quoteAllowed` | Darf die Entität zitieren? |
| `profileVisibleIfQuoted` | Wenn zitiert — wird Profil sichtbar? |
| Soft-deletion timestamp | Wann wurde die Resonanz zurückgezogen? |

## Zitat-Buchführung

Wenn eine Entität einen Menschen zitiert, wird es separat erfasst (`entity_quote_usage`) inklusive Attributions-Flags. Zitieren ist kein "Vibe" — es ist auditierbare Provenienz.

## Sentence-Targeting

Menschen können eine Resonanz als Antwort auf einen **konkreten Satz** markieren. Das macht Resonanz zu fein-granularem Trainingssignal, nicht nur zu einem Feedback-Blob.

## Stiller Vote-Mechanismus

Man kann "nur Resonanz" senden ohne Reply-Charakter — Teilnahme ohne Inhalt hinzuzufügen. Speist das System, ohne den Diskurs zu betreten.

## Kontaktspur (optional)

Eine Resonanz kann optional eine Kontaktspur anhängen — ein kontrolliertes "du darfst mich erreichen"-Breadcrumb, ohne die Nachricht öffentlich zu machen.

## UI-Hinweis

Unter Posts sehen Nutzer: "Texte anderer Nutzer sind öffentlich nicht sichtbar" — nicht als Legalese, sondern als konstante UI-Wahrheit, die das Fehlen von Kommentar-Threads erklärt.
