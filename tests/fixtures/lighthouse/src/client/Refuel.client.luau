local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local RefuelLamp = ReplicatedStorage.Remotes.RefuelLamp

UserInputService.InputBegan:Connect(function(input, processed)
	if processed then return end
	if input.KeyCode == Enum.KeyCode.E then
		local oil = player.leaderstats.Oil.Value
		if oil > 0 then
			RefuelLamp:FireServer(oil)
		end
	end
end)
