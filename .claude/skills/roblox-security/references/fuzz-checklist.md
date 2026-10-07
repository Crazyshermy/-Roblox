# Remote abuse checklist

For each client→server remote, decide what the server does in each case below. "Reject" means no state change, no error and no crash.

| Category | Malicious input / sequence |
|---|---|
| Type confusion | string for number, table for string, Instance for number, `nil` everywhere, extra args |
| Numbers | `0/0` (NaN), `math.huge`, `-math.huge`, `-0`, negatives, `2^53`, fractional where integer expected, huge counts |
| Strings | empty, 100k chars, unicode or zero-width chars, names of other players' items |
| Tables | deeply nested, 100k entries, metatables (stripped in transit), mixed array/dict keys, cyclic structures |
| Instances | another player's character or tool, a destroyed instance, an instance not replicated to the server (arrives as `nil`), ServerStorage paths |
| Sequence | claim reward before completing; equip before owning; complete twice; act while dead, ragdolled or in a menu; act during a teleport |
| Timing | spam at 60/s and 500/s; two remotes interleaved to bypass per-remote limits; calls during PlayerRemoving |
| Concurrency | the same action from two clients on one shared object; trade accept plus inventory change in the same frame |
| Spatial | act at distance 10,000; act through walls; teleport-then-act |
| Economy | buy with a negative quantity; sell an item you don't have; integer overflow on stacked multipliers; rapid buy/sell arbitrage |

Server-side oracles to check after each probe: the value totals didn't change, there are no server errors in the console, server frame time didn't spike, and other players' state wasn't touched.
