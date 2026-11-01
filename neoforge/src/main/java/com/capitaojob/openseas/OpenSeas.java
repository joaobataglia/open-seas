package com.capitaojob.openseas;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.repository.Pack;
import net.minecraft.server.packs.repository.PackSource;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.AddPackFindersEvent;

@Mod(Constants.MOD_ID)
public class OpenSeas {

    public OpenSeas(IEventBus eventBus) {
        CommonClass.init();
        // BUILT_IN packs are added automatically to new and existing worlds, and can be turned off per world.
        eventBus.addListener(AddPackFindersEvent.class, event -> event.addPackFinders(
                ResourceLocation.fromNamespaceAndPath(Constants.MOD_ID, "resourcepacks/" + Constants.PACK),
                PackType.SERVER_DATA,
                Component.literal(Constants.MOD_NAME),
                PackSource.BUILT_IN,
                false,
                Pack.Position.TOP));
    }
}
