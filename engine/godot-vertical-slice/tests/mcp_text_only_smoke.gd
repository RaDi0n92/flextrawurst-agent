extends SceneTree

const ASSET_B64_PATH := "res://assets/test_cube.glb.b64"
const EXPECTED_SHA256 := "ca481b86fb41d80f59af4b3714ea34c0798adf2acd9d871d4bf563861e17ca00"

func _init() -> void:
	_run.call_deferred()

func _run() -> void:
	if not FileAccess.file_exists(ASSET_B64_PATH):
		push_error("MCP-Textkörper fehlt: %s" % ASSET_B64_PATH)
		quit(1)
		return

	var file := FileAccess.open(ASSET_B64_PATH, FileAccess.READ)
	if file == null:
		push_error("MCP-Textkörper nicht lesbar")
		quit(1)
		return
	var raw_bytes := Marshalls.base64_to_raw(file.get_as_text().strip_edges())
	if raw_bytes.is_empty():
		push_error("MCP-Textkörper ergab keine Bytes")
		quit(1)
		return

	var hashing := HashingContext.new()
	if hashing.start(HashingContext.HASH_SHA256) != OK:
		push_error("SHA-256-Kontext konnte nicht gestartet werden")
		quit(1)
		return
	if hashing.update(raw_bytes) != OK:
		push_error("SHA-256-Bytes konnten nicht verarbeitet werden")
		quit(1)
		return
	var actual_sha256 := hashing.finish().hex_encode()
	if actual_sha256 != EXPECTED_SHA256:
		push_error("MCP-Textkörper-Hash falsch: %s" % actual_sha256)
		quit(1)
		return

	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var error := document.append_from_buffer(raw_bytes, "", state)
	if error != OK:
		push_error("GLB-Puffer konnte nicht gelesen werden: %s" % error_string(error))
		quit(1)
		return
	var scene := document.generate_scene(state)
	if scene == null:
		push_error("GLB-Puffer erzeugte keine Szene")
		quit(1)
		return
	root.add_child(scene)
	await process_frame
	print("FLEXTRAWURST_MCP_TEXT_ONLY_GLB_PASS %s %s" % [raw_bytes.size(), actual_sha256])
	quit(0)
