# Economy design

1. **Purpose per currency.** One sentence each: what decision does it create? If two currencies create the same decision, merge them.
2. **Source/sink table.** List every faucet (rate per hour for a typical player) and every sink (one-time and repeatable). Repeatable sinks are what keep late-game currency meaningful.
3. **Time model.** Simulate on paper: currency held at hour 1, day 1, day 7 and day 30 for casual and dedicated players. Find where prices become trivial or impossible.
4. **Inflation controls.** Consumables, upkeep, crafting losses, cosmetic prestige sinks, trade taxes, soft caps and diminishing returns on AFK sources.
5. **Trading economies** add arbitrage, scams, duplication incentives and real-money trading pressure. Only add trading if player-to-player exchange serves the fantasy, and then involve `roblox-security` and `roblox-data`.
6. **Monetization fit.** Prefer purchases that add expression, convenience without breaking competitive fairness, or access to content. Paid random items have policy restrictions in some regions (`PolicyService`). Design for a young audience ethically: no deceptive scarcity and no pay-to-skip of artificially painful grinds.
7. **Tuning.** Put prices and rates in config (not hardcoded), and instrument sources and sinks (`AnalyticsService` economy events) so you can see the real flow.
