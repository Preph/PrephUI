# Contributing to PrephUI

Thanks for wanting to contribute to **PrephUI**! We're trying to keep the addon reliable, light on resources, and easy to maintain across **World of Warcraft Midnight (12.1+) and WoW Forever**.

Please skim the guidelines below before you open a pull request. They aren't arbitrary: they're the result of how the project is built and the trade-offs we've settled on. Following them saves everyone a review round or two.

## Reuse what's already there

Before you build something new, check whether PrephUI already does it. If a helper, cache, or piece of UI behavior could be useful to more than one module, it belongs in the core. If a shared system almost does what you need, extend it rather than writing a parallel version next to it.

Good places to start looking:

- **Aura handling:** `PrephUI/Core/AuraSystem.lua`, exposed as `PrephUI.AuraSys`. Every aura display must use `PrephUI.AuraSystem` as its container system.
- **Borders and glows:** `PrephUI/Core/BorderGlows.lua` and `PrephUI/Core/Borders.lua`.
- **Shared UI elements:** `PrephUI/Libs/LibPrephSettingsBuilder/UIElements.lua`.
- **Settings and system integration:** `PrephUI/Libs/LibPrephSettingsBuilder/Settings.lua` and `PrephUI/Core/SystemsBridge.lua`.
- **Profiling:** the module's own `Profiler.lua`, or the shared `PrephUI/Core/Profiling.lua`.
- **Engine and events:** `PrephUI/Core/Engine.lua` for core behavior like profiles and pixel rounding, and `PrephUI/Core/EngineEvents.lua` for event handling.
- **Edit Mode and layout:** `PrephUI/Core/EditMode.lua`, `OverrideEditmode.lua`, and `PrephUI/Core/LayoutSetup.lua`.
- **Cached data:** `PrephUI/Util/cacheData.lua` for anything you'd otherwise end up querying over and over.
- **Version helpers:** `PrephUI/Util/versionUtil.lua`, available as `PrephUI.Version`.

## A disabled feature should cost nothing

If a user has a setting turned off, it shouldn't touch their performance at all. Until the feature is enabled, it must not register events, install active hooks, create frames, or start any `OnUpdate` work.

Set up feature-specific resources lazily, the first time the feature is actually enabled. On login, check whether the feature is enabled and skip registration entirely if it isn't.

## Opt-in by default

New settings default to **OFF**. An update shouldn't change how the addon looks or behaves for existing users unless they choose to turn something on. The only exception is a verified bug fix.

## Keep enabled features lightweight

Even when a feature is on, it should stay cheap:

- **Prefer events over polling.** Don't add your own `OnUpdate` loops. If you really can't avoid polling, use the core's queue, and ideally find a way around it first.
- **If you do need to poll,** go through the core `OnUpdate` queue with `PrephUI:RegisterOnUpdate(fn, metadata)` and `PrephUI:UnregisterOnUpdate(fn)`. Give users a configurable threshold and debounce the work. The core queue returns the metadata you pass in.
- **Don't allocate tables every frame** in code that runs often.
- **Keep loops tight.** Localize values before using them inside a loop where it makes sense.

## Treat secret values carefully

Secret values are off limits for comparisons, table indices, and arithmetic. This covers protected combat aura and unit data in the 12.x API. Pass them straight to native widget APIs that accept them and nothing else.

This one can't be caught automatically, so reviewers will check it by hand. Please double-check your own code before submitting.

## Follow the Midnight API model

PrephUI targets the **World of Warcraft 12.1+ API**, including its restrictions around secret values and related data paths.

We keep a single, unified codebase. Don't add version checks beyond the existing `Engine.Version.isForever` check for WoW Forever. Retail is the baseline.

## Stay within Lua compiler limits

Every Lua file has to compile under **Lua 5.1**. Keep each function under **200 local variables** and **60 upvalues**. Go over either limit and the whole file fails to load, so this is worth watching in large modules.

## Defer combat-locked work through the engine

Don't register `PLAYER_REGEN_ENABLED` yourself to run deferred tasks. Use the engine helper instead:

```lua
PrephUI.Engine.DereferForAfterCombat(key, fn)
```

## Avoid deprecated Blizzard globals

Please don't use deprecated globals such as `GetSpecialization`, `GetSpecializationInfo`, `GetItemInfo`, `GetItemInfoInstant`, or `GetItemQualityColor`. Use the namespaced equivalents on supported clients, such as `C_SpecializationInfo.*` and `C_Item.*`.

## Hook securely and respect protected frames

Never modify protected Blizzard frames or call protected functions from an insecure context, especially in combat. Use `hooksecurefunc` where it fits, and keep hooks limited to cosmetic styling.

Like the secret-value rule, this needs manual review, so take a second look at anything that touches Blizzard frames.

## Include profiling data if you can

If you're able to, attach profiling results to your pull request. Numbers help reviewers see the real performance impact of a change, and they make it much easier to say yes.

---

These conventions keep PrephUI consistent, safe, and fast as it grows. Thanks for helping make it better!
