# Contributing to PrephUI

Thanks for considering a contribution to **PrephUI**. The goal is to keep the addon reliable, efficient, and straightforward to maintain across **World of Warcraft Midnight (12.1+) and WoW Forever**.

Before opening a pull request, please read through the conventions below. They reflect how the project is structured and the trade-offs we make when adding or changing features.

## Reuse the existing systems

Check whether PrephUI already provides the functionality you need before building something new. Shared helpers, caches, and UI behavior should live in the core when they can benefit more than one module or improve the wider interface.

Useful starting points:

- **Aura handling:** `PrephUI/Core/AuraSystem.lua`, exposed through `PrephUI.AuraSys`. All aura displays must use `PrephUI.AuraSystem` as their container system.
- **Borders and glow effects:** `PrephUI/Core/BorderGlows.lua` and `PrephUI/Core/Borders.lua`.
- **Shared UI elements:** `PrephUI/Libs/LibPrephSettingsBuilder/UIElements.lua`.
- **Settings and system integration:** `PrephUI/Libs/LibPrephSettingsBuilder/Settings.lua` and `PrephUI/Core/SystemsBridge.lua`.
- **Profiling:** a module's own `Profiler.lua`, or the shared `PrephUI/Core/Profiling.lua`.
- **Engine and events:** `PrephUI/Core/Engine.lua` for core behavior such as profiles and pixel rounding; `PrephUI/Core/EngineEvents.lua` for event handling.
- **Edit Mode and layout setup:** `PrephUI/Core/EditMode.lua`, `OverrideEditmode.lua`, and `PrephUI/Core/LayoutSetup.lua`.
- **Cached data:** `PrephUI/Util/cacheData.lua` for information that does not need to be queried repeatedly.
- **Version helpers:** `PrephUI/Util/versionUtil.lua`, available through `PrephUI.Version`.

If a capability belongs in a shared system, extend that system rather than creating a separate implementation.

## Disabled features must be free of cost

A setting that is turned off should not cost users performance. Until the user enables a feature, it must not register events, install active hooks, create frames, or start `OnUpdate` work.

Initialize feature-specific resources lazily, when the feature is first enabled. Check enabled states on logins and skip registration alltogether if disabled.

## Make opt-in the default

New settings must default to **OFF**. An update must not introduce a new visible or functional change for existing users unless they explicitly enable it. Verified bug fixes are the only exception to this rule.

## Keep enabled features lightweight

Features should remain efficient even when active:

- Prefer event-driven updates. Do not add feature-owned `OnUpdate` polling but use the core's polling mechanism - but ideally even try to avoid this.
- If polling is genuinely needed, use the core `OnUpdate` queue, with a user-configurable threshold and debouncing: `PrephUI:RegisterOnUpdate(fn, metadata)` and `PrephUI:UnregisterOnUpdate(fn)`. The metadata is returned by the core queue.
- Avoid allocating tables every frame in frequently executed code.
- Keep loops small and efficient. Localize values before using them inside loops where appropriate.

## Handle secret values safely

Do not compare secret values, use them as table indices, or perform arithmetic on them. This includes protected combat aura and unit data in the 12.x API. Pass these values directly to native widget APIs that support them. This requirement needs manual review.

### Follow the Midnight API model

PrephUI targets the **World of Warcraft 12.1+ API**, including its restrictions around secret values and related data paths.

Keep the codebase unified. Do not add version checks beyond the existing `Engine.Version.isForever` check used for WoW Forever; Retail is the baseline.

---

### Stay within Lua compiler limits

Every Lua file must compile under **Lua 5.1**. Keep functions below **200 local variables** and **60 upvalues**; exceeding these limits will prevent the file from working entirely.

### Defer combat-locked work through the engine

Do not register `PLAYER_REGEN_ENABLED` directly to run deferred tasks. Use the engine helper instead:

`PrephUI.Engine.DereferForAfterCombat(key, fn)`

### Avoid deprecated Blizzard globals

Do not use deprecated global functions such as `GetSpecialization`, `GetSpecializationInfo`, `GetItemInfo`, `GetItemInfoInstant`, or `GetItemQualityColor`. On supported clients, use the corresponding namespaced APIs, including `C_SpecializationInfo.*` and `C_Item.*`.

### Hook securely and respect protected frames

Never modify protected Blizzard frames or call protected functions from an insecure execution context, especially during combat. Use `hooksecurefunc` where appropriate, and keep hooks limited to cosmetic styling. This requirement also needs manual review.

## Include profiling data when possible

If you can, include profiling results with your pull request. They help reviewers understand the performance impact of a change.

---

Following these conventions helps keep PrephUI consistent, safe, and efficient as it grows. Thanks for helping improve it.
