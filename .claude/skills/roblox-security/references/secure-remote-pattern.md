# Validated remote skeleton

A pattern, not a library. Adapt it to the project's existing networking layer. If the project already uses one (a typed wrapper, a Packet/Net library), extend that instead of adding a second one.

```lua
--!strict
-- ServerScriptService/Services/ShopService (illustrative)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catalog = require(ReplicatedStorage.Shared.Catalog) -- static data, safe to replicate
local Inventory = require(script.Parent.Inventory)          -- the ONLY writer of inventory/currency

local BuyRequest: RemoteEvent = ReplicatedStorage.Remotes.BuyRequest

-- per-player token bucket
local RATE, BURST = 4, 6 -- per second / burst
local buckets: {[Player]: {tokens: number, t: number}} = {}
local busy: {[Player]: boolean} = {}

local function allow(player: Player): boolean
	local now = os.clock()
	local b = buckets[player]
	if not b then b = {tokens = BURST, t = now}; buckets[player] = b end
	b.tokens = math.min(BURST, b.tokens + (now - b.t) * RATE)
	b.t = now
	if b.tokens < 1 then return false end
	b.tokens -= 1
	return true
end

local function isPositiveInt(n: unknown, max: number): boolean
	return typeof(n) == "number" and n == n and n >= 1 and n <= max and n % 1 == 0
end

BuyRequest.OnServerEvent:Connect(function(player: Player, itemId: unknown, quantity: unknown)
	if not allow(player) then return end
	if typeof(itemId) ~= "string" or #itemId > 64 then return end
	if not isPositiveInt(quantity, 99) then return end
	local item = Catalog[itemId]
	if not item or not item.purchasable then return end
	if busy[player] then return end
	busy[player] = true
	-- check + mutate happen inside Inventory without yielding between them
	local ok, reason = Inventory.tryPurchase(player, item, quantity :: number)
	busy[player] = nil
	if not ok then
		-- optional: tell the client why, for UX; never trust the client to enforce it
	end
end)

Players.PlayerRemoving:Connect(function(p) buckets[p] = nil; busy[p] = nil end)
```

Things to notice: price comes from the server catalog, never from arguments. Quantity is bounded and must be an integer. NaN is rejected by `n == n`. The busy flag blocks interleaving. Cleanup on leave prevents leaks.
