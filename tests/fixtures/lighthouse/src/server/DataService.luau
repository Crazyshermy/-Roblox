local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local Config = require(game.ReplicatedStorage.Shared.Config)

local store = DataStoreService:GetDataStore("PlayerData")

local DataService = {}

local function onPlayerAdded(player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	leaderstats.Parent = player

	local oil = Instance.new("IntValue")
	oil.Name = "Oil"
	oil.Parent = leaderstats

	local ok, data = pcall(function()
		return store:GetAsync(Config.SaveKeyPrefix .. player.UserId)
	end)
	if ok and data then
		oil.Value = data.Oil
	else
		oil.Value = 0
	end
end

local function onPlayerRemoving(player)
	local leaderstats = player:FindFirstChild("leaderstats")
	if leaderstats then
		pcall(function()
			store:SetAsync(Config.SaveKeyPrefix .. player.UserId, { Oil = leaderstats.Oil.Value })
		end)
	end
end

function DataService.start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	Players.PlayerRemoving:Connect(onPlayerRemoving)
end

return DataService
