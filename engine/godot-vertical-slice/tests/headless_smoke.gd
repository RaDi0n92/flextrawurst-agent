extends SceneTree

func _init() -> void:
	var failures: Array[String] = []
	_check(FileAccess.file_exists("res://project.godot"), "project.godot fehlt", failures)
	_check(FileAccess.file_exists("res://main.tscn"), "main.tscn fehlt", failures)
	_check(FileAccess.file_exists("res://data/world_seed.json"), "world_seed.json fehlt", failures)

	var seed_file := FileAccess.open("res://data/world_seed.json", FileAccess.READ)
	_check(seed_file != null, "world_seed.json nicht lesbar", failures)
	if seed_file != null:
		var parsed: Variant = JSON.parse_string(seed_file.get_as_text())
		_check(typeof(parsed) == TYPE_DICTIONARY, "world_seed ist kein JSON-Objekt", failures)
		if typeof(parsed) == TYPE_DICTIONARY:
			var seed := parsed as Dictionary
			_check(str(seed.get("world_id", "")) == "flextrawurst.engine.slice.001", "world_id stimmt nicht", failures)
			_check(not bool(seed.get("origin", {}).get("replaces_html_game", true)), "HTML-Schutzgrenze verletzt", failures)
			_check(str(seed.get("origin", {}).get("working_repo", "")) == "RaDi0n92/flextrawurst-agent", "falscher Arbeitsrepo eingetragen", failures)
			_check(str(seed.get("origin", {}).get("public_description_repo", "")) == "RaDi0n92/Flextrawurst", "öffentlicher Beschreibungsrepo fehlt", failures)
			_check(not bool(seed.get("bridge", {}).get("enabled", true)), "unbewiesene VPS-Route darf nicht aktiv sein", failures)

	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main.tscn kann nicht geladen werden", failures)
	if packed != null:
		var instance := packed.instantiate()
		_check(instance.get_node_or_null("Player") is CharacterBody3D, "Player fehlt oder ist kein CharacterBody3D", failures)
		_check(instance.get_node_or_null("Player/Camera") is Camera3D, "Kamera fehlt", failures)
		_check(instance.get_node_or_null("Ground/Collision") is CollisionShape3D, "Bodenkollision fehlt", failures)
		_check(instance.get_node_or_null("WorldBridge") != null, "WorldBridge fehlt", failures)
		instance.free()

	if failures.is_empty():
		print("FLEXTRAWURST_AGENT_ENGINE_SLICE_SMOKE_PASS")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		print("FLEXTRAWURST_AGENT_ENGINE_SLICE_SMOKE_FAIL: %s" % failures.size())
		quit(1)

func _check(condition: bool, message: String, failures: Array[String]) -> void:
	if not condition:
		failures.append(message)
