"""Top-down preview of the overworld continentalness defined by the mod's worldgen data.

Evaluates the `continents` density function JSON (the subset of types we use) with a port of Minecraft's noise,
colours it by the continentalness bands vanilla biome placement uses, and prints island counts and sizes.
Seeds do not match the game: compare the character of the maps, not exact coordinates.

    python preview.py                      # mod vs vanilla, 16k blocks, seeds 1 2 3
    python preview.py --size 4096 --seeds 5 --out zoom.png
"""
import argparse
import json
import os
import zipfile
import zlib
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

from mcnoise import NormalNoise

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DATA = os.path.normpath(os.path.join(HERE, "../../common/src/main/resources/data"))
VANILLA_JAR = os.path.expanduser("~/.gradle/caches/fabric-loom/1.21.1/minecraft-client.jar")
VANILLA_CONTINENTS = "minecraft:overworld/continents"
MOD_CONTINENTS = "openseas:continents"  # the mod rebinds vanilla's continents to this at runtime

# continentalness bands used by vanilla biome placement (upper bound, colour)
BANDS = [
    (-1.05, (150, 60, 160)),   # mushroom fields
    (-0.455, (20, 40, 110)),   # deep ocean
    (-0.19, (40, 90, 180)),    # ocean
    (-0.11, (230, 215, 150)),  # coast
    (0.03, (140, 200, 100)),   # near inland
    (0.30, (80, 160, 70)),     # mid inland
    (9e9, (40, 110, 50)),      # far inland
]
LAND_BANDS = [("coast", -0.19, -0.11), ("near", -0.11, 0.03), ("mid", 0.03, 0.30), ("far", 0.30, 9e9)]
SPAWN_MIN = -0.11  # vanilla's spawn search targets near inland and up


class DataSource:
    """Resolves worldgen JSON by id, looking in the mod's data first (if enabled) and then the vanilla jar."""

    def __init__(self, use_mod):
        self.use_mod = use_mod
        self.jar = zipfile.ZipFile(VANILLA_JAR)

    def load(self, kind, ident):
        ns, path = ident.split(":", 1) if ":" in ident else ("minecraft", ident)
        rel = f"{ns}/worldgen/{kind}/{path}.json"
        if self.use_mod and os.path.exists(os.path.join(MOD_DATA, rel)):
            with open(os.path.join(MOD_DATA, rel)) as f:
                return json.load(f)
        return json.loads(self.jar.read("data/" + rel))


class Evaluator:
    def __init__(self, seed, data):
        self.seed = seed
        self.data = data
        self.noises = {}

    def noise(self, ident):
        if ident not in self.noises:
            d = self.data.load("noise", ident)
            rng = np.random.default_rng([self.seed, zlib.crc32(ident.encode())])
            self.noises[ident] = NormalNoise(rng, d["firstOctave"], d["amplitudes"])
        return self.noises[ident]

    def eval(self, df, x, z):
        # full_like/empty_like below inherit the coordinates' dtype: integer coordinates would truncate every value
        x, z = np.asarray(x, np.float64), np.asarray(z, np.float64)
        if isinstance(df, (int, float)):
            return np.full_like(x, float(df))
        if isinstance(df, str):
            return self.eval(self.data.load("density_function", df), x, z)
        t = df["type"].removeprefix("minecraft:")
        if t in ("flat_cache", "cache_2d", "cache_once", "interpolated", "cache_all_in_cell"):
            return self.eval(df["argument"], x, z)
        if t == "add":
            return self.eval(df["argument1"], x, z) + self.eval(df["argument2"], x, z)
        if t == "mul":
            return self.eval(df["argument1"], x, z) * self.eval(df["argument2"], x, z)
        if t in ("min", "max"):
            return getattr(np, t + "imum")(self.eval(df["argument1"], x, z), self.eval(df["argument2"], x, z))
        if t == "clamp":
            return np.clip(self.eval(df["input"], x, z), df["min"], df["max"])
        if t == "abs":
            return np.abs(self.eval(df["argument"], x, z))
        if t == "constant":
            return np.full_like(x, float(df["argument"]))
        if t in ("shift_a", "shift_b"):
            n = self.noise(df["argument"])
            return (n.value(x * 0.25, 0, z * 0.25) if t == "shift_a" else n.value(z * 0.25, x * 0.25, 0)) * 4
        if t == "noise":
            return self.noise(df["noise"]).value(x * df["xz_scale"], 0, z * df["xz_scale"])
        if t == "shifted_noise":
            sx = self.eval(df["shift_x"], x, z)
            sz = self.eval(df["shift_z"], x, z)
            return self.noise(df["noise"]).value(x * df["xz_scale"] + sx, 0, z * df["xz_scale"] + sz)
        if t == "spline":
            return self.spline(df["spline"], x, z)
        raise NotImplementedError(f"density function type {df['type']} is not supported by the preview")

    def spline(self, sp, x, z):
        """minecraft:spline (CubicSpline.Multipoint): hermite segments, linear extension past the ends."""
        if isinstance(sp, (int, float)):
            return np.full_like(x, float(sp))
        c = self.eval(sp["coordinate"], x, z)
        pts = sp["points"]
        loc = np.array([p["location"] for p in pts])
        der = np.array([p["derivative"] for p in pts])
        val = [self.spline(p["value"], x, z) for p in pts]
        out = np.empty_like(c)
        i = np.searchsorted(loc, c, side="right") - 1
        lo = i < 0
        out[lo] = val[0][lo] + der[0] * (c[lo] - loc[0])
        hi = i >= len(pts) - 1
        out[hi] = val[-1][hi] + der[-1] * (c[hi] - loc[-1])
        for k in range(len(pts) - 1):
            m = i == k
            if not m.any():
                continue
            w = loc[k + 1] - loc[k]
            t = (c[m] - loc[k]) / w
            y0, y1 = val[k][m], val[k + 1][m]
            p = der[k] * w - (y1 - y0)
            q = -der[k + 1] * w + (y1 - y0)
            out[m] = y0 + t * (y1 - y0) + t * (1 - t) * (p + t * (q - p))
        return out


def colorize(c):
    img = np.zeros(c.shape + (3,), np.uint8)
    lo = -9e9
    for hi, col in BANDS:
        img[(c >= lo) & (c < hi)] = col
        lo = hi
    return img


def island_areas(land, bpp):
    """Connected land components (4-neighbour), as areas in square blocks, largest first."""
    h, w = land.shape
    seen = np.zeros_like(land, bool)
    sizes = []
    for y0, x0 in zip(*np.nonzero(land)):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        n = 0
        while q:
            y, x = q.popleft()
            n += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < h and 0 <= xx < w and land[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        sizes.append(n * bpp * bpp)
    return sorted(sizes, reverse=True)


def stats(c, bpp, dist):
    land = c >= -0.19  # coast band and above is dry land
    diam = [2 * np.sqrt(a / np.pi) for a in island_areas(land, bpp)]
    small = sum(d < 300 for d in diam)
    med = sum(300 <= d < 1500 for d in diam)
    big = sum(d >= 1500 for d in diam)
    top = ", ".join(f"{d:.0f}" for d in diam[:5])
    bands = "  ".join(f"{name} {((c >= lo) & (c < hi)).sum() / max(land.sum(), 1) * 100:2.0f}%"
                      for name, lo, hi in LAND_BANDS)
    spawnable = c >= SPAWN_MIN
    spawn = f"{dist[spawnable].min():.0f}b" if spawnable.any() else "none in view"
    return (f"land {land.mean() * 100:4.1f}%  islands {len(diam):3d} "
            f"(<300b: {small}, 300-1500b: {med}, >1500b: {big})  largest diameters: {top}\n"
            f"{'':17s}land by band: {bands}  nearest spawnable land: {spawn}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=16384, help="blocks per tile side (default 16384)")
    ap.add_argument("--px", type=int, default=512, help="pixels per tile side (default 512)")
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--no-vanilla", action="store_true", help="skip the vanilla comparison row")
    ap.add_argument("--out", default="preview.png")
    args = ap.parse_args()

    bpp = args.size / args.px
    ax = (np.arange(args.px) - args.px / 2) * bpp
    x, z = np.meshgrid(ax, ax)
    dist = np.hypot(x, z)
    rows = [("mod", True, MOD_CONTINENTS)] + ([] if args.no_vanilla else [("vanilla", False, VANILLA_CONTINENTS)])

    pad = 22
    canvas = Image.new("RGB", (len(args.seeds) * args.px, len(rows) * (args.px + pad)), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for r, (name, use_mod, continents) in enumerate(rows):
        data = DataSource(use_mod)
        draw.text((4, r * (args.px + pad) + 4),
                  f"{name}  ({args.size} x {args.size} blocks per tile, origin at centre, seeds {args.seeds})", fill=(0, 0, 0))
        for s, seed in enumerate(args.seeds):
            c = Evaluator(seed, data).eval(continents, x, z)
            print(f"{name:8s} seed {seed}: {stats(c, bpp, dist)}")
            canvas.paste(Image.fromarray(colorize(c)), (s * args.px, r * (args.px + pad) + pad))
    canvas.save(args.out)
    print("saved", os.path.abspath(args.out))


if __name__ == "__main__":
    main()
