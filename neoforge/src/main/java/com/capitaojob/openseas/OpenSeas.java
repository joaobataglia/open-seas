package com.capitaojob.openseas;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(Constants.MOD_ID)
public class OpenSeas {

    public OpenSeas(IEventBus eventBus) {
        CommonClass.init();
    }
}
