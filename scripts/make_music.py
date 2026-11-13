"""Música de fondo muy suave y libre de derechos (generada aquí, sin samples): pad ambiental + campanitas.

Uso: python scripts/make_music.py salida.wav --dur 10.6 [--seed 3]
Acordes Cmaj7 - Am9 - Fmaj7 - G6, con ataque y caída lentos, filtro paso bajo y fundido de entrada/salida.
"""
import argparse, wave
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--dur", type=float, default=10.0); ap.add_argument("--seed", type=int, default=3)
a = ap.parse_args()
SR = 44100; n = int(a.dur * SR); t = np.arange(n) / SR
rng = np.random.default_rng(a.seed)
f = lambda m: 440 * 2 ** ((m - 69) / 12)  # nota MIDI -> Hz
chords = [[48, 55, 59, 64], [45, 52, 59, 60], [41, 48, 57, 64], [43, 50, 59, 64]]
seg = a.dur / len(chords)
pad = np.zeros(n)
for i, ch in enumerate(chords):
    s0 = i * seg; env = np.clip((t - s0 + .6) / 1.2, 0, 1) * np.clip((s0 + seg + .6 - t) / 1.2, 0, 1)  # cruce suave entre acordes
    for m in ch:
        for det in (-.12, .12):  # dos osciladores algo desafinados = sonido cálido
            fr = f(m) * 2 ** (det / 12)
            pad += env * (np.sin(2 * np.pi * fr * t) + .25 * np.sin(4 * np.pi * fr * t)) * (1 + .15 * np.sin(2 * np.pi * .3 * t))
pad /= np.abs(pad).max()
bells = np.zeros(n)
for k in range(int(a.dur * 2)):  # una campanita cada ~0,5 s, notas de la escala, muy bajita
    st = k * .5 + rng.uniform(0, .05); i0 = int(st * SR)
    if i0 >= n: break
    m = rng.choice([72, 74, 76, 79, 81, 84]); L = min(int(1.5 * SR), n - i0); tt = np.arange(L) / SR
    bells[i0:i0 + L] += np.sin(2 * np.pi * f(m) * tt) * np.exp(-tt * 3.5) * rng.uniform(.5, 1)
bells /= max(np.abs(bells).max(), 1e-9)
mix = .8 * pad + .25 * bells
k = 40; mix = np.convolve(mix, np.ones(k) / k, mode="same")  # paso bajo sencillo
fade = np.minimum(1, np.minimum(t / 1.0, (a.dur - t) / 1.5))
mix = mix / np.abs(mix).max() * fade * 0.5
st = np.stack([mix, np.roll(mix, int(.012 * SR))], 1)  # pequeño retardo entre canales = estéreo
with wave.open(a.out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())
print(a.out)
