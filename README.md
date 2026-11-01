# Open Seas

Turns the overworld into open ocean dotted with islands and archipelagos of every size, from sea stacks and rocky
islets to the occasional landmass a few thousand blocks across. Everything on the islands is still vanilla terrain
and biomes, or whatever terrain and biome mods you run, so it stays compatible with them.

For Minecraft 1.21.1, on Fabric and NeoForge.

## What you get
- About 84% ocean. Most islands are 1-2 km long and well separated, with stretches of empty sea between groups.
- Archipelagos of small islands, rocks and sea stacks along coastlines.
- Rare large islands, 2-3 km and beyond, that form as one body rather than a cluster of merged neighbours.
- Biomes follow the coasts the same way they do in vanilla: beaches, then lowland, with mountains on the bigger
  islands.
- Ocean monuments are about six times sparser, since you would otherwise pass one every few hundred blocks of sailing.

## Compatibility
- Works with the Default, Large Biomes and Amplified world types.
- Biome mods (TerraBlender-based and others) keep working: Open Seas only changes where land is, not how biomes are
  picked.
- Tectonic: supported. Tectonic's terrain is kept, but its land layout is replaced with Open Seas islands.
- Other terrain mods that replace the overworld's noise settings may ignore Open Seas. Reports are welcome.
- Only the overworld is changed. World presets with their own generator (Superflat, Single Biome, and mods that add
  their own world type) are left alone.

## Install
- Fabric: needs [Fabric API](https://modrinth.com/mod/fabric-api).
- NeoForge: nothing else needed.
- Servers: install it on the server. Clients don't need it; vanilla clients can join.

## Turning it off for a world
Everything Open Seas changes lives in a built-in data pack, **Open Seas**, which is on by default. To get vanilla
terrain in a world, turn it off under **Create World → More → Data Packs**. Each world remembers its own setting.

## Adding it to an existing world
Only newly generated chunks change. Expect sharp cliffs or walls of water where new chunks meet already explored
ones.

## Building
`./gradlew build` produces both jars:

- `fabric/build/libs/openseas-fabric-1.21.1-<version>.jar`
- `neoforge/build/libs/openseas-neoforge-1.21.1-<version>.jar`

## License
MIT, see [LICENSE](LICENSE).
