"""
Wesen Organ Hunger — prüft ob ein Organ unterversorgt ist.

Organhunger erzeugt KEINE Fake-Events.
Er erzeugt Prüfanlässe: wo soll das System als nächstes schauen?

Wenn kein echter Anlass → no_trigger protokollieren.
Wenn Anlass → can_be_considered = True für diesen Tick setzen.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import psycopg2
import psycopg2.extras


import os as _os; DB_URL = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")


def get_conn():
    conn = psycopg2.connect(DB_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


@dataclass
class OrganHunger:
    organ_id: str
    entity_id: str
    hunger_level: float       # 0.0–1.0
    hunger_reason: str
    has_trigger: bool
    trigger_sources: list[str] = field(default_factory=list)
    last_activity: datetime | None = None
    recommended_action: str | None = None


@dataclass
class EntityHungerReport:
    entity_id: str
    calculated_at: datetime
    organ_hungers: list[OrganHunger]

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "calculated_at": self.calculated_at.isoformat(),
            "organs": [
                {
                    "organ_id": h.organ_id,
                    "hunger_level": round(h.hunger_level, 2),
                    "hunger_reason": h.hunger_reason,
                    "has_trigger": h.has_trigger,
                    "trigger_sources": h.trigger_sources,
                    "last_activity": h.last_activity.isoformat() if h.last_activity else None,
                    "recommended_action": h.recommended_action,
                }
                for h in self.organ_hungers
            ],
        }


def _now() -> datetime:
    return datetime.now(timezone.utc)


def berechne_organ_hunger(entity_id: str) -> EntityHungerReport:
    """
    Berechnet den Organhunger für ein Wesen.
    Liest nur — schreibt nichts.
    """
    conn = get_conn()
    hungers: list[OrganHunger] = []

    try:
        with conn.cursor() as cur:
            now = _now()

            # ── DENKFENSTER-HUNGER ────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as cnt,
                       MAX(tick_at) as letzte
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND tick_at > NOW() - INTERVAL '24h'
            """, (entity_id,))
            denk = cur.fetchone()
            denk_cnt = denk["cnt"] or 0
            denk_letzte = denk["letzte"]

            cur.execute("""
                SELECT COUNT(*) as cnt
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND entscheidung = 'nachdenken'
                  AND tick_at > NOW() - INTERVAL '24h'
                  AND (meta->>'denkfenster_genutzt' IS NULL OR meta->>'denkfenster_genutzt' = 'false')
            """, (entity_id,))
            ohne_denkf = cur.fetchone()["cnt"] or 0

            denkf_hunger = 0.0
            if denk_cnt > 0:
                ratio = ohne_denkf / max(denk_cnt, 1)
                denkf_hunger = min(1.0, ratio)

            hungers.append(OrganHunger(
                organ_id="denkfenster",
                entity_id=entity_id,
                hunger_level=denkf_hunger,
                hunger_reason=f"{ohne_denkf} von {denk_cnt} Ticks ohne Denkfenster",
                has_trigger=denkf_hunger > 0.4,
                trigger_sources=["entity_thinking_log"],
                last_activity=denk_letzte,
                recommended_action="denkfenster_vertiefen" if denkf_hunger > 0.6 else None,
            ))

            # ── TRAUM-HUNGER ──────────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as schlaf_cnt
                FROM sleep_phases
                WHERE entity_id = %s
                  AND phase_type = 'hauptschlaf'
                  AND ended_at IS NOT NULL
                  AND started_at > NOW() - INTERVAL '72h'
            """, (entity_id,))
            schlaf_cnt = cur.fetchone()["schlaf_cnt"] or 0

            cur.execute("""
                SELECT COUNT(*) as traum_cnt, MAX(tick_at) as letzte
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND (entscheidung LIKE 'traum%%' OR entscheidung = 'traum_integrieren')
                  AND tick_at > NOW() - INTERVAL '72h'
            """, (entity_id,))
            traum_row = cur.fetchone()
            traum_cnt = traum_row["traum_cnt"] or 0
            traum_letzte = traum_row["letzte"]

            traum_hunger = 0.0
            if schlaf_cnt > 0:
                traum_hunger = min(1.0, max(0.0, (schlaf_cnt - traum_cnt) / max(schlaf_cnt, 1)))

            hungers.append(OrganHunger(
                organ_id="traum",
                entity_id=entity_id,
                hunger_level=traum_hunger,
                hunger_reason=f"{schlaf_cnt} Schlafphasen, {traum_cnt} Traum-Events (72h)",
                has_trigger=traum_hunger > 0.3 and schlaf_cnt > 0,
                trigger_sources=["sleep_phases", "entity_thinking_log"],
                last_activity=traum_letzte,
                recommended_action="traumrest_integrieren" if traum_hunger > 0.5 else None,
            ))

            # ── SPLITTER-HUNGER ───────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as cnt, MAX(tick_at) as letzte
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND (entscheidung = 'splitter_aufsammeln' OR entscheidung = 'splitter_erzeugen')
                  AND tick_at > NOW() - INTERVAL '48h'
            """, (entity_id,))
            spl_row = cur.fetchone()
            spl_in_log = spl_row["cnt"] or 0
            spl_letzte = spl_row["letzte"]

            cur.execute("""
                SELECT COUNT(*) as cnt
                FROM events
                WHERE (actor_id = %s OR payload->>'entity_id' = %s)
                  AND event_type IN ('entity.konflikt_erkannt', 'cyberling.conflict')
                  AND created_at > NOW() - INTERVAL '48h'
            """, (entity_id, entity_id))
            konflikt_cnt = cur.fetchone()["cnt"] or 0

            spl_hunger = 0.0
            if konflikt_cnt > 0 and spl_in_log == 0:
                spl_hunger = min(1.0, konflikt_cnt * 0.3)

            hungers.append(OrganHunger(
                organ_id="splitter",
                entity_id=entity_id,
                hunger_level=spl_hunger,
                hunger_reason=f"{konflikt_cnt} Konflikte ohne Splitter-Reaktion (48h)",
                has_trigger=spl_hunger > 0.3,
                trigger_sources=["events", "entity_thinking_log"],
                last_activity=spl_letzte,
                recommended_action="splitter_erzeugen" if spl_hunger > 0.5 else None,
            ))

            # ── SCHATTEN-HUNGER ───────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as offen, MAX(sk.created_at) as letzte
                FROM schattenkommentare sk
                JOIN ftw_posts p ON p.id = sk.post_id
                WHERE p.autor_type = 'entity' AND p.autor_id = %s
                  AND sk.antwortstatus IN ('offen', 'gelesen')
            """, (entity_id,))
            sch_row = cur.fetchone()
            sch_offen = sch_row["offen"] or 0
            sch_letzte = sch_row["letzte"]

            cur.execute("""
                SELECT COUNT(*) as beantwortet
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND entscheidung = 'schattenkommentar_antworten'
                  AND tick_at > NOW() - INTERVAL '48h'
            """, (entity_id,))
            sch_beantw = cur.fetchone()["beantwortet"] or 0

            sch_hunger = 0.0
            if sch_offen > 0:
                sch_hunger = min(1.0, sch_offen * 0.2 * (1 - min(1, sch_beantw / max(sch_offen, 1))))

            hungers.append(OrganHunger(
                organ_id="schatten",
                entity_id=entity_id,
                hunger_level=sch_hunger,
                hunger_reason=f"{sch_offen} offene Schatten, {sch_beantw} beantwortet (48h)",
                has_trigger=sch_hunger > 0.2 and sch_offen > 0,
                trigger_sources=["schattenkommentare", "entity_thinking_log"],
                last_activity=sch_letzte,
                recommended_action="schattenkommentar_antworten" if sch_hunger > 0.4 else None,
            ))

            # ── BEZIEHUNGS-HUNGER ─────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as interakt, MAX(letzte_interaktion) as letzte
                FROM entity_relationships
                WHERE entity_id = %s
            """, (entity_id,))
            bez_row = cur.fetchone()
            bez_interakt = bez_row["interakt"] or 0
            bez_letzte = bez_row["letzte"]

            cur.execute("""
                SELECT COUNT(*) as lese_cnt
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND entscheidung IN ('menschenprofil_lesen', 'profil_lesen')
                  AND tick_at > NOW() - INTERVAL '48h'
            """, (entity_id,))
            lese_cnt = cur.fetchone()["lese_cnt"] or 0

            bez_hunger = 0.0
            if lese_cnt > 0 and bez_interakt == 0:
                bez_hunger = min(1.0, lese_cnt * 0.15)

            hungers.append(OrganHunger(
                organ_id="beziehung",
                entity_id=entity_id,
                hunger_level=bez_hunger,
                hunger_reason=f"{lese_cnt} Profil-Reads ohne Beziehungsdrift (48h)",
                has_trigger=bez_hunger > 0.3,
                trigger_sources=["entity_relationships", "entity_thinking_log"],
                last_activity=bez_letzte,
                recommended_action="beziehung_pruefen" if bez_hunger > 0.5 else None,
            ))

            # ── KOMPOASE-HUNGER ───────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as spl_cnt
                FROM splitter
                WHERE entity_id = %s AND status = 'aktiv'
            """, (entity_id,))
            spl_aktiv = cur.fetchone()["spl_cnt"] or 0

            cur.execute("""
                SELECT COUNT(*) as park_cnt
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND entscheidung LIKE 'kompoase%%'
                  AND tick_at > NOW() - INTERVAL '48h'
            """, (entity_id,))
            park_cnt = cur.fetchone()["park_cnt"] or 0

            komp_hunger = 0.0
            if spl_aktiv > 2 and park_cnt == 0:
                komp_hunger = min(1.0, (spl_aktiv - 2) * 0.15)

            hungers.append(OrganHunger(
                organ_id="kompoase",
                entity_id=entity_id,
                hunger_level=komp_hunger,
                hunger_reason=f"{spl_aktiv} aktive Splitter, {park_cnt} KompOase-Besuche (48h)",
                has_trigger=komp_hunger > 0.3 and spl_aktiv > 0,
                trigger_sources=["splitter", "entity_thinking_log"],
                recommended_action="kompoase_betreten" if komp_hunger > 0.5 else None,
            ))

            # ── AMPEL-HUNGER ──────────────────────────────────
            cur.execute("""
                SELECT COUNT(*) as state_changes
                FROM events
                WHERE (actor_id = %s OR payload->>'entity_id' = %s)
                  AND event_type LIKE 'cyberling%%'
                  AND created_at > NOW() - INTERVAL '24h'
            """, (entity_id, entity_id))
            state_changes = cur.fetchone()["state_changes"] or 0

            cur.execute("""
                SELECT COUNT(*) as ampel_events
                FROM events
                WHERE (actor_id = %s OR payload->>'entity_id' = %s)
                  AND event_type LIKE '%%ampel%%'
                  AND created_at > NOW() - INTERVAL '24h'
            """, (entity_id, entity_id))
            ampel_events = cur.fetchone()["ampel_events"] or 0

            ampel_hunger = 0.0
            if state_changes > 5 and ampel_events == 0:
                ampel_hunger = min(1.0, (state_changes - 5) * 0.1)

            hungers.append(OrganHunger(
                organ_id="ampel",
                entity_id=entity_id,
                hunger_level=ampel_hunger,
                hunger_reason=f"{state_changes} Zustandsänderungen ohne Ampel-Event (24h)",
                has_trigger=ampel_hunger > 0.2,
                trigger_sources=["events"],
                recommended_action=None,
            ))

    finally:
        conn.close()

    return EntityHungerReport(
        entity_id=entity_id,
        calculated_at=_now(),
        organ_hungers=hungers,
    )


def alle_wesen_hunger(entity_ids: list[str]) -> list[dict]:
    """Berechnet Organhunger für mehrere Wesen. Gibt kompakte Übersicht zurück."""
    result = []
    for eid in entity_ids:
        try:
            report = berechne_organ_hunger(eid)
            hungry = [h for h in report.organ_hungers if h.has_trigger]
            result.append({
                "entity_id": eid,
                "hungry_count": len(hungry),
                "top_hunger": sorted(hungry, key=lambda h: h.hunger_level, reverse=True)[:3],
                "calculated_at": report.calculated_at.isoformat(),
            })
        except Exception as e:
            result.append({"entity_id": eid, "error": str(e)})
    return result
