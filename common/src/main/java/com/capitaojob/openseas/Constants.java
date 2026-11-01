package com.capitaojob.openseas;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Constants {

	public static final String MOD_ID = "openseas";
	public static final String MOD_NAME = "Open Seas";
	public static final Logger LOG = LoggerFactory.getLogger(MOD_NAME);
	// Built-in data pack at resourcepacks/<PACK> in the jar, on by default. It holds everything that changes the world
	// (the replace/ functions, structure tweaks), so turning it off for a world gives vanilla terrain.
	public static final String PACK = "open_seas";
}