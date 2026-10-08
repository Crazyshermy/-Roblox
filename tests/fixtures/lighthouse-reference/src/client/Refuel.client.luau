local ContextActionService = game:GetService("ContextActionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local RefuelLamp = ReplicatedStorage.Remotes.RefuelLamp

-- Only asks to refuel. The server checks range and oil, and decides how much is used.
local function onRefuel(_, inputState)
	if inputState == Enum.UserInputState.Begin then
		RefuelLamp:FireServer()
	end
end

-- E on keyboard, X on gamepad, and an on-screen button on touch devices.
ContextActionService:BindAction("RefuelLamp", onRefuel, true, Enum.KeyCode.E, Enum.KeyCode.ButtonX)
ContextActionService:SetTitle("RefuelLamp", "Refuel")
-- The default spot sits on top of the Jump button on small phones. Measured from the
-- bottom-right corner, this is left of the small Jump button and below the large one.
-- The touch button only exists a moment after BindAction (setting it earlier didn't
-- stick), so wait for it. Desktop has no touch button, so this just gives up.
task.spawn(function()
	for _ = 1, 50 do
		if ContextActionService:GetButton("RefuelLamp") then
			ContextActionService:SetPosition("RefuelLamp", UDim2.new(1, -149, 1, -80))
			return
		end
		task.wait(0.1)
	end
end)
