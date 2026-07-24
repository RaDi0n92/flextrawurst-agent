extends Node3D

const WORLD_SEED_PATH := "res://data/world_seed.json"
const MOVE_SPEED := 7.0
const GRAVITY := 24.0

@onready var player: CharacterBody3D = $Player
@onready var status_label: Label = $HUD/Panel/Status
@onready var bridge: Node = $WorldBridge

var world_seed: Dictionary = {}

func _ready() -> void:
	_ensure_input_actions()
	world_seed = _load_world_seed()
	_apply_world_seed(world_seed)
	bridge.world_event_received.connect(_on_world_event_received)
	bridge.bridge_status_changed.connect(_on_bridge_status_changed)
	bridge.configure_from_seed(world_seed)
	bridge.start_sync()

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
	if not FileAccess.file_exists(WORLD_SEED_PATH):
		push_error("Weltseed fehlt: %s" % WORLD_SEED_PATH)
		return {}
	var file := FileAccess.open(WORLD_SEED_PATH, FileAccess.READ)
	if file == null:
		push_error("Weltseed konnte nicht geöffnet werden")
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Weltseed ist kein JSON-Objekt")
		return {}
	return parsed as Dictionary

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

func _on_world_event_received(event: Dictionary) -> void:
	var event_type := str(event.get("event_type", "unbekannt"))
	var base_status := status_label.text.get_slice("\nLive-Ereignis:", 0)
	status_label.text = "%s\nLive-Ereignis: %s" % [base_status, event_type]

func _on_bridge_status_changed(status: String) -> void:
	print("[WORLD_BRIDGE] %s" % status)
