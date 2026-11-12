# Verification: v1.2.0

Target: official Mindustry **v160.7**. Minimum supported version: v160.7. Later versions are allowed by metadata, not individually tested.

## Unit tests

`node --test tests/controller.test.js`: **13 passing tests**. Covers host pause/resume, guest and offline rejection, menu, game over, post-campaign state, pause-disabled rule, PvP waiting, cutscene, authority recheck, external pause changes, rule preservation and new-map GameState replacement.

## Actual game integration

All four v1.2 runs passed using the real official game JAR, not a mock engine:

- Mobile landscape / iOS path: **27 checks/actions**, unmodded guest.
- Mobile portrait / iOS path: **33 checks/actions**, unmodded guest; adds native single-player pause preservation and host players-list access checks.
- Desktop: **27 checks/actions**, unmodded guest.
- Mobile landscape / iOS path with mod ALSO on guest: **37 checks/actions**; confirms guest still gets the ordinary players list, not pause control, and no extra host-only players button.

All runs verify actual UI click changes native pause, host and guest simulation ticks stop, resume/re-pause synchronize, guests join/reconnect while paused, and pause-disabled rules disable host control. Touch-size/on-screen bounds checked. Native pause/play icon and added players-list icon inspected in landscape and portrait screenshots.

The unchanged controller also passed a previous real headless-server test: tick and wave countdown stayed exactly unchanged for 15 seconds, then advanced after resume. This headless run was on the earlier UI version, not rerun for v1.2.

## Mobile test method and limits

`tests/IosPathLauncher.java` runs the official released desktop game with mobile HUD, Rhino optimization level -1 (matching IOSLauncher), and iOS interface-proxy behavior activated before Rhino initializes. JavaAdapter is replaced with a throwing implementation to detect accidental generated-class use.

This is a **desktop compatibility harness, not an iOS emulator**. No physical iPad/iPhone/Android or actual iOS Simulator test has been performed. A Mac capability check found no Xcode/Simulator or connected iPad. No WAN/Steam relay, long-duration campaign, or unrelated-mod compatibility tests.

Tests use isolated temporary profiles and a separate hidden instrumentation mod to issue commands/capture screenshots. Neither instrumentation nor test launcher is included in the installable ZIP. The no-mod guest runs have no Multiplayer pausing mod; only test instrumentation.

## Native button implementation

v1.2 keeps the actual original mobile pause button, its cell, style and internal click listener. Replaces its action/update callbacks with host/guest/single-player branches. Host uses native synchronized pause; guest and offline behavior match v160.7 original logic. The extra host-only players-list cell collapses outside host mode. Desktop has no mobile toolbar, so retains a separate native-style pause/play icon below the resource area.

No reflection, generated subclasses, `extend()`, JavaAdapter or custom packets added. It uses existing classes and supported Runnable/Cons/Boolp interfaces. Metadata: `displayName: Multiplayer pausing`, `description: Controlled by host`, `iosCompatible: true`, `hidden: true`.

## Publication and behavioral limits

GitHub publication and browser indexing must be verified separately. This test report does not establish listing status. Native pause stops simulation, not network/chat; it does not block every possible player action. There is no voting, auto-pause on menu/disconnect/backgrounding, custom speed, or remote dedicated-server control.

## Official sources

- [GameState](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/GameState.java)
- [Simulation pause gate](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/Logic.java)
- [Native HUD controls](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/HudFragment.java)
- [Server snapshots](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/NetServer.java)
- [Guest snapshot handling](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/NetClient.java)
- [iOS interpreter](https://github.com/Anuken/Mindustry/blob/v160.7/ios/src/mindustry/ios/IOSLauncher.java)
- [iOS browser filtering](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ModBrowserDialog.java)
- [Rhino interface proxies](https://github.com/Anuken/rhino/blob/32395f942976a6d1d21ec9877664554cd5762306/src/rhino/NativeJavaClass.java)
- [Browser indexing](https://github.com/Anuken/MindustryMods)
