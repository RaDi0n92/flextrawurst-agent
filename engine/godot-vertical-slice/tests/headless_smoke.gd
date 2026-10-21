extends SceneTree

func _init() -> void:
	var failures: Array[String] = []
	_check(FileAccess.file_exists("res://project.godot"), "project.godot fehlt", failures)
	_check(FileAccess.file_exists("res://main.tscn"), "main.tscn fehlt", failures)
	_check(FileAccess.file_exists("res://data/world_seed.json"), "world_seed.json fehlt", failures)
	_check(FileAccess.file_exists("res://data/asset_manifest.json"), "asset_manifest.json fehlt", failures)
	_check(FileAccess.file_exists("res://assets/test_cube.glb"), "vorbereitetes GLB fehlt", failures)

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
			_check(not bool(seed.get("bridge", {}).get("enabled", true)), "Repo-Grundseed darf die VPS-Route nicht aktivieren", failures)

	var manifest_file := FileAccess.open("res://data/asset_manifest.json", FileAccess.READ)
	_check(manifest_file != null, "asset_manifest.json nicht lesbar", failures)
	if manifest_file != null:
		var manifest_value: Variant = JSON.parse_string(manifest_file.get_as_text())
		_check(typeof(manifest_value) == TYPE_DICTIONARY, "Asset-Manifest ist kein JSON-Objekt", failures)
		if typeof(manifest_value) == TYPE_DICTIONARY:
			var manifest := manifest_value as Dictionary
			var assets := manifest.get("assets", []) as Array
			_check(assets.size() == 1, "genau ein Vertikalschnitt-Asset erwartet", failures)
			if assets.size() == 1:
				var asset := assets[0] as Dictionary
				_check(str(asset.get("asset_id", "")) == "alleswisser.asset.3d.test-cube.001", "Alleswisser-Asset-ID stimmt nicht", failures)
				_check(str(asset.get("sha256", "")) == "ca481b86fb41d80f59af4b3714ea34c0798adf2acd9d871d4bf563861e17ca00", "GLB-Hash stimmt nicht", failures)

	var glb := ResourceLoader.load("res://assets/test_cube.glb") as PackedScene
	_check(glb != null, "GLB konnte nicht als PackedScene importiert werden", failures)

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
