extends SceneTree

func _init() -> void:
	_run.call_deferred()

func _run() -> void:
	var output_path := "/tmp/flextrawurst-godot-slice-proof.png"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):
			output_path = arg.trim_prefix("--output=")

	var packed := load("res://main.tscn") as PackedScene
	if packed == null:
		push_error("main.tscn konnte für Screenshot nicht geladen werden")
		quit(1)
		return
	var instance := packed.instantiate()
	root.add_child(instance)

	for _index in range(12):
		await process_frame

	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		push_error("Viewport lieferte kein Bild")
		quit(1)
		return
	var error := image.save_png(output_path)
	if error != OK:
		push_error("Screenshot konnte nicht gespeichert werden: %s" % error_string(error))
		quit(1)
		return
	print("FLEXTRAWURST_ENGINE_SCREENSHOT_PASS: %s" % output_path)
	quit(0)
