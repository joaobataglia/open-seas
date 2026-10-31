package com.capitaojob.openseas;

import com.capitaojob.openseas.platform.Services;

// Shared between all loaders: only vanilla code, vanilla's libraries and the Services abstraction may be used here.
// Loader-specific concepts (NeoForge events, Fabric callbacks) belong in the loader projects.
// The terrain itself is pure data for now: see data/minecraft/worldgen/density_function/overworld/continents.json.
public class CommonClass {

    public static void init() {
        Constants.LOG.info("Initializing {} on {} ({})", Constants.MOD_NAME, Services.PLATFORM.getPlatformName(), Services.PLATFORM.getEnvironmentName());
    }
}
