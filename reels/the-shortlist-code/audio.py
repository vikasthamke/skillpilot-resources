"""Voice-over processing, synthesized music bed and sound effects for the reel.

Writes build/mix.wav (48 kHz stereo, -14 LUFS, -1 dBTP). Every effect is
generated here with numpy, so the mix has no third-party audio to license.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
SR = 48000
DUR = 29.0
N = int(SR * DUR)
rng = np.random.default_rng(7)


def ff(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def read_wav(path):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def db(x):
    return 10 ** (x / 20)


# ---------- voice-over ----------
def process_voice():
    chain = ",".join([
        "highpass=f=80",                                  # rumble
        "afftdn=nf=-45:tn=1",                             # light broadband denoise
        "equalizer=f=250:t=q:w=1.2:g=-2.5",               # mud
        "bass=g=1.5:f=120",                               # a little warmth
        "equalizer=f=3500:t=q:w=1.0:g=2.5",               # presence
        "deesser=i=0.35:m=0.5:f=0.5",
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2",
        "alimiter=limit=0.89",
    ])
    ff("-i", str(ROOT / "audio/voiceover-raw.mp3"), "-af", chain, "-ar", str(SR), "-ac", "1", str(BUILD / "vo_clean.wav"))
    # two-pass loudness to -16 LUFS for the voice stem
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(BUILD / "vo_clean.wav"), "-af",
                          "loudnorm=I=-16:TP=-2:LRA=7:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    ff("-i", str(BUILD / "vo_clean.wav"), "-af",
       f"loudnorm=I=-16:TP=-2:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
       f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
       "-ar", str(SR), str(BUILD / "vo_norm.wav"))
    v = read_wav(BUILD / "vo_norm.wav")
    out = np.zeros(N)
    out[:min(N, len(v))] = v[:N]
    return out


# ---------- small DSP helpers ----------
def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip((f - lo * .7) / (lo * .3 + 1e-9), 0, 1) * np.clip((hi * 1.3 - f) / (hi * .3), 0, 1)
    return np.fft.irfft(X * m, len(x))


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


def add(buf, t0, sig, gain_db=0.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * db(gain_db)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


# ---------- sound effects ----------
def thump(strength=1.0):
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 50 + 70 * np.exp(-t / .05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .12)
    click = band(rng.standard_normal(n), 800, 5000) * np.exp(-t / .012) * .5
    paper = band(rng.standard_normal(n), 1500, 7000) * env_ad(n, .003, .06) * .35
    return norm(body + click + paper) * strength


def whoosh(d=.35, lo=600, hi=5000):
    n = int(d * SR)
    w = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return norm(band(rng.standard_normal(n), lo, hi) * w)


def scribble(d=.3):
    n = int(d * SR); t = np.arange(n) / SR
    am = .55 + .45 * np.sin(2 * np.pi * (26 + 8 * np.sin(2 * np.pi * 3 * t)) * t)
    fade = np.minimum(1, t / .02) * np.minimum(1, (d - t) / .04)
    return norm(band(rng.standard_normal(n), 2200, 7500) * am * fade)


def pop(f0=900):
    n = int(.12 * SR); t = np.arange(n) / SR
    f = f0 * (1 - .4 * (1 - np.exp(-t / .02)))
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, .002, .03))


def tick():
    n = int(.03 * SR)
    return norm(band(rng.standard_normal(n), 2000, 9000) * env_ad(n, .0005, .004))


def key():
    n = int(.06 * SR)
    x = band(rng.standard_normal(n), 1200, 5000) * env_ad(n, .0005, .008)
    x += band(rng.standard_normal(n), 300, 1200) * env_ad(n, .001, .015) * .5
    return norm(x) * rng.uniform(.6, 1.0)


def bell(freqs, d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (.35 / (k + 1))) * (.6 ** k) for k, f in enumerate(freqs))
    return norm(x * np.minimum(1, t / .003))


def page_flip():
    n = int(.42 * SR); t = np.arange(n) / SR
    am = .6 + .4 * np.sin(2 * np.pi * 17 * t)
    w = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return norm(band(rng.standard_normal(n), 900, 8000) * am * w + band(rng.standard_normal(n), 150, 600) * w * .3)


def riser(d=.8):
    n = int(d * SR); t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 2500, 9000) * (t / d) ** 2
    s = np.sin(2 * np.pi * np.cumsum(300 + 900 * (t / d) ** 2) / SR) * (t / d) ** 2 * .25
    return norm(x + s)


def shimmer(d=.9):
    n = int(d * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (2093, 2637, 3136, 4186))
    return norm(x * env_ad(n, .01, .25))


def sfx_track():
    s = np.zeros(N)
    add(s, 0.0, thump(), -9)                                     # STOP stamp
    for i in range(5):                                           # same resume to every job
        t0 = 1.0 + i * .26
        add(s, t0, whoosh(.28, 1500, 7000), -24)
        add(s, t0 + .38, tick(), -22)
        add(s, 2.72 + i * .27, scribble(.14), -24)               # "no reply"
    add(s, 3.95, scribble(.4), -22)                              # circling the 0
    for t0 in (4.42, 10.88, 18.0, 21.7):
        add(s, t0, page_flip(), -15)
    for t0 in (6.30, 7.58, 8.28):
        add(s, t0, scribble(.5), -21)                            # red pen circles
    add(s, 9.3, riser(.8) * .6, -26)                             # recruiter scan
    add(s, 10.22, thump(.9), -9)                                 # NOT SHORTLISTED
    add(s, 11.6, riser(.77), -23)
    add(s, 12.37, thump(.6), -16)                                # cover lands
    add(s, 12.4, shimmer(), -27)
    add(s, 13.55, pop(700), -18)                                 # logo sticker
    add(s, 14.22, pop(520), -17)
    for i in range(6):
        add(s, 14.24 + i * .11, pop(800 + i * 90), -21)          # six templates
    for i in range(9):
        add(s, 14.45 + i * .055, key(), -24)                     # typing "Your Name"
    for i in range(3):
        add(s, 14.9 + i * .1, tick(), -20)                       # locks
    add(s, 15.62, whoosh(.3), -24)
    add(s, 15.98, whoosh(.35), -22)
    for i in range(3):
        add(s, 16.35 + i * .15, pop(1300 + i * 150), -24)        # checks
        add(s, 17.05 + i * .2, whoosh(.3, 800, 6000), -25)       # guide cards
    for t0 in (18.63, 18.95, 19.25):
        add(s, t0, whoosh(.22, 3000, 9000), -25)                 # highlighter
    add(s, 19.45, whoosh(.3, 600, 4000), -27)
    for i in range(3):
        add(s, 19.6 + i * .3, scribble(.16), -24)                # strike old bullet
        add(s, 19.8 + i * .3, pop(1100), -25)
    add(s, 20.4, whoosh(.25), -27)
    add(s, 20.58, whoosh(.25), -27)
    add(s, 20.95, bell([1318.5, 2637]), -19)                     # matched
    add(s, 21.03, bell([1975.5, 3951]), -21)
    add(s, 22.43, whoosh(.35), -24)
    add(s, 23.72, tick(), -14)                                   # mouse click
    add(s, 23.95, thump(.5), -18)                                # sticky note slap
    add(s, 23.95, whoosh(.2, 1500, 7000), -22)
    add(s, 24.42, whoosh(.35), -22)
    for i in range(6):
        add(s, 24.88 + i * .075, key(), -20)                     # typing RESUME
    add(s, 25.36, pop(900), -16)                                 # send
    add(s, 25.62, pop(1500), -22)                                # heart
    add(s, 25.72, bell([1760, 2637]), -17)                       # DM arrives
    add(s, 26.5, whoosh(.4), -22)
    add(s, 26.8, thump(.7), -13)                                 # RESUME lands
    add(s, 26.82, shimmer(1.2), -24)
    add(s, 27.2, scribble(.45), -24)                             # arrow
    return s


# ---------- music bed ----------
def music_track():
    bpm = 100
    beat = 60 / bpm
    bar = 4 * beat
    t = np.arange(N) / SR
    m = np.zeros(N)
    # Am7 - Fmaj7 - Cmaj7 - G6, one chord per bar
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 59, 64], [55, 59, 62, 64]]
    hz = lambda k: 440 * 2 ** ((k - 69) / 12)
    nbars = int(DUR / bar) + 1
    for b in range(nbars):
        c = chords[b % 4]
        i0, i1 = int(b * bar * SR), min(N, int((b + 1) * bar * SR) + int(.3 * SR))
        if i0 >= N:
            break
        tt = np.arange(i1 - i0) / SR
        e = np.minimum(1, tt / .35) * np.minimum(1, np.maximum(0, (i1 - i0) / SR - tt) / .3)
        pad = sum(np.sin(2 * np.pi * hz(k) * tt) + .3 * np.sin(2 * np.pi * hz(k) * 2.003 * tt) for k in c)
        m[i0:i1] += pad * e * .05
        # plucked arpeggio, eighth notes
        for s8 in range(8):
            k = c[[0, 2, 1, 3, 2, 1, 3, 2][s8]] + 12
            j0 = i0 + int(s8 * beat / 2 * SR)
            n = int(.4 * SR)
            if j0 + n > N:
                continue
            tp = np.arange(n) / SR
            pl = (np.sin(2 * np.pi * hz(k) * tp) + .25 * np.sin(2 * np.pi * hz(k) * 2 * tp)) * env_ad(n, .003, .12)
            m[j0:j0 + n] += pl * .07
        # bass
        bn = int(bar * SR) if i0 + int(bar * SR) <= N else N - i0
        tb = np.arange(bn) / SR
        m[i0:i0 + bn] += np.sin(2 * np.pi * hz(c[0] - 12) * tb) * np.minimum(1, tb / .02) * np.exp(-tb / 1.4) * .12
    # light drums once the product is introduced, until the end card
    for k in range(int(DUR / beat * 2)):
        t0 = k * beat / 2
        if not (11.45 <= t0 < 26.4):
            continue
        if k % 2 == 0:
            n = int(.25 * SR); tk = np.arange(n) / SR
            kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-tk / .03)) / SR) * np.exp(-tk / .09)
            add(m, t0, kick * .22)
        else:
            add(m, t0, tick() * .05)
    # gentle intro swell and outro fade
    m *= np.minimum(1, t / .6) * np.clip((DUR - t) / 1.6, 0, 1)
    return m


def duck(music, voice):
    win = int(.05 * SR)
    e = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
    target = 1 - .55 * np.clip(e / .05, 0, 1)
    # smooth gain changes (~120 ms)
    k = int(.12 * SR)
    g = np.convolve(target, np.ones(k) / k, mode="same")
    return music * g


def main():
    BUILD.mkdir(exist_ok=True)
    vo = process_voice()
    mus = duck(music_track(), vo)
    mus *= db(-31) / (np.sqrt(np.mean(mus[int(12 * SR):int(20 * SR)] ** 2)) + 1e-9)  # bed sits ~-31 dBFS RMS under the voice
    sfx = sfx_track()
    # light stereo: music widened with a short Haas delay, voice centred
    d = int(.012 * SR)
    musR = np.concatenate([np.zeros(d), mus[:-d]])
    L = vo + mus + sfx
    R = vo + musR + sfx
    st = np.stack([L, R], 1).astype(np.float32)
    raw = BUILD / "mix_raw.f32"
    st.tofile(raw)
    out = subprocess.run(["ffmpeg", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(raw), "-af",
                          "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    ff("-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(raw), "-af",
       f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
       f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
       "-ar", str(SR), str(BUILD / "mix.wav"))
    raw.unlink()
    print("mix written:", BUILD / "mix.wav")


if __name__ == "__main__":
    main()
