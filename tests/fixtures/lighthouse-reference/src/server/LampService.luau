local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)

local LampChanged = ReplicatedStorage.Remotes.LampChanged
local lamp = workspace.Lamp

local LampService = {}
local fuel = Config.MaxFuel

-- Must match Lamp.Light.Brightness in default.project.json. Above ~1 the light
-- blows the baseplate out to pure white and the dimming can't be seen.
local MAX_BRIGHTNESS = 1

local function update()
	lamp.Light.Brightness = MAX_BRIGHTNESS * (fuel / Config.MaxFuel)
	-- Neon glows by itself, so without this the lamp never looks dark.
	lamp.Material = if fuel > 0 then Enum.Material.Neon else Enum.Material.SmoothPlastic
	LampChanged:FireAllClients(fuel)
end

-- Adds up to `amount` fuel without overfilling. Returns how much was actually used.
function LampService.addFuel(amount)
	local added = math.max(0, math.min(amount, Config.MaxFuel - fuel))
	if added > 0 then
		fuel += added
		update()
	end
	return added
end

function LampService.start()
	task.spawn(function()
		while true do
			task.wait(1)
			fuel = math.max(0, fuel - Config.FuelDrainPerSecond)
			update()
		end
	end)
end

return LampService
