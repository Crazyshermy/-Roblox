local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Config = require(ReplicatedStorage.Shared.Config)
local LampService = require(script.Parent.LampService)

local RefuelLamp = ReplicatedStorage.Remotes.RefuelLamp

local OilService = {}

local function setupCan(can)
	local available = true
	can.Touched:Connect(function(hit)
		if not available then return end
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if not player then return end
		available = false
		can.Transparency = 1
		player.leaderstats.Oil.Value += Config.OilPerCan
		task.wait(Config.CanRespawnSeconds)
		can.Transparency = 0
		available = true
	end)
end

function OilService.start()
	for _, can in workspace.OilCans:GetChildren() do
		setupCan(can)
	end

	RefuelLamp.OnServerEvent:Connect(function(player, amount)
		player.leaderstats.Oil.Value -= amount
		LampService.addFuel(amount)
	end)
end

return OilService
