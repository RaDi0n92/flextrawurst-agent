extends SceneTree

const RUNTIME_SEED_PATH := "res://data/world_seed.runtime.json"
const WORLD_ID := "flextrawurst.engine.slice.001"
const ASSET_ID := "alleswisser.asset.3d.test-cube.001"

var confirmed := false
var last_status := ""

func _init() -> void:
	_run.call_deferred()

func _run() -> void:
	var runtime_seed := _read_json_dictionary(RUNTIME_SEED_PATH)
	var bridge_config := runtime_seed.get("bridge", {}) as Dictionary
	if not bool(bridge_config.get("enabled", false)):
		push_error("Runtime-Bridge ist nicht aktiviert")
		quit(1)
		return

	var bridge_script := load("res://scripts/world_bridge.gd") as Script
	if bridge_script == null:
		push_error("WorldBridge-Script fehlt")
		quit(1)
		return
	var bridge: Node = bridge_script.new() as Node
	if bridge == null:
		push_error("WorldBridge konnte nicht instanziiert werden")
		quit(1)
		return
	root.add_child(bridge)
	await process_frame

	bridge.bridge_status_changed.connect(_on_bridge_status_changed)
	bridge.configure_from_seed({
		"world_id": WORLD_ID,
		"bridge": bridge_config
	})
	bridge.start_sync()
	bridge.queue_world_event({
		"event_id": "godot-vps-probe-%s" % str(Time.get_unix_time_from_system()),
		"event_type": "GODOT_VPS_BRIDGE_PROBE",
		"origin": "RaDi0n92/flextrawurst-agent",
		"truth_status": "REAL_VPS_RUNTIME_EVENT",
		"timestamp": Time.get_datetime_string_from_system(true),
		"payload": {
			"asset_id": ASSET_ID,
			"probe": "bidirectional_localhost_append_only"
		}
	})

	var deadline := Time.get_ticks_msec() + 10000
	while not confirmed and Time.get_ticks_msec() < deadline:
		await process_frame

	if confirmed:
		print("FLEXTRAWURST_GODOT_LIVE_BRIDGE_PROBE_PASS")
		quit(0)
	else:
		push_error("Bridge-Probe ohne Bestätigung; letzter Status: %s" % last_status)
		quit(1)

func _on_bridge_status_changed(status: String) -> void:
	last_status = status
	print("[LIVE_BRIDGE_PROBE] %s" % status)
	if status == "Ereignis bestätigt":
		confirmed = true

func _read_json_dictionary(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	return parsed as Dictionary if typeof(parsed) == TYPE_DICTIONARY else {}
