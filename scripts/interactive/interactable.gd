class_name Interactable
extends Area3D

signal interacted(player: CharacterBody3D)
signal focused(player: CharacterBody3D)
signal unfocused(player: CharacterBody3D)

@export var prompt_message: String = "Press E to Interact"
@export var is_interactable: bool = true

func _ready() -> void:
	collision_layer = 4  # Layer 3 for interactables
	collision_mask = 2   # Player layer

func can_interact(_player: CharacterBody3D) -> bool:
	return is_interactable

func interact(player: CharacterBody3D) -> void:
	if is_interactable:
		interacted.emit(player)
