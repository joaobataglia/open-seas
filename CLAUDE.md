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
- `continents = clamp(-1, 1, island_shape + spline(archipelago_mask))`
  - `openseas:island_shape`: island outlines. firstOctave -8 (features about half vanilla's continent size), coarse
    octaves weighted up and fine ones down so islands come out chunky, not lacy.
  - `openseas:archipelago` → `archipelago_mask`: very slow regional noise; the spline maps it to a bias from -0.85
    (open sea) to +0.12 (large landmass), so the land threshold varies across the world and island sizes vary with it.
  - The clamp at -1 keeps values above the mushroom fields band (< -1.05).
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
