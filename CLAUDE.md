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
- The jars are per loader: the mod has mixins, and Fabric runs on intermediary names while NeoForge runs on Mojang
  names. Common mixins are written against Mojang names; Loom remaps them statically for the Fabric jar.
- Fabric needs Fabric API at runtime: it is what loads data from mod jars.
- Publishing metadata (version, author, license, description, repo URL) is in `gradle.properties` and expanded into
  `fabric.mod.json`, `neoforge.mods.toml` and `pack.mcmeta`. `README.md` doubles as the Modrinth/CurseForge
  description; release notes go in `CHANGELOG.md`.
- The icon is `assets/openseas/icon.png` (both loaders' metadata point there) and the built-in pack's `pack.png`.
  The current one is a local placeholder (git-ignored, with its generator in `tools/icon/`) until the real icon is
  drawn.
- The dev Fabric Loader must be >= 0.19 for test mods that ship `classTweaker v2` access wideners (Tectonic,
  Lithostitched). `fabric.mod.json` pins the runtime requirement separately (`>=0.15`).

## How the terrain works
- The island layout is data: `openseas:continents` in `common/src/main/resources/data/`. Continentalness is the one
  value that both the terrain shape splines (offset/factor/jaggedness) and biome placement read, so biomes and coasts
  stay consistent and biome mods (TerraBlender etc.) keep working.
- `worldgen/ContinentsReplacer` (called from `RegistryDataLoaderMixin` once worldgen data has loaded) rebinds every
  density function `openseas:replace/<ns>/<path>` onto `<ns>:<path>`, if that id exists. All references to a density
  function share one `Holder.Reference`, so this reroutes the router, the terrain splines and the biome sampler at
  once, regardless of load order. A replacement must not reference its own target, directly or through other
  replacements (it would loop): the replacer checks by binding a probe to the target and walking the replacement with
  `mapAll`, and skips it with an error.
  - `replace/minecraft/overworld/continents` (Default, Amplified) and `replace/minecraft/overworld_large_biomes/
    continents`: `add(openseas:continents, 0)`. A density function file cannot be a bare `"ns:id"` reference (the
    registry codec only takes a number or an object), hence the add.
  - `replace/tectonic/noise/raw_continents`: Tectonic replaces the whole overworld noise settings and its terrain
    splines read `raw_continents`, not the router's continents. Its `island_selector` turns raw values in [-1, -0.5)
    into Tectonic islands, so this is `max(openseas:continents, -0.49)` (what Tectonic's own `disable_islands` does);
    -0.49 is still deep ocean for biomes, and Tectonic's depth spline is flat below -0.45.
  - Adding support for another terrain mod: find the density function its terrain splines read for continentalness
    and add a `replace/` file for it to the pack.
- Everything that changes the world lives in a built-in data pack, `common/src/main/resources/resourcepacks/
  open_seas/` (registered by each loader's `OpenSeas`: Fabric `ResourceManagerHelper`, NeoForge
  `AddPackFindersEvent`). It is added automatically to new and existing worlds and can be turned off per world, which
  gives vanilla terrain. `openseas:continents` and its noises stay in the jar's main data (unused without the pack).
  - The `replace/` functions above.
  - `minecraft:ocean_monuments`: spacing 80 / separation 24 instead of 32 / 5 (~1/6 the density). With ~84% ocean,
    mostly deep, vanilla spacing put a monument every ~500 blocks of sailing.
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
- The replacement applies to every world, so adding the mod to an existing world leaves seams at the old chunk border.
- survivalisland is a separate world preset with its own noise settings and a custom density function type, so it is
  not affected (its mixin only captures the seed).

## Previewing changes without launching the game
`tools/preview/preview.py` evaluates `openseas:continents` (supported subset: add/mul/min/max/clamp/abs/
constant/caches/noise/shifted_noise/shift_a/shift_b/spline) with a port of Minecraft's noise, renders mod vs vanilla
maps and prints land %, island size counts, land share per continentalness band and the distance from the origin to
the nearest land vanilla's spawn search accepts. Seeds do not match the game. Needs numpy + pillow
(`python -m venv tools/preview/.venv && tools/preview/.venv/bin/pip install -r tools/preview/requirements.txt`).
Reads vanilla data from Loom's cached `minecraft-client.jar`.

## Conventions
- Package `com.capitaojob.openseas`, mod id and data namespace `openseas`.
- Core behaviour must work server-side with vanilla clients.
