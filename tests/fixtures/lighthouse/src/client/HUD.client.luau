local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local humanoid = player.Character.Humanoid

local gui = Instance.new("ScreenGui")
gui.Name = "HUD"
gui.Parent = player.PlayerGui

local label = Instance.new("TextLabel")
label.Size = UDim2.new(0, 250, 0, 40)
label.Position = UDim2.new(0, 10, 0, 10)
label.TextScaled = true
label.Parent = gui

ReplicatedStorage.Remotes.LampChanged.OnClientEvent:Connect(function(fuel)
	label.Text = "Lamp fuel: " .. fuel .. "  |  Health: " .. math.floor(humanoid.Health)
end)
