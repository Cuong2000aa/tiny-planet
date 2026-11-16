class_name GameManager
extends Node

@export var total_fragments: int = 3
@export var player: PlayerController
@export var hud: HUD
@export var switch_pedestal: SwitchPedestal
@export var energy_bridge: EnergyBridge
@export var exit_portal: ExitPortal

var collected_fragments: int = 0
var is_switch_on: bool = false
var is_game_won: bool = false

func _ready() -> void:
	if hud:
		hud.update_fragments(collected_fragments, total_fragments)
		hud.update_objective("Explore the floating island & collect 3 Energy Fragments")
		hud.restart_requested.connect(_on_restart_requested)

	if player:
		player.interaction_target_changed.connect(_on_player_target_changed)

	if switch_pedestal:
		switch_pedestal.switch_activated.connect(_on_switch_activated)

	if energy_bridge:
		energy_bridge.bridge_fully_extended.connect(_on_bridge_extended)

	if exit_portal:
		exit_portal.portal_entered.connect(_on_portal_entered)

	# Find and connect all fragments in the scene
	var fragments = get_tree().get_nodes_in_group("energy_fragments")
	if fragments.is_empty() and has_node("../Collectibles"):
		for child in get_node("../Collectibles").get_children():
			if child is EnergyFragment:
				fragments.append(child)

	total_fragments = fragments.size()
	if hud:
		hud.update_fragments(collected_fragments, total_fragments)
	for f in fragments:
		if f is EnergyFragment:
			if not f.collected.is_connected(_on_fragment_collected):
				f.collected.connect(_on_fragment_collected)

func _on_fragment_collected(_frag: EnergyFragment) -> void:
	collected_fragments += 1
	if hud:
		hud.update_fragments(collected_fragments, total_fragments)
		
	if collected_fragments >= total_fragments:
		if not is_switch_on:
			if hud:
				hud.update_objective("All fragments collected! Activate the Ancient Switch.")
	else:
		if hud:
			hud.update_objective("Collect Energy Fragments: %d left" % (total_fragments - collected_fragments))

func _on_switch_activated() -> void:
	is_switch_on = true
	if hud:
		hud.update_objective("Energy surging! The bridge is activating...")
	if energy_bridge:
		energy_bridge.activate()

func _on_bridge_extended() -> void:
	if exit_portal:
		exit_portal.unlock()
	if hud:
		hud.update_objective("Bridge formed! Enter the Portal to restore the island.")

func _on_portal_entered() -> void:
	if is_game_won:
		return
	is_game_won = true
	if player:
		player.trigger_victory()
	if hud:
		hud.update_objective("🌟 ISLAND RESTORED!")
		hud.show_victory()

func _on_player_target_changed(target: Interactable) -> void:
	if not hud:
		return
	if target and target.is_interactable:
		hud.show_interaction_prompt(target.prompt_message)
	else:
		hud.hide_interaction_prompt()

func _on_restart_requested() -> void:
	get_tree().reload_current_scene()
