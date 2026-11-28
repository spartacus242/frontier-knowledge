"""The edge of the known: a silent film for frontierknowledge.org.

Every element is a pure function of time t (seconds), so frames can be
rendered in any order and in parallel. Run:
    python3 render.py out.mp4            # full film
    python3 render.py --still 30 a.png   # one frame
"""
import math, sys, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
T_END = 98.0
HW, HH = W // 2, H // 2

SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

BG = np.array([7, 11, 20], np.float32) / 255
INNER = np.array([22, 36, 74], np.float32) / 255
INNER_HI = np.array([40, 58, 108], np.float32) / 255
AMBER = np.array([245, 182, 96], np.float32) / 255
GOLD = np.array([255, 214, 150], np.float32) / 255
TEXT = (238, 242, 250)
MUTED = (150, 162, 190)
AMBER8 = (245, 182, 96)

C = np.array([800.0, 480.0])  # world centre of the known


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def smoother(x):
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)

def back(x, s=1.9):
    """ease out with a playful overshoot"""
    x = clamp(x)
    x -= 1
    return 1 + x * x * ((s + 1) * x + s)

def ramp(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def window(t, a, b, f=0.5):
    """1 inside [a,b] with fades of f seconds"""
    return smooth(ramp(t, a, a + f)) * (1 - smooth(ramp(t, b - f, b)))

def angdiff(a, b):
    return (a - b + math.pi) % (2 * math.pi) - math.pi


# ---------------------------------------------------------------- story data
rng = random.Random(7)

TH_G = -0.30   # Gauss: how do the primes thin out?
TH_R = 0.22    # Riemann hypothesis
TH_F = 0.95    # the far shape that comes into reach

BUMPS = []      # (theta, t0, dur, height, width)
QUESTIONS = []  # dicts
PROBES = []     # ambient wandering lights
STREAMERS = []  # the swarm


def add_q(theta, ts, ta=None, off=34.0, label=None, key=None, fixed=None, fade=None):
    q = dict(theta=theta, ts=ts, ta=ta, off=off, label=label, key=key, fixed=fixed, fade=fade)
    QUESTIONS.append(q)
    return q


def answer(q, ta, h, w, dur=1.3):
    q["ta"] = ta
    BUMPS.append((q["theta"], ta - 0.15, dur, h, w))


# first ring of questions, 12.5 s on
first = [-2.75, -1.95, -1.25, TH_G, 0.62, 1.15, 1.85, 2.45, 3.08]
order = [4, 0, 6, 2, 8, 3, 1, 7, 5]
QA = {}
for i, k in enumerate(order):
    th = first[k]
    QA[th] = add_q(th, 12.7 + i * 0.42, key="G" if th == TH_G else None)

# answer one: up-left
answer(QA[-1.95], 20.4, 105, 0.30)
for j, (dth, ts) in enumerate([(-0.30, 21.9), (0.27, 22.3), (0.0, 22.75)]):
    add_q(-1.95 + dth, ts, off=34 if dth else 40)
# answer two: down-right
answer(QA[1.15], 25.2, 90, 0.28)
for dth, ts in [(-0.25, 26.5), (0.26, 26.9), (0.02, 27.3)]:
    add_q(1.15 + dth, ts)

# the primes
G = QA[TH_G]
G["label"] = "How do the primes thin out?"
BUMPS.append((TH_R + 0.05, 40.6, 2.2, 80, 0.20))            # 1859, Riemann's step
RH = add_q(TH_R + 0.05, 42.2, label="Do all its zeros lie on one line?", key="R", off=36)
answer(G, 47.4, 92, 0.24, dur=1.8)                             # 1896

# far shapes: questions nobody can ask yet
far = []
for k, xy in enumerate([None, (1390, 700), (1520, 250), (1720, 560), (1250, 110),
                        (1640, 905), (1830, 170), (1230, 960)]):
    th = TH_F if xy is None else math.atan2(xy[1] - C[1], xy[0] - C[0])
    xy = (0, 0) if xy is None else xy
    far.append(add_q(th, 60.8 + 0.3 * k, key="far%d" % k, fixed=np.array(xy, float),
                     fade=(60.8 + 0.3 * k, 74.0 if k else None)))
FAR_F = far[0]
BUMPS.append((TH_F, 67.6, 2.6, 140, 0.24))  # the edge reaches the nearest one

# the swarm: 78 s on, the known grows fast and questions pop everywhere
SW0, SW1 = 79.5, 91.0
for q in QUESTIONS:
    if q["ta"] is None and q is not RH and (q["fade"] is None or q is FAR_F):
        if q["ts"] < 70:
            q["ta"] = rng.uniform(81, 88.5)

for i in range(80):
    ts = rng.uniform(80.5, 88.8)
    add_q(rng.uniform(-math.pi, math.pi), ts, ta=ts + rng.uniform(0.6, 1.5))
for i in range(26):  # the questions left waiting at the end
    th = -math.pi + (i + rng.uniform(0.2, 0.8)) * 2 * math.pi / 26
    add_q(th, 89.6 + rng.uniform(0, 1.8), off=30)

# ambient probes
def add_probe(t0, dur, th, out, wig, seed):
    PROBES.append(dict(t0=t0, dur=dur, th=th, out=out, wig=wig, seed=seed))

t = 6.5
while t < 18.0:
    add_probe(t, rng.uniform(2.6, 3.8), rng.uniform(-math.pi, math.pi), rng.uniform(70, 170), rng.uniform(0.1, 0.25), rng.random() * 6)
    t += rng.uniform(0.7, 1.2)
t = 26
while t < 31:
    add_probe(t, rng.uniform(2.6, 3.4), rng.uniform(-math.pi, math.pi), rng.uniform(60, 140), 0.15, rng.random() * 6)
    t += 1.3
t = 69.5
while t < 77:
    add_probe(t, rng.uniform(2.6, 3.6), rng.uniform(-math.pi, math.pi), rng.uniform(60, 150), 0.18, rng.random() * 6)
    t += rng.uniform(0.8, 1.2)
# the curious one that goes far out and finds nothing it can hold
add_probe(62.0, 4.4, 0.42, 300, 0.05, 1.0)

# directed probes that answer questions in the early scenes
DIRECTED = [(QA[-1.95], 18.6), (QA[1.15], 23.6)]

for i in range(230):
    ts = rng.uniform(79.2, 88.0)
    STREAMERS.append(dict(ts=ts, dur=rng.uniform(1.1, 1.8), x0=rng.uniform(-200, W + 200),
                          th=rng.uniform(-math.pi, math.pi), drift=rng.uniform(-0.05, 0.05),
                          r=rng.uniform(3, 16), ph=rng.random() * 6.28, b=rng.uniform(0.55, 1.0)))


# ---------------------------------------------------------------- the edge
def base_R(t):
    r = 250 * back(ramp(t, 0.3, 2.4), 1.2) + 0.9 * max(0.0, t - 3)
    r += 470 * smoother(ramp(t, SW0, SW1))
    return r

def wobble(th, t):
    return (0.055 * np.sin(3 * th + 0.35 * t + 1.0) + 0.035 * np.sin(5 * th - 0.55 * t + 2.0)
            + 0.02 * np.sin(7 * th + 0.9 * t) + 0.045 * np.sin(2 * th + 0.22 * t + 4.0))

def radius(th, t):
    """edge radius at angle(s) th (numpy or float)"""
    th = np.asarray(th, dtype=np.float64)
    r = base_R(t) * (1 + wobble(th, t))
    for (b, t0, dur, h, w) in BUMPS:
        if t <= t0:
            continue
        g = back(ramp(t, t0, t0 + dur), 1.4)
        d = (th - b + np.pi) % (2 * np.pi) - np.pi
        r = r + h * g * np.exp(-(d / w) ** 2) * (1 - 0.65 * smoother(ramp(t, SW0, SW1)))
    return r


FAR_F["fixed"] = C + np.array([math.cos(TH_F), math.sin(TH_F)]) * (float(radius(TH_F, 60.8)) + 150)


# ---------------------------------------------------------------- camera
def camera(t):
    cx, cy, z = 960.0, 540.0, 1.0
    a = smoother(ramp(t, 31.5, 34.0)) * (1 - smoother(ramp(t, 59.0, 61.5)))
    cx += (1120 - 960) * a; cy += (470 - 540) * a; z += 0.4 * a
    b = smoother(ramp(t, 79.0, 92.0))
    cx += (C[0] - 960) * b; cy += (C[1] + 10 - 540) * b; z += (0.6 - 1.0) * b
    # gentle drift so nothing is ever quite still
    cx += 6 * math.sin(t * 0.21); cy += 4 * math.sin(t * 0.17 + 1)
    return cx, cy, z

def to_screen(p, cam):
    cx, cy, z = cam
    return ((p[0] - cx) * z + W / 2, (p[1] - cy) * z + H / 2)


# ---------------------------------------------------------------- static layers
YS, XS = np.mgrid[0:HH, 0:HW].astype(np.float32)
XS = XS * 2 + 1.0
YS = YS * 2 + 1.0

srng = np.random.default_rng(3)
STARS = np.zeros((H, W), np.float32)
for _ in range(1600):
    x, y = srng.integers(0, W), srng.integers(0, H)
    STARS[y, x] += srng.uniform(0.05, 0.35)
STARS = np.asarray(Image.fromarray((np.clip(STARS, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255 * 2.2
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
SCRIM = np.exp(-((_xx - 300) / 1150) ** 2 - ((_yy - (H - 120)) / 270) ** 2)[..., None]
del _yy, _xx
GRAIN = (srng.random((H, W, 1), dtype=np.float32) - 0.5) * (1.4 / 255)

# constellation of the known (world space)
nrng = np.random.default_rng(11)
pts = []
while len(pts) < 1500:
    p = nrng.uniform(-1250, 1250, 2)
    if np.hypot(*p) < 1250:
        pts.append(p + C)
NODES = np.array(pts)
d2 = ((NODES[:, None, :] - NODES[None, :, :]) ** 2).sum(-1)
EDGES = set()
for i in range(len(NODES)):
    for j in np.argsort(d2[i])[1:4]:
        if d2[i, j] < 95 ** 2:
            EDGES.add((min(i, j), max(i, j)))
EDGES = np.array(sorted(EDGES))
TWINK = nrng.random(len(NODES)) * 6.28


def sprite(r):
    s = int(r * 3.2) + 2
    y, x = np.mgrid[-s:s + 1, -s:s + 1].astype(np.float32)
    return np.exp(-(x * x + y * y) / (2 * r * r))

SPRITES = {k: sprite(k / 2) for k in range(2, 40)}


def add_glow(buf, x, y, r, color, inten):
    if inten <= 0.003:
        return
    k = int(clamp(round(r * 2), 2, 39))
    sp = SPRITES[k]
    s = sp.shape[0] // 2
    xi, yi = int(round(x)), int(round(y))
    x0, x1, y0, y1 = xi - s, xi + s + 1, yi - s, yi + s + 1
    if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
        return
    sx0, sy0 = max(0, -x0), max(0, -y0)
    sx1, sy1 = sp.shape[1] - max(0, x1 - W), sp.shape[0] - max(0, y1 - H)
    sub = sp[sy0:sy1, sx0:sx1, None] * (color * inten)
    buf[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] += sub


def blend(buf, img, x, y, alpha=1.0):
    """composite an RGBA float image (0..1) with top-left at x, y"""
    if alpha <= 0.003:
        return
    h, w = img.shape[:2]
    x, y = int(round(x)), int(round(y))
    if x >= W or y >= H or x + w <= 0 or y + h <= 0:
        return
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = w - max(0, x + w - W), h - max(0, y + h - H)
    sub = img[sy0:sy1, sx0:sx1]
    a = sub[..., 3:4] * alpha
    tgt = buf[y + sy0:y + sy1, x + sx0:x + sx1]
    tgt *= (1 - a)
    tgt += sub[..., :3] * a


# ---------------------------------------------------------------- glyphs and text
def rgba(im):
    return np.asarray(im, np.float32) / 255


def make_q_sprites():
    f = ImageFont.truetype(SERIF_B, 96)
    out = []
    for blur in [0, 3, 7, 12, 18, 26]:
        pad = 70
        im = Image.new("RGBA", (64 + 2 * pad, 100 + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.text((pad + 32, pad + 50), "?", font=f, fill=(255, 205, 130, 255), anchor="mm")
        glow = im.filter(ImageFilter.GaussianBlur(14 + blur))
        ga = np.asarray(glow, np.float32)
        ga[..., 3] *= 0.85
        sharp = im.filter(ImageFilter.GaussianBlur(blur)) if blur else im
        sa = np.asarray(sharp, np.float32)
        a = np.clip(sa[..., 3:4] / 255 + ga[..., 3:4] / 255 * (1 - sa[..., 3:4] / 255), 0, 1)
        col = np.where(sa[..., 3:4] > 0, sa[..., :3], ga[..., :3])
        a = a / max(1e-3, float(a.max())) * [1.0, 0.92, 0.84, 0.76, 0.7, 0.64][len(out)]
        arr = np.concatenate([col / 255, a], -1).astype(np.float32)
        out.append(Image.fromarray((arr * 255).astype(np.uint8), "RGBA"))
    return out

Q_SPRITES = make_q_sprites()
_qcache = {}

def q_img(level, size):
    key = (level, size)
    if key not in _qcache:
        im = Q_SPRITES[level]
        w = max(4, int(im.width * size / 100))
        h = max(4, int(im.height * size / 100))
        _qcache[key] = rgba(im.resize((w, h), Image.LANCZOS))
        if len(_qcache) > 3000:
            _qcache.clear()
    return _qcache[key]


def text_block(lines, font, fill, shadow=True, spacing=1.18, tag=None, tagfont=None):
    asc, desc = font.getmetrics()
    lh = int((asc + desc) * spacing)
    widths = [font.getlength(l) for l in lines]
    th = 0
    if tag:
        th = int(sum(tagfont.getmetrics()) * 1.6)
    pad = 40
    w = int(max(widths + ([tagfont.getlength(tag)] if tag else []))) + 2 * pad
    h = lh * len(lines) + th + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = pad
    if tag:
        d.text((pad, y), tag, font=tagfont, fill=AMBER8 + (255,))
        y += th
    for l in lines:
        d.text((pad, y), l, font=font, fill=fill + (255,))
        y += lh
    arr = rgba(im)
    if shadow:
        a = im.split()[3].filter(ImageFilter.GaussianBlur(14))
        sa = np.asarray(a, np.float32)[..., None] / 255 * 0.75
        base = np.zeros_like(arr)
        base[..., :3] = BG
        base[..., 3:4] = np.clip(sa * 1.6, 0, 0.8)
        a2 = arr[..., 3:4]
        out = np.empty_like(arr)
        out[..., 3:4] = a2 + base[..., 3:4] * (1 - a2)
        out[..., :3] = (arr[..., :3] * a2 + base[..., :3] * base[..., 3:4] * (1 - a2)) / np.maximum(out[..., 3:4], 1e-4)
        arr = out
    return arr, pad


F_CAP = ImageFont.truetype(SERIF, 58)
F_TAG = ImageFont.truetype(MONO, 30)
F_LABEL = ImageFont.truetype(SANS, 31)
F_BIG = ImageFont.truetype(SERIF, 124)
F_SUB = ImageFont.truetype(SERIF, 50)
F_URL = ImageFont.truetype(MONO, 34)

CAPTIONS = [
    (1.6, 6.6, ["This is everything we know."], None),
    (7.1, 12.2, ["Out here is everything", "we don't know yet."], None),
    (12.7, 18.6, ["Every open question", "sits right on the edge."], None),
    (19.0, 24.6, ["Answer one,", "and what we know grows."], None),
    (25.0, 31.0, ["The edge grows too,", "and new questions appear along it."], None),
    (33.6, 39.8, ["Gauss and Legendre guess", "how the primes thin out."], "1790s"),
    (40.2, 46.4, ["Riemann links the primes to the", "zeros of one function. A new question appears."], "1859"),
    (46.8, 52.8, ["Gauss's guess is proved:", "the prime number theorem."], "1896"),
    (53.2, 59.6, ["The Riemann hypothesis is still open.", "Before 1859, nobody could even ask it."], "TODAY"),
    (61.6, 66.8, ["Far past the edge are questions", "we can't even ask yet."], None),
    (67.2, 72.6, ["We'd have no way to understand them.", "Each answer brings a few within reach."], None),
    (73.0, 78.6, ["So every question we can work on today", "sits on the edge. The big ones too."], None),
    (79.0, 84.8, ["And now anyone with an AI agent", "can work on it."], None),
    (85.2, 90.6, ["Ask questions. Answer them.", "Check each other's work."], None),
]
CAP_IMG = [text_block(l, F_CAP, TEXT, tag=tg, tagfont=F_TAG) for (_, _, l, tg) in CAPTIONS]
LABEL_IMG = {}
for q in QUESTIONS:
    if q["label"]:
        LABEL_IMG[q["key"]] = text_block([q["label"]], F_LABEL, (226, 232, 246))
LABEL_RH, _ = text_block(["The Riemann hypothesis"], F_TAG, AMBER8)
END_BIG = text_block(["The edge is open."], F_BIG, TEXT)
END_SUB = text_block(["Come move it with us."], F_SUB, (226, 232, 246))
END_URL = text_block(["frontierknowledge.org"], F_URL, AMBER8)


# ---------------------------------------------------------------- dynamic pieces
def q_pos(q, tt, t=None):
    t = tt if t is None else t
    bob = 4 * math.sin(t * 2.2 + q["ts"] * 5.1)
    if q["fixed"] is not None:   # far shapes are fixed in the world
        return q["fixed"] + np.array([3 * math.sin(t * 0.9 + q["ts"]), bob])
    r = float(radius(q["theta"], tt)) + q["off"]
    th = q["theta"] + 0.012 * math.sin(t * 1.3 + q["ts"] * 3)
    return C + np.array([math.cos(th), math.sin(th)]) * (r + bob)


def q_state(q, t):
    """position (world), scale, alpha for a question at time t, or None"""
    if t < q["ts"]:
        return None
    if q["fade"] is not None:
        a0, a1 = q["fade"]
        alpha = smooth(ramp(t, a0, a0 + 1.2))
        if a1 is not None:
            alpha *= 1 - smooth(ramp(t, a1 - 1.0, a1))
    else:
        alpha = 1.0
    tt = t if q["ta"] is None else min(t, q["ta"])
    p = q_pos(q, tt, t)
    scale = back(ramp(t, q["ts"], q["ts"] + 0.55), 2.6)
    if q["ta"] is not None and t > q["ta"]:
        k = ramp(t, q["ta"] + 0.15, q["ta"] + 0.55)
        if k >= 1:
            return None
        scale *= 1 + 0.4 * math.sin(math.pi * min(1, (t - q["ta"]) / 0.4)) * (1 - k)
        alpha *= 1 - smooth(k)
    edge_d = math.hypot(*(p - C)) - float(radius(math.atan2(p[1] - C[1], p[0] - C[0]), t))
    return p, scale, alpha, edge_d


def bursts(t):
    """sparkles where questions were answered"""
    for q in QUESTIONS:
        ta = q["ta"]
        if ta is None or not (ta + 0.1 <= t <= ta + 1.6):
            continue
        p = q_pos(q, ta)
        k = clamp((t - ta - 0.1) / 1.5)
        n = 12
        for i in range(n):
            a = i * 2 * math.pi / n + q["ts"]
            sp = 70 + 40 * ((i * 7) % 5) / 4
            dist = sp * (1 - (1 - k) ** 3)
            yield p + np.array([math.cos(a), math.sin(a)]) * dist, 1.6, (1 - k) ** 1.5 * 0.9, GOLD
        yield p, 9 * (1 - k) + 2, (1 - k) ** 2 * 1.3, GOLD


def probe_pos(pr, s, t):
    th = pr["th"] + pr["wig"] * math.sin(s * 2 * math.pi * 1.5 + pr["seed"])
    re = float(radius(th, t))
    sn = max(0.0, math.sin(math.pi * s))
    out = pr["out"] * sn ** 0.8
    rr = re * 0.72 + (re * 0.28 + out) * sn ** 0.6
    rr += 10 * math.sin(s * 17 + pr["seed"])
    return C + np.array([math.cos(th), math.sin(th)]) * rr


def lights(t):
    """all the small moving lights: (world pos, radius, intensity, colour)"""
    for pr in PROBES:
        s = (t - pr["t0"]) / pr["dur"]
        if 0 <= s <= 1:
            fade = smooth(min(s, 1 - s) * 6)
            for k in range(7):
                tk = t - k * 0.035
                sk = (tk - pr["t0"]) / pr["dur"]
                if sk < 0:
                    break
                yield probe_pos(pr, sk, tk), 3.2 - 0.35 * k, fade * (1.1 if k == 0 else 0.35 * (1 - k / 7)), GOLD
    for q, t0 in DIRECTED:
        ta = q["ta"]
        if t0 <= t <= ta + 0.1:
            r_end = float(radius(q["theta"], ta)) + q["off"]
            end = C + np.array([math.cos(q["theta"]), math.sin(q["theta"])]) * r_end
            start = C + np.array([math.cos(q["theta"] + 0.9), math.sin(q["theta"] + 0.9)]) * 90
            for k in range(8):
                tk = t - k * 0.03
                s = smoother(ramp(tk, t0, ta))
                ctrl = C + np.array([math.cos(q["theta"] - 0.5), math.sin(q["theta"] - 0.5)]) * (r_end * 1.25)
                p = (1 - s) ** 2 * start + 2 * (1 - s) * s * ctrl + s * s * end
                p = p + np.array([math.sin(tk * 9), math.cos(tk * 7)]) * 6 * (1 - s)
                yield p, 3.6 - 0.35 * k, (1.2 if k == 0 else 0.4 * (1 - k / 8)) * smooth(ramp(t, t0, t0 + 0.3)), GOLD
    for st in STREAMERS:
        if t < st["ts"]:
            continue
        s = smoother(ramp(t, st["ts"], st["ts"] + st["dur"]))
        th = st["th"] + st["drift"] * max(0.0, t - st["ts"] - st["dur"])
        edge = C + np.array([math.cos(th), math.sin(th)]) * (float(radius(th, t)) + st["r"] + 4 * math.sin(t * 3 + st["ph"]))
        cam = camera(st["ts"])
        start = np.array([(st["x0"] - W / 2) / cam[2] + cam[0], (H + 60 - H / 2) / cam[2] + cam[1]])
        p = start * (1 - s) + edge * s
        p = p + np.array([math.sin(t * 5 + st["ph"]), math.cos(t * 4 + st["ph"])]) * 18 * (1 - s) * s * 4
        dim = 1 - 0.55 * smooth(ramp(t, 91, 93))
        yield p, 2.6, st["b"] * dim * (0.9 if s >= 1 else 1.1), GOLD


# ---------------------------------------------------------------- frame
def render(t):
    cam = camera(t)
    cx, cy, z = cam
    # field at half resolution, in world coordinates
    wx = (XS - W / 2) / z + cx - C[0]
    wy = (YS - H / 2) / z + cy - C[1]
    d = np.sqrt(wx * wx + wy * wy)
    th = np.arctan2(wy, wx)
    NA = 2048
    angs = np.linspace(-np.pi, np.pi, NA, endpoint=False)
    rt = radius(angs, t).astype(np.float32)
    idx = ((th + np.pi) / (2 * np.pi) * NA).astype(np.int32) % NA
    r = rt[idx]
    s = (d - r) * z                         # screen px from the edge, + outside
    inside = 1 / (1 + np.exp(np.clip(s / 1.3, -40, 40)))
    depth = np.clip(-s / (260 * z + 1e-3), 0, 1)

    col = np.empty((HH, HW, 3), np.float32)
    col[:] = BG
    lit = INNER_HI * (1 - depth[..., None]) ** 2 + INNER * (1 - (1 - depth[..., None]) ** 2)
    col = col * (1 - inside[..., None]) + lit * inside[..., None]
    pulse = 1 + 0.08 * math.sin(t * 2.4)
    line = np.exp(-(s / 2.2) ** 2) * 1.0 * pulse
    glow_in = np.exp(-np.clip(-s, 0, None) / 26) * inside * 0.20
    glow_out = np.exp(-np.clip(s, 0, None) / 55) * (1 - inside) * 0.16 * pulse
    col += AMBER * (line + glow_in + glow_out)[..., None]

    full = np.empty((H, W, 3), np.float32)
    for c in range(3):
        full[..., c] = np.asarray(Image.fromarray(col[..., c]).resize((W, H), Image.BILINEAR))
    insf = np.asarray(Image.fromarray(inside.astype(np.float32)).resize((W, H), Image.BILINEAR))

    # faint stars in the dark
    full += (STARS * (1 - insf) * (0.7 + 0.3 * math.sin(t * 0.7)))[..., None] * np.array([0.6, 0.7, 1.0], np.float32)

    # the constellation inside the known
    net = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(net)
    sp = (NODES - [cx, cy]) * z + [W / 2, H / 2]
    vis = (sp[:, 0] > -100) & (sp[:, 0] < W + 100) & (sp[:, 1] > -100) & (sp[:, 1] < H + 100)
    for i, j in EDGES:
        if vis[i] or vis[j]:
            dr.line([tuple(sp[i]), tuple(sp[j])], fill=34, width=1)
    tw = 0.55 + 0.45 * np.sin(t * 1.7 + TWINK)
    for i in np.nonzero(vis)[0]:
        x, y = sp[i]
        v = int(70 + 110 * tw[i])
        dr.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=v)
    netf = np.asarray(net, np.float32) / 255 * insf
    endfade = 1 - 0.45 * smooth(ramp(t, 91, 93.5))
    full += netf[..., None] * np.array([0.55, 0.68, 1.0], np.float32) * endfade

    # moving lights
    for p, rad, inten, colr in list(lights(t)) + list(bursts(t)):
        x, y = to_screen(p, cam)
        add_glow(full, x, y, max(1.2, rad * (0.5 + 0.5 * z)) * 2.4, colr, inten * 0.35)
        add_glow(full, x, y, max(1.0, rad * (0.5 + 0.5 * z)) * 0.8, colr, inten)

    # question marks
    prime_focus = window(t, 32.5, 60.0, 1.2)
    rh_pulse = window(t, 42.2, 60.0, 0.8)
    for q in QUESTIONS:
        stt = q_state(q, t)
        if stt is None:
            continue
        p, scale, alpha, ed = stt
        if q["key"] not in ("G", "R"):
            alpha *= 1 - 0.65 * prime_focus
        if q["fade"] is not None:
            # blurrier and dimmer the further from the edge
            alpha *= clamp(1.05 - (ed - 40) / 900, 0.75, 1)
            if q["key"] == "far1":   # the probe reaches it and it slips away
                alpha *= 1 - smooth(ramp(t, 63.6, 64.6))
        if q["fixed"] is not None:
            lvl = clamp((ed - 40) / 110, 0, 4)
            alpha *= 0.75 + 0.25 * math.sin(t * 3.1 + q["ts"] * 7)
            grow = 1 + 0.3 * clamp((ed - 40) / 300)
        else:
            lvl = clamp((ed - 45) / 75, 0, 5)
            grow = 1
        size = int(round(66 * z * scale * grow))
        if size < 3 or alpha <= 0.01:
            continue
        x, y = to_screen(p, cam)
        l0 = int(lvl)
        l1 = min(5, l0 + 1)
        fr = lvl - l0
        for lv, wgt in ((l0, 1 - fr), (l1, fr)):
            if wgt < 0.02:
                continue
            img = q_img(lv, size)
            blend(full, img, x - img.shape[1] / 2, y - img.shape[0] / 2, alpha * wgt)
        if q["key"] == "R" and rh_pulse > 0:
            k = (t * 0.9) % 1
            for a in np.linspace(0, 2 * np.pi, 48, endpoint=False):
                rr = (24 + 46 * k) * z
                add_glow(full, x + rr * math.cos(a), y + rr * math.sin(a), 1.4, AMBER, 0.25 * (1 - k) * rh_pulse)

    # labels in the primes story
    for q in QUESTIONS:
        if not q["label"]:
            continue
        stt = q_state(q, t)
        if stt is None:
            continue
        p, scale, alpha, _ = stt
        if q["key"] == "G":
            la = window(t, 34.2, 47.6, 0.6)
        else:
            la = window(t, 43.0, 59.6, 0.6)
        img, pad = LABEL_IMG[q["key"]]
        x, y = to_screen(p, cam)
        blend(full, img, x + 34 - pad, y - 24 - pad, la)
        if q["key"] == "R":
            blend(full, LABEL_RH, x + 34 - 40, y + 14 - 40, window(t, 53.6, 59.6, 0.6))

    # captions, over a soft dark scrim
    sc = max(window(t, a, b, 0.55) for (a, b, _, _) in CAPTIONS)
    if sc > 0:
        full *= 1 - 0.62 * sc * SCRIM
    for (a, b, _, _), (img, pad) in zip(CAPTIONS, CAP_IMG):
        al = window(t, a, b, 0.55)
        if al > 0:
            rise = 10 * (1 - smooth(ramp(t, a, a + 0.8)))
            blend(full, img, 110 - pad, H - 110 - img.shape[0] + pad + rise, al)

    # the end card, inside the known
    if t > 91:
        for (img, pad), (dy, t0) in zip((END_BIG, END_SUB, END_URL), ((-95, 91.6), (40, 92.6), (120, 93.4))):
            al = smooth(ramp(t, t0, t0 + 0.9))
            rise = 14 * (1 - smooth(ramp(t, t0, t0 + 1.2)))
            sx, sy = to_screen(C, cam)
            blend(full, img, sx - img.shape[1] / 2, sy + dy - img.shape[0] / 2 + rise, al)

    # fade in from black, gentle fade at the very end
    full *= smooth(ramp(t, 0, 0.8)) * (1 - 0.0 * smooth(ramp(t, T_END - 0.6, T_END)))
    full += GRAIN
    return (np.clip(full, 0, 1) * 255 + 0.5).astype(np.uint8)


def _frame(i):
    return render(i / FPS).tobytes()


def main():
    if sys.argv[1] == "--still":
        t = float(sys.argv[2])
        Image.fromarray(render(t)).save(sys.argv[3])
        return
    out = sys.argv[1]
    n = int(T_END * FPS)
    crf = sys.argv[2] if len(sys.argv) > 2 else "22"
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", crf, "-tune", "animation",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    from multiprocessing import Pool
    with Pool(4) as pool:
        for k, buf in enumerate(pool.imap(_frame, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if k % 300 == 0:
                print("frame", k, "/", n, flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
