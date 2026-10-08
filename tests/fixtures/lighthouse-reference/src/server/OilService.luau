local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Config = require(ReplicatedStorage.Shared.Config)
local LampService = require(script.Parent.LampService)

local RefuelLamp = ReplicatedStorage.Remotes.RefuelLamp
local lamp = workspace.Lamp

local OilService = {}
local lastRefuel = {}

local function setupCan(can)
	local available = true
	can.Touched:Connect(function(hit)
		if not available then return end
		local character = hit.Parent
		local player = Players:GetPlayerFromCharacter(character)
		if not player then return end
		-- leaderstats only exists once the player's data has loaded.
		local leaderstats = player:FindFirstChild("leaderstats")
		if not leaderstats then return end
		-- The owning client reports touches on its character, so check them against the
		-- server's view: a living character whose root is actually near the can.
		-- Written as `not (<=)` so a NaN position is rejected too.
		local humanoid = character:FindFirstChildOfClass("Humanoid")
		local root = character:FindFirstChild("HumanoidRootPart")
		if not (humanoid and root) or humanoid.Health <= 0 then return end
		if not ((root.Position - can.Position).Magnitude <= Config.PickupRange) then return end
		available = false
		can.Transparency = 1
		can.CanCollide = false
		leaderstats.Oil.Value += Config.OilPerCan
		task.wait(Config.CanRespawnSeconds)
		can.Transparency = 0
		can.CanCollide = true
		available = true
	end)
end

-- The client only asks to refuel. The server decides whether it can and how much oil is used.
local function onRefuel(player, ...)
	if select("#", ...) ~= 0 then return end

	local now = os.clock()
	if now - (lastRefuel[player] or 0) < Config.RefuelCooldownSeconds then return end
	lastRefuel[player] = now

	local leaderstats = player:FindFirstChild("leaderstats")
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not (leaderstats and humanoid and root) or humanoid.Health <= 0 then return end

	-- Must be near the lamp, measured along the ground since the lamp sits up high.
	-- Written as `not (<=)` so a NaN position is rejected too.
	local offset = root.Position - lamp.Position
	if not (Vector3.new(offset.X, 0, offset.Z).Magnitude <= Config.RefuelRange) then return end

	local oil = leaderstats.Oil
	if oil.Value <= 0 then return end
	-- Only use as much oil as the lamp has room for. No yields between check and write.
	oil.Value -= LampService.addFuel(oil.Value)
end

function OilService.start()
	for _, can in workspace.OilCans:GetChildren() do
		setupCan(can)
	end

	RefuelLamp.OnServerEvent:Connect(onRefuel)
	Players.PlayerRemoving:Connect(function(player)
		lastRefuel[player] = nil
	end)
end

return OilService
