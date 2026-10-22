"""Trilha do anúncio de 30s: música sintetizada (numpy), efeitos sincronizados e narração (Kokoro)."""
import wave, numpy as np, os
SR = 44100
D = 30.0
N = int(SR * D)
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'narracao')
rng = np.random.default_rng(7)

def tt(n): return np.arange(n) / SR
def env(n, a=.005, r=.2):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, min(n, int(r * SR)))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr)
    return e
def add(buf, x, t):
    i = int(t * SR)
    if i >= len(buf) or i < 0: return
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y
def midi(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- música (120 bpm: 1 compasso = 2 s) ----------------
music = np.zeros(N)
BEAT = 0.5
prog = [(48, [48, 52, 55]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])]  # C G Am F
def kick():
    n = int(.3 * SR); t = tt(n); f = 120 * np.exp(-t * 22) + 44
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * .95
def hat(open_=False):
    n = int((.16 if open_ else .05) * SR); x = rng.standard_normal(n); x = x - np.concatenate([[0], x[:-1]]) * .95
    return x * np.exp(-tt(n) * (28 if open_ else 80)) * (.2 if open_ else .17)
def clap():
    n = int(.2 * SR); x = rng.standard_normal(n); x = lp(x, 6000) - lp(x, 600)
    return x * np.exp(-tt(n) * 18) * .5
def pluck(m, dur=.22):
    n = int(dur * SR); t = tt(n); f = midi(m)
    x = np.sin(2 * np.pi * f * t) + .5 * np.sign(np.sin(2 * np.pi * f * 1.004 * t)) * .3
    return x * np.exp(-t * 13) * .15
def bass(m, dur=.42):
    n = int(dur * SR); t = tt(n); f = midi(m - 12)
    return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * env(n, .008, .1) * .42
def pad(notes, dur):
    n = int(dur * SR); t = tt(n); x = np.zeros(n)
    for m in notes:
        f = midi(m + 12)
        for d in (-.4, 0, .4): x += np.sin(2 * np.pi * f * (1 + d * .003) * t)
    return x * env(n, .5, .7) * .034

bars = int(D / (4 * BEAT))
for b in range(bars):
    t0 = b * 4 * BEAT
    root, ch = prog[b % 4]
    add(music, pad(ch, 4 * BEAT + .3), t0)
    if t0 >= 1.5:                      # a "luz acende" no segundo 1.5: entra a batida
        for k in range(4): add(music, bass(root), t0 + k * BEAT)
    if t0 >= 1.5:
        for k in range(8): add(music, hat(k % 4 == 3), t0 + k * BEAT / 2 + BEAT / 4)
        for k in range(4): add(music, kick(), t0 + k * BEAT)
        add(music, clap(), t0 + BEAT); add(music, clap(), t0 + 3 * BEAT)
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        for k in range(16):
            n = ch[pat[k % 8] % 3] + (12 if k % 8 >= 4 else 24)
            add(music, pluck(n), t0 + k * BEAT / 4)
# compasso 0 (0–2 s) e antes do hit de 1.5: só pad escuro + kick sozinho em 1.5 (compasso novo começa em 2.0)
add(music, kick() * 1.2, 1.5)         # o hit da "luz acendendo"; a batida completa entra no compasso seguinte (2.0 s)
# riser até o hit
n = int(1.5 * SR); r = rng.standard_normal(n); r = lp(r, 5000) - lp(r, 300); r *= np.linspace(0, 1, n) ** 2.2 * .35
add(music, r, 0.05)
# riser para o final + hit em 27.2
n = int(2.2 * SR); r = rng.standard_normal(n); r = lp(r, 5000) - lp(r, 300); r *= np.linspace(0, 1, n) ** 2 * .3
add(music, r, 25.0)
add(music, kick() * 1.3, 27.2)
add(music, pad([48, 52, 55, 60], 3.2) * 3.2, 27.2)
# na cena final a batida cai pela metade (só pad + arp leve): abaixa a música a partir de 27.2
fade = np.ones(N); fo = int(1.4 * SR); fade[-fo:] = np.linspace(1, 0, fo)
fade[:int(.3 * SR)] = np.linspace(0, 1, int(.3 * SR))
music *= fade

# ---------------- efeitos sincronizados com a animação ----------------
sfx = np.zeros(N)
def whoosh(t, dur=.55, vol=.5):
    n = int(dur * SR); x = rng.standard_normal(n); x = lp(x, 4500) - lp(x, 450)
    add(sfx, x * np.sin(np.linspace(0, np.pi, n)) ** 2 * vol, t)
def pop(t, f=900, vol=.14):
    n = int(.11 * SR); tm = tt(n)
    add(sfx, np.sin(2 * np.pi * (f + 700 * tm * 9) * tm) * np.exp(-tm * 38) * vol, t)
def click(t, vol=.14):
    n = int(.03 * SR); x = rng.standard_normal(n); add(sfx, x * np.exp(-tt(n) * 200) * vol, t)
def tick(t, f=1700, vol=.07):
    n = int(.03 * SR); tm = tt(n); add(sfx, np.sin(2 * np.pi * f * tm) * np.exp(-tm * 160) * vol, t)
def ding(t, m=84, vol=.13):
    n = int(.9 * SR); tm = tt(n)
    add(sfx, (np.sin(2 * np.pi * midi(m) * tm) + .4 * np.sin(2 * np.pi * midi(m + 12) * tm)) * np.exp(-tm * 5) * vol, t)
def coin(t, vol=.14):
    n = int(.5 * SR); tm = tt(n)
    x = np.sin(2 * np.pi * 1976 * tm) * (tm < .09) + np.sin(2 * np.pi * 2637 * tm) * (tm >= .09)
    add(sfx, x * np.exp(-tm * 7) * vol, t)
def boom(t, vol=.9):
    n = int(1.1 * SR); tm = tt(n); f = 90 * np.exp(-tm * 3.2) + 30
    add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm * 3) * vol, t)
def sparkle(t, vol=.06):
    for i in range(5):
        f = 2400 + rng.integers(0, 2600); n = int(.18 * SR); tm = tt(n)
        add(sfx, np.sin(2 * np.pi * f * tm) * np.exp(-tm * 25) * vol, t + i * .035)
def snip(t):
    click(t, .2); click(t + .07, .2)
def confetti_pop(t, vol=.3):
    n = int(.35 * SR); x = rng.standard_normal(n); x = lp(x, 7000) - lp(x, 800)
    add(sfx, x * np.exp(-tt(n) * 12) * vol, t); add(sfx, np.sin(2 * np.pi * 180 * tt(n)) * np.exp(-tt(n) * 30) * .4, t)
def stinger(t, notes, vol=.07):
    for k, m in enumerate(notes):
        n = int(1.0 * SR); tm = tt(n)
        add(sfx, (np.sin(2 * np.pi * midi(m) * tm) + .3 * np.sin(4 * np.pi * midi(m) * tm)) * np.exp(-tm * 3.5) * vol, t + k * .06)

# transições
for s in (3.12, 6.88, 11.06, 14.68, 18.12, 20.78, 24.32): whoosh(s - .24)
# 1 · gancho
boom(1.5); ding(1.52, 79, .16); stinger(1.5, [72, 76, 79, 84], .06)
for i in range(30): tick(1.55 + (i / 30) ** .9 * .5 + rng.random() * .02, 1500 + (i % 6) * 260, .06)
for i in range(10): sparkle(1.6 + i * .12)
pop(.2, 300, .1)
# 2 · busca
pop(3.25, 600, .2); pop(4.0, 900, .2); pop(4.62, 700, .2); pop(4.05, 1100, .15)
for i in range(14): tick(4.85 + i * .65 / 14, 2000, .08)
tick(4.67, 2200); tick(4.73, 2200)
for i in range(18):                                   # slot machine desacelerando
    tk = 5.2 + (1 - (1 - i / 17) ** 2.2) * .8
    tick(tk, 1200 + 40 * i, .1)
pop(5.05, 1000, .22); pop(5.9, 1300, .15)
click(6.15, .22); pop(6.2, 500, .2); coin(6.32)
# 3 · resultados
for i in range(6): pop(7.2 + i * .36, 750 + i * 60, .14)
for i in range(24): tick(7.1 + (i / 24) ** .8 * 2.5, 1400 + (i % 5) * 100, .05)
snip(9.05); snip(9.25); pop(9.38, 400, .2); pop(8.9, 1000, .2); ding(9.4, 91, .1)
# 4 · filtro + CSV
pop(11.5, 800, .18); click(12.05, .22); pop(12.15, 1200, .15)
click(13.25, .22); pop(13.3, 500, .2); whoosh(13.4, .7, .5); ding(14.1, 88, .12); sparkle(14.1, .06)
# 5 · biblioteca
pop(14.9, 700, .18)
for i in range(7): tick(15.2 + i * .32, 1500 + 90 * i, .12)
for i in range(8): pop(14.95 + i * .1, 600 + i * 70, .09)
ding(16.2, 88, .13); sparkle(16.3); pop(16.0, 1000, .22)
pop(17.0, 800, .22); whoosh(16.95, .35, .35)
click(17.55, .22); ding(17.72, 91, .13)
# 6 · CRM
for i in range(5): pop(18.3 + i * .07, 600 + i * 90, .1)
whoosh(18.9, 1.0, .35)
pop(18.55, 900, .2)
for i in range(4): tick(19.0 + i * .25, 1400, .08)
confetti_pop(20.05); coin(20.07, .18); coin(20.2, .14); stinger(20.05, [72, 76, 79], .06); pop(20.1, 1100, .2)
# 7 · e mais
for t0, m in ((20.9, 84), (21.75, 86), (22.65, 88), (23.25, 89), (23.6, 91), (23.95, 93)):
    pop(t0, 800 + (m - 84) * 30, .2); sparkle(t0 + .1, .05); ding(t0 + .02, m, .07)
# 8 · planos + CTA
for t0 in (24.65, 25.15, 25.65): pop(t0, 600, .2); click(t0 + .1, .14)
ding(25.3, 91, .08)
boom(27.2, .8); ding(27.22, 84, .15); stinger(27.2, [72, 76, 79, 84], .06)
pop(27.45, 900, .2); pop(27.85, 700, .22)
click(29.15, .25); pop(29.17, 500, .25); confetti_pop(29.15, .35); ding(29.2, 91, .16); ding(29.3, 96, .1); sparkle(29.3, .07)

# ---------------- narração ----------------
def load(p):
    w = wave.open(p); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    if w.getnchannels() > 1: x = x[::w.getnchannels()]
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
voice = np.zeros(N); mask = np.zeros(N)
# (clipe, início da fala em s, ataque medido no arquivo)
for name, t, onset in (('n1', .25, .05), ('n2', 3.23, .03), ('n3', 6.94, .04), ('n4', 11.14, .04),
                       ('n5', 14.74, .04), ('n6', 18.19, .04), ('n7', 20.83, .03), ('n8', 24.39, .04)):
    x = load(os.path.join(A, name + '.wav'))
    x = x / (np.abs(x).max() + 1e-9) * .92
    x = x + .3 * (x - lp(x, 1800))               # presença
    add(voice, x, t - onset)
    i = int((t - onset) * SR); mask[i:i + len(x)] = 1
k = int(.12 * SR); kern = np.hanning(k * 2) / np.hanning(k * 2).sum()
duck = 1 - .55 * np.clip(np.convolve(mask, kern, mode='same'), 0, 1)
mix = music * duck * .72 + sfx * .85 + voice * 1.0
mix = np.tanh(mix * 1.1) / 1.1
mix /= max(1e-9, np.abs(mix).max()) / .92
st = np.stack([mix, mix], 1)
dl = int(.012 * SR); st[dl:, 1] = mix[:-dl] * .95 + st[dl:, 1] * .05     # leve abertura estéreo
out = (np.clip(st, -1, 1) * 32767).astype(np.int16)
w = wave.open(os.path.join(HERE, 'mix.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
print('ok', len(out) / SR)
