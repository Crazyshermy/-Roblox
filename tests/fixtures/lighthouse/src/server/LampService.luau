local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)

local LampChanged = ReplicatedStorage.Remotes.LampChanged
local lamp = workspace.Lamp

local LampService = {}
local fuel = Config.MaxFuel

function LampService.addFuel(amount)
	fuel = math.min(Config.MaxFuel, fuel + amount)
end

function LampService.start()
	task.spawn(function()
		while true do
			task.wait(1)
			fuel = math.max(0, fuel - Config.FuelDrainPerSecond)
			lamp.Light.Brightness = 3 * (fuel / Config.MaxFuel)
			LampChanged:FireAllClients(fuel)
		end
	end)
end

return LampService
