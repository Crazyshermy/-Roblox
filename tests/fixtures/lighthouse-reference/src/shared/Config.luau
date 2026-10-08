-- Tunable values shared by server and client.
return {
	MaxFuel = 100,
	FuelDrainPerSecond = 1,
	OilPerCan = 10,
	CanRespawnSeconds = 20,
	SaveKeyPrefix = "player_",
	RefuelRange = 20, -- studs from the lamp, measured along the ground
	RefuelCooldownSeconds = 0.5,
	PickupRange = 10, -- studs from a can to the character's root (server view); slack for latency
}
