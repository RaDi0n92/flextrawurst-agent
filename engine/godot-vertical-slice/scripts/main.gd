extends Node3D

const WORLD_SEED_PATH := "res://data/world_seed.json"
const RUNTIME_SEED_PATH := "res://data/world_seed.runtime.json"
const ASSET_PATH := "res://assets/test_cube.glb"
const ASSET_B64_PATH := "res://assets/test_cube.glb.b64"
const ASSET_MANIFEST_PATH := "res://data/asset_manifest.json"
const MOVE_SPEED := 7.0
const GRAVITY := 24.0

@onready var player: CharacterBody3D = $Player
@onready var status_label: Label = $HUD/Panel/Status
@onready var bridge: Node = $WorldBridge

var world_seed: Dictionary = {}
var loaded_asset_id := ""

func _ready() -> void:
	_ensure_input_actions()
	world_seed = _load_world_seed()
	_apply_world_seed(world_seed)
	_load_provenance_asset()
	bridge.world_event_received.connect(_on_world_event_received)
	bridge.bridge_status_changed.connect(_on_bridge_status_changed)
	bridge.configure_from_seed(world_seed)
	bridge.start_sync()
	var bridge_config := world_seed.get("bridge", {}) as Dictionary
	if bool(bridge_config.get("proof_event_on_start", false)):
		_queue_startup_proof.call_deferred()

func _physics_process(delta: float) -> void:
	var input_vector := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction := Vector3(input_vector.x, 0.0, input_vector.y)
	if direction.length_squared() > 1.0:
		direction = direction.normalized()

	player.velocity.x = direction.x * MOVE_SPEED
	player.velocity.z = direction.z * MOVE_SPEED
	if not player.is_on_floor():
		player.velocity.y -= GRAVITY * delta
	else:
		player.velocity.y = 0.0
	player.move_and_slide()

func _ensure_input_actions() -> void:
	_bind_key("move_forward", KEY_W)
	_bind_key("move_forward", KEY_UP)
	_bind_key("move_back", KEY_S)
	_bind_key("move_back", KEY_DOWN)
	_bind_key("move_left", KEY_A)
	_bind_key("move_left", KEY_LEFT)
	_bind_key("move_right", KEY_D)
	_bind_key("move_right", KEY_RIGHT)

func _bind_key(action: StringName, keycode: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action, 0.2)
	for existing in InputMap.action_get_events(action):
		if existing is InputEventKey and existing.physical_keycode == keycode:
			return
	var event := InputEventKey.new()
	event.physical_keycode = keycode
	InputMap.action_add_event(action, event)

func _load_world_seed() -> Dictionary:
	var base_seed := _read_json_dictionary(WORLD_SEED_PATH)
	if FileAccess.file_exists(RUNTIME_SEED_PATH):
		var runtime_seed := _read_json_dictionary(RUNTIME_SEED_PATH)
		return _merge_dictionaries(base_seed, runtime_seed)
	return base_seed

func _read_json_dictionary(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("JSON-Datei fehlt: %s" % path)
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("JSON-Datei konnte nicht geöffnet werden: %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("JSON-Datei ist kein Objekt: %s" % path)
		return {}
	return parsed as Dictionary

func _merge_dictionaries(base: Dictionary, override: Dictionary) -> Dictionary:
	var merged := base.duplicate(true)
	for key in override:
		var incoming: Variant = override[key]
		if merged.has(key) and typeof(merged[key]) == TYPE_DICTIONARY and typeof(incoming) == TYPE_DICTIONARY:
			merged[key] = _merge_dictionaries(merged[key] as Dictionary, incoming as Dictionary)
		else:
			merged[key] = incoming
	return merged

func _apply_world_seed(seed: Dictionary) -> void:
	var world_id := str(seed.get("world_id", "unbekannt"))
	var region := seed.get("region", {}) as Dictionary
	var region_name := str(region.get("name", "Unbenannte Region"))
	var truth_status := str(seed.get("truth_status", "NICHT_BEWIESEN"))
	status_label.text = "Welt-ID: %s\nRegion: %s · Status: %s" % [world_id, region_name, truth_status]

	var spawn := seed.get("player_spawn", {}) as Dictionary
	player.position = Vector3(
		float(spawn.get("x", 0.0)),
		float(spawn.get("y", 1.0)),
		float(spawn.get("z", 5.0))
	)

func _load_provenance_asset() -> void:
	var manifest := _read_json_dictionary(ASSET_MANIFEST_PATH)
	var assets := manifest.get("assets", []) as Array
	if assets.is_empty():
		push_error("Asset-Manifest enthält keine Assets")
		return
	var asset_entry := assets[0] as Dictionary
	loaded_asset_id = str(asset_entry.get("asset_id", "unbekannt"))

	var instance := _load_asset_scene()
	if instance == null:
		push_error("GLB konnte weder importiert noch aus dem Textkörper geladen werden")
		status_label.text += "\nGLB: FEHLT · %s" % loaded_asset_id
		return
	instance.name = "AlleswisserProvenanceAsset"
	instance.position = Vector3(0.0, 1.25, -8.0)
	instance.scale = Vector3(2.0, 2.0, 2.0)
	instance.set_meta("alleswisser_id", loaded_asset_id)
	instance.set_meta("truth_status", asset_entry.get("origin", {}).get("truth_status", "UNBEKANNT"))
	add_child(instance)
	$OriginAnchor.visible = false
	status_label.text += "\nGLB: GELADEN · %s" % loaded_asset_id

func _load_asset_scene() -> Node:
	if ResourceLoader.exists(ASSET_PATH):
		var packed := ResourceLoader.load(ASSET_PATH) as PackedScene
		if packed != null:
			return packed.instantiate()

	if not FileAccess.file_exists(ASSET_B64_PATH):
		push_error("Weder importiertes GLB noch Base64-Quellkörper vorhanden")
		return null
	var encoded_file := FileAccess.open(ASSET_B64_PATH, FileAccess.READ)
	if encoded_file == null:
		push_error("Base64-Quellkörper konnte nicht geöffnet werden")
		return null
	var raw_bytes := Marshalls.base64_to_raw(encoded_file.get_as_text().strip_edges())
	if raw_bytes.is_empty():
		push_error("Base64-Quellkörper ergab keine GLB-Bytes")
		return null

	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var error := document.append_from_buffer(raw_bytes, "", state)
	if error != OK:
		push_error("GLB-Puffer konnte nicht gelesen werden: %s" % error_string(error))
		return null
	var generated := document.generate_scene(state)
	if generated == null:
		push_error("GLB-Puffer erzeugte keine Szene")
	return generated

func _queue_startup_proof() -> void:
	await get_tree().create_timer(0.25).timeout
	bridge.queue_world_event({
		"event_id": "godot-start-%s" % str(Time.get_unix_time_from_system()),
		"event_type": "GODOT_ENGINE_SLICE_STARTED",
		"origin": "RaDi0n92/flextrawurst-agent",
		"truth_status": "REAL_VPS_RUNTIME_EVENT",
		"timestamp": Time.get_datetime_string_from_system(true),
		"payload": {
			"asset_id": loaded_asset_id,
			"player_position": {
				"x": player.position.x,
				"y": player.position.y,
				"z": player.position.z
			}
		}
	})

func _on_world_event_received(event: Dictionary) -> void:
	var event_type := str(event.get("event_type", "unbekannt"))
	var base_status := status_label.text.get_slice("\nLive-Ereignis:", 0)
	status_label.text = "%s\nLive-Ereignis: %s" % [base_status, event_type]

func _on_bridge_status_changed(status: String) -> void:
	print("[WORLD_BRIDGE] %s" % status)
