extends SceneTree

func _init():
	var glb = load("res://assets/models/characters/bot.glb")
	if not glb:
		printerr("Failed to load bot.glb")
		quit(1)
		return
	var inst = glb.instantiate()
	print("Root Node: ", inst.name)
	_dump_children(inst, "  ")
	quit(0)

func _dump_children(node: Node, indent: String):
	for child in node.get_children():
		print(indent, child.name, " [", child.get_class(), "]")
		_dump_children(child, indent + "  ")
