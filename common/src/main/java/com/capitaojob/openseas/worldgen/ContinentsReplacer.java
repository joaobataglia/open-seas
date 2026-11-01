package com.capitaojob.openseas.worldgen;

import com.capitaojob.openseas.Constants;
import com.capitaojob.openseas.mixin.HolderReferenceAccessor;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.DensityFunction;

import java.util.Map;

// Points other mods' (and vanilla's) continentalness functions at ours once all worldgen data has loaded.
// Every density function `openseas:replace/<namespace>/<path>` replaces `<namespace>:<path>` if that one exists, so
// supporting another terrain mod is a data file, and load order does not matter.
// Every reference to a density function shares one Holder.Reference, so rebinding its value reroutes all of them
// (noise router, terrain splines, biome sampler) at once.
// A replacement must not reference its own target: the target now resolves to the replacement, which would loop.
public final class ContinentsReplacer {

    private static final String PREFIX = "replace/";

    private ContinentsReplacer() {
    }

    public static void apply(RegistryAccess registries) {
        registries.registry(Registries.DENSITY_FUNCTION).ifPresent(ContinentsReplacer::apply);
    }

    private static void apply(Registry<DensityFunction> registry) {
        for (Map.Entry<ResourceKey<DensityFunction>, DensityFunction> entry : registry.entrySet()) {
            ResourceLocation id = entry.getKey().location();
            if (!id.getNamespace().equals(Constants.MOD_ID) || !id.getPath().startsWith(PREFIX)) {
                continue;
            }
            String target = id.getPath().substring(PREFIX.length());
            int slash = target.indexOf('/');
            if (slash <= 0) {
                Constants.LOG.warn("Ignoring {}: expected {}<namespace>/<path>", id, PREFIX);
                continue;
            }
            ResourceLocation targetId = ResourceLocation.fromNamespaceAndPath(target.substring(0, slash), target.substring(slash + 1));
            registry.getHolder(ResourceKey.create(Registries.DENSITY_FUNCTION, targetId)).ifPresentOrElse(
                    holder -> {
                        ((HolderReferenceAccessor) (Object) holder).openseas$bindValue(entry.getValue());
                        Constants.LOG.info("Replaced density function {} with {}", targetId, id);
                    },
                    () -> Constants.LOG.debug("Skipping {}: {} is not loaded", id, targetId));
        }
    }
}
