# Open Seas: working notes

Multiloader (Fabric + NeoForge) mod for Minecraft 1.21.1 that turns the overworld into open ocean with islands and
archipelagos of every size, while keeping vanilla (and modded) terrain and biomes. Built for an HTTYD modpack.
Next steps: `TODO.md`.

## Build
- `./gradlew build` produces `fabric/build/libs/openseas-fabric-1.21.1-<ver>.jar` and
  `neoforge/build/libs/openseas-neoforge-1.21.1-<ver>.jar`. Upload both to one Modrinth/CurseForge project;
  launchers pick the right one per instance.
- `./gradlew :fabric:runClient`, `./gradlew :neoforge:runClient`.
- Build setup is copied from `../temperaments-1.21.1` (MultiLoader template): Gradle 9.2.1 because the host JDK is 25,
  Loom 1.13.6, ModDevGradle 2.0.141, mod code targets Java 21 via toolchain.
- One jar for both loaders only works while the mod is data-only; Fabric runs on intermediary names and NeoForge on
  Mojang names, so any Java touching Minecraft classes needs per-loader jars.
- Fabric needs Fabric API at runtime: it is what loads data from mod jars.

## How the terrain works
- Everything is data in `common/src/main/resources/data/`. It overrides `minecraft:overworld/continents`, the one
  value that both the terrain shape splines (offset/factor/jaggedness) and biome placement read, so biomes and coasts
  stay consistent and biome mods (TerraBlender etc.) keep working.
- `continents = clamp(-1, 1, island_shape(warped) + spline(archipelago_mask) + islets * spline(islet_mask)
  + spline(big_island_mask))`
  - `openseas:island_shape`: island outlines, sampled at xz_scale 0.18. Coarse octaves weighted up so islands come out
    chunky, not lacy. The bias keeps the threshold high (~-0.78), so only noise peaks become land: islands stay
    separate and typically 1-2km long instead of chaining into continents.
  - `warp_x`/`warp_z`: domain warp (vanilla shift + noise * 100) fed to island_shape and big_island_mask as shifts.
    Without it, high-threshold peaks come out as round blobs.
  - `openseas:archipelago` → `archipelago_mask`: slow regional noise. Nearly flat bias except its low tail, which
    opens up empty sea. Keep it flat: a wide bias range clumps islands into dense patches.
  - `openseas:islets` × spline(`islet_mask`): fine noise. Gate floor 0.25 everywhere gives coastline detail and rocks;
    up to 0.8 in islet regions gives archipelagos of small islands.
  - `big_island_mask` spline: adds up to +0.6 in the top ~10% of a slow noise, so rare 2-3km+ islands form as one body
    rather than as merged neighbours.
  - Splines extend linearly past their end points: gate/dome splines need derivative 0 at both ends, or they go
    negative outside their range.
  - The clamp at -1 keeps values above the mushroom fields band (< -1.05).
  - Preview targets (per 16x16km): ~16% land, ~27 islands 1-2km long, ~8 over 2km, max ~3-5km.
- Vanilla continentalness bands: mushroom < -1.05 < deep ocean < -0.455 < ocean < -0.19 < coast < -0.11 < near inland
  < 0.03 < mid inland < 0.3 < far inland.
- Only the Default (and Amplified) presets read `minecraft:overworld/continents`; Large Biomes has its own file.
- Data overrides apply to every world, so adding the mod to an existing world leaves seams at the old chunk border.
- Terrain mods that override the same file (Tectonic, survival-islands) conflict; load order decides who wins.

## Previewing changes without launching the game
`tools/preview/preview.py` evaluates the mod's `continents.json` (supported subset: add/mul/min/max/clamp/abs/
constant/caches/noise/shifted_noise/shift_a/shift_b/spline) with a port of Minecraft's noise, renders mod vs vanilla
maps and prints land % and island size counts. Seeds do not match the game. Needs numpy + pillow
(`python -m venv tools/preview/.venv && tools/preview/.venv/bin/pip install -r tools/preview/requirements.txt`).
Reads vanilla data from Loom's cached `minecraft-client.jar`.

## Conventions
- Package `com.capitaojob.openseas`, mod id and data namespace `openseas`.
- Core behaviour must work server-side with vanilla clients.
