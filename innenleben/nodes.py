#!/usr/bin/env python3
"""
LangGraph Nodes: memory_writer, reflection_node, self_model_integrator.
Spec Abschnitte 5.3, 5.4, 5.5.
"""

import hashlib
import json
import logging
import re
from typing import Optional
from datetime import datetime, timezone

import chromadb
import httpx

import emotion_bewerter
import selbstmodell
from config import (
    CHROMA_DIR,
    MODELL,
    OLLAMA_URL,
    LOGS_DIR,
)
from reflection_score import berechne as score_berechne
from state import AgentState

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "innenleben.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("innenleben")

_chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))


def _collection(entity_id: str):
    return _chroma.get_or_create_collection(
        name=f"memories_{entity_id}",
        metadata={"hnsw:space": "cosine"},
    )


def _llm(prompt: str, num_predict: int = 600) -> str:
    try:
        with httpx.Client(timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)) as c:
            r = c.post(
                OLLAMA_URL,
                json={
                    "model": MODELL,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0.7, "num_predict": num_predict},
                },
            )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        log.warning(f"LLM-Fehler: {e}")
        return ""


def _parse_json_response(response: str) -> Optional[dict]:
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# Node 1: Memory Writer
# ---------------------------------------------------------------------------

def memory_writer_node(state: AgentState) -> AgentState:
    entity_id    = state["entity_id"]
    event_text   = state["current_event"]
    event_source = state.get("event_source", "observation")

    emotions = emotion_bewerter.bewerte(event_text)
    hr       = state.get("human_resonance", 0.0)
    pr       = state.get("pattern_repeat", 0)
    score    = score_berechne(emotions, hr, pr)

    ts = datetime.now(timezone.utc).isoformat()

    # Deterministische ID: vom Feeder gesetzt oder Hash aus Inhalt
    raw_event_id = state.get("event_id") or None
    if raw_event_id:
        memory_id = raw_event_id
    else:
        h = hashlib.sha256(f"{entity_id}|{event_source}|{event_text[:500]}".encode()).hexdigest()[:16]
        memory_id = f"auto:{entity_id}:{h}"

    memory_doc = {
        "entity_id":      entity_id,
        "timestamp":      ts,
        "event_text":     event_text,
        "source":         event_source,
        "event_id":       memory_id,
        "memory_type":    "message",
        "valence":        emotions["valence"],
        "arousal":        emotions["arousal"],
        "dominance":      emotions["dominance"],
        "reason":         emotions["reason"],
        "is_reflection":  False,
        "human_resonance": hr,
    }

    col = _collection(entity_id)
    col.upsert(
        documents=[event_text],
        ids=[memory_id],
        metadatas=[{k: v for k, v in memory_doc.items() if k != "event_text"}],
    )

    selbstmodell.emotional_history_speichern(entity_id, {
        "ts": ts, "score": score,
        "valence": emotions["valence"],
        "arousal": emotions["arousal"],
        "dominance": emotions["dominance"],
        "source": event_source,
    })

    memory_count = col.count()

    log.info(
        f"[MEMORY] {entity_id} | {memory_id} | "
        f"V:{emotions['valence']} A:{emotions['arousal']} D:{emotions['dominance']} | "
        f"Score:{score:.1f} | Source:{event_source}"
    )

    return {
        **state,
        "emotions":         emotions,
        "reflection_score": score,
        "memory_count":     memory_count,
        "event_id":         memory_id,
    }


# ---------------------------------------------------------------------------
# Node 2: Reflection Node
# ---------------------------------------------------------------------------

def reflection_node(state: AgentState) -> AgentState:
    entity_id  = state["entity_id"]
    self_model = state.get("self_model") or selbstmodell.laden(entity_id)

    col = _collection(entity_id)
    result = col.query(
        query_texts=[state["current_event"]],
        n_results=min(12, col.count()),
        where={"is_reflection": False},
    )
    erinnerungen = result["documents"][0] if result["documents"] else []

    log.info(f"[REFLECT] {entity_id} | Erinnerungen geladen: {len(erinnerungen)}")

    memories_text = "\n\n".join(
        f"[{i+1}] {m}" for i, m in enumerate(erinnerungen)
    )

    prompt = f"""Du bist {entity_id}.
Aktuelles Selbstbild: {json.dumps(self_model, ensure_ascii=False)[:800]}
Deine letzten relevanten Erinnerungen:
{memories_text[:2000]}

Analysiere:
1. Was wiederholt sich?
2. Was hat mich irritiert?
3. Was hat mich angezogen?
4. Was habe ich vermieden?
5. Welche kleine Veraenderung meines Selbstbildes ist gerechtfertigt?

Antworte NUR mit validem JSON:
{{"reflection": "...", "insight": "max 15 Woerter"}}"""

    raw = _llm(prompt, num_predict=400)
    parsed = _parse_json_response(raw)

    if not parsed:
        log.warning(f"[REFLECT] {entity_id} | JSON-Parse fehlgeschlagen")
        parsed = {"reflection": raw[:200], "insight": "Reflexion unklar"}

    insight = parsed.get("insight", "")
    log.info(f"[INSIGHT] {entity_id} | '{insight}'")

    # Reflexion als eigene Erinnerung speichern — ID an auslösendes Event gebunden
    triggering_event_id = state.get("event_id", "")
    ts = datetime.now(timezone.utc).isoformat()
    reflection_id = f"reflection:{entity_id}:{ts[:19].replace(':', '-')}"
    col.upsert(
        documents=[parsed.get("reflection", "")[:1000]],
        ids=[reflection_id],
        metadatas=[{
            "entity_id":            entity_id,
            "timestamp":            ts,
            "source":               "reflection",
            "event_id":             reflection_id,
            "triggering_event_id":  triggering_event_id,
            "memory_type":          "reflection",
            "is_reflection":        True,
            "valence":              state["emotions"].get("valence", 5.0),
            "arousal":              state["emotions"].get("arousal", 5.0),
            "dominance":            state["emotions"].get("dominance", 5.0),
            "reason":               "auto_reflection",
            "human_resonance":      0.0,
        }],
    )

    return {
        **state,
        "recent_memories":      erinnerungen,
        "new_insight":          insight,
        "last_reflection_time": datetime.now(),
        "self_model":           self_model,
        "event_id":             triggering_event_id,
    }


# ---------------------------------------------------------------------------
# Node 3: Self Model Integrator
# ---------------------------------------------------------------------------

def _diff_keys(old: dict, new: dict) -> list:
    changed = []
    for k in set(list(old.keys()) + list(new.keys())):
        if old.get(k) != new.get(k):
            changed.append(k)
    return sorted(changed)


def self_model_integrator(state: AgentState) -> AgentState:
    entity_id           = state["entity_id"]
    new_insight         = state.get("new_insight", "")
    self_model          = state.get("self_model") or selbstmodell.laden(entity_id)
    triggering_event_id = state.get("event_id", "")

    if not new_insight:
        log.info(f"[INTEGRATOR] {entity_id} | Kein Insight — kein Update")
        return state

    prompt = f"""Du bist ein Selbstbild-Integrator fuer {entity_id}.
Aktuelles Selbstmodell: {json.dumps(self_model, ensure_ascii=False)[:1000]}
Neue Erkenntnis: {new_insight}

Entscheide: Ist diese Erkenntnis stark genug um das Selbstbild zu veraendern?
Wenn ja: Gib das aktualisierte Selbstmodell als JSON.
Wenn nein: Antworte exakt mit NO_CHANGE
Kein anderer Text."""

    raw = _llm(prompt, num_predict=600)

    if "NO_CHANGE" in raw.upper():
        log.info(f"[INTEGRATOR] {entity_id} | NO_CHANGE")
        selbstmodell.integrator_log_schreiben(entity_id, {
            "action":               "NO_CHANGE",
            "raw_insight":          new_insight,
            "triggering_event_id":  triggering_event_id,
            "changed_keys":         [],
            "accepted":             False,
        })
        return state

    updated = _parse_json_response(raw)
    if updated:
        # symbolic_self_image.self_interpretation niemals von außen überschreiben
        if "symbolic_self_image" in updated:
            updated["symbolic_self_image"]["self_interpretation"] = (
                self_model.get("symbolic_self_image", {}).get("self_interpretation", "")
            )
        changed_keys = _diff_keys(self_model, updated)
        provenienz = {
            "action":               "UPDATE",
            "raw_insight":          new_insight,
            "triggering_event_id":  triggering_event_id,
            "changed_keys":         changed_keys,
            "accepted":             True,
        }
        selbstmodell.speichern(entity_id, updated, provenienz=provenienz)
        log.info(f"[INTEGRATOR] {entity_id} | UPDATE | Geändert: {changed_keys}")
        return {**state, "self_model": updated}

    log.warning(f"[INTEGRATOR] {entity_id} | Parse fehlgeschlagen — kein Update")
    return state
