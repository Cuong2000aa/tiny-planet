class_name PlayerController
extends CharacterBody3D

signal interacted_with(target: Interactable)
signal interaction_target_changed(target: Interactable)

@export var move_speed: float = 6.0
@export var acceleration: float = 18.0
@export var deceleration: float = 14.0
@export var jump_velocity: float = 8.5
@export var rotation_speed: float = 15.0
@export var camera_controller: CameraController

# Movement state
var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 9.8) * 2.2
var _spawn_point: Vector3 = Vector3.ZERO
var _was_on_floor: bool = false
var _is_victory: bool = false

# Visual and audio nodes
@onready var visual_root: Node3D = $VisualRoot
@onready var animation_player: AnimationPlayer = $VisualRoot/AnimationPlayer if has_node("VisualRoot/AnimationPlayer") else null
@onready var sfx_jump: AudioStreamPlayer3D = $SFXJump
@onready var sfx_land: AudioStreamPlayer3D = $SFXLand
@onready var interaction_detector: Area3D = $InteractionDetector
@onready var dust_particles: GPUParticles3D = $DustParticles if has_node("DustParticles") else null

# Interaction tracking
var _nearby_interactables: Array[Interactable] = []
var current_target: Interactable = null

# Procedural animation parameters
var _wobble_time: float = 0.0

func _ready() -> void:
	_spawn_point = global_position
	collision_layer = 2  # Layer 2 for Player
	collision_mask = 1 | 4 | 8 # Environment + Interactables + Collectibles
	
	if interaction_detector:
		interaction_detector.area_entered.connect(_on_interaction_area_entered)
		interaction_detector.area_exited.connect(_on_interaction_area_exited)

func _physics_process(delta: float) -> void:
	if _is_victory:
		_process_victory(delta)
		return

	# Fall recovery
	if global_position.y < -15.0:
		_respawn()
		return

	# Apply Gravity
	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		if not _was_on_floor:
			_on_landed()

	_was_on_floor = is_on_floor()

	# Jump handling
	if is_on_floor() and Input.is_action_just_pressed("jump"):
		velocity.y = jump_velocity
		_on_jumped()

	# Movement input
	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var move_direction := Vector3.ZERO

	if camera_controller:
		var cam_yaw = camera_controller.rotation.y
		var cam_forward = -Vector3(sin(cam_yaw), 0, cos(cam_yaw))
		var cam_right = Vector3(cos(cam_yaw), 0, -sin(cam_yaw))
		move_direction = (cam_right * input_dir.x + cam_forward * -input_dir.y).normalized()
	else:
		move_direction = Vector3(input_dir.x, 0, input_dir.y).normalized()

	# Smooth horizontal velocity
	var target_vel = move_direction * move_speed
	var accel = acceleration if move_direction.length_squared() > 0.01 else deceleration
	velocity.x = move_toward(velocity.x, target_vel.x, accel * delta)
	velocity.z = move_toward(velocity.z, target_vel.z, accel * delta)

	move_and_slide()

	# Visual orientation & procedural animation
	_update_visuals(delta, move_direction)

	# Handle interaction input
	_update_interaction_target()
	if Input.is_action_just_pressed("interact") and current_target:
		current_target.interact(self)
		interacted_with.emit(current_target)

func _update_visuals(delta: float, move_dir: Vector3) -> void:
	if not visual_root:
		return

	# Face movement direction
	var horizontal_vel = Vector3(velocity.x, 0, velocity.z)
	if horizontal_vel.length_squared() > 0.1:
		var target_angle = atan2(-horizontal_vel.x, -horizontal_vel.z)
		visual_root.rotation.y = lerp_angle(visual_root.rotation.y, target_angle, rotation_speed * delta)
		
		# Cute walking tilt/wobble
		if is_on_floor():
			_wobble_time += delta * 14.0
			visual_root.rotation.z = sin(_wobble_time) * 0.08
			visual_root.position.y = abs(sin(_wobble_time)) * 0.04
		else:
			visual_root.rotation.z = lerp(visual_root.rotation.z, 0.0, 10.0 * delta)
	else:
		visual_root.rotation.z = lerp(visual_root.rotation.z, 0.0, 10.0 * delta)
		visual_root.position.y = lerp(visual_root.position.y, 0.0, 10.0 * delta)
		_wobble_time = 0.0

func _on_jumped() -> void:
	if sfx_jump:
		sfx_jump.pitch_scale = randf_range(0.95, 1.05)
		sfx_jump.play()
	# Stretch on jump
	if visual_root:
		var tween = create_tween()
		tween.tween_property(visual_root, "scale", Vector3(0.8, 1.25, 0.8), 0.1).set_trans(Tween.TRANS_BACK)
		tween.tween_property(visual_root, "scale", Vector3.ONE, 0.15)
	if dust_particles:
		dust_particles.restart()
		dust_particles.emitting = true

func _on_landed() -> void:
	if sfx_land:
		sfx_land.play()
	# Squash on land
	if visual_root:
		var tween = create_tween()
		tween.tween_property(visual_root, "scale", Vector3(1.25, 0.75, 1.25), 0.08).set_trans(Tween.TRANS_QUAD)
		tween.tween_property(visual_root, "scale", Vector3.ONE, 0.18).set_trans(Tween.TRANS_SPRING)
	if dust_particles:
		dust_particles.restart()
		dust_particles.emitting = true

func _respawn() -> void:
	global_position = _spawn_point + Vector3(0, 1.5, 0)
	velocity = Vector3.ZERO

func trigger_victory() -> void:
	_is_victory = true
	velocity = Vector3.ZERO
	# Celebratory bounce tween
	if visual_root:
		var tween = create_tween().set_loops(4)
		tween.tween_property(visual_root, "position:y", 0.4, 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tween.tween_property(visual_root, "position:y", 0.0, 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)

func _process_victory(delta: float) -> void:
	if visual_root:
		visual_root.rotate_y(4.0 * delta)

func _on_interaction_area_entered(area: Area3D) -> void:
	if area is Interactable:
		_nearby_interactables.append(area)

func _on_interaction_area_exited(area: Area3D) -> void:
	if area is Interactable:
		_nearby_interactables.erase(area)

func _update_interaction_target() -> void:
	var closest: Interactable = null
	var min_dist: float = 999.0

	for item in _nearby_interactables:
		if is_instance_valid(item) and item.can_interact(self):
			var dist = global_position.distance_squared_to(item.global_position)
			if dist < min_dist:
				min_dist = dist
				closest = item

	if closest != current_target:
		current_target = closest
		interaction_target_changed.emit(current_target)
