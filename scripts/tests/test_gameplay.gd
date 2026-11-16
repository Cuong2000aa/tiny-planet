extends SceneTree

func _initialize() -> void:
	print("=== Running Tiny Planet Automated Gameplay Verification Test ===")
	_run_tests()

func _run_tests() -> void:
	var main_scene = load("res://scenes/levels/awakening_island.tscn")
	assert(main_scene != null, "Main level scene could not be loaded!")
	var level = main_scene.instantiate()
	root.add_child(level)
	
	# Wait for idle frame so _ready() runs on all nodes
	await process_frame
	
	print("✓ Main level scene instantiated and _ready completed.")
	
	# Verify Player
	var player = level.get_node("Player") as PlayerController
	assert(player != null, "PlayerController not found!")
	print("✓ PlayerController verified at position: ", player.global_position)
	
	# Verify Collectibles
	var fragments_container = level.get_node("Collectibles")
	var fragments = fragments_container.get_children()
	assert(fragments.size() == 3, "Expected 3 energy fragments, found: %d" % fragments.size())
	print("✓ 3 Energy Fragments verified in scene.")
	
	# Verify Interactive elements
	var switch = level.get_node("Interactive/SwitchPedestal") as SwitchPedestal
	assert(switch != null, "SwitchPedestal not found!")
	var bridge = level.get_node("Interactive/EnergyBridge") as EnergyBridge
	assert(bridge != null, "EnergyBridge not found!")
	var portal = level.get_node("Interactive/ExitPortal") as ExitPortal
	assert(portal != null, "ExitPortal not found!")
	print("✓ Interactive elements (Switch, Bridge, Portal) verified.")
	
	# Verify HUD
	var hud = level.get_node("HUD") as HUD
	assert(hud != null, "HUD not found!")
	print("✓ HUD verified.")
	
	# Verify GameManager
	var gm = level.get_node("GameManager") as GameManager
	assert(gm != null, "GameManager not found!")
	assert(gm.total_fragments == 3, "GameManager total_fragments should be 3, was %d" % gm.total_fragments)
	
	# Simulate fragment collection
	print("Simulating fragment collection...")
	for f in fragments:
		if f is EnergyFragment:
			f._collect()
	
	assert(gm.collected_fragments == 3, "GameManager did not register 3 fragments! Got: %d" % gm.collected_fragments)
	print("✓ All 3 Energy Fragments collected successfully.")
	
	# Simulate switch interaction
	print("Simulating switch activation...")
	switch._on_interacted(player)
	assert(switch.is_activated == true, "Switch should be activated!")
	assert(gm.is_switch_on == true, "GameManager should register switch active!")
	print("✓ Switch mechanism activated successfully.")
	
	# Verify bridge activation
	print("Simulating bridge activation...")
	bridge.activate()
	print("✓ Bridge activation initiated.")
	
	# Unlock portal & victory simulation
	print("Simulating portal unlock & level completion...")
	portal.unlock()
	assert(portal.is_unlocked == true, "Portal should be unlocked!")
	portal._on_body_entered(player)
	assert(gm.is_game_won == true, "Game should register level won!")
	print("✓ Victory sequence triggered successfully.")
	
	print("=== All Automated Gameplay Tests Passed Perfectly! ===")
	quit(0)
