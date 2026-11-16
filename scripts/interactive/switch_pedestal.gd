class_name SwitchPedestal
extends Interactable

signal switch_activated

@export var is_activated: bool = false
@onready var button_mesh: Node3D = $VisualRoot/PedestalButton if has_node("VisualRoot/PedestalButton") else null
@onready var sfx_switch: AudioStreamPlayer3D = $AudioStreamPlayer3D
@onready var omni_light: OmniLight3D = $OmniLight3D

func _ready() -> void:
	super._ready()
	prompt_message = "Press E to Activate Switch"
	interacted.connect(_on_interacted)

func _on_interacted(_player: CharacterBody3D) -> void:
	if is_activated:
		return
	is_activated = true
	is_interactable = false
	prompt_message = "Activated"
	
	if sfx_switch:
		sfx_switch.play()
		
	# Depress button animation
	if button_mesh:
		var tween = create_tween()
		tween.tween_property(button_mesh, "position:y", button_mesh.position.y - 0.08, 0.2).set_trans(Tween.TRANS_SPRING)
	
	if omni_light:
		omni_light.light_color = Color(1.0, 0.85, 0.2) # Change from cyan to gold
		omni_light.light_energy = 3.0
	
	switch_activated.emit()
