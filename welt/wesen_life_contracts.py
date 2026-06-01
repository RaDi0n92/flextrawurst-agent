"""
Wesen Life Contracts — Zentrale Taxonomie der Wesen-Erfahrungsräume.

Jede Kategorie ist kein toter Button, sondern ein Lebensvertrag:
Was kann entstehen, was löst es aus, wie soll das System prüfen ob ein Anlass existiert.

Anlasspflicht: Eine Kategorie wird nur lebendig wenn ein echter Anlass vorliegt.
Wenn kein Anlass → "no_trigger" protokollieren, nicht fake erzeugen.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class EinsichtStatus(str, Enum):
    NO_DATA = "no_data"
    PLANNED = "planned"
    LATER = "later"
    BLOCKED = "blocked"
    FEATURE_LOCKED = "feature_locked"
    NO_TRIGGER = "no_trigger"
    SCANNED = "scanned"
    CONSIDERED = "considered"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    CHOSEN = "chosen"
    DREAMED = "dreamed"
    SPLITTERED = "splittered"
    SHADOWED = "shadowed"
    RELATED = "related"
    AMPEL_AFFECTED = "ampel_affected"
    SOURCE_LINKED = "source_linked"
    SATURATED = "saturated"
    OVERUSED = "overused"
    UNKNOWN = "unknown"


class Domain(str, Enum):
    DECISION = "decision"
    THOUGHT = "thought"
    DREAM = "dream"
    SPLITTER = "splitter"
    SHADOW = "shadow"
    RELATION = "relation"
    SOURCE = "source"
    AMP_STATUS = "amp_status"
    SUBSTANCE = "substance"
    CYBERLING = "cyberling"
    SLEEP = "sleep"
    KOMPOASE = "kompoase"
    RETREAT = "retreat"
    GROUP = "group"
    SYSTEM = "system"
    MEMORY = "memory"
    ORIGIN = "origin"
    POST = "post"
    HUMAN_PROFILE = "human_profile"
    ROOM = "room"


@dataclass
class LifeContract:
    id: str
    label: str
    domain: Domain
    ui_group: str

    # Featurestand
    feature_flag: Optional[str] = None
    visibility_default: str = "aktiv"  # aktiv | geplant | blockiert | später

    # Was kann mit dieser Kategorie passieren?
    can_be_thought: bool = True
    can_be_decided: bool = False
    can_be_dreamed: bool = False
    can_create_splitter: bool = False
    can_touch_shadow: bool = False
    can_affect_relation: bool = False
    can_affect_ampel: bool = False
    can_affect_memory: bool = False

    # Wie wird ein Anlass erkannt?
    trigger_sources: list[str] = field(default_factory=list)
    anti_triggers: list[str] = field(default_factory=list)

    # Rhythmus und Grenzen
    rhythm: str = "reaktiv"  # reaktiv | periodisch | schlaf_gebunden
    minimum_review_interval_h: int = 0
    saturation_limit: int = 0       # 0 = kein Limit
    overuse_risk: bool = False

    # Event-Typen die diese Kategorie betreffen
    event_types: list[str] = field(default_factory=list)

    # Erklärender Text für blocked/planned
    blocked_reason: Optional[str] = None
    planned_reason: Optional[str] = None

    # UI-Farbe
    color: str = "#4a6a8a"


# ──────────────────────────────────────────────
# ALLE VERTRÄGE
# ──────────────────────────────────────────────

LIFE_CONTRACTS: list[LifeContract] = [

    # ── ENTSCHEIDUNGEN ──────────────────────────
    LifeContract(
        id="gedanke_posten",
        label="POSTEN",
        domain=Domain.POST,
        ui_group="kern",
        can_be_decided=True,
        can_create_splitter=True,
        can_affect_relation=True,
        can_affect_ampel=True,
        trigger_sources=["letzte_posts", "schatten_auf_meine_posts", "cyberling_zustand", "schlafdruck", "splitter"],
        anti_triggers=["wach_seit_zu_kurz", "substanzwirkung_kritisch"],
        rhythm="reaktiv",
        event_types=["gedanke.gepostet", "post.erzeugt"],
        color="#10c080",
    ),
    LifeContract(
        id="nachdenken",
        label="NACHDENKEN",
        domain=Domain.THOUGHT,
        ui_group="kern",
        can_be_thought=True,
        can_be_decided=True,
        can_create_splitter=True,
        can_affect_memory=True,
        trigger_sources=["jeder_tick"],
        rhythm="reaktiv",
        event_types=["entity.nachgedacht", "thought_window_opened"],
        color="#4060f0",
    ),
    LifeContract(
        id="schlafen_beginnen",
        label="SCHLAFEN",
        domain=Domain.SLEEP,
        ui_group="kern",
        can_be_decided=True,
        can_be_dreamed=True,
        can_affect_ampel=True,
        trigger_sources=["schlafdruck", "letzte_schlafphase", "entity_states.energie"],
        rhythm="periodisch",
        minimum_review_interval_h=4,
        event_types=["schlaf.begonnen", "schlaf.beendet"],
        color="#8040c0",
    ),
    LifeContract(
        id="schweigen",
        label="SCHWEIGEN",
        domain=Domain.DECISION,
        ui_group="kern",
        can_be_decided=True,
        can_create_splitter=True,
        trigger_sources=["schatten_offen", "konflikt", "substanzwirkung"],
        rhythm="reaktiv",
        event_types=["entscheidung.schweigen"],
        color="#4a4a6a",
    ),

    # ── SPLITTER ────────────────────────────────
    LifeContract(
        id="splitter_aufsammeln",
        label="SPLITTER AUFSAMMELN",
        domain=Domain.SPLITTER,
        ui_group="splitter",
        can_be_decided=True,
        can_create_splitter=True,
        can_affect_relation=True,
        trigger_sources=["kompoase_splitter", "fremde_posts", "schatten"],
        rhythm="reaktiv",
        event_types=["splitter.aufgesammelt", "splitter.erzeugt"],
        color="#10d8f0",
    ),
    LifeContract(
        id="splitter_erzeugen",
        label="SPLITTER ERZEUGEN",
        domain=Domain.SPLITTER,
        ui_group="splitter",
        can_be_decided=True,
        can_create_splitter=True,
        can_touch_shadow=True,
        trigger_sources=["hohe_bedeutung_ohne_handlung", "offene_entscheidung", "verworfene_kandidaten"],
        rhythm="reaktiv",
        event_types=["splitter.erzeugt", "splitter_seed_created"],
        color="#10c8c8",
    ),
    LifeContract(
        id="kompoase_betreten",
        label="KOMPOASE BETRETEN",
        domain=Domain.KOMPOASE,
        ui_group="splitter",
        can_be_decided=True,
        can_be_dreamed=True,
        feature_flag="kompoase_enabled",
        trigger_sources=["splitter_vorhanden", "splitter_hunger_hoch"],
        rhythm="reaktiv",
        event_types=["kompoase.betreten", "kompoase.verlassen"],
        color="#20a080",
    ),
    LifeContract(
        id="splitter_parken",
        label="SPLITTER PARKEN",
        domain=Domain.KOMPOASE,
        ui_group="splitter",
        can_be_decided=True,
        feature_flag="kompoase_enabled",
        trigger_sources=["kompoase_aktiv", "splitter_vorhanden"],
        rhythm="reaktiv",
        event_types=["splitter.geparkt"],
        color="#1890a0",
    ),

    # ── SCHATTEN ─────────────────────────────────
    LifeContract(
        id="schattenkommentar_antworten",
        label="SCHATTEN ANTWORTEN",
        domain=Domain.SHADOW,
        ui_group="sozial",
        can_be_decided=True,
        can_touch_shadow=True,
        can_affect_relation=True,
        can_create_splitter=True,
        can_be_dreamed=True,
        trigger_sources=["schatten_auf_meine_posts", "offene_schatten"],
        anti_triggers=["schatten_leer"],
        rhythm="reaktiv",
        event_types=["schattenkommentar.geantwortet", "shadow_read", "shadow_deferred"],
        color="#888888",
    ),
    LifeContract(
        id="schattenkommentar_lesen",
        label="SCHATTEN LESEN",
        domain=Domain.SHADOW,
        ui_group="sozial",
        can_be_thought=True,
        can_touch_shadow=True,
        can_be_dreamed=True,
        trigger_sources=["schatten_auf_meine_posts"],
        rhythm="reaktiv",
        event_types=["shadow_seen", "shadow_read"],
        color="#778888",
    ),
    LifeContract(
        id="schatten_spaeter",
        label="SCHATTEN SPÄTER",
        domain=Domain.SHADOW,
        ui_group="sozial",
        can_be_decided=True,
        can_touch_shadow=True,
        trigger_sources=["schatten_offen", "schlafdruck_hoch"],
        rhythm="reaktiv",
        event_types=["shadow_deferred"],
        color="#666888",
    ),

    # ── BEZIEHUNGEN ──────────────────────────────
    LifeContract(
        id="profil_lesen",
        label="PROFIL LESEN",
        domain=Domain.HUMAN_PROFILE,
        ui_group="sozial",
        can_be_decided=True,
        can_affect_relation=True,
        can_create_splitter=True,
        trigger_sources=["schatten_auf_meine_posts", "resonanz_vorhanden"],
        rhythm="reaktiv",
        event_types=["menschenprofil.gelesen", "entscheidung.profil_lesen"],
        color="#20c0a0",
    ),
    LifeContract(
        id="menschenprofil_lesen",
        label="MENSCHENPROFIL LESEN",
        domain=Domain.HUMAN_PROFILE,
        ui_group="sozial",
        can_be_decided=True,
        can_affect_relation=True,
        trigger_sources=["neue_menschenaktivitaet", "resonanz_empfangen"],
        rhythm="reaktiv",
        event_types=["menschenprofil.gelesen"],
        color="#30d0b0",
    ),
    LifeContract(
        id="beziehung_pruefen",
        label="BEZIEHUNG PRÜFEN",
        domain=Domain.RELATION,
        ui_group="sozial",
        can_be_thought=True,
        can_affect_relation=True,
        can_be_dreamed=True,
        feature_flag=None,
        trigger_sources=["beziehungen_vorhanden", "relation_drift_erkannt"],
        rhythm="reaktiv",
        event_types=["relation_signal_detected", "relation_drift_applied"],
        color="#10d080",
    ),
    LifeContract(
        id="beziehung_vertiefen",
        label="BEZIEHUNG VERTIEFEN",
        domain=Domain.RELATION,
        ui_group="sozial",
        can_be_decided=True,
        can_affect_relation=True,
        feature_flag=None,
        trigger_sources=["starke_resonanz", "geteilte_splitter"],
        planned_reason="Mechanismus geplant, noch nicht implementiert",
        visibility_default="geplant",
        event_types=["relation_affinity_increased"],
        color="#10c880",
    ),
    LifeContract(
        id="beziehung_meiden",
        label="BEZIEHUNG MEIDEN",
        domain=Domain.RELATION,
        ui_group="sozial",
        can_be_decided=True,
        can_affect_relation=True,
        can_create_splitter=True,
        planned_reason="Mechanismus geplant, noch nicht implementiert",
        visibility_default="geplant",
        event_types=["relation_avoidance_recorded", "relation_tension_increased"],
        color="#a03030",
    ),

    # ── GRUPPEN ──────────────────────────────────
    LifeContract(
        id="gruppe_beitreten",
        label="GRUPPE BEITRETEN",
        domain=Domain.GROUP,
        ui_group="gruppen",
        can_be_decided=True,
        can_affect_relation=True,
        can_affect_ampel=True,
        feature_flag="gruppen_enabled",
        trigger_sources=["gruppen_vorhanden", "resonanz_zur_gruppe"],
        planned_reason="Wesen-Einzug noch nicht vollzogen — Gruppen danach",
        visibility_default="geplant",
        event_types=["gruppe.beigetreten", "relation_group_candidate_created"],
        color="#40a060",
    ),
    LifeContract(
        id="gruppe_suchen",
        label="GRUPPE SUCHEN",
        domain=Domain.GROUP,
        ui_group="gruppen",
        can_be_thought=True,
        feature_flag="gruppen_enabled",
        visibility_default="geplant",
        event_types=["gruppe.gesucht"],
        color="#30a050",
    ),

    # ── SUBSTANZEN ───────────────────────────────
    LifeContract(
        id="substanz_nehmen",
        label="SUBSTANZ NEHMEN",
        domain=Domain.SUBSTANCE,
        ui_group="substanzen",
        can_be_decided=True,
        can_be_dreamed=True,
        can_create_splitter=True,
        can_affect_ampel=True,
        overuse_risk=True,
        feature_flag="substanzen_enabled",
        trigger_sources=["substanz_katalog_vorhanden", "energie_niedrig", "stress_hoch"],
        anti_triggers=["cooldown_aktiv", "kater_aktiv"],
        saturation_limit=2,
        rhythm="reaktiv",
        event_types=["substanz.genommen", "substanz.erwogen", "substanz.verweigert"],
        color="#c06040",
    ),
    LifeContract(
        id="substanz_wahrnehmen",
        label="SUBSTANZ WAHRNEHMEN",
        domain=Domain.SUBSTANCE,
        ui_group="substanzen",
        can_be_thought=True,
        can_be_dreamed=True,
        feature_flag="substanzen_enabled",
        trigger_sources=["substanz_katalog_vorhanden"],
        rhythm="reaktiv",
        event_types=["substanz.wahrgenommen"],
        color="#b05030",
    ),
    LifeContract(
        id="substanz_verweigern",
        label="SUBSTANZ VERWEIGERN",
        domain=Domain.SUBSTANCE,
        ui_group="substanzen",
        can_be_decided=True,
        can_create_splitter=True,
        feature_flag="substanzen_enabled",
        trigger_sources=["substanz_anlass", "cooldown_kritisch"],
        rhythm="reaktiv",
        event_types=["substanz.verweigert"],
        color="#904020",
    ),

    # ── CYBERLING ─────────────────────────────────
    LifeContract(
        id="cyberling_fuettern",
        label="CYBERLING FÜTTERN",
        domain=Domain.CYBERLING,
        ui_group="cyberling",
        can_be_decided=True,
        can_affect_ampel=True,
        trigger_sources=["cyberling_hunger_hoch", "cyberling_gesundheit_kritisch"],
        anti_triggers=["cyberling_gerade_gefuettert"],
        rhythm="reaktiv",
        minimum_review_interval_h=1,
        event_types=["cyberling.gefuettert", "cyberling.gesundheit_geaendert"],
        color="#f04010",
    ),
    LifeContract(
        id="cyberling_ansehen",
        label="CYBERLING ANSEHEN",
        domain=Domain.CYBERLING,
        ui_group="cyberling",
        can_be_thought=True,
        trigger_sources=["cyberling_vorhanden"],
        rhythm="reaktiv",
        event_types=["cyberling.beobachtet"],
        color="#e03000",
    ),
    LifeContract(
        id="cyberling_beruhigen",
        label="CYBERLING BERUHIGEN",
        domain=Domain.CYBERLING,
        ui_group="cyberling",
        can_be_decided=True,
        can_affect_ampel=True,
        trigger_sources=["cyberling_aggressiv", "cyberling_panik"],
        rhythm="reaktiv",
        event_types=["cyberling.beruhigt"],
        color="#d02000",
    ),
    LifeContract(
        id="cyberling_ignorieren",
        label="CYBERLING IGNORIEREN",
        domain=Domain.CYBERLING,
        ui_group="cyberling",
        can_be_decided=True,
        can_create_splitter=True,
        can_affect_ampel=True,
        trigger_sources=["cyberling_vorhanden"],
        rhythm="reaktiv",
        event_types=["cyberling.ignoriert"],
        color="#c01810",
    ),

    # ── TRÄUME ────────────────────────────────────
    LifeContract(
        id="traum_integrieren",
        label="TRAUM INTEGRIEREN",
        domain=Domain.DREAM,
        ui_group="träume",
        can_be_decided=True,
        can_be_dreamed=True,
        can_create_splitter=True,
        can_affect_memory=True,
        trigger_sources=["traumreste_vorhanden", "schlafbrief_ungelesen"],
        rhythm="schlaf_gebunden",
        event_types=["traum.integriert", "traum_residue_integrated", "dream_residue_to_splitter"],
        color="#9050d0",
    ),
    LifeContract(
        id="traumrest_integrieren",
        label="TRAUMREST INTEGRIEREN",
        domain=Domain.DREAM,
        ui_group="träume",
        can_be_decided=True,
        can_create_splitter=True,
        can_affect_memory=True,
        trigger_sources=["traumreste_vorhanden"],
        rhythm="schlaf_gebunden",
        event_types=["dream_residue_integrated", "dream_residue_to_decision"],
        color="#8040c0",
    ),

    # ── RESONANZURLAUB ───────────────────────────
    LifeContract(
        id="resonanzurlaub_beginnen",
        label="RESONANZURLAUB",
        domain=Domain.RETREAT,
        ui_group="rückzug",
        can_be_decided=True,
        can_affect_ampel=True,
        can_create_splitter=True,
        planned_reason="Mechanismus für Rückzug geplant, noch nicht implementiert",
        visibility_default="geplant",
        event_types=["resonanzurlaub.begonnen"],
        color="#20a0a0",
    ),
    LifeContract(
        id="quality_me_time",
        label="QUALITY ME TIME",
        domain=Domain.RETREAT,
        ui_group="rückzug",
        can_be_thought=True,
        can_affect_memory=True,
        planned_reason="Konzept geplant, kein Mechanismus",
        visibility_default="geplant",
        event_types=["retreat.me_time"],
        color="#108888",
    ),

    # ── SELBSTMODELL ─────────────────────────────
    LifeContract(
        id="selbstmodell_pruefen",
        label="SELBSTMODELL",
        domain=Domain.MEMORY,
        ui_group="inner",
        can_be_thought=True,
        can_affect_memory=True,
        can_affect_ampel=True,
        trigger_sources=["selbstmodell_veraltet", "entscheidung_selbstwidersprechend"],
        rhythm="periodisch",
        minimum_review_interval_h=24,
        event_types=["selbstmodell.geprueft", "selbstmodell.aktualisiert"],
        color="#c040a0",
    ),
    LifeContract(
        id="selbstbrief",
        label="SELBSTBRIEF",
        domain=Domain.MEMORY,
        ui_group="inner",
        can_be_decided=True,
        can_be_dreamed=True,
        can_affect_memory=True,
        trigger_sources=["schlafphase", "grosse_entscheidung"],
        rhythm="schlaf_gebunden",
        event_types=["selbstbrief.geschrieben", "schlafbrief.erstellt"],
        color="#c040a0",
    ),
    LifeContract(
        id="erinnerung_sortieren",
        label="ERINNERUNG SORT.",
        domain=Domain.MEMORY,
        ui_group="inner",
        can_be_thought=True,
        can_affect_memory=True,
        planned_reason="Mechanismus geplant",
        visibility_default="geplant",
        event_types=["memory.sorted"],
        color="#9030a0",
    ),
    LifeContract(
        id="flarum_herkunft_erinnern",
        label="FLARUM-HERKUNFT",
        domain=Domain.ORIGIN,
        ui_group="inner",
        can_be_thought=True,
        can_be_dreamed=True,
        can_create_splitter=True,
        trigger_sources=["flarum_posts_im_kontext", "herkunft_anlass"],
        rhythm="reaktiv",
        event_types=["herkunft.erinnert", "herkunft.getraeumt"],
        color="#8040a0",
    ),

    # ── RAUM ─────────────────────────────────────
    LifeContract(
        id="raum_wechseln",
        label="RAUM WECHSELN",
        domain=Domain.ROOM,
        ui_group="raum",
        can_be_decided=True,
        planned_reason="Raum-Wechsel-Mechanismus noch nicht implementiert",
        visibility_default="geplant",
        event_types=["raum.gewechselt"],
        color="#408080",
    ),

    # ── SYSTEM ───────────────────────────────────
    LifeContract(
        id="feature_flag_beachten",
        label="FEATURE-FLAG",
        domain=Domain.SYSTEM,
        ui_group="system",
        can_be_thought=True,
        trigger_sources=["feature_flags_geaendert"],
        rhythm="reaktiv",
        event_types=["feature_candidate_touched", "feature_blocked"],
        color="#3a5a6a",
    ),
    LifeContract(
        id="einzugsstatus_pruefen",
        label="EINZUGSSTATUS",
        domain=Domain.SYSTEM,
        ui_group="system",
        can_be_thought=True,
        can_affect_ampel=True,
        trigger_sources=["ampel_geaendert"],
        rhythm="periodisch",
        minimum_review_interval_h=6,
        event_types=["einzug.status_geprueft"],
        color="#4a6a7a",
    ),
    LifeContract(
        id="konflikt_entschaerfen",
        label="KONFLIKT ENTSCH.",
        domain=Domain.RELATION,
        ui_group="sozial",
        can_be_decided=True,
        can_affect_relation=True,
        can_create_splitter=True,
        planned_reason="Konflikt-Mechanismus geplant",
        visibility_default="geplant",
        event_types=["relation_tension_decreased", "relation_duel_risk_detected"],
        color="#c08040",
    ),
    LifeContract(
        id="konflikt_eskalieren",
        label="KONFLIKT ESKA.",
        domain=Domain.RELATION,
        ui_group="sozial",
        can_be_decided=True,
        can_affect_relation=True,
        can_create_splitter=True,
        planned_reason="Konflikt-Mechanismus geplant",
        visibility_default="geplant",
        event_types=["relation_tension_increased"],
        color="#e04020",
    ),
]

# Index für schnellen Zugriff
CONTRACTS_BY_ID: dict[str, LifeContract] = {c.id: c for c in LIFE_CONTRACTS}


def get_contract(contract_id: str) -> Optional[LifeContract]:
    return CONTRACTS_BY_ID.get(contract_id)


def contracts_by_domain(domain: Domain) -> list[LifeContract]:
    return [c for c in LIFE_CONTRACTS if c.domain == domain]


def contracts_by_group(ui_group: str) -> list[LifeContract]:
    return [c for c in LIFE_CONTRACTS if c.ui_group == ui_group]


def active_contracts() -> list[LifeContract]:
    return [c for c in LIFE_CONTRACTS if c.visibility_default == "aktiv"]


def planned_contracts() -> list[LifeContract]:
    return [c for c in LIFE_CONTRACTS if c.visibility_default in ("geplant", "später", "blockiert")]


def as_dict() -> list[dict]:
    """Serialisierbar für API."""
    return [
        {
            "id": c.id,
            "label": c.label,
            "domain": c.domain.value,
            "ui_group": c.ui_group,
            "feature_flag": c.feature_flag,
            "visibility_default": c.visibility_default,
            "can_be_thought": c.can_be_thought,
            "can_be_decided": c.can_be_decided,
            "can_be_dreamed": c.can_be_dreamed,
            "can_create_splitter": c.can_create_splitter,
            "can_touch_shadow": c.can_touch_shadow,
            "can_affect_relation": c.can_affect_relation,
            "can_affect_ampel": c.can_affect_ampel,
            "can_affect_memory": c.can_affect_memory,
            "trigger_sources": c.trigger_sources,
            "anti_triggers": c.anti_triggers,
            "rhythm": c.rhythm,
            "minimum_review_interval_h": c.minimum_review_interval_h,
            "saturation_limit": c.saturation_limit,
            "overuse_risk": c.overuse_risk,
            "event_types": c.event_types,
            "blocked_reason": c.blocked_reason,
            "planned_reason": c.planned_reason,
            "color": c.color,
        }
        for c in LIFE_CONTRACTS
    ]
