class_name EnergyBridge
extends Node3D

signal bridge_fully_extended

@export var extend_delay_per_step: float = 0.15
@onready var sfx_bridge: AudioStreamPlayer3D = $AudioStreamPlayer3D

var _steps: Array[AnimatableBody3D] = []
var _is_extended: bool = false

func _ready() -> void:
	for child in get_children():
		if child is AnimatableBody3D:
			_steps.append(child)
			# Initially disable collision and scale down (using 0.001 to prevent singular transform determinant)
			child.scale = Vector3(0.001, 0.001, 0.001)
			var col = child.get_node_or_null("CollisionShape3D")
			if col:
				col.disabled = true

func activate() -> void:
	if _is_extended:
		return
	_is_extended = true
	
	if sfx_bridge:
		sfx_bridge.play()
		
	for i in range(_steps.size()):
		var step = _steps[i]
		var delay = i * extend_delay_per_step
		var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tween.tween_interval(delay)
		tween.tween_property(step, "scale", Vector3.ONE, 0.35)
		
		# Enable collision after tween starts
		get_tree().create_timer(delay + 0.1).timeout.connect(func():
			var col = step.get_node_or_null("CollisionShape3D")
			if col:
				col.disabled = false
		)
		
	var total_time = _steps.size() * extend_delay_per_step + 0.4
	await get_tree().create_timer(total_time).timeout
	bridge_fully_extended.emit()
