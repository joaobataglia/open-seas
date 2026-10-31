# TODO

- [ ] In-game check of the data-only version on both loaders (Distant Horizons flyover for the big picture).
- [ ] Investigate the "far lands"-like spots seen in the first test: likely continentalness changing faster than
      vanilla terrain expects (island_shape is twice vanilla's frequency). Get coordinates + seed, then compare the
      gradient in the preview tool. Possible fixes: lower the fine island_shape octaves, or soften the spline.
- [ ] Spawn: vanilla searches a limited radius for land, so players can spawn in open sea. Make sure an island
      exists near spawn.
- [ ] Wrap instead of replace: inject into the noise router at runtime (like survivalisland's NoiseWiringHelper
      mixin) so terrain mods that ship their own continents still get islands, and load order stops mattering.
- [ ] Config: island size, sea amount, archipelago scale. Possibly a world preset instead of a global override.
