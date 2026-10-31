"""Port of Minecraft 1.21.1 ImprovedNoise / PerlinNoise / NormalNoise (vectorised, seeding not bit-exact)."""
import numpy as np

GRAD = np.array([
    (1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
    (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
    (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1),
    (1, 1, 0), (0, -1, 1), (-1, 1, 0), (0, -1, -1),
], dtype=np.float64)


class ImprovedNoise:
    def __init__(self, rng):
        self.xo, self.yo, self.zo = rng.random(3) * 256
        self.p = np.concatenate([rng.permutation(256)] * 2)

    def noise(self, x, y, z):
        x = x + self.xo; y = y + self.yo; z = z + self.zo
        xi = np.floor(x).astype(np.int64); yi = np.floor(y).astype(np.int64); zi = np.floor(z).astype(np.int64)
        xf = x - xi; yf = y - yi; zf = z - zi
        xi &= 255; yi &= 255; zi &= 255
        p = self.p

        def g(h, dx, dy, dz):
            gr = GRAD[h & 15]
            return gr[..., 0] * dx + gr[..., 1] * dy + gr[..., 2] * dz

        a = p[xi] + yi; aa = p[a] + zi; ab = p[a + 1] + zi
        b = p[xi + 1] + yi; ba = p[b] + zi; bb = p[b + 1] + zi
        s = lambda t: t * t * t * (t * (t * 6 - 15) + 10)
        u, v, w = s(xf), s(yf), s(zf)
        lerp = lambda t, a_, b_: a_ + t * (b_ - a_)
        x1 = lerp(u, g(p[aa], xf, yf, zf), g(p[ba], xf - 1, yf, zf))
        x2 = lerp(u, g(p[ab], xf, yf - 1, zf), g(p[bb], xf - 1, yf - 1, zf))
        x3 = lerp(u, g(p[aa + 1], xf, yf, zf - 1), g(p[ba + 1], xf - 1, yf, zf - 1))
        x4 = lerp(u, g(p[ab + 1], xf, yf - 1, zf - 1), g(p[bb + 1], xf - 1, yf - 1, zf - 1))
        return lerp(w, lerp(v, x1, x2), lerp(v, x3, x4))


class PerlinNoise:
    def __init__(self, rng, first_octave, amplitudes):
        self.amps = amplitudes
        self.levels = [ImprovedNoise(rng) if a != 0 else None for a in amplitudes]
        n = len(amplitudes)
        self.in0 = 2.0 ** first_octave
        self.val0 = 2.0 ** (n - 1) / (2.0 ** n - 1)

    def value(self, x, y, z):
        out = 0.0
        fi, fv = self.in0, self.val0
        for amp, lvl in zip(self.amps, self.levels):
            if lvl is not None:
                out = out + amp * lvl.noise(x * fi, y * fi, z * fi) * fv
            fi *= 2; fv /= 2
        return out


class NormalNoise:
    def __init__(self, rng, first_octave, amplitudes):
        self.a = PerlinNoise(rng, first_octave, amplitudes)
        self.b = PerlinNoise(rng, first_octave, amplitudes)
        nz = [i for i, a in enumerate(amplitudes) if a != 0]
        d = nz[-1] - nz[0]
        self.vf = (1 / 6) / (0.1 * (1 + 1 / (d + 1)))

    def value(self, x, y, z):
        f = 1.0181268882175227
        return (self.a.value(x, y, z) + self.b.value(x * f, y * f, z * f)) * self.vf
