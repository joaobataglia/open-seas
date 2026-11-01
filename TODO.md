# TODO

- [ ] Spawn: vanilla searches a limited radius for land, so players can spawn in open sea. Make sure an island
      exists near spawn. More likely since the rework (land ~31% -> ~16%).
- [ ] In-game check of the runtime replacement: vanilla on both loaders, Tectonic on Fabric (log should say
      "Replaced density function ..."), Large Biomes preset.
- [ ] Config: island size, sea amount, archipelago scale. Possibly a world preset instead of a global override.

## Done
- [x] In-game check of the data-only version (Fabric).
- [x] "Far lands"-like spots: gone after the island rework.
- [x] Replace continents at runtime instead of overriding the file (`ContinentsReplacer`), so load order does not
      matter and Tectonic gets islands.
