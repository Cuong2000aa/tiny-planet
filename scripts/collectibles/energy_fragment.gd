class_name EnergyFragment
extends Area3D

signal collected(fragment: EnergyFragment)

@export var bob_amplitude: float = 0.18
@export var bob_speed: float = 2.5
@export var rotation_speed: float = 1.8

var _base_y: float = 0.0
var _time_passed: float = 0.0
var _is_collected: bool = false

@onready var visual_root: Node3D = get_node_or_null("VisualRoot")
@onready var sfx_collect: AudioStreamPlayer3D = get_node_or_null("AudioStreamPlayer3D")
@onready var particles: GPUParticles3D = get_node_or_null("CollectParticles")

func _ready() -> void:
	_base_y = position.y
	body_entered.connect(_on_body_entered)
	collision_layer = 8   # Layer 4 for collectibles
	collision_mask = 2    # Layer 2 for player

func _process(delta: float) -> void:
	if _is_collected:
		return
	_time_passed += delta
	# Floating bobbing
	position.y = _base_y + sin(_time_passed * bob_speed) * bob_amplitude
	# Continuous rotation
	if visual_root:
		visual_root.rotate_y(rotation_speed * delta)

func _on_body_entered(body: Node3D) -> void:
	if _is_collected:
		return
	if body is CharacterBody3D:
		_collect()

func _collect() -> void:
	_is_collected = true
	collected.emit(self)
	
	if sfx_collect:
		sfx_collect.play()
	if particles:
		particles.emitting = true
		
	# Quick scale-down animation
	if visual_root:
		var tween = create_tween()
		tween.tween_property(visual_root, "scale", Vector3.ZERO, 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	
	# Wait for audio/particles before removing
	await get_tree().create_timer(0.45).timeout
	queue_free()
