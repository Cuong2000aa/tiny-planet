class_name PlayerController
extends CharacterBody3D

signal interacted_with(target: Interactable)
signal interaction_target_changed(target: Interactable)

enum AnimState {
	IDLE,
	IDLE_SECONDARY,
	WALK,
	RUN,
	JUMP_START,
	JUMP_LOOP,
	FALL,
	LANDING,
	COLLECT,
	INTERACT,
	VICTORY,
	RESPAWN
}

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
@onready var sfx_jump: AudioStreamPlayer3D = $SFXJump
@onready var sfx_land: AudioStreamPlayer3D = $SFXLand
@onready var interaction_detector: Area3D = $InteractionDetector
@onready var dust_particles: Node3D = get_node_or_null("DustParticles")

var animation_player: AnimationPlayer = null

# Animation state management
var current_anim_state: AnimState = AnimState.IDLE
var _idle_timer: float = 0.0
var _one_shot_timer: float = 0.0
var _is_in_one_shot: bool = false
var _last_yaw: float = 0.0
var _banking_angle: float = 0.0

# Interaction tracking
var _nearby_interactables: Array[Interactable] = []
var current_target: Interactable = null

func _ready() -> void:
	_spawn_point = global_position if is_inside_tree() else position
	collision_layer = 2  # Layer 2 for Player
	collision_mask = 1 | 4 | 8 # Environment + Interactables + Collectibles
	
	if interaction_detector and not interaction_detector.area_entered.is_connected(_on_interaction_area_entered):
		interaction_detector.area_entered.connect(_on_interaction_area_entered)
		interaction_detector.area_exited.connect(_on_interaction_area_exited)

	_setup_animation_player()
	_change_state(AnimState.IDLE)

func _setup_animation_player() -> void:
	if not visual_root:
		visual_root = get_node_or_null("VisualRoot")
	if visual_root:
		animation_player = visual_root.find_child("AnimationPlayer", true, false)
	
	if not animation_player:
		push_warning("PlayerController: AnimationPlayer not found under VisualRoot")
		return

	# Setup animation library aliases and loop modes
	var anim_list = animation_player.get_animation_list()
	
	# Add Jump_Loop alias if only Jump is imported
	if animation_player.has_animation("Jump") and not animation_player.has_animation("Jump_Loop"):
		var jump_anim = animation_player.get_animation("Jump")
		animation_player.get_animation_library("").add_animation("Jump_Loop", jump_anim)
	
	# Set looping animations
	var looping_anims = ["Idle", "Walk", "Run", "Fall", "Jump", "Jump_Loop", "Victory"]
	for anim_name in looping_anims:
		if animation_player.has_animation(anim_name):
			var a = animation_player.get_animation(anim_name)
			a.loop_mode = Animation.LOOP_LINEAR

	# Set non-looping one-shots
	var oneshot_anims = ["Idle_Secondary", "Jump_Start", "Landing", "Collect", "Interact", "Respawn", "Turn_Left", "Turn_Right"]
	for anim_name in oneshot_anims:
		if animation_player.has_animation(anim_name):
			var a = animation_player.get_animation(anim_name)
			a.loop_mode = Animation.LOOP_NONE

	# Configure default crossfade blend
	animation_player.playback_default_blend_time = 0.15
	
	# Snappy blend timings
	animation_player.set_blend_time("Walk", "Run", 0.12)
	animation_player.set_blend_time("Run", "Walk", 0.12)
	animation_player.set_blend_time("Walk", "Idle", 0.18)
	animation_player.set_blend_time("Run", "Idle", 0.18)
	animation_player.set_blend_time("Jump_Start", "Jump", 0.08)
	animation_player.set_blend_time("Jump_Start", "Jump_Loop", 0.08)
	animation_player.set_blend_time("Fall", "Landing", 0.06)
	animation_player.set_blend_time("Landing", "Idle", 0.14)
	animation_player.set_blend_time("Landing", "Walk", 0.12)
	animation_player.set_blend_time("Collect", "Idle", 0.18)
	animation_player.set_blend_time("Interact", "Idle", 0.18)
	animation_player.set_blend_time("Respawn", "Idle", 0.22)

	if not animation_player.animation_finished.is_connected(_on_animation_finished):
		animation_player.animation_finished.connect(_on_animation_finished)

func _physics_process(delta: float) -> void:
	if _is_victory:
		_process_victory(delta)
		return

	# Fall recovery
	if global_position.y < -15.0:
		_respawn()
		return

	# Timers update
	if _is_in_one_shot:
		_one_shot_timer -= delta
		if _one_shot_timer <= 0.0:
			_is_in_one_shot = false

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

	# Cancel landing squash early if player aggressively inputs movement
	if _is_in_one_shot and current_anim_state == AnimState.LANDING and move_direction.length_squared() > 0.05:
		_is_in_one_shot = false

	# Smooth horizontal velocity
	var target_vel = move_direction * move_speed
	var accel = acceleration if move_direction.length_squared() > 0.01 else deceleration
	velocity.x = move_toward(velocity.x, target_vel.x, accel * delta)
	velocity.z = move_toward(velocity.z, target_vel.z, accel * delta)

	move_and_slide()

	# Update visual orientation & secondary banking
	_update_visuals(delta, move_direction)

	# Update animation state machine
	_update_animation_state(delta)

	# Handle interaction input
	_update_interaction_target()
	if Input.is_action_just_pressed("interact") and current_target:
		play_interact_animation(current_target)
		current_target.interact(self)
		interacted_with.emit(current_target)

func _update_visuals(delta: float, move_dir: Vector3) -> void:
	if not visual_root:
		return

	var horizontal_vel = Vector3(velocity.x, 0, velocity.z)
	var speed = horizontal_vel.length()

	if speed > 0.15:
		var target_angle = atan2(-horizontal_vel.x, -horizontal_vel.z)
		var current_angle = visual_root.rotation.y
		var diff = wrapf(target_angle - current_angle, -PI, PI)
		
		# Turn rate banking (Astro Bot stylized tilt)
		var turn_rate = diff / maxf(delta, 0.001)
		var target_bank = clampf(turn_rate * -0.015, -0.22, 0.22)
		_banking_angle = lerpf(_banking_angle, target_bank, 12.0 * delta)
		
		visual_root.rotation.y = lerp_angle(current_angle, target_angle, rotation_speed * delta)
		visual_root.rotation.z = _banking_angle
	else:
		_banking_angle = lerpf(_banking_angle, 0.0, 10.0 * delta)
		visual_root.rotation.z = _banking_angle

func _update_animation_state(delta: float) -> void:
	if not animation_player:
		return

	# In one-shot states, don't override until finished (unless handled)
	if _is_in_one_shot:
		return

	# Air states
	if not is_on_floor():
		_idle_timer = 0.0
		if velocity.y > 0.5:
			if current_anim_state != AnimState.JUMP_START and current_anim_state != AnimState.JUMP_LOOP:
				_change_state(AnimState.JUMP_LOOP)
		elif velocity.y <= -0.5:
			_change_state(AnimState.FALL)
		return

	# Ground states
	var horizontal_speed = Vector3(velocity.x, 0, velocity.z).length()
	
	if horizontal_speed < 0.25:
		# Idle
		_idle_timer += delta
		if _idle_timer >= 6.0:
			_idle_timer = 0.0
			_play_one_shot(AnimState.IDLE_SECONDARY, 3.5)
		else:
			if current_anim_state != AnimState.IDLE:
				_change_state(AnimState.IDLE)
	elif horizontal_speed < 4.2:
		# Walk
		_idle_timer = 0.0
		_change_state(AnimState.WALK)
		# Proportional stride speed matching
		animation_player.speed_scale = clampf(horizontal_speed / 2.8, 0.8, 1.35)
	else:
		# Run
		_idle_timer = 0.0
		_change_state(AnimState.RUN)
		animation_player.speed_scale = clampf(horizontal_speed / 5.8, 0.9, 1.45)

func _change_state(new_state: AnimState) -> void:
	current_anim_state = new_state
	if not animation_player:
		return

	animation_player.speed_scale = 1.0

	match new_state:
		AnimState.IDLE:
			_play_animation("Idle")
		AnimState.IDLE_SECONDARY:
			_play_animation("Idle_Secondary")
		AnimState.WALK:
			_play_animation("Walk")
		AnimState.RUN:
			_play_animation("Run")
		AnimState.JUMP_START:
			_play_animation("Jump_Start")
		AnimState.JUMP_LOOP:
			if animation_player.has_animation("Jump_Loop"):
				_play_animation("Jump_Loop")
			else:
				_play_animation("Jump")
		AnimState.FALL:
			_play_animation("Fall")
		AnimState.LANDING:
			_play_animation("Landing")
		AnimState.COLLECT:
			_play_animation("Collect")
		AnimState.INTERACT:
			_play_animation("Interact")
		AnimState.VICTORY:
			_play_animation("Victory")
		AnimState.RESPAWN:
			_play_animation("Respawn")

func _play_animation(anim_name: String, blend: float = -1.0) -> void:
	if animation_player and animation_player.has_animation(anim_name):
		if animation_player.current_animation != anim_name:
			animation_player.play(anim_name, blend)

func _play_one_shot(state: AnimState, duration: float) -> void:
	_is_in_one_shot = true
	_one_shot_timer = duration
	_change_state(state)

func _on_animation_finished(anim_name: StringName) -> void:
	if _is_victory:
		return

	if anim_name in ["Landing", "Jump_Start", "Collect", "Interact", "Respawn", "Idle_Secondary"]:
		_is_in_one_shot = false
		if is_on_floor():
			var speed = Vector3(velocity.x, 0, velocity.z).length()
			if speed > 0.25:
				_change_state(AnimState.WALK)
			else:
				_change_state(AnimState.IDLE)
		else:
			if velocity.y <= -0.5:
				_change_state(AnimState.FALL)
			else:
				_change_state(AnimState.JUMP_LOOP)

func _on_jumped() -> void:
	if sfx_jump:
		sfx_jump.pitch_scale = randf_range(0.95, 1.05)
		sfx_jump.play()
	if dust_particles:
		dust_particles.restart()
		dust_particles.emitting = true
	
	# Start with quick takeoff anticipation, then launch into Jump_Loop
	_play_one_shot(AnimState.JUMP_START, 0.20)

func _on_landed() -> void:
	if sfx_land:
		sfx_land.play()
	if dust_particles:
		dust_particles.restart()
		dust_particles.emitting = true
	
	# Landing squash compression
	_play_one_shot(AnimState.LANDING, 0.28)

func _respawn() -> void:
	if is_inside_tree():
		global_position = _spawn_point + Vector3(0, 1.5, 0)
	else:
		position = _spawn_point + Vector3(0, 1.5, 0)
	velocity = Vector3.ZERO
	_play_one_shot(AnimState.RESPAWN, 0.9)

func play_collect_animation() -> void:
	# Joyful celebration hop and fist pump
	_play_one_shot(AnimState.COLLECT, 0.75)

func play_interact_animation(target: Node3D = null) -> void:
	if target and visual_root:
		var dir = (target.global_position - global_position)
		dir.y = 0
		if dir.length_squared() > 0.01:
			visual_root.rotation.y = atan2(-dir.x, -dir.z)
	_play_one_shot(AnimState.INTERACT, 0.75)

func trigger_victory() -> void:
	_is_victory = true
	velocity = Vector3.ZERO
	_change_state(AnimState.VICTORY)

func _process_victory(delta: float) -> void:
	if visual_root and current_anim_state != AnimState.VICTORY:
		_change_state(AnimState.VICTORY)

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
