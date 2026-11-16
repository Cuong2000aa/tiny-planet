class_name TouchVirtualJoystick
extends Control

@export var max_radius: float = 64.0
@export var deadzone: float = 10.0

@onready var knob: Control = $Knob
@onready var base: Control = $Base

var _touch_index: int = -1
var _center: Vector2 = Vector2.ZERO
var output_vector: Vector2 = Vector2.ZERO

func _ready() -> void:
	_center = size / 2.0
	_reset_knob()

func _reset_knob() -> void:
	if knob:
		knob.position = _center - knob.size / 2.0
	output_vector = Vector2.ZERO
	_update_input_actions(Vector2.ZERO)

func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed and _touch_index == -1:
			_touch_index = event.index
			_update_from_pos(event.position)
		elif not event.pressed and event.index == _touch_index:
			_touch_index = -1
			_reset_knob()
	elif event is InputEventScreenDrag and event.index == _touch_index:
		_update_from_pos(event.position)

func _update_from_pos(pos: Vector2) -> void:
	var diff = pos - _center
	var dist = diff.length()
	if dist > max_radius:
		diff = diff.normalized() * max_radius
	
	if knob:
		knob.position = (_center + diff) - knob.size / 2.0
	
	if dist < deadzone:
		output_vector = Vector2.ZERO
	else:
		output_vector = diff / max_radius

	_update_input_actions(output_vector)

func _update_input_actions(vec: Vector2) -> void:
	# Emulate Godot actions
	_set_action_state("move_right", max(0.0, vec.x))
	_set_action_state("move_left", max(0.0, -vec.x))
	_set_action_state("move_back", max(0.0, vec.y))
	_set_action_state("move_forward", max(0.0, -vec.y))

func _set_action_state(action_name: String, strength: float) -> void:
	if strength > 0.2:
		Input.action_press(action_name, strength)
	else:
		Input.action_release(action_name)
