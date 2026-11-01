package com.capitaojob.openseas.mixin;

import net.minecraft.core.Holder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(Holder.Reference.class)
public interface HolderReferenceAccessor {

    @Invoker("bindValue")
    void openseas$bindValue(Object value);
}
