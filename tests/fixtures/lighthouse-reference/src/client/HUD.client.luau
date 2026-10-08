local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local humanoid = nil -- the current character's Humanoid, replaced on every respawn
local healthChanged = nil
local fuel = "-"

local gui = Instance.new("ScreenGui")
gui.Name = "HUD"
gui.ResetOnSpawn = false -- this script runs once, so the HUD must survive respawns
gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets -- keep clear of notches and the home indicator
gui.Parent = player:WaitForChild("PlayerGui")

local label = Instance.new("TextLabel")
label.Size = UDim2.new(0, 250, 0, 40)
-- Bottom-center: the legacy chat window spans 40%+ of the width at the top-left on
-- small screens, so top-center still overlaps it there. Touch controls sit in the corners.
label.AnchorPoint = Vector2.new(0.5, 1)
label.Position = UDim2.new(0.5, 0, 1, -10)
label.TextScaled = true
label.Parent = gui

local function render()
	local health = if humanoid then math.floor(humanoid.Health) else "-"
	label.Text = "Lamp fuel: " .. fuel .. "  |  Health: " .. health
end

local function onCharacterAdded(character)
	local newHumanoid = character:WaitForChild("Humanoid")
	if player.Character ~= character then
		return
	end
	if healthChanged then
		healthChanged:Disconnect()
	end
	humanoid = newHumanoid
	healthChanged = humanoid.HealthChanged:Connect(render)
	render()
end

player.CharacterAdded:Connect(onCharacterAdded)
if player.Character then
	task.spawn(onCharacterAdded, player.Character)
end

ReplicatedStorage.Remotes.LampChanged.OnClientEvent:Connect(function(newFuel)
	fuel = newFuel
	render()
end)

render()
