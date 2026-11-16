class_name HUD
extends CanvasLayer

signal restart_requested
signal interact_button_pressed

@onready var fragment_label: Label = $TopBar/FragmentBox/FragmentLabel
@onready var objective_label: Label = $TopBar/ObjectiveBox/ObjectiveLabel
@onready var prompt_container: Control = $InteractionPrompt
@onready var prompt_text: Label = $InteractionPrompt/PromptButton/PromptLabel
@onready var prompt_button: Button = $InteractionPrompt/PromptButton
@onready var victory_modal: Control = $VictoryModal
@onready var restart_button: Button = $VictoryModal/Panel/RestartButton
@onready var mobile_controls: Control = $MobileControls
@onready var mobile_jump_btn: Button = $MobileControls/JumpButtonMobile if has_node("MobileControls/JumpButtonMobile") else null

func _ready() -> void:
	prompt_container.visible = false
	victory_modal.visible = false
	
	if prompt_button:
		prompt_button.pressed.connect(_on_prompt_pressed)
	if restart_button:
		restart_button.pressed.connect(_on_restart_pressed)
	if mobile_jump_btn:
		mobile_jump_btn.button_down.connect(func(): Input.action_press("jump"))
		mobile_jump_btn.button_up.connect(func(): Input.action_release("jump"))

func update_fragments(current: int, total: int) -> void:
	if fragment_label:
		fragment_label.text = "⚡ %d / %d" % [current, total]
		# Pop animation on update
		var tween = create_tween()
		tween.tween_property(fragment_label, "scale", Vector2(1.2, 1.2), 0.1).set_trans(Tween.TRANS_BACK)
		tween.tween_property(fragment_label, "scale", Vector2.ONE, 0.1)

func update_objective(text: String) -> void:
	if objective_label:
		objective_label.text = text

func show_interaction_prompt(message: String) -> void:
	if prompt_container and prompt_text:
		prompt_text.text = message
		prompt_container.visible = true

func hide_interaction_prompt() -> void:
	if prompt_container:
		prompt_container.visible = false

func show_victory() -> void:
	if victory_modal:
		victory_modal.visible = true
		victory_modal.modulate = Color(1, 1, 1, 0)
		var tween = create_tween()
		tween.tween_property(victory_modal, "modulate:a", 1.0, 0.4)

func _on_prompt_pressed() -> void:
	interact_button_pressed.emit()
	Input.action_press("interact")
	await get_tree().create_timer(0.05).timeout
	Input.action_release("interact")

func _on_restart_pressed() -> void:
	restart_requested.emit()
