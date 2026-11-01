package com.capitaojob.openseas.worldgen;

import com.capitaojob.openseas.Constants;
import com.capitaojob.openseas.mixin.HolderReferenceAccessor;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.DensityFunction;
import net.minecraft.world.level.levelgen.DensityFunctions;

import java.util.Map;

// Points other mods' (and vanilla's) continentalness functions at ours once all worldgen data has loaded.
// Every density function `openseas:replace/<namespace>/<path>` replaces `<namespace>:<path>` if that one exists, so
// supporting another terrain mod is a data file, and load order does not matter.
// Every reference to a density function shares one Holder.Reference, so rebinding its value reroutes all of them
// (noise router, terrain splines, biome sampler) at once.
// A replacement must not reference its own target (directly or through other replacements): the target would resolve
// to the replacement and loop. Such replacements are skipped with an error instead of overflowing the stack in worldgen.
public final class ContinentsReplacer {

    private static final String PREFIX = "replace/";
    // Stands in for a target while its replacement is searched for references to it; matched by identity.
    private static final DensityFunction PROBE = DensityFunctions.constant(0.0);

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
                        HolderReferenceAccessor binding = (HolderReferenceAccessor) (Object) holder;
                        DensityFunction original = holder.value();
                        binding.openseas$bindValue(PROBE);
                        if (references(entry.getValue(), PROBE)) {
                            binding.openseas$bindValue(original);
                            Constants.LOG.error("Ignoring {}: it references {}, its own target, which would loop", id, targetId);
                            return;
                        }
                        binding.openseas$bindValue(entry.getValue());
                        Constants.LOG.info("Replaced density function {} with {}", targetId, id);
                    },
                    () -> Constants.LOG.debug("Skipping {}: {} is not loaded", id, targetId));
        }
    }

    // mapAll walks the whole tree, following holder references into their current values.
    private static boolean references(DensityFunction function, DensityFunction probe) {
        boolean[] found = {false};
        function.mapAll(node -> {
            found[0] |= node == probe;
            return node;
        });
        return found[0];
    }
}
