package com.capitaojob.openseas;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.resource.ResourceManagerHelper;
import net.fabricmc.fabric.api.resource.ResourcePackActivationType;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

public class OpenSeas implements ModInitializer {

    @Override
    public void onInitialize() {
        CommonClass.init();
        ResourceManagerHelper.registerBuiltinResourcePack(
                ResourceLocation.fromNamespaceAndPath(Constants.MOD_ID, Constants.PACK),
                FabricLoader.getInstance().getModContainer(Constants.MOD_ID).orElseThrow(),
                Component.literal(Constants.MOD_NAME),
                ResourcePackActivationType.DEFAULT_ENABLED);
    }
}
