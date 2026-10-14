Why sacrifice performance for a gorgeous UI? Built for peak efficiency, this sub-1.5MB suite delivers everything you love about modern UI overhauls without the overhead. Featuring ultra-responsive, high-performance nameplates, hyper-optimized modules, and insane granular customization—right down to your group leader crown placement. Handcrafted for players who demand perfection and peak framerates.

<!-- START DEFINITION TOC -->
# Table of Contents

- [What it offers](#what-it-offers)
- [Changelog](#changelog)
  - [V0.2.3](#v023)
  - [V0.2.2](#v022)
  - [V0.2.1](#v021)
  - [V0.2.00](#v0200)
  - [V0.1.16](#v0116)
  - [V0.1.15](#v0115)
  - [V0.1.14](#v0114)
  - [V0.1.13](#v0113)
  - [V0.1.1](#v011)
  - [V0.1.0Alpha](#v010alpha)
  - [V0.0.9Alpha](#v009alpha)
  - [V0.0.8Alpha](#v008alpha)
  - [V0.0.7Alpha](#v007alpha)
  - [V0.0.6Alpha](#v006alpha)
  - [V0.0.5Alpha](#v005alpha)
  - [V0.0.4Alpha](#v004alpha)
  - [V0.0.3Alpha](#v003alpha)
  - [V0.0.2Alpha](#v002alpha)
  - [V0.0.1Alpha](#v001alpha)
<!-- END DEFINITION TOC -->

## Changelog

## Pending fixes

Actionbar
  - When a new staance is learned, make sure we only grow to the right without moving the dummy mover, just extend it by 1 button to the right only when growdirection is right. Same for left, then left.

Unitframe Settings
  - Aura watch rpeview is still scuffed

Unitframe
  - performance in raids is still scuffed

### V0.2.3

*New Unitframe System*

+ Editmode
  - Fixed scuffed WIDTH match
  - Fixed a bug where anchoring at and for detached Powerbar/Castbars was not working as intended

+ Settings
  - Reworked settings  a bit to support drag-n-drop resorting and ordered highlighted entries for our widget editors

+ Borders
  - Added proper borders to every element

+ 


### V0.2.2

*Every frame is now properly snapped to whole pixels*

+ GitHub / Release
  - Prepared `CONTRIBUTING.md` file for the GitHub project

+ UnlockUI
  - Added a grid toggler with fine tunings to 1 5 10 25 50 100

+ QoL
  - Added Flighttimer with Flighttimer-Bar which also properly is influenced by the Frequent Flier legacy talent on WoW Forever

+ Performance
  - Minimap and Map CPU time reduced

+ Unitframes
  - Fixed a layouting issue causing flickering in groups
  - Fixed a bug where defaults were not properly integrated into separate addons and added new ones

+ Borders
  - Now forcing everything to full pixels so borders work as intended
  - Fixed a issue with wrong strata for borders on unitframes

+ Settings
  - Added background textures
  - Added a small blue indent indicator to collapsible elements for more clarity

+ Pending Features / Bugfixes
  - UnlockUI-Mode
    - Allow anchoring of DataBars to to the DamageMeter

  - Blizzard Editmode Cross-Compability
    - Fix BagBar positioning
    - Add proper right-click settings that display editmode settings, for all OEM movers except actionbars

  - Classbars
    - Dynamic coloring of wanted power thresholds

  - Unitframes
    - Dynamic Texts for Frames including [LEVEL]
    - Boss Frames
  
  - Dynamic Texts
    - Corrctly respond to `[foreName]` and `[surName]` tags and also rename them to `firstName` and `SecondName`

  - Settings
    - Quick access buttons for `Collapse All` `Uncollapse All`

### V0.2.1

*Every module is now its own load-on-demand addon*

+Classbars
  - Made them properly work on buffs in secret environments, mostly relevant for `WoW: Forever`
  - Optimized for CPU time spent

+Performance
  - Fixed CPU time spent on `QoL`, `Actionbars` and `Tooltips`
  - Added profiling tools
  - Added proper info entries for them

+Engine
  - Added pixel perfect border system
  - Split up all modules into separate addons for easier toggling, load-on-demand and profiling
  - Added layout setup to now properly enforce certain Blizzard Edit Mode things our UI expects
  - Added proper `borderGlows` for borders with in and outward glow, currently utilized in Nameplates and Actionbars

+Unitframes
  - Added a target highlight border
  +Settings
    - Added `property` setting category
      - Added 3D Model Portrait option
      - Added Castbar Color option
      - Added border properties
      - Added class color accent settings
    - Made dual names showable as property option
    - Buff/Debuff Frame
      - Added option to disable duration timer, swipe or invert the swipe
    - Reduced CPU time spent
  +Aurawatch
    - Fixed bleeding over excluded debuff spells from Retail to Forever

+Actionbar
  - Added proper glow via centralized glow code
  +Settings
    |-Stancebar button count option|+Stancebar is now fixed to 3 icons on classes with no stances
    - Added Border Property/Color settings
    - Petbar now has proper icon previews
    - Removed: -Show empty buttons option-, -Buff and debuff uptimers-

+Nameplates
  - Added offtank color picker
  - Added Important Unit colorations via `UnitIsLieutenant` for Retail
  - Reworked glow to use the new centralized glow code
  - Added color options and functionality for interruptible spell cast bars
  +Settings
    - Fixed targeted selected preview to use the new glow
    - Added offtank threat toggler & color

+Chat
  |-Double timestamps in Copy chat|+Copy chat no longer displays them twice

+Worldmap
  - Option to toggle Zeppelin & Boat Route Lines

+Databars
  - Added menu when friends or guild is rightclicked to select players for direct invite or messaging
  - Added border properties
  - Added bar texture selector

+EditMode
  - Changed sorting of element togglers
  - Added more anchor options to `Anchoring` and reworked menu to override anchors with modernized buttons

### V0.2.00

Nameplates
  - Added proper border glow + option to change it between thick and thin

Aurawatch
  - Fixed aurawatch for forever

Settings
  - Fixed sliders to properly show a unit like yrd, px, % etc
  - Added style overrides for settings menu that export and import with profiles
  - Fixed colorpicker slider colors
  
  Unitframes
    - Fixed AuraWatch previews, rewritten some retail logic
    - Fixed live previews for all types
  Chat
    - Fixed live previews

  Nameplates
    - Fixed live previews

  Minimap
    - Fixed live preview

  Databars
    - Fixed live previews

Tooltips
  - Added option to not show icons in tooltips

UnlockUI
  - Now when locking UI it reopens the PUI Window
  - Modernized buttons

Unitframes
  - Fixed secure error when trying to ping a enemy target

Localization
  - Made runtime strings to properly be fixed and localizable instead

Worldmap
  - Added Level range and fishing for zones in worldmap
  - Added route previews for zeppelins and boats
  - Added a option to uncover worldmap unexplored areas

### V0.1.16

Engine
  - Fully updated settings menu

Unitframes
  - Fixed summon pending, acceptfed, declined icons
  - Fixed resurrect icon
  - Proper lua side event routing to unit events
  - Group renders in combat now and delays secure actions until combat drop

Engine
  - Integrated proper default for DamageMeter aswell as Nameplate Widgets

Databar
  - Refactored Livepreview

Actionbars
  - Fixed a newly introduced error that prevented Actionbar from working properly
  - Now showing uptimer properly again

Nameplates
  - Widget based designer
  - Heavily optimized

Editmode
  - Added OEM Movers for Buffs and Debufs
  - Added OEM Movers for LossOfContorl, Vehicle Exit
  - Fixed TotemBar mover
  - Added Element toggler to deactivate movers

### V0.1.15

Cross-compatible AddOns
  - PrephDamageMeter
    - Now can create a mover within the UI based on standalone windows or anchored windows together as containers
    - Position saved and applied for profiles when PrephUI is detected

Databars
  - Ideally fixed appearance of "Unknown" entries in

ESC Menu
  - Fixed ESC button scaling
  - Integrated that general font also applies here

Tooltips
  - Fixed tooltips sometimes not showing proper style on unit tooltips
  - Fixed unit tooltips sometimes not rendering at the EditMode anchor
  - Fixed Tooltip logic a bit

Editmode
  - Fixed TargetTarget Castbar always appearing in center and snapping back
  - Fixed when moving a focus frame with active focus, that no ghost castbar will appear
  - Integrated proper movers cross compatible with native EditMode, that come and apply on profiles, for
    - QuestObjective
    - BagBar
    - MicroMenu
    - Totembar
    - CooldownManager managed frames
      - Tracked Bars
      - Tracked Buffs
      - Essential Cooldowns
      - Utility
    - Chat
    - Swingtimers

Skins
  - Retail:
    - Added MPlus Overlay
    - BlizzUIEnhanced:
      - CharacterFrame will show ItemLevel with two decimals

  - Added Maps:
    - Make map moveable option
    - Transparency option

Actionbars
  - Made actionbar glows properly work in restricted enviroments

Nameplates
  - Fixed performance:
    - Reduced amount of pcalls
    - per-frame coalescing events
    - proper UnitEvents with bindings

Chat
  - Changed "Left, Changed and Joined" channel messages to never be truncated, so its clear what number corresponds to which
  - Fixed chat dummy and they now play nice with anchored databar, see Editmode changes
  - Fixed proper databar anchoring and editbox playing nice together

Unitframes
  - Optimized Aurawatch heavily
  - Reduced overlay alpha for absorb
  - Changed absorb texture to have less tight stripes
  - Made them pingable

### V0.1.14

Tooltips
  - Fixed duplicate displays in tooltips
  - Fixed auracontainers not showing proper spellIDs and alike

Engine
  - Guarded handlers so crashes cannot propagate and crash another module

Actionbars
  - Added glow tab with glow settings based on Buff IDs

Nameplates
  - Added truncation settings to shorten HP from 4.000.000 to 4Mil and 400.000 to 400k for example

Chat
  - Rewritten truncatcion to use filters instead
  - Now with secret save fallback if they happen to be restricted
  - Fixed dummy chat mover to properly cross manipulate EditMode<->UnlockUI

Databars
  - Fixed databars not applying font directly on General Font Changes
  - Fixed databars properly attaching to chat
  - Clock
    - Added realmtime when hovering
    - Added shift+rightclick functionality to permanently swap realm with localtime or vice versa

Profiles
  - Fixed profiles not properly applying some elements due to a timing issue

Actionbar
  - Fixed SetCooldown and Attribute Errors
  - Rewritten to proper refresh single button states instead of all

Unitframes/Aurawatch
  - Fixed that enemys now do not have a dispellable texture anymore
  - Fixed Forever Aurawatch to properly display alt ranks again
  - Made it so that Castbar has higher strata then powerbar, but powerbartexts even higher so u can now place them overlapped

RaidControl
  - Modernized buttons

### V0.1.13

Engine
  - Fixed a reoccuring tainting issue when opening CharacterFrame

Profiles
  - Fixed character profiles to be properly version agnostic (WoW Forever with Dualnames; Retail with Realm)

Nameplates
  - Tap denied color was not mixed-in when threat state changed; fixed to now appropiately display Threat State Color overlayed with Tap Denied and less Alpha.

Unitframes
  - Properly using SetAlphaFromBoolean to avoid the UNKNOWN() LUA Error within Unitframe Code
  -  Bugfix: Added pendingUpdate to when in-combat group state is not initalizable, it will do so after combat ends
  - Fixed Aurawatch settings to properly differentiate between Forever and Retail

Skins
  - Integrated Skins into EngineEvents system
  - BlizzUI Enhanced
    - Added a "Show most valuable Quest Reward" option with self explanatory functionality

Chat
  - Skinned copy chat window to be more inline with PrephUI
  - Integrated chat into EngineEvents system

Databars
  - Fixed databar erroring with protected GetGuildMOTD() by caching it from save situations
  - Integrated databars into EngineEvents system

### V0.1.1 / V0.1.11 / V0.1.12

Skins
  - BlizzUI Enhanced
    - Retail: Option to display upgrade tracks
    - Shows Itemlevels on Items, excluding throwables, arrows and bullets

Chat
  - Fixed chat entirely
  - Added truncation option for Channels

General AddOn Engine
  - Overhauled API accesses to be inline with how we supposed to handle thigns in Midnight 12.1
  - Therefore Retail supports this UI now

Classbars
  - Added Retail and Forever agnostic classbars for combo points, arcane charges and alike
  - Also made classbars buff based as for example Maelstrom Weapon via talent and buff will be a thing in WOW Forever
  
Unitframes
  - Added focus frame
  - Added Heal Prediction via fill
  - Added Absorb Indication via texture
  - Added MaxHealth reduction via texture
  - Added HealAbsorb Indication via fill
  - Added back DispellOverlays but modern
  - Added proper Aurawatch for Retail with Season agnostic collection of Auras to watch for
  - Fixed proper range tracking in Ghost and alike

Nameplates
  - Added gray alphaed out color for denied tags
  - Added focus color and texture options
  - Added Questmarker Indicators for active quest objectives on mobs with objective count
  - Added quest indicators for all type of quests on friendly NPCs
  - Added Hostile, Friendly and Neutral plate color settings
  - Added Absorb display on nameplates

Actionbars
  - Fixed debuff / buff timers
  - Added uptimer for buffs

Bag
  - Removed since combined backpack does the same
  - But made bags moveable, now also persisting location

EXP Bar
  - Added Rested Indicator
  - Added QuestLOG XP
  - Added Session XP
  - Added XP/Hour
  - Added Estimated time to Level based on stats above
  - Appropiately coloring the EXP Bar
  - Properly color QuestlogXP Commpleted to be before RestedXP since it doesnt contribute to RestedXP anyway

Raidtools
  - Added grounded raid marker selection
  - Fixed collapse/expand to work during combat

Tooltip
  - Made it restricted environment agnostic and deactivating some QOL that causes taint or secure errors
  - Added Itemlevel display with option to disable/enable
  - Added Mythic+ Score Display
  - Removed "Show Guild" option and functionality since it is now natively in the tooltips

Engine/Core
  - Added add-on internal meta tables that are combined with LSM results

### V0.1.0Alpha

Nameplates
  - Added ClassColor setting for player characters

Target / TargetOfTarget
  - Event driven immediate update 
  - Removed native blizzard combo points

Chat
  - Potentially fixed framelevel and strata for whisper tabs

Bags 
  - Fixed bag buff timers

Actionbars
  - Fixed settings not applying instantly
  - Fixed icon previews to proper display bars
  - Fixed stance bar properly growing
  - Fixed item equip border
  - Fixed stance bar scaling
  

### V0.0.9Alpha

Unitframes
  - Performance updates
  - Added proper aurawatch
  - Memory churn reduction
  - Added proper buff overview for target, player and pet
  - Threat indicator via border color

Nameplates
  - Added hover color function

Bags
  - Fixed keyring missing tooltip
  - Added option to hide itemlevle above certrain threshold
  - Fixed proper cooldowns showing
  - Added active buff timer
  - Fixed cooldown duration showing

Tooltips
  - Added Item, Buff and Actionbar tooltips

Databar
  - Made Guild also show level, and also show proper <AFK> or <DND> tags

Actionbar
  - Added active item buff uptimer

Settings & Edit Mode
  - Added a recover button with a slack setting in General

  

### V0.0.8Alpha

Minimap
  - Fixed minimap icons beeing moveable when they were not proper minimap icons

Tooltips
  - Added tooltip anchor/dummy mover to reposition player tooltip
  - Added tooltip skin
  - Tooltip Skin affected by global font

Engine Events
  - migrated actionbars, nameplates and remainder unitframes to use the unified events bus instead of theyre own standalone frames
  - added engineDedup flag to auto-drop duplicate high-frequency events in the same frame tick
  - optimized the main dispatcher to kill redundant spam early before looping through modules
  - cached dedup args to keep event processing memory-lean

Profiles / EditMode
  - Fixed wrongful stale references in DB when switching profiles, which fixes every element properly registering changes after a profile switch
  - Fixed powerbar and castbar of target disappearing aswell as pet frame going wild when dragging elements
  - Fixed a error where per-character profile was nulled out to early
  - Updated default profile

Actionbars
  - Fixed stance bar aswell as its dummy to autoscale to avaiable button per row that is avaiable

Databars
  - Gold Tooltip:
    - properly differentiating between horde and alliance
    - added session profit data
  - Guild Tooltip:
    - removed the numbers beside a name

PUI
  - Added Colorpicker
    - Added reskinned colorpicker with RGBA and hex inputs
    - Made it draggable
  - Added Fontdropdown
    - Added reusable font dropdown

Unitframes
  - Fixed wrong truncation
  - Fixed glyph and encoding errors
  - Optimized
  - Added masterlooter icon

Bags
  - Fixed some laggs caused by Bags
  - Made bags open when AH or Bank opens automatically
  - Fixed that useable items like arrows or bullets will not show a itemlevel anymore
  - Fixed a closing bug within Bank code
  - Fixed a tooltip bug that caused flickering

Editmode
  - Now properly resetting previous actions when clicking between W Match  and alike
  - Anchor dropdown properly respects screenspace and opens in different directions
  - Moved labels abvove elements into theyre middle
  - Fixed a positioning bug
  - Fixed a bug with snapping
  - reworked Snap to be "1 2 5 10 Off" instead
  - Added guidance angles settings

Chat
  - Fixed that using blizzards native edit mode now applies the values to ours aswell
  - Applied a dummy mover which now databars can snap onto

### V0.0.7Alpha

Minimap
  - Made Zone text be affected by global font
  - Made zone text dynamically scale

General
  - Added primitve global font toggler

Databar
  - Rewritten "Friends online:" to just "Friends:"
  - Added color indicators to FPS; Latency; Durability

Chat
  - Now also applying Chat Font to the editbox and editboxheader

Profiles
  - Made profiles ID based
  - Added more auto save mechanisms
  - Added a new button to "Unsaved Changes"-PopUp `Save & Switch`
  - Now prompting unsaved changes before switching when importing or making a new profile

Nameplates
  - Made use of the animation system

Actionbars
  - Fixed keyboard button truncation
  - Made font affected by global font setting
  - Added a option to disable macro text
  - Fixed show empty button
  - Fixed ActionBar1 not showing tooltips
  - Added mouseover functionality to hide using the animation system

Engine
  - Added EngineEvent system
  - Added EngineAnimation system

### V0.0.6Alpha

Nameplates
  - Proper coloring and settings added
  - Threat colors implemented
  - Visual fidelity upgrades

Bag / Bank
  - Fixed search not working
  - Fixed a recursion bug on closing the bank
  - Separated Bags into Bag and Bank Settings

Unitframes
  - Fixed raidmarkers and ready check icons not showing on target frames
  - Added power bar options for group and raid
  - Fixed powerbar beeing always mana blue

Chat
  - Fixed that now all tabs for chats are hooked into historys


### V0.0.5Alpha

Bags:
  - Fixed bag keyrings

Floating Combat Text
  - Font toggler

QoL
  - Fixed Guild and Guild Rank tooltip
  - Made target tooltip update on target switches
  
New Module: Raidtools
  - AutoInvite tab with proper auto invite settings
  - Raidcontrols tab to set up the raidcontrol window
  Raidcontrols:
    - Added a toggleable hider
    - Hidden defaulted when not assist or raidlead
    - Fixed Break2 and Break5 not working
    - Added a raid warning when Pull0 is pressed "Pull canceled."
    - When collapsed showing Raid split now aswell

Chat
  - Chat style properly applied to whisper windows
  - Finally forever fixed CopyChat
  - Added a Whispers tab as option that consolidates all whispers

Nameplates
  - When something is "interrupted" by not a interrupt, but f.e. a crowd control we now flash "Interrupted"
  - Reduced visible time of interrupter to 0.5second, and fading duration to 0.3s

Pet frames
  - Happiness indication via icon

Uniframes
  - Clique Integration
  - Added blue shaman class color

EditMode
  - Added smooth animations and proper width matching of elements to fit property buttons


### V0.0.4Alpha

Chat
  - Restyled chat with proper background
  - Restyled native buttons to match
  - Resytyled native tabs
  - Added Font selector

Raidcontrol
  - Renamed/changed texts and reordered things
    -- [Role splitup]
    -- "Ready Check" "Role Check" "Break 2" "Break 5"
    -- "Pull 0sec" "Pull 10sec" "Pull 15sec"
    -- [Raid Markers] 

  
Nameplates
  - Interrupt now shown when done by placer
  - Now showing interrupt name longer

Unitframes
  - Added more Grow Directions for Raid (DownRight, DownLeft, UpRight, UpLeft)
  - Made maintank frames update live when settings are changing
  - Added pet frame + pet happiness

Actionbar:
  - Actionbar orientation (Left, Right, Up, Down) to sort icons

Bags:
  - Added Keyring



### V0.0.3Alpha

Databars:
  - Upgraded guild and Clock databars
  - Made them update every second when hovered
  
Actionbars:
  - Added Pet Bar
  - Added Totem Bar

Classbars:
  - Added proper classbars with class tools

Unitframes
  - Changed dispells to colored striped overlay
  - Fixed range fader check

Maintank Frames:
  - Fader option and functionality for MT, MTTarget, MTToT
  - Fader fix

Profile:
  - Multi profile support
  - Proper exporting of profiles
  - Proper serialization of profiles and delta table exportation

QoL:
  - Faster Loot
  - Skip Loot Warnings
  - Auto Repair

### V0.0.2Alpha

Castbar:
  - Added latency indicator

Nameplates:
  - Fixed missing castbars sometimes that are not properly recycled mid combat
  - Fixed interrupter not shown

Raid/GroupFrames:
  - Rewritten as SecureGroupHeaders to encompass blizzard secure C-Environment and allow changes midcombat
  - If in a raid that is then convert to Partyed, we now clearup icons like assist, mainassist and also hide the raid frames
  - Added proper MainAssist, MainTank Icons
  - Added Maintank & MainTanKTarget and MainTankTargetOfTarget frames
  - Added Raid control Panel for readycheck and quick marks, with role split overview (Tank/Heal/DD) and when hovered onto display class splitups (2 Warriors etc)
  - Range Check for Faders via LibRangeCheck.3-0
  - Proper dispell color logic
  - Added proper resurrect and summon icons
  - Fixed proper live updating of bar textures
  - Added Raidmarker to be viewed in unitframe
  - Fixed MainTank frame to be properly useable as target shortcut
  Target of Target:
    - Fixed tainting issue
  - Now using proper StateDrivers for Target/Player/ToT
  - Added PVP Indicator

Minimap:
  - Fixed scaling
  - Fixed icons not properly working with edge detection
  - Made LFG Icon and Mail Icons draggable
  - Moved text of zone into the minimap and dynamically scale if overflow

Raidcontrol:
  - Added /pull 10 and /pull 15
  - More accurate Role Splitup Tooltip

Databars:
  - Stick to edge should now properly work when /pui reset and setting to default
  - Added friends element
  - Added shift hover functionality to display more information on guild and friend elements
  - Combined Latency and FPS to a System element
  - Added more functionality when hovering over System element
  - If anchored to any element, properly grows with it with when resizing and respect its width
  - Made texts dynamically change size depending on avaiable space
  - Added Note and OfficerNote to Guild databar shift 

Bags:
  - Fixed a lag issue
  - Fixed that items werent useable
  - Fixed X button of bag not useable

Actionbars
  - Removed preview in general actionbars
  - Fixed anchoring issues when Rightclicking a Actionbar in Edit Mode and pressing APPLY
  - Added temporary, buggy stancebar

Chat
  - Half way fixed Copy Chat
  - Properly added restoring messages after reload with proper colors
  - Added click-on-name to whisper or directly message in channels


### V0.0.1Alpha

EditMode:
  - Fixed Dummy Frames for Raid and Group Frames
  - Fixed dummy frame for castbar, target and target of target

Added QOL Module:
  - With camera distance max setting
  - With nameplate distance setting
  - Buff and Debuff timer text formats

Actionbars:
  - Cooldown Font Size 
  - Added timers for casted debuffs to buttons aswell as options

Minimap
  - Added a drawer setting for minimap icons
  - Properly attaching icons to the edge based on style
  - Properly remember minimap icon positions

Nameplates
  - Fixed width of castbar with icon
  - Fixed castbar not displaying cast times
  - Added Colored castbar if interruptible
  - Fixed Nameplate in duels not working
  - Strata for Raid Icon was below cast bar, fixed
  - Added a setting to limit amount of debuffs, and owned ones and display more on nameplates baseline
  - Added Nameplates showing interrupters name
  - Fixed stacking nameplates, added stacking namepalte options and live preview


Code changes
  - Split Settings.lua into multiple per module
  - Properly integrated into custom processing system to autoparse changelogs

ESC Menu
  - PrephUI button added

Bags:
  - Added gold indicator on bags
  - Made drag-n-drop action easier
  - Fixed item cooldowns not properly displayed

Databars
  - Added option to attach to bottom or top of screen no matter the UI Scale
  - Added option to auto fill the screens width

PUI Reset
  - Target of Target now properly resets to a good default

Chat
  - Fixed copy text functionality (maybe)
  - Modified [C] button styling
  - Added UP and DOWN arrow to cycle between personally send messages
  - Added "Chat Mentions" that class color known names (Guild, Raid/Group), also as Setting 
  - Fixed color picker for background
  - Added timestamp and timestamp options

Unitframes
  - Fixed secure tainting issues on raid and group frame
  - Added Assist, MainTank, Raid/Group Leader Icons
  - Fixed castbar disappearing when instant spells like fireblast were casted
  - Fixed role not showing in bottom right corners
  - Fixed group not properly loading when joining a group
  - Added DEAD and OFFLINE indcators to group and raid frame units
  - Added ready check indicators