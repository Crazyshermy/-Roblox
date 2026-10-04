---
name: roblox-ui-ux
description: "Roblox UI/UX: onboarding, information hierarchy, HUD, menus and shops, prompts, mobile touch layout and safe areas, controller navigation, Input Action System, accessibility, readability, localization, UI implementation and performance."
---

# UI / UX

Players don't read; they scan, tap, and leave. Every element must earn its screen space, especially on a phone.

## Information hierarchy
1. What must the player know **right now** (threat, objective, health)? → always visible, high contrast.
2. What do they need **often** (currency, ability cooldowns)? → peripheral, compact.
3. Everything else → on demand (menus), or diegetic (in the world).
Prefer **diegetic/in-world** feedback (prompts on objects, world-space markers via `BillboardGui`, lighting cues) over HUD clutter. Remove UI that doesn't change decisions.

## Mobile first (majority of Roblox sessions are on phones — E3)
- Touch targets ≥ ~44–48 px equivalent; keep critical buttons in thumb zones (bottom corners), away from the default jump/thumbstick areas.
- Respect safe areas/notches. `ScreenGui.ScreenInsets` takes `Enum.ScreenInsets.None` / `DeviceSafeInsets` / `CoreUISafeInsets` / `TopbarSafeInsets` (E4, exact names), plus `SafeAreaCompatibility`; test the smallest phone preset in the Device Emulator.
- Text: minimum readable size on phone at actual scale; use `TextScaled` sparingly (inconsistent sizes) — prefer fixed sizes with `UIScale`/`UITextSizeConstraint`.
- Layout: Scale-based sizing + `UIAspectRatioConstraint`; `UIListLayout`/`UIGridLayout` (flex options) for lists; avoid pixel-absolute layouts that break across resolutions.

## Input across devices
- Use the **Input Action System** (`InputContext`/`InputAction`/`InputBinding`, full release 2026) or `ContextActionService` for actions so keyboard, touch and gamepad bind to one action; offer on-screen touch buttons for actions that have keys.
- Gamepad: every menu navigable by selection (`GuiService.SelectedObject`, `NextSelection*`), visible focus state, B/back always closes.
- Show device-appropriate prompts (key vs button glyph) — `UserInputService:GetLastInputType()` / `LastInputTypeChanged`.

## Onboarding UX
First 60 seconds: one goal, one action, immediate feedback. Teach with contextual prompts at the moment of need, not a wall of text. Delay shops, settings and secondary currencies until after the first fun. Tooltips must be dismissible and not repeat forever.

## Menus and shops
Two taps to anything important. Clear purchase confirmation with exact cost and what you get; never trick taps (no buy button where close used to be). Show *why* something is locked and how to unlock it.

## Accessibility
Don't encode meaning in color alone (add icon/shape); colorblind-safe palette for gameplay signals; subtitles/captions for audio-critical games (horror cues!); reduced-motion option for camera shake/flashes; adjustable sensitivity; avoid rapid flashing.

## Implementation notes
- Build UI from reusable components (a button module with press feedback + sound); keep state → view one-directional (a declarative library like React-lua/Fusion if the project uses one; otherwise a small render function per state).
- Performance: don't rebuild lists every frame; pool list items; avoid hundreds of live `TextLabel`s; disable invisible UI (`Enabled=false`).
- Localization: leave 30–40% text expansion room; use `LocalizationService` keys if localizing.
- Server never trusts UI state (see `roblox-security`).

## Verify
Device Emulator: smallest phone, tablet, 1080p desktop, console (10-ft). Screenshot each. Navigate every flow with touch only and gamepad only. Report what was checked.
