import wave, numpy as np, os
SR = 44100
D = 30.0
N = int(SR * D)
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
rng = np.random.default_rng(5)

def tt(n): return np.arange(n) / SR
def env(n, a=.005, r=.2):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, min(nr, n))
    return e
def add(buf, x, t):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y
def midi(m): return 440 * 2 ** ((m - 69) / 12)

music = np.zeros(N)
BEAT = 0.5  # 120 bpm
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]  # Am F C G
bars = int(D / (4 * BEAT))

def kick():
    n = int(.28 * SR); t = tt(n); f = 120 * np.exp(-t * 22) + 42
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * .9
def hat():
    n = int(.06 * SR); x = rng.standard_normal(n); x = x - np.concatenate([[0], x[:-1]]) * .95
    return x * np.exp(-tt(n) * 70) * .18
def clap():
    n = int(.2 * SR); x = rng.standard_normal(n); x = lp(x, 6000) - lp(x, 600)
    return x * np.exp(-tt(n) * 18) * .5
def pluck(m, dur=.22):
    n = int(dur * SR); t = tt(n); f = midi(m)
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sign(np.sin(2 * np.pi * f * 1.003 * t)) * .3)
    return x * np.exp(-t * 14) * .16
def bass(m, dur=.45):
    n = int(dur * SR); t = tt(n); f = midi(m - 12)
    return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * env(n, .01, .12) * .42
def pad(notes, dur):
    n = int(dur * SR); t = tt(n); x = np.zeros(n)
    for m in notes:
        f = midi(m + 12)
        for d in (-.4, 0, .4):
            x += np.sin(2 * np.pi * f * (1 + d * .003) * t)
    return x * env(n, .6, .8) * .035

for b in range(bars):
    t0 = b * 4 * BEAT
    root, ch = prog[b % 4]
    add(music, pad(ch, 4 * BEAT + .3), t0)
    if t0 >= 1.9:
        for k in range(4):
            add(music, bass(root), t0 + k * BEAT)
        for k in range(8):
            add(music, hat(), t0 + k * BEAT / 2 + BEAT / 4)
    if t0 >= 3.9:
        for k in range(4): add(music, kick(), t0 + k * BEAT)
    if t0 >= 5.9:
        add(music, clap(), t0 + BEAT); add(music, clap(), t0 + 3 * BEAT)
    # arp
    if t0 >= 1.9:
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        for k in range(16):
            n = ch[pat[k % 8] % 3] + (12 if k % 8 >= 4 else 24)
            add(music, pluck(n), t0 + k * BEAT / 4)
# riser into last scene + big hit at 26s
n = int(1.5 * SR); r = rng.standard_normal(n); r = lp(r, 5000) - lp(r, 300)
r *= np.linspace(0, 1, n) ** 2 * .35
add(music, r, 24.5)
hit = kick() * 1.2
add(music, hit, 26.0)
add(music, pad([57, 60, 64, 69], 4.2) * 3.5, 26.0)
# silencia batida depois da cena final (so pad)
tail = np.ones(N); i = int(26.0 * SR)
# fade global
fade = np.ones(N); fo = int(1.6 * SR); fade[-fo:] = np.linspace(1, 0, fo)
fade[:int(.4 * SR)] = np.linspace(0, 1, int(.4 * SR))
music *= fade

# ---- sfx ----
sfx = np.zeros(N)
def whoosh(t, dur=.7):
    n = int(dur * SR); x = rng.standard_normal(n)
    x = lp(x, 4000) - lp(x, 400)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    add(sfx, x * e * .5, t)
def pop(t, f=900, vol=.12):
    n = int(.1 * SR); tm = tt(n)
    add(sfx, np.sin(2 * np.pi * (f + 600 * tm * 10) * tm) * np.exp(-tm * 40) * vol, t)
def click(t):
    n = int(.03 * SR); x = rng.standard_normal(n)
    add(sfx, x * np.exp(-tt(n) * 200) * .12, t)
def ding(t, m=84):
    n = int(.8 * SR); tm = tt(n)
    add(sfx, (np.sin(2 * np.pi * midi(m) * tm) + .4 * np.sin(2 * np.pi * midi(m + 12) * tm)) * np.exp(-tm * 5) * .12, t)
for h in (7.4, 12.4, 20.2, 26.0): whoosh(h - .25)
U = lambda u: 3.3 + u / 1.4
whoosh(0.0, .6); pop(0.35, 500, .2); pop(1.05, 800, .2); pop(1.3, 1000, .15)
for i in range(5): ding(1.3 + i * .12, 72 + i * 2)
whoosh(3.0, .7)
for i in range(7): pop(U(1.4 + i * .18), 500 + i * 60)
for i in range(5): ding(U(1.0 + i * .18), 72 + i * 2)
pop(U(3.6), 1200, .2); pop(U(4.7)); pop(U(3.4)); pop(U(2.2))
pop(8.0, 700, .2); ding(9.3, 88)
for i in range(60): pop(13.4 + (i / 60) ** .8 * 4.6, 700 + (i % 7) * 120, .06)
for t in (12.9, 16.1, 16.8, 17.5, 18.1): pop(t, 1100, .2)
for i in range(28): click(20.7 + i * 1.4 / 28)
pop(22.15, 600, .25)
for i in range(7): pop(22.6 + i * .42, 800 + i * 70, .12)
for t in (23.4, 24.1, 24.8): ding(t, 91)
ding(26.1, 84); ding(26.5, 91)

# ---- narracao ----
def load(p):
    w = wave.open(p); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    if w.getnchannels() > 1: x = x[::w.getnchannels()]
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
voice = np.zeros(N); mask = np.zeros(N)
for name, t in (('n1', .6), ('n2', 7.4), ('n3', 12.4), ('n4', 20.0), ('n5', 26.0)):
    x = load(os.path.join(A, name + '.wav'))
    x = x / (np.abs(x).max() + 1e-9) * .9
    # leve realce de presenca
    x = x + .35 * (x - lp(x, 1800))
    add(voice, x, t)
    i = int(t * SR); mask[i:i + len(x)] = 1
# ducking suave da musica sob a voz
k = int(.15 * SR); kern = np.hanning(k * 2) / np.hanning(k * 2).sum()
duck = 1 - .5 * np.clip(np.convolve(mask, kern, mode='same'), 0, 1)
mix = music * duck * .75 + sfx * .9 + voice * 1.0
mix = np.tanh(mix * 1.1) / 1.1
mix /= max(1e-9, np.abs(mix).max()) / .92
st = np.stack([mix, mix], 1)
# leve efeito estereo na musica
dl = int(.012 * SR)
st[dl:, 1] = mix[:-dl] * .95 + st[dl:, 1] * .05
out = (np.clip(st, -1, 1) * 32767).astype(np.int16)
w = wave.open(os.path.join(os.path.dirname(A), 'mix.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
print('ok', len(out) / SR)
