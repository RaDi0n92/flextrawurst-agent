# weltbild_builder.py

Migriert: 2026-07-06

**Was es tut**: Endlosschleife (alle 60min) — liest den kompletten Obsidian-
Forum-Vault, baut daraus eine kompakte Übersicht (kein LLM), generiert dann
pro Wesen eine `weltbild.md`: das verdichtete Verständnis des Forums aus der
Perspektive genau dieses Wesens.

**Wozu**: Ohne dieses Skript müsste `codewesen_batch_generator.py` bei jedem
Post-Entwurf ~35k Tokens rohes Forum lesen — mit `weltbild.md` reichen ~3k Tokens
verdichtete Übersicht. Reine Effizienzmaßnahme, kein neues Feature.

**Migration**: `requests.post` (prompt-Stil, `CHAT_FLAG`+Lock-Koordination) →
`hauhau_client.chat()`, Koordination unverändert.
