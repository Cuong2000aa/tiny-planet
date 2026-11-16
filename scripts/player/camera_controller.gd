class_name CameraController
extends Node3D

@export var target: Node3D
@export var mouse_sensitivity: float = 0.004
@export var touch_sensitivity: float = 0.005
@export var follow_smoothness: float = 12.0
@export var min_pitch: float = deg_to_rad(-60.0)
@export var max_pitch: float = deg_to_rad(25.0)

@onready var spring_arm: SpringArm3D = $SpringArm3D
@onready var camera: Camera3D = $SpringArm3D/Camera3D

var _pitch: float = deg_to_rad(-18.0)
var _yaw: float = 0.0
var _is_dragging_mouse: bool = false

func _ready() -> void:
	top_level = true
	if target:
		global_position = target.global_position
	rotation.x = _pitch
	rotation.y = _yaw

func _unhandled_input(event: InputEvent) -> void:
	# Mouse drag rotation
	if event is InputEventMouseButton:
		if event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
			_is_dragging_mouse = event.pressed
	elif event is InputEventMouseMotion and _is_dragging_mouse:
		rotate_camera(event.relative.x * mouse_sensitivity, -event.relative.y * mouse_sensitivity)

func rotate_camera(yaw_delta: float, pitch_delta: float) -> void:
	_yaw -= yaw_delta
	_pitch = clamp(_pitch + pitch_delta, min_pitch, max_pitch)
	rotation.y = _yaw
	rotation.x = _pitch

func _physics_process(delta: float) -> void:
	if not target:
		return
	var target_pos = target.global_position + Vector3(0, 1.2, 0)
	global_position = global_position.lerp(target_pos, follow_smoothness * delta)
