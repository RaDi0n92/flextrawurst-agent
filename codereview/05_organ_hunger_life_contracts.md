# Review: Organhunger und Life-Contracts

## Hoch

- Kompakte Organhunger-API gibt Dataclass-Objekte zurueck. `/root/werkraum/welt/wesen_organ_hunger.py:334` bis `:344` legt in `top_hunger` rohe `OrganHunger`-Objekte ab. `/root/werkraum/welt/api.py:12058` bis `:12068` gibt `_alle_hunger(...)` direkt aus. FastAPI kann diese Objekte je nach Encoder zwar teilweise handhaben, aber das Format ist inkonsistent zum Einzelreport `to_dict()` und riskant.

- Empfehlungen sind teils nicht ausfuehrbar. `/root/werkraum/welt/wesen_organ_hunger.py:114`, `:187`, `:257`, `:288` empfehlen Aktionen wie `denkfenster_vertiefen`, `splitter_erzeugen`, `beziehung_pruefen`, `kompoase_betreten`. Im Kern sind diese Aktionen nicht Teil von `AKTIONEN` in `/root/werkraum/welt/entity_kern.py:35` bis `:48`. Das Organ zeigt Hunger, den das Wesen nicht direkt stillen kann.

- Schattenhunger bleibt wahrscheinlich dauerhaft offen. `/root/werkraum/welt/wesen_organ_hunger.py:202` bis `:223` zaehlt offene/gelesene Schatten. Da `entity_kern.py` beantwortete Schatten nicht markiert, wird dieser Hunger nach Antworten nicht verlaesslich kleiner.

## Mittel

- Traumhunger zaehlt moeglicherweise die falsche Quelle. `/root/werkraum/welt/wesen_organ_hunger.py:128` bis `:133` sucht `entity_thinking_log.entscheidung LIKE 'traum%'`. Die Traum-/Takt-Systeme schreiben aber auch `events`, `traumspuren` oder andere Tabellen. Dadurch kann echter Traumvollzug als Hunger erscheinen.

- Cursor-Konfiguration ist uneinheitlich. `/root/werkraum/welt/wesen_organ_hunger.py:21` bis `:22` setzt `conn.cursor_factory = RealDictCursor`, statt wie in den meisten Dateien `psycopg2.connect(..., cursor_factory=RealDictCursor)` zu verwenden. Das sollte verifiziert werden, weil sonst `denk["cnt"]`-Zugriffe zur Laufzeit brechen.

- Organhunger ist lesend, aber nicht statusbewusst. Die Funktion nimmt jedes `entity_id` an und prueft nicht, ob das Wesen eingezogen, bereit, deaktiviert oder nur Blueprint ist. Bei Pre-Entry kann das falsche rote Ampeln erzeugen.

## Tests, die fehlen

- `/admin/wesen-einsicht/organ-hunger` muss JSON ohne Dataclass-Rohobjekte liefern.
- Jede `recommended_action` muss entweder im Kern ausfuehrbar sein oder als Admin-/Planungsaktion markiert werden.
- Eine beantwortete Schattenreaktion muss den Schattenhunger senken.
