class_name TouchCameraDrag
extends Control

@export var camera_controller: CameraController
@export var touch_sensitivity: float = 0.005

var _touch_index: int = -1

func _gui_input(event: InputEvent) -> void:
	if not camera_controller:
		return
		
	if event is InputEventScreenTouch:
		if event.pressed and _touch_index == -1:
			_touch_index = event.index
		elif not event.pressed and event.index == _touch_index:
			_touch_index = -1
	elif event is InputEventScreenDrag and event.index == _touch_index:
		camera_controller.rotate_camera(event.relative.x * touch_sensitivity, -event.relative.y * touch_sensitivity)
