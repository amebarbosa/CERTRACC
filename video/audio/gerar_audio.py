"""Gera as duas camadas de áudio do vídeo (só numpy, determinístico).

  public/audio/trilha.wav  — trilha emotiva: piano em arpejo, pad, baixo,
                             batida tipo "coração" e melodia, Am F C G | Am G F C
  public/audio/efeitos.wav — efeitos sincronizados com as animações
                             (surgimento de texto, barras, itens da lista, logo)

Uso: python3 audio/gerar_audio.py   (a partir da pasta video/)
Os tempos dos efeitos espelham os `delay` de src/CuidarDoSeuFilho.tsx (30 fps).
"""
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 20.0
N = int(SR * DUR)
FPS = 30
SCENE = 5.0
BPM = 72
BEAT = 60 / BPM  # 0,833 s
CHORD = 2.5      # 2 acordes por cena
rng = np.random.default_rng(7)
OUT = Path(__file__).resolve().parent.parent / 'public' / 'audio'


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def t_of(n):
    return np.arange(n) / SR


def add(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i : i + len(sig)] += sig


def lowpass(x, cutoff):
    """Passa-baixa de 1 polo; cutoff pode ser escalar ou array (varia no tempo)."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def reverb(x, seconds=2.4, seed=0):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    ir = r.standard_normal(n) * np.exp(-t_of(n) * 6.5 / seconds)
    ir[: int(0.012 * SR)] = 0  # pré-delay
    ir /= np.sqrt(np.sum(ir**2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)
    return y[: len(x)]


# ---------------------------------------------------------------- trilha
chords = [  # (baixo, vozes)
    (45, [57, 60, 64]),  # Am
    (41, [57, 60, 65]),  # F
    (48, [55, 60, 64]),  # C
    (43, [55, 59, 62]),  # G
    (45, [57, 60, 64]),  # Am
    (43, [55, 59, 62]),  # G
    (41, [57, 60, 65]),  # F
    (48, [55, 60, 64]),  # C (resolução no logo)
]


def piano(f, length=1.8, vel=1.0):
    t = t_of(int(length * SR))
    sig = np.zeros_like(t)
    for k, amp in enumerate([1.0, 0.45, 0.22, 0.12, 0.06], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        sig += amp * np.sin(2 * np.pi * fk * t) * np.exp(-t * (2.2 + 1.3 * k))
    attack = np.minimum(t / 0.004, 1)
    return vel * sig * attack


def pad(notes, length):
    t = t_of(int(length * SR))
    sig = np.zeros_like(t)
    for m in notes:
        for det in (-0.004, 0, 0.004):
            sig += np.sin(2 * np.pi * hz(m) * (1 + det) * t + rng.uniform(0, 6.28))
            sig += 0.3 * np.sin(2 * np.pi * hz(m + 12) * (1 + det) * t)
    env = np.minimum(t / 0.7, 1) * np.minimum((length - t) / 0.9, 1)
    return sig * np.clip(env, 0, 1) / (len(notes) * 4)


def kick(vel=1.0):
    t = t_of(int(0.35 * SR))
    f = 45 + 75 * np.exp(-t * 28)
    return vel * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)


music = np.zeros(N)
pads = np.zeros(N)
melody_bus = np.zeros(N)

melody = {  # (tempo, nota midi) — entra na cena 2 e cresce
    5.0: 76, 6.25: 72, 7.5: 74, 8.75: 79,
    10.0: 76, 11.25: 74, 12.5: 74, 13.75: 71,
    15.0: 72, 16.25: 69, 17.5: 72, 18.1: 76,
}

for ci, (bass, voices) in enumerate(chords):
    start = ci * CHORD
    add(pads, pad(voices, CHORD + 0.9), start - 0.2 if ci else 0)
    # arpejo em colcheias: 6 por acorde
    arp = [voices[0] + 12, voices[1] + 12, voices[2] + 12, voices[0] + 24, voices[2] + 12, voices[1] + 12]
    for k, m in enumerate(arp):
        vel = 0.55 if k % 2 else 0.75
        add(music, piano(hz(m), vel=vel), start + k * BEAT / 2)
    # baixo a partir da cena 2
    if start >= SCENE:
        t = t_of(int(CHORD * SR))
        b = np.sin(2 * np.pi * hz(bass) * t) + 0.3 * np.sin(2 * np.pi * hz(bass + 12) * t)
        add(music, 0.35 * b * np.minimum(t / 0.05, 1) * np.exp(-t * 0.9), start)

for when, m in melody.items():
    add(melody_bus, piano(hz(m), length=2.4, vel=0.9), when)

# batida "coração" (tum-tum) a cada compasso, cenas 2 e 3; cena 4 só a primeira
beat = np.zeros(N)
bar = 4 * BEAT
t0 = SCENE
while t0 < 15.0 - 0.01:
    add(beat, kick(0.9), t0)
    add(beat, kick(0.6), t0 + 0.22)
    t0 += bar
add(beat, kick(1.0), 15.0)

dry = music * 0.55 + pads * 0.5 + melody_bus * 0.45 * (t_of(N) >= 5) + beat * 0.6
left = dry + 0.35 * reverb(dry, seed=1)
right = dry + 0.35 * reverb(dry, seed=2)
trilha = np.stack([left, right], axis=1)
tt = t_of(N)
fade = np.clip(np.minimum(tt / 0.4, (DUR - tt) / 2.2), 0, 1)
trilha *= fade[:, None]

# ---------------------------------------------------------------- efeitos


def whoosh(length=0.5, lo=300, hi=3500, vel=1.0):
    n = int(length * SR)
    t = t_of(n)
    shape = np.sin(np.pi * t / length) ** 2
    cut = lo + (hi - lo) * shape
    return vel * lowpass(rng.standard_normal(n), cut) * shape * 1.6


def pop(f0=900, f1=380, vel=1.0):
    t = t_of(int(0.09 * SR))
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    return vel * s


def blip(m, vel=1.0):
    t = t_of(int(0.45 * SR))
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return vel * 0.6 * s * np.exp(-t * 9) * np.minimum(t / 0.002, 1)


def line_sweep(length=0.6, vel=1.0):
    n = int(length * SR)
    t = t_of(n)
    f = 500 + 1100 * (t / length) ** 1.5
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(t / 0.02, 1) * np.exp(-((t / length) ** 2) * 2.5)
    air = lowpass(rng.standard_normal(n), 2500 + 4000 * t / length) * 0.5
    return vel * 0.45 * (tone + air) * env


def riser(length=1.4, vel=1.0):
    n = int(length * SR)
    t = t_of(n)
    p = t / length
    noise = lowpass(rng.standard_normal(n), 400 + 7000 * p**2)
    return vel * noise * p**2.5 * 1.3


def hit(vel=1.0):
    t = t_of(int(2.5 * SR))
    boom = np.sin(2 * np.pi * (42 + 60 * np.exp(-t * 18)) * t) * np.exp(-t * 3.5)
    shimmer = sum(
        np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * (1.6 + 0.3 * i)) * 0.25
        for i, m in enumerate([84, 88, 91, 96])
    )
    return vel * (boom + shimmer * np.minimum(t / 0.003, 1))


def f(scene, frames):
    return scene * SCENE + frames / FPS


sfx = np.zeros(N)
# Cena 1 — duas linhas sobem, barra branca se desenha
add(sfx, whoosh(0.45, vel=0.55), f(0, 6) - 0.1)
add(sfx, whoosh(0.45, vel=0.6), f(0, 22) - 0.1)
add(sfx, line_sweep(0.6), f(0, 40))
# transições entre cenas (fade em 150, 300)
for s in (1, 2):
    add(sfx, whoosh(0.7, lo=200, hi=2500, vel=0.5), s * SCENE - 0.45)
# Cena 2 — rótulo + 5 itens (notas ascendentes em pentatônica de Lá menor)
add(sfx, pop(vel=0.7), f(1, 4) + 0.03)
for i, m in enumerate([81, 84, 86, 88, 91]):
    add(sfx, blip(m, vel=0.75), f(1, 16 + i * 12) + 0.03)
    add(sfx, pop(1400, 600, vel=0.35), f(1, 16 + i * 12) + 0.03)
# Cena 3 — título sobe, barra laranja, subtítulo
add(sfx, whoosh(0.45, vel=0.6), f(2, 6) - 0.1)
add(sfx, line_sweep(0.6), f(2, 26))
add(sfx, pop(vel=0.6), f(2, 36) + 0.05)
# Cena 4 — subida até o logo, impacto + brilho, @certracc, frase
add(sfx, riser(1.3, vel=0.7), f(3, 6) - 1.3)
add(sfx, hit(0.9), f(3, 6) + 0.02)
add(sfx, pop(1100, 450, vel=0.8), f(3, 24) + 0.05)
add(sfx, blip(88, vel=0.5), f(3, 38) + 0.05)
add(sfx, blip(93, vel=0.4), f(3, 38) + 0.17)

sfx_l = sfx + 0.25 * reverb(sfx, seconds=1.2, seed=3)
sfx_r = sfx + 0.25 * reverb(sfx, seconds=1.2, seed=4)
efeitos = np.stack([sfx_l, sfx_r], axis=1)


def save(path, data, peak):
    data = data / np.max(np.abs(data)) * peak
    pcm = (data * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


OUT.mkdir(parents=True, exist_ok=True)
save(OUT / 'trilha.wav', trilha, 0.89)
save(OUT / 'efeitos.wav', efeitos, 0.89)
print('ok:', OUT / 'trilha.wav', OUT / 'efeitos.wav')
