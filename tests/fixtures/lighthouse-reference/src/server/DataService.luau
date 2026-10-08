local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local Config = require(game.ReplicatedStorage.Shared.Config)

-- GetDataStore errors in an unpublished place (or with Studio API access off).
-- The game still runs then, it just doesn't save.
local storeOk, store = pcall(function()
	return DataStoreService:GetDataStore("PlayerData")
end)
if not storeOk then
	warn("DataService: saving disabled, DataStores unavailable:", store)
	store = nil
end

local DataService = {}

-- Only players whose data loaded get saved, so a failed load can never
-- overwrite real progress with 0.
local canSave = {}
local savesInFlight = 0

local function load(player)
	if not store then
		return false
	end
	for attempt = 1, 3 do
		local ok, data = pcall(function()
			return store:GetAsync(Config.SaveKeyPrefix .. player.UserId)
		end)
		if ok then
			return true, data
		end
		warn("DataService: load failed for", player.Name, data)
		if attempt < 3 then
			task.wait(attempt * 2)
		end
	end
	return false
end

local function onPlayerAdded(player)
	local loaded, data = load(player)
	if player.Parent ~= Players then
		return -- left while loading
	end

	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"

	local oil = Instance.new("IntValue")
	oil.Name = "Oil"
	oil.Parent = leaderstats

	if loaded and typeof(data) == "table" and typeof(data.Oil) == "number" then
		oil.Value = math.max(0, data.Oil)
	end
	canSave[player] = loaded or nil

	-- Parented last: other scripts treat leaderstats existing as "data is ready".
	leaderstats.Parent = player
end

-- One final save per player, on leave or shutdown, whichever comes first.
local function save(player)
	local allowed = canSave[player]
	canSave[player] = nil
	local leaderstats = player:FindFirstChild("leaderstats")
	if not allowed or not leaderstats then
		return
	end

	local oil = leaderstats.Oil.Value
	savesInFlight += 1
	local ok, err = pcall(function()
		store:UpdateAsync(Config.SaveKeyPrefix .. player.UserId, function(old)
			local data = if typeof(old) == "table" then old else {}
			data.Oil = oil
			return data
		end)
	end)
	savesInFlight -= 1
	if not ok then
		warn("DataService: save failed for", player.Name, err)
	end
end

function DataService.start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	Players.PlayerRemoving:Connect(save)
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end

	game:BindToClose(function()
		for _, player in Players:GetPlayers() do
			task.spawn(save, player)
		end
		while savesInFlight > 0 do
			task.wait()
		end
	end)
end

return DataService
