extends SceneTree

func _init() -> void:
	print("=== Running B.O.T Character & Animation Verification Suite ===")
	var player_scene = load("res://scenes/player/player.tscn")
	assert(player_scene != null, "Player scene could not be loaded!")
	var player = player_scene.instantiate() as PlayerController
	root.add_child(player)
	player.set_physics_process(false)
	player._ready()
	
	# 1. Verify Model, Skeleton & Bones
	var skeleton: Skeleton3D = player.find_child("Skeleton3D", true, false)
	assert(skeleton != null, "Skeleton3D not found on B.O.T!")
	print("✓ Skeleton3D detected on B.O.T.")
	
	var expected_bones = [
		"Root", "Torso", "Head",
		"Antenna.L", "Antenna.R",
		"Arm.L", "Hand.L",
		"Arm.R", "Hand.R",
		"Leg.L", "Foot.L",
		"Leg.R", "Foot.R"
	]
	for bone in expected_bones:
		var bone_idx = skeleton.find_bone(bone)
		assert(bone_idx != -1, "Missing expected bone: %s" % bone)
	print("✓ All 13 deformation bones verified in Armature hierarchy: ", expected_bones)
	
	# 2. Verify AnimationPlayer and All 14 Actions
	var anim_player: AnimationPlayer = player.animation_player
	assert(anim_player != null, "AnimationPlayer not found on B.O.T!")
	print("✓ AnimationPlayer detected on B.O.T.")
	
	var required_actions = [
		"Idle", "Idle_Secondary", "Walk", "Run",
		"Jump_Start", "Jump_Loop", "Fall", "Landing",
		"Turn_Left", "Turn_Right", "Collect", "Interact",
		"Victory", "Respawn"
	]
	
	for act in required_actions:
		assert(anim_player.has_animation(act), "Missing required animation action: %s" % act)
	print("✓ All 14 required animation actions present: ", required_actions)
	
	# 3. Verify Animation State System in PlayerController
	assert(player.current_anim_state == PlayerController.AnimState.IDLE, "Initial state should be IDLE!")
	assert(anim_player.current_animation == "Idle", "AnimationPlayer should be playing Idle!")
	print("✓ Initial state correctly initialized to IDLE.")
	
	# 4. Verify Movement State Transitions (Walk & Run)
	player._change_state(PlayerController.AnimState.WALK)
	assert(player.current_anim_state == PlayerController.AnimState.WALK, "State should be WALK!")
	assert(anim_player.current_animation == "Walk", "AnimationPlayer should be playing Walk!")
	print("✓ Walk locomotion state transition verified.")
	
	player._change_state(PlayerController.AnimState.RUN)
	assert(player.current_anim_state == PlayerController.AnimState.RUN, "State should be RUN!")
	assert(anim_player.current_animation == "Run", "AnimationPlayer should be playing Run!")
	print("✓ Run locomotion state transition verified.")
	
	# 5. Verify Airborne & Fall States
	player._change_state(PlayerController.AnimState.JUMP_START)
	assert(player.current_anim_state == PlayerController.AnimState.JUMP_START, "State should be JUMP_START!")
	assert(anim_player.current_animation == "Jump_Start", "Jump_Start animation playing")
	print("✓ Jump_Start takeoff state verified.")

	player._change_state(PlayerController.AnimState.JUMP_LOOP)
	assert(player.current_anim_state == PlayerController.AnimState.JUMP_LOOP, "State should be JUMP_LOOP!")
	assert(anim_player.current_animation == "Jump_Loop" or anim_player.current_animation == "Jump", "Jump loop animation playing in ascent")
	print("✓ Jump_Loop airborne state verified.")
	
	player._change_state(PlayerController.AnimState.FALL)
	assert(player.current_anim_state == PlayerController.AnimState.FALL, "State should be FALL!")
	assert(anim_player.current_animation == "Fall", "Fall animation playing in descent")
	print("✓ Fall airborne state verified.")

	player._change_state(PlayerController.AnimState.LANDING)
	assert(player.current_anim_state == PlayerController.AnimState.LANDING, "State should be LANDING!")
	assert(anim_player.current_animation == "Landing", "Landing animation playing on floor impact")
	print("✓ Landing squash state verified.")
	
	# 6. Verify One-shot Actions: Collect, Interact, Respawn, Victory
	player.play_collect_animation()
	assert(player.current_anim_state == PlayerController.AnimState.COLLECT, "State should be COLLECT!")
	assert(anim_player.current_animation == "Collect", "AnimationPlayer should be playing Collect!")
	print("✓ Collect animation trigger verified.")
	
	player.play_interact_animation()
	assert(player.current_anim_state == PlayerController.AnimState.INTERACT, "State should be INTERACT!")
	assert(anim_player.current_animation == "Interact", "AnimationPlayer should be playing Interact!")
	print("✓ Interact animation trigger verified.")
	
	player._respawn()
	assert(player.current_anim_state == PlayerController.AnimState.RESPAWN, "State should be RESPAWN!")
	assert(anim_player.current_animation == "Respawn", "AnimationPlayer should be playing Respawn!")
	print("✓ Respawn animation trigger verified.")
	
	player.trigger_victory()
	assert(player.current_anim_state == PlayerController.AnimState.VICTORY, "State should be VICTORY!")
	assert(anim_player.current_animation == "Victory", "AnimationPlayer should be playing Victory!")
	print("✓ Victory animation trigger verified.")
	
	print("=== All B.O.T Character & Animation Tests Passed With Flying Colors! ===")
	quit(0)
