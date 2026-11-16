class_name ExitPortal
extends Area3D

signal portal_entered

@export var is_unlocked: bool = false
@onready var vortex_mesh: Node3D = get_node_or_null("VisualRoot/PortalVortex")
@onready var portal_light: OmniLight3D = get_node_or_null("OmniLight3D")
@onready var sfx_portal: AudioStreamPlayer3D = get_node_or_null("AudioStreamPlayer3D")
@onready var sfx_victory: AudioStreamPlayer3D = get_node_or_null("VictoryAudio")
@onready var particles: Node3D = get_node_or_null("PortalParticles")

var _rotation_speed: float = 1.0

func _ready() -> void:
	collision_layer = 4
	collision_mask = 2
	body_entered.connect(_on_body_entered)
	_update_state_visuals()

func _process(delta: float) -> void:
	if vortex_mesh:
		vortex_mesh.rotate_z(_rotation_speed * delta)

func unlock() -> void:
	if is_unlocked:
		return
	is_unlocked = true
	_rotation_speed = 3.0
	_update_state_visuals()
	if sfx_portal:
		sfx_portal.play()

func _update_state_visuals() -> void:
	if portal_light:
		portal_light.visible = is_unlocked
		portal_light.light_energy = 4.0 if is_unlocked else 0.5
	if particles:
		particles.emitting = is_unlocked
	if vortex_mesh:
		vortex_mesh.scale = Vector3.ONE if is_unlocked else Vector3(0.3, 0.3, 0.3)

func _on_body_entered(body: Node3D) -> void:
	if not is_unlocked:
		return
	if body is CharacterBody3D:
		if sfx_victory:
			sfx_victory.play()
		portal_entered.emit()
