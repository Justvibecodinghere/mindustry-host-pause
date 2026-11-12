# Multiplayer pausing

Controlled by host

Restores the **built-in top-left pause/play button** while hosting multiplayer on iPad, iPhone and Android. The host pauses the shared simulation; guests do not need the mod.

## Use

1. Both players need **Mindustry v160.7 or newer**.
2. Install this mod on the **hosting device**, then restart Mindustry.
3. Host a game normally and tap the original top-left pause icon. Tap its play icon to resume.

The actual native mobile button stays in its original slot, with its original style and size. A separate native-style players-list icon is added to the same toolbar for the host, preserving access to players/admin controls. Guests retain the game's ordinary players-list button. Single-player keeps the original pause behavior. On desktop, where this mobile toolbar does not exist, a small pause/play icon is provided on the left below the resource area; the native pause key still works.

Only the host can pause through this mod. It respects pause-disabled map rules, game-over state, cutscenes and native PvP waiting-for-players pause. It does not auto-pause when menus open, implement voting, grant guest/admin permissions, change simulation speed or lock every player input.

## How it works

The button sets Mindustry's native paused/playing state. The game's existing server snapshots synchronize it to guests. No custom packets, guest-side install, timer hacks or rule overrides. Chat announcements identify host pause/resume. Networking and chat remain live; guests can join or reconnect while paused. Normal network latency applies.

## iPad compatibility

This is a JavaScript-only utility with `iosCompatible: true`. It uses supported interface callbacks, not generated Java subclasses, `extend()` or `JavaAdapter`. The internal `hidden: true` metadata makes it an optional utility mod so guests need not install it; it does **not** hide it from the mod browser.

**No physical iPad/iPhone, actual iOS Simulator or Android-device test has been performed.** Real desktop-hosted mobile UI runs exercise the official game's iOS interpreter/interface-proxy paths, but are not on-device tests. See [TESTING.md](TESTING.md).

## Install

After publication and indexing: **Mods → Mod Browser → Multiplayer pausing → Install**, then restart. If search indexing is pending, use **Import Mod → Import From GitHub** with the published repository name.

For a test ZIP: download `host-pause-1.2.0.zip` into Files, then **Import Mod → Import File**. Do not unzip it. The joining device does not need this ZIP.

## Publishing

The root of a public GitHub repository must contain `mod.json` and `scripts/`, and the repository must have the `mindustry-mod` topic. The [official index](https://github.com/Anuken/MindustryMods) automatically discovers qualifying repositories, ordinarily every few hours. Publication and successful indexing are separate steps; verify listing after publication. Do not add `hideBrowser: true`. No Java JAR or dex build is required.

## Develop

- `node --test tests/controller.test.js`
- `python3 build.py`
- `python3 tests/integration.py --jar /path/to/Mindustry.jar`
- Add `--ios-path` for mobile HUD/interpreter/proxy tests, `--portrait` for portrait, or `--guest-mod` to verify a guest who also installed the mod.

Integration tests use isolated temporary profiles, Java 17+, Linux Xorg/dummy driver, xauth and software OpenGL. They do not alter ordinary saves. Instrumentation and the test launcher are not shipped in the installable ZIP.
