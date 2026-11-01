# TODO

## Before publishing 1.0.0
- [ ] Screenshots for the Modrinth/CurseForge page.

## Next
- [ ] Config: island size, sea amount, archipelago scale. On/off per world is the built-in pack; variants could be
      more built-in packs (off by default) that override `openseas:continents` or its noises.

## Later
- Islands sit lower than vanilla land: more coast, less far inland, so fewer mountains and peaks. Might balance it,
  but it fits a world with more ocean and smaller land masses. Share of land per band (preview.py prints this):

  |         | coast | near inland | mid inland | far inland |
  |---------|-------|-------------|------------|------------|
  | mod     | 20%   | 28%         | 33%        | 19%        |
  | vanilla | 12%   | 22%         | 38%        | 29%        |

  Levers: `island_shape` bias (interior height), the `big_island_mask` boost.

## Done
- [x] In-game check of the runtime replacement (both loaders, Tectonic, Large Biomes) and the built-in `open_seas`
      data pack.
- [x] License (MIT), publishing metadata and icon.
- [x] Spawn in open sea: never happened in play; preview shows spawnable land within ~1.4km of the origin.
- [x] In-game check of the data-only version (Fabric).
- [x] "Far lands"-like spots: gone after the island rework.
- [x] Replace continents at runtime instead of overriding the file (`ContinentsReplacer`), so load order does not
      matter and Tectonic gets islands.
