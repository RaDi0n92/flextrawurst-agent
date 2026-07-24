extends Node

signal world_event_received(event: Dictionary)
signal bridge_status_changed(status: String)

var enabled := false
var base_url := ""
var world_id := ""
var sync_interval_seconds := 5.0
var last_cursor := ""
var pending_events: Array[Dictionary] = []

var _http: HTTPRequest
var _timer: Timer
var _request_mode := "idle"

func _ready() -> void:
	_http = HTTPRequest.new()
	_http.name = "WorldBridgeHTTP"
	add_child(_http)
	_http.request_completed.connect(_on_request_completed)

	_timer = Timer.new()
	_timer.name = "WorldBridgeTimer"
	_timer.one_shot = false
	add_child(_timer)
	_timer.timeout.connect(_sync_tick)

func configure_from_seed(seed: Dictionary) -> void:
	world_id = str(seed.get("world_id", ""))
	var bridge_config := seed.get("bridge", {}) as Dictionary
	enabled = bool(bridge_config.get("enabled", false))
	base_url = str(bridge_config.get("base_url", "")).trim_suffix("/")
	sync_interval_seconds = maxf(float(bridge_config.get("sync_interval_seconds", 5.0)), 1.0)
	_timer.wait_time = sync_interval_seconds

func start_sync() -> void:
	if not enabled:
		bridge_status_changed.emit("deaktiviert: keine bestätigte Live-Route konfiguriert")
		return
	if base_url.is_empty() or world_id.is_empty():
		bridge_status_changed.emit("blockiert: base_url oder world_id fehlt")
		return
	bridge_status_changed.emit("aktiv: %s" % base_url)
	_timer.start()
	_sync_tick()

func queue_world_event(event: Dictionary) -> void:
	var copy := event.duplicate(true)
	copy["world_id"] = world_id
	copy["client_kind"] = "godot_vertical_slice"
	pending_events.append(copy)
	if enabled and _request_mode == "idle":
		_push_next_event()

func _sync_tick() -> void:
	if _request_mode != "idle":
		return
	if not pending_events.is_empty():
		_push_next_event()
	else:
		_pull_world_delta()

func _pull_world_delta() -> void:
	_request_mode = "pull"
	var url := "%s/worlds/%s/events?after=%s" % [base_url, world_id.uri_encode(), last_cursor.uri_encode()]
	var error := _http.request(url, PackedStringArray(["Accept: application/json"]), HTTPClient.METHOD_GET)
	if error != OK:
		_request_mode = "idle"
		bridge_status_changed.emit("pull-fehler: %s" % error_string(error))

func _push_next_event() -> void:
	if pending_events.is_empty():
		return
	_request_mode = "push"
	var payload := JSON.stringify(pending_events[0])
	var url := "%s/worlds/%s/events" % [base_url, world_id.uri_encode()]
	var headers := PackedStringArray(["Accept: application/json", "Content-Type: application/json"])
	var error := _http.request(url, headers, HTTPClient.METHOD_POST, payload)
	if error != OK:
		_request_mode = "idle"
		bridge_status_changed.emit("push-fehler: %s" % error_string(error))

func _on_request_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	var completed_mode := _request_mode
	_request_mode = "idle"
	if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300:
		bridge_status_changed.emit("%s fehlgeschlagen: result=%s http=%s" % [completed_mode, result, response_code])
		return

	var parsed: Variant = JSON.parse_string(body.get_string_from_utf8())
	if completed_mode == "push":
		pending_events.pop_front()
		bridge_status_changed.emit("Ereignis bestätigt")
		return

	if typeof(parsed) != TYPE_DICTIONARY:
		bridge_status_changed.emit("pull ungültig: Antwort ist kein JSON-Objekt")
		return
	var response := parsed as Dictionary
	last_cursor = str(response.get("cursor", last_cursor))
	var events := response.get("events", []) as Array
	for event_value in events:
		if typeof(event_value) == TYPE_DICTIONARY:
			world_event_received.emit(event_value as Dictionary)
	bridge_status_changed.emit("pull bestätigt: %s Ereignisse" % events.size())
