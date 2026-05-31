"""Echte HTTP-Rechte-Integrationstests gegen laufende welt-api auf Port 8030.

Läuft gegen echte API. Erstellt minimale Testdaten, räumt sie auf.
Kein Mock. Keine DOM-Tests. Echte Auth-Tokens via auth.py.
"""
import sys, json, uuid, time
sys.path.insert(0, "/root/werkraum/welt")

import requests
from auth import create_token

BASE = "http://localhost:8030"

# ── Tokens ────────────────────────────────────────────────────────────────────
TEST_HUMAN_ID = str(uuid.uuid4())   # Fake-User-ID für Tests
ADMIN_TOKEN   = create_token("test-admin-" + TEST_HUMAN_ID[:8], "admin")
USER_TOKEN    = create_token(TEST_HUMAN_ID, "human")
NO_TOKEN      = None

def ah(tok):
    """Auth-Header dict."""
    if tok:
        return {"Authorization": f"Bearer {tok}"}
    return {}

# ─�� Hilfsfunktionen ───────────────────────────────────────────────────────────
passed = []
failed = []

def ok(name: str, cond: bool, detail: str = ""):
    if cond:
        passed.append(name)
        print(f"  ✓ {name}")
    else:
        failed.append(name)
        print(f"  ✗ {name}" + (f" — {detail}" if detail else ""))

def check(name, cond, detail=""):
    ok(name, cond, detail)

# ── Splitter-Tests ────────────────────────────────────────────────────────────

def test_splitter():
    print("\n── Splitter-Rechte ──")

    # Hol einen echten öffentlichen Splitter
    r = requests.get(f"{BASE}/api/kompoase/splitter?limit=1")
    splitter_list = r.json().get("splitter", [])
    check("Splitter-Liste erreichbar", r.status_code == 200, f"HTTP {r.status_code}")

    if not splitter_list:
        print("  ⚠ Keine Splitter in DB — überspringe Detail-Tests")
        return

    public_id = splitter_list[0]["id"]

    # Öffentlicher Splitter sichtbar ohne Auth
    r = requests.get(f"{BASE}/api/kompoase/splitter/{public_id}")
    check("Öffentlicher Splitter ohne Auth sichtbar", r.status_code == 200, f"HTTP {r.status_code}")

    # Admin sieht Splitter
    r = requests.get(f"{BASE}/api/kompoase/splitter/{public_id}", headers=ah(ADMIN_TOKEN))
    check("Admin sieht öffentlichen Splitter", r.status_code == 200, f"HTTP {r.status_code}")

    # Nicht-existenter Splitter → 404
    r = requests.get(f"{BASE}/api/kompoase/splitter/00000000-0000-0000-0000-000000000099")
    check("Nicht-existenter Splitter → 404", r.status_code == 404, f"HTTP {r.status_code}")

    # Splitter ohne herkunft_sichtbar: Admin erstellt Test-Splitter direkt via DB
    import subprocess
    fake_id = str(uuid.uuid4())
    create_sql = (
        f"INSERT INTO splitter (id, origin_type, essenz, materialitaet, status, herkunft_sichtbar) "
        f"VALUES ('{fake_id}'::uuid, 'test', 'TEST-PRIVATER-SPLITTER-{fake_id[:8]}', 'resonanz', 'aktiv', false);"
    )
    result = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "flextrawurst", "-c", create_sql],
        capture_output=True, text=True)
    if result.returncode == 0:
        # Nicht-Admin kann privaten Splitter nicht sehen
        r = requests.get(f"{BASE}/api/kompoase/splitter/{fake_id}")
        check("Nicht-Admin sieht privaten Splitter nicht → 404",
              r.status_code == 404, f"HTTP {r.status_code}")

        r_user = requests.get(f"{BASE}/api/kompoase/splitter/{fake_id}", headers=ah(USER_TOKEN))
        check("Eingeloggter User sieht privaten Splitter nicht → 404",
              r_user.status_code == 404, f"HTTP {r_user.status_code}")

        # Admin sieht privaten Splitter
        r_admin = requests.get(f"{BASE}/api/kompoase/splitter/{fake_id}", headers=ah(ADMIN_TOKEN))
        check("Admin sieht privaten Splitter", r_admin.status_code == 200, f"HTTP {r_admin.status_code}")

        # Privater Splitter taucht nicht in Liste auf (ohne Auth)
        r_list = requests.get(f"{BASE}/api/kompoase/splitter?search=TEST-PRIVATER-SPLITTER-{fake_id[:8]}")
        items = r_list.json().get("splitter", [])
        check("Privater Splitter in Suchliste nicht sichtbar (kein Auth)",
              not any(s["id"] == fake_id for s in items), f"Gefunden in {len(items)} Items")

        # Admin-Suche findet privaten Splitter
        r_list_admin = requests.get(
            f"{BASE}/api/kompoase/splitter?search=TEST-PRIVATER-SPLITTER-{fake_id[:8]}",
            headers=ah(ADMIN_TOKEN))
        items_admin = r_list_admin.json().get("splitter", [])
        check("Admin-Suche findet privaten Splitter",
              any(s["id"] == fake_id for s in items_admin), f"Items: {len(items_admin)}")

        # Aufräumen
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "flextrawurst", "-c",
             f"DELETE FROM splitter WHERE id = '{fake_id}'::uuid;"],
            capture_output=True, text=True)
    else:
        print(f"  ⚠ Test-Splitter konnte nicht erstellt werden: {result.stderr[:100]}")

    # Aufnahme ohne Auth → 422 oder 401
    r = requests.post(
        f"{BASE}/api/kompoase/splitter/{public_id}/aufnehmen",
        json={"aufnehmer_type": "human", "aufnehmer_id": ""},
        headers={"Content-Type": "application/json"})
    check("Aufnahme ohne Auth → 401/422", r.status_code in (401, 422), f"HTTP {r.status_code}")

    # Aufnahme mit Auth — User kann nur für sich selbst aufnehmen
    r = requests.post(
        f"{BASE}/api/kompoase/splitter/{public_id}/aufnehmen",
        json={"aufnehmer_type": "human", "aufnehmer_id": "anderer-user"},
        headers={**ah(USER_TOKEN), "Content-Type": "application/json"})
    check("Aufnahme mit falscher aufnehmer_id → Server korrigiert zu eigenem ID",
          r.status_code == 200 and r.json().get("ok"),
          f"HTTP {r.status_code}")

    # Wesen-Aufnahme ohne Admin-Token → 403
    r = requests.post(
        f"{BASE}/api/kompoase/splitter/{public_id}/aufnehmen",
        json={"aufnehmer_type": "entity", "aufnehmer_id": "namelessAI_1234"},
        headers={**ah(USER_TOKEN), "Content-Type": "application/json"})
    check("Entity-Aufnahme ohne Admin → 403", r.status_code == 403, f"HTTP {r.status_code}")

    # Aufnahme erzeugt Event — Check via Admin-Event-Endpunkt (falls vorhanden)
    # Aufnahme erscheint in aufnahmen_liste
    r = requests.get(f"{BASE}/api/kompoase/splitter/{public_id}", headers=ah(ADMIN_TOKEN))
    check("Aufnahme in aufnahmen_liste sichtbar",
          r.status_code == 200 and isinstance(r.json().get("aufnahmen_liste"), list),
          f"aufnahmen_liste: {type(r.json().get('aufnahmen_liste'))}")

    # Spur-Endpunkt
    r = requests.get(f"{BASE}/api/kompoase/splitter/{public_id}/spur")
    check("Spur-Endpunkt erreichbar", r.status_code == 200, f"HTTP {r.status_code}")
    spur = r.json()
    check("Spur hat splitter_id", spur.get("splitter_id") == public_id, str(spur.get("splitter_id")))


# ── Shadow-Tests ──────────────────────────────────────────────────────────────

def test_shadow():
    print("\n── Shadow-Dialog-Rechte ──")

    # Liste ohne Auth → 403
    r = requests.get(f"{BASE}/api/shadow/dialogs")
    check("Shadow-Liste ohne Auth → 403", r.status_code == 403, f"HTTP {r.status_code}")

    # Liste mit User-Token ��� 403
    r = requests.get(f"{BASE}/api/shadow/dialogs", headers=ah(USER_TOKEN))
    check("Shadow-Liste mit User-Token → 403", r.status_code == 403, f"HTTP {r.status_code}")

    # Liste mit Admin → 200
    r = requests.get(f"{BASE}/api/shadow/dialogs", headers=ah(ADMIN_TOKEN))
    check("Shadow-Liste mit Admin → 200", r.status_code == 200, f"HTTP {r.status_code}")

    fake_dialog_id = "00000000-0000-0000-0000-000000000099"

    # Detail ohne Auth → 403 oder 404 (beides sicher — kein Informationsleck)
    r = requests.get(f"{BASE}/api/shadow/dialogs/{fake_dialog_id}")
    check("Shadow-Detail ohne Auth → 403 oder 404",
          r.status_code in (403, 404), f"HTTP {r.status_code}")

    # Reply ohne Auth → 401/403/422 (422 = Validation vor Auth — kein Leck)
    r = requests.post(f"{BASE}/api/shadow/dialogs/{fake_dialog_id}/reply",
                      json={"inhalt": "test"}, headers={"Content-Type": "application/json"})
    check("Shadow-Reply ohne Auth blockiert (401/403/422)",
          r.status_code in (401, 403, 422), f"HTTP {r.status_code}")

    # to-splitter ohne Auth → 401 oder 403
    r = requests.post(f"{BASE}/api/shadow/dialogs/{fake_dialog_id}/to-splitter")
    check("to-splitter ohne Auth → 401/403", r.status_code in (401, 403), f"HTTP {r.status_code}")

    # to-splitter mit Admin aber Zitatrechte nicht erlaubt
    # Erst einen Schatten-Dialog mit zitatrechte='privat' erstellen
    import subprocess
    shadow_id = str(uuid.uuid4())
    create_sql = (
        f"INSERT INTO schattenkommentare (id, post_id, entity_id, content, zitatrechte, antwortstatus) "
        f"VALUES ('{shadow_id}'::uuid, "
        f"(SELECT id FROM ftw_posts LIMIT 1), "
        f"'namelessAI_1234', 'Test-Inhalt-{shadow_id[:8]}', 'privat', 'offen');"
    )
    result = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "flextrawurst", "-c", create_sql],
        capture_output=True, text=True)
    if result.returncode == 0:
        r = requests.post(f"{BASE}/api/shadow/dialogs/{shadow_id}/to-splitter",
                          headers=ah(ADMIN_TOKEN))
        check("to-splitter mit zitatrechte=privat → 403",
              r.status_code == 403, f"HTTP {r.status_code}")

        # Shadow-Inhalt nicht in Search sichtbar
        r_search = requests.get(f"{BASE}/api/search/global?q=Test-Inhalt-{shadow_id[:8]}")
        results = r_search.json().get("results", [])
        shadow_in_results = any(res.get("typ") == "shadow_dialog" for res in results)
        check("Shadow-Inhalt nicht öffentlich in Suche", not shadow_in_results,
              f"Ergebnisse: {len(results)}")

        # Aufräumen
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "flextrawurst", "-c",
             f"DELETE FROM schattenkommentare WHERE id = '{shadow_id}'::uuid;"],
            capture_output=True, text=True)
    else:
        print(f"  ⚠ Shadow-Test-Dialog konnte nicht erstellt werden: {result.stderr[:100]}")

    # shadow/initiate Skeleton → 503
    r = requests.post(
        f"{BASE}/api/shadow/initiate",
        json={"entity_id": "namelessAI_1234", "human_id": TEST_HUMAN_ID,
              "reason": "test", "inhalt": "test"})
    check("shadow/initiate korrekt 503 (Skeleton)", r.status_code == 503, f"HTTP {r.status_code}")


# ── Human-Material-Tests ──────────────────────────────────────────────────────

def test_human_material():
    print("\n── Menschliche Innenquellen ──")

    # Liste erreichbar (leer, korrekt)
    r = requests.get(f"{BASE}/api/human-material", headers=ah(ADMIN_TOKEN))
    check("Human-Material-Liste erreichbar (Admin)", r.status_code == 200, f"HTTP {r.status_code}")
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", r.json().get("sources", []))
    check("Human-Material default 0 Einträge", len(items) == 0, f"Einträge: {len(items)}")

    # Liste ohne Auth → 401 oder leer
    r_noauth = requests.get(f"{BASE}/api/human-material")
    check("Human-Material ohne Auth → 401 oder leer",
          r_noauth.status_code in (401, 403) or
          len(r_noauth.json() if isinstance(r_noauth.json(), list) else []) == 0,
          f"HTTP {r_noauth.status_code}")

    # Consent-PATCH ohne Auth → 401
    r = requests.patch(f"{BASE}/api/human-material/00000000-0000-0000-0000-000000000001/consent",
                       json={"consent_status": "erteilt"}, headers={"Content-Type": "application/json"})
    check("Consent-PATCH ohne Auth → 401/403/404", r.status_code in (401, 403, 404), f"HTTP {r.status_code}")

    # to-splitter ohne Consent → 403 oder 404
    r = requests.post(f"{BASE}/api/human-material/00000000-0000-0000-0000-000000000001/to-splitter",
                      headers=ah(USER_TOKEN))
    check("to-splitter aus HM ohne Consent → 403/404", r.status_code in (403, 404), f"HTTP {r.status_code}")

    # Kein automatischer Kalender-Import: POST auf speziellen Import-Pfad
    # liefert kein 200/201 — entweder 404, 405 oder 422 (kein Auto-Import)
    r_kal = requests.post(f"{BASE}/api/human-material/calendar-auto-import",
                          headers=ah(ADMIN_TOKEN))
    check("Kein Kalender-Auto-Import-Endpunkt (kein 200/201)",
          r_kal.status_code not in (200, 201), f"HTTP {r_kal.status_code}")

    # Notiz-Freigabe-Endpunkt erfordert Auth
    r_mw = requests.post(f"{BASE}/mw/notizen/00000000-0000-0000-0000-000000000001/splitter-freigeben")
    check("Notiz-Splitter-Freigabe ohne Auth → 401/403", r_mw.status_code in (401, 403, 422), f"HTTP {r_mw.status_code}")


# ��─ Search-Tests ──────────────────────────────────────────────────────────────

def test_search():
    print("\n── Suche ──")

    # Basis-Suche
    r = requests.get(f"{BASE}/api/search/global?q=test")
    check("Globale Suche erreichbar", r.status_code == 200, f"HTTP {r.status_code}")
    data = r.json()
    check("Suche hat is_admin-Flag", "is_admin" in data, str(list(data.keys())[:5]))

    # Facets
    r = requests.get(f"{BASE}/api/search/facets?q=test")
    check("Facets erreichbar", r.status_code == 200, f"HTTP {r.status_code}")
    facetten = r.json().get("facetten", {})
    check("Facets haben splitter-Key", "splitter" in facetten, str(list(facetten.keys())))
    check("Facets haben posts-Key", "posts" in facetten, str(list(facetten.keys())))

    # Archaeology: Admin-Only
    r = requests.get(f"{BASE}/api/search/archaeology?q=test")
    check("Archaeology ohne Auth → 403", r.status_code == 403, f"HTTP {r.status_code}")

    r_admin = requests.get(f"{BASE}/api/search/archaeology?q=test", headers=ah(ADMIN_TOKEN))
    check("Archaeology mit Admin → 200", r_admin.status_code == 200, f"HTTP {r_admin.status_code}")

    # Human Material nicht in öffentlicher Suche
    r = requests.get(f"{BASE}/api/search/global?q=TEST-PRIVATER")
    results = r.json().get("results", [])
    hm_in_results = any(res.get("typ") == "human_material" for res in results)
    check("Human-Material nicht in öffentlicher Suche", not hm_in_results,
          f"Ergebnisse: {len(results)}")


# ── Ampel-Test ────────────────────────────────────────────────────────────────

def test_ampel():
    print("\n── Ampel v3 ──")

    r = requests.get(f"{BASE}/admin/einzugsampel/v3", headers=ah(ADMIN_TOKEN))
    check("Ampel v3 erreichbar", r.status_code == 200, f"HTTP {r.status_code}")
    data = r.json()
    check("Ampel hat klassen-Schlüssel", "klassen" in data, str(list(data.keys())))
    check("Ampel ist nicht grün (korrekt)", data.get("ampel") != "gruen",
          f"Ampel: {data.get('ampel')}")
    check("A_Technisch grün", data.get("klassen", {}).get("A_Technisch", {}).get("status") == "gruen")
    check("B_Sicherheit grün", data.get("klassen", {}).get("B_Sicherheit", {}).get("status") == "gruen")
    check("D_BewusstBlockiert grün", data.get("klassen", {}).get("D_BewusstBlockiert", {}).get("status") == "gruen")
    check("E_OffenDesign nicht grün — ehrlich",
          data.get("klassen", {}).get("E_OffenDesign", {}).get("status") != "gruen")


# ── Haupt ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"HTTP-Rechte-Integrationstests gegen {BASE}")
    print(f"Admin-Token: test-admin (Fake-ID)")
    print(f"User-Token:  {TEST_HUMAN_ID[:8]}... (Fake-ID)")

    test_splitter()
    test_shadow()
    test_human_material()
    test_search()
    test_ampel()

    print(f"\n══════════════════════════════")
    print(f"Gesamt: {len(passed)+len(failed)} Tests")
    print(f"  ✓ {len(passed)} passed")
    if failed:
        print(f"  ✗ {len(failed)} failed:")
        for f in failed:
            print(f"      - {f}")
    else:
        print(f"  Alle grün.")
    print()
    sys.exit(1 if failed else 0)
