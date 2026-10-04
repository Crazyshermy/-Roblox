# Monetization and live ops

Read this when adding purchases, deciding what to sell, or instrumenting and tuning a live game. Purchase *safety* (receipts, grants) belongs to the data and security skills. This file covers design and tooling. APIs verified against creator-docs, 2026-10 (E4).

## What to sell (design first)
| Product | Fits | API |
|---|---|---|
| **Game pass** (one-time, permanent) | permanent unlocks: a cosmetic set, a convenience, an extra slot, a mode | `MarketplaceService:PromptGamePassPurchase`, check with `UserOwnsGamePassAsync` (cache per session) plus `PromptGamePassPurchaseFinished` |
| **Developer product** (repeatable) | consumables, currency packs, revives | `PromptProductPurchase` → grant **only** in `ProcessReceipt` (see the data skill) |
| **Subscription** (recurring) | ongoing benefits (monthly cosmetics, a VIP lounge) | `PromptSubscriptionPurchase`, check with `GetUserSubscriptionStatusAsync` |

- Sell **expression, convenience and access**. Don't sell competitive power in competitive modes. Never sell relief from pain you designed in (artificial grind or waits). Paid random items need a `PolicyService` check and are restricted in some regions. Young audience means no fake scarcity, no confusing currency conversions, and clear prices.
- Make it fantasy-specific. "Lighthouse keeper's brass lantern skin" beats "VIP pass 2x".
- Show prices from `GetProductInfoAsync`, not hardcoded numbers.

## Instrument (`AnalyticsService`)
- **Funnels:** `LogOnboardingFunnelStepEvent` for the first session, `LogFunnelStepEvent` for shops and quests. Find where players drop.
- **Economy:** `LogEconomyEvent` for every source and sink, so you can see inflation and which sinks are actually used.
- **Progression:** `LogProgressionStartEvent`, `LogProgressionCompleteEvent` and `LogProgressionFailEvent` for levels and attempts. Use `LogCustomEvent` for the rest.
- Decide the 3–5 questions you need answered *before* instrumenting. Logging everything answers nothing.

## Tune live (`ConfigService`)
- Put tunables (prices, rates, drop odds, difficulty) in experience configs. Read them with `ConfigService:GetConfigAsync()` → `ConfigSnapshot:GetValue(key)`, and react to `UpdateAvailable` / `Refresh()` for live changes without a republish.
- Configs double as **kill switches** for risky features, and as the basis for A/B experiments.
- Keep code defaults for every key. Never put secrets in configs.

## Release hygiene
Test purchases in Studio test mode first. Keep a rollback plan (republish the previous place version, or flip a config). After an update, compare per-version performance and funnels before and after.
