package com.capitaojob.openseas.mixin;

import com.capitaojob.openseas.worldgen.ContinentsReplacer;
import net.minecraft.core.RegistryAccess;
import net.minecraft.resources.RegistryDataLoader;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(RegistryDataLoader.class)
public class RegistryDataLoaderMixin {

    // The overload that loads from data packs (server side; clients never receive density functions).
    @Inject(
            method = "load(Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/core/RegistryAccess;Ljava/util/List;)Lnet/minecraft/core/RegistryAccess$Frozen;",
            at = @At("RETURN"))
    private static void openseas$replaceContinents(CallbackInfoReturnable<RegistryAccess.Frozen> cir) {
        ContinentsReplacer.apply(cir.getReturnValue());
    }
}
