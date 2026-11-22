# -*- coding: utf-8 -*-
"""
KELİME YAĞMURU — İngilizce kelime yazma oyunu (modern arayüz)

Kurulum : pip install pygame          (sorun çıkarsa: pip install pygame-ce)
Çalıştır: python kelime_yagmuru.py

Oynanış:
  - Üstten içinde İngilizce kelime yazan kartlar düşer.
  - Alttaki sabit kutuya klavyeden yazarsın.
  - Hedef her zaman EN ALTTAKİ karttır; sabit kutuyla arasında ışık hattı çekilir.
  - Kelime birebir yazılınca kart parçalanarak patlar, hat bir üstteki karta geçer.
  - Kart kırmızı çizgiye değerse bir can gider.

Kısayollar:
  Enter            : Başlat / yanlış yazılanı sil
  ESC              : Duraklat / devam
  F11              : Tam ekran aç / kapat
  Backspace        : Son harfi sil      Ctrl+Backspace : Hepsini sil
  Başlık çubuğunu sürükleyerek pencereyi taşıyabilirsin (çift tık: tam ekran).

Kendi kelimelerin için bu dosyanın yanına "words.txt" koy.
Her satır:  kelime;Türkçe anlamı      (örnek:  apple;elma)
"""

import os
import sys
import math
import random
import warnings
from collections import deque

# Windows'ta bulanık görüntüyü önlemek için (ekran ölçekleme %125/%150 vb.)
if sys.platform == "win32":
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

# ------------------------------------------------------------------ tasarım ölçüleri
# Her şey 800 piksel yüksekliğe göre tasarlandı, ekrana göre ölçeklenir.
BASE_H = 800
TITLE_H = 40
MARGIN = 16
SIDE_W = 296
HUD_H = 60
BOX_H = 46
INPUT_W, INPUT_H = 520, 62
FPS = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BEST_FILE = os.path.join(BASE_DIR, "kelime_yagmuru_rekor.txt")
WORDS_FILE = os.path.join(BASE_DIR, "words.txt")

# ------------------------------------------------------------------ renkler
BG_TOP = (8, 10, 24)
BG_BOT = (15, 9, 30)
TEXT = (240, 244, 255)
MUTED = (150, 158, 194)
FAINT = (96, 104, 140)
CYAN = (56, 189, 248)
VIOLET = (139, 92, 246)
PINK = (236, 72, 153)
MINT = (52, 211, 153)
RED = (244, 63, 94)
AMBER = (251, 191, 36)
WHITE = (255, 255, 255)

SANS = ["segoeui", "inter", "helveticaneue", "dejavusans", "liberationsans", "freesans"]
SEMI = ["segoeuisemibold", ("segoeui", True), ("inter", True), ("dejavusans", True), ("liberationsans", True)]
BLACK = ["segoeuiblack", ("segoeui", True), "arialblack", ("dejavusans", True)]
NUM = ["bahnschrift", "segoeuisemibold", ("segoeui", True), ("dejavusans", True)]

# ------------------------------------------------------------------ kelimeler
WORDS = {
    "Kolay": [
        ("cat", "kedi"), ("dog", "köpek"), ("apple", "elma"), ("house", "ev"),
        ("water", "su"), ("book", "kitap"), ("chair", "sandalye"), ("table", "masa"),
        ("door", "kapı"), ("window", "pencere"), ("tree", "ağaç"), ("sun", "güneş"),
        ("moon", "ay"), ("star", "yıldız"), ("bird", "kuş"), ("fish", "balık"),
        ("milk", "süt"), ("bread", "ekmek"), ("car", "araba"), ("road", "yol"),
        ("city", "şehir"), ("friend", "arkadaş"), ("school", "okul"),
        ("teacher", "öğretmen"), ("river", "nehir"), ("green", "yeşil"),
        ("happy", "mutlu"), ("small", "küçük"), ("big", "büyük"), ("fast", "hızlı"),
        ("slow", "yavaş"), ("cold", "soğuk"), ("hot", "sıcak"), ("rain", "yağmur"),
        ("snow", "kar"), ("red", "kırmızı"), ("blue", "mavi"), ("money", "para"),
        ("phone", "telefon"), ("music", "müzik"), ("egg", "yumurta"), ("hand", "el"),
    ],
    "Orta": [
        ("weather", "hava durumu"), ("journey", "yolculuk"), ("knowledge", "bilgi"),
        ("library", "kütüphane"), ("mountain", "dağ"), ("kitchen", "mutfak"),
        ("village", "köy"), ("answer", "cevap"), ("question", "soru"),
        ("important", "önemli"), ("different", "farklı"), ("believe", "inanmak"),
        ("remember", "hatırlamak"), ("forget", "unutmak"), ("decide", "karar vermek"),
        ("improve", "geliştirmek"), ("explain", "açıklamak"),
        ("compare", "karşılaştırmak"), ("borrow", "ödünç almak"),
        ("healthy", "sağlıklı"), ("dangerous", "tehlikeli"), ("comfortable", "rahat"),
        ("expensive", "pahalı"), ("success", "başarı"), ("future", "gelecek"),
        ("history", "tarih"), ("science", "bilim"), ("language", "dil"),
        ("energy", "enerji"), ("opinion", "fikir"), ("neighbor", "komşu"),
        ("purpose", "amaç"), ("surprise", "sürpriz"), ("environment", "çevre"),
        ("experience", "deneyim"), ("government", "hükümet"),
        ("necessary", "gerekli"), ("argue", "tartışmak"), ("prepare", "hazırlamak"),
        ("discover", "keşfetmek"),
    ],
    "Zor": [
        ("ambiguous", "belirsiz"), ("meticulous", "titiz"), ("resilient", "dayanıklı"),
        ("ubiquitous", "her yerde bulunan"), ("ephemeral", "geçici, kısa ömürlü"),
        ("inevitable", "kaçınılmaz"), ("perseverance", "azim, sebat"),
        ("conscientious", "vicdanlı, özenli"), ("eloquent", "güzel konuşan"),
        ("scrutinize", "dikkatle incelemek"), ("deteriorate", "kötüleşmek"),
        ("comprehensive", "kapsamlı"), ("controversial", "tartışmalı"),
        ("reluctant", "isteksiz"), ("phenomenon", "olgu, fenomen"),
        ("hypothesis", "hipotez"), ("infrastructure", "altyapı"),
        ("entrepreneur", "girişimci"), ("acquaintance", "tanıdık"),
        ("accommodate", "barındırmak, uyum sağlamak"), ("consequence", "sonuç"),
        ("vulnerable", "savunmasız"), ("benevolent", "iyiliksever"),
        ("diligent", "çalışkan"), ("tenacious", "azimli, inatçı"),
        ("unprecedented", "eşi görülmemiş"), ("mitigate", "hafifletmek"),
        ("obsolete", "modası geçmiş"), ("pervasive", "yaygın"),
        ("candid", "açık sözlü"), ("frugal", "tutumlu"),
        ("ostentatious", "gösterişli"), ("gregarious", "girişken, sosyal"),
        ("ambivalent", "karışık duygulu, kararsız"), ("substantial", "önemli, büyük"),
    ],
}


def load_custom_words():
    if not os.path.exists(WORDS_FILE):
        return []
    out = []
    try:
        with open(WORDS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                en, _, tr = line.partition(";")
                if en.strip():
                    out.append((en.strip(), tr.strip()))
    except OSError:
        return []
    return out


def load_best():
    try:
        with open(BEST_FILE, encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_best(v):
    try:
        with open(BEST_FILE, "w", encoding="utf-8") as f:
            f.write(str(v))
    except OSError:
        pass


# ------------------------------------------------------------------ yardımcılar
def clamp(v, a, b):
    return max(a, min(b, v))


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def mul(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c[:3])


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_out_back(t):
    c1 = 1.70158
    return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2


def rgba(c, a=255):
    return tuple(c) if len(c) == 4 else (c[0], c[1], c[2], a)


def normalize(s, case_sensitive):
    """Büyük/küçük harf duyarsız modda Türkçe klavyedeki İ/ı farkını da yok sayar."""
    if case_sensitive:
        return s
    return s.replace("İ", "i").replace("I", "i").replace("ı", "i").lower()


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    a, b, c, d = u * u * u, 3 * u * u * t, 3 * u * t * t, t * t * t
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
            a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def gradient(w, h, c1, c2, horizontal=True):
    w, h = max(1, int(w)), max(1, int(h))
    c1, c2 = rgba(c1), rgba(c2)
    n = w if horizontal else h
    line = pygame.Surface((n, 1) if horizontal else (1, n), pygame.SRCALPHA)
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0
        line.set_at((i, 0) if horizontal else (0, i), tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2)))
    return pygame.transform.scale(line, (w, h))


def aa_rrect(w, h, r, color, width=0, ss=3):
    """Kenarları yumuşatılmış (antialias) yuvarlak köşeli dikdörtgen."""
    w, h = max(1, int(w)), max(1, int(h))
    c = rgba(color)
    big = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    big.fill((c[0], c[1], c[2], 0))
    bw = max(1, int(round(width * ss))) if width else 0
    pygame.draw.rect(big, c, (0, 0, w * ss, h * ss), bw, border_radius=int(r * ss))
    return pygame.transform.smoothscale(big, (w, h))


def masked(surf, mask):
    out = surf.copy()
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def blur(surf, k=6):
    w, h = surf.get_size()
    k = max(2, int(k))
    sw, sh = max(1, w // k), max(1, h // k)
    s = pygame.transform.smoothscale(surf, (sw, sh))
    s = pygame.transform.smoothscale(s, (max(1, sw // 2), max(1, sh // 2)))
    s = pygame.transform.smoothscale(s, (sw, sh))
    s = pygame.transform.smoothscale(s, (w, h))
    off = int(round(0.6 * k))          # ölçekleme sağ-alta kaydırıyor, geri al
    s.scroll(-off, -off)
    return s


_GLOW_BASE = None


def glow_base():
    global _GLOW_BASE
    if _GLOW_BASE is None:
        n = 128
        s = pygame.Surface((n, n))
        s.fill((0, 0, 0))
        steps = 64
        for i in range(steps):
            t = i / steps
            v = int(255 * t ** 2.2)
            pygame.draw.circle(s, (v, v, v), (n // 2, n // 2), max(1, int((n / 2) * (1 - t))))
        _GLOW_BASE = s
    return _GLOW_BASE


def heart_sprite(size, color):
    ss = 4
    n = size * ss
    big = pygame.Surface((n, n), pygame.SRCALPHA)
    big.fill((*color[:3], 0))
    pts = []
    for i in range(72):
        t = 2 * math.pi * i / 72
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((n / 2 + x * n / 35, n / 2 + n * 0.05 - y * n / 35))
    pygame.draw.polygon(big, rgba(color), pts)
    return pygame.transform.smoothscale(big, (size, size))


_FONT_PATHS = {}


def load_font(specs, px):
    key = tuple(specs)
    if key not in _FONT_PATHS:
        _FONT_PATHS[key] = None
        for sp in specs:
            name, bold = (sp, False) if isinstance(sp, str) else sp
            try:
                p = pygame.font.match_font(name, bold=bold)
            except Exception:
                p = None
            if p:
                _FONT_PATHS[key] = p
                break
    path = _FONT_PATHS[key]
    try:
        return pygame.font.Font(path, px) if path else pygame.font.Font(None, int(px * 1.3))
    except Exception:
        return pygame.font.Font(None, int(px * 1.3))


def get_sdl_window():
    fn = getattr(pygame.display, "get_window", None)  # pygame-ce
    if fn:
        try:
            w = fn()
            if w is not None:
                return w
        except Exception:
            pass
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from pygame._sdl2.video import Window
            return Window.from_display_module()
    except Exception:
        return None


class BRect:
    """Tasarım birimlerinde (ölçeklenmemiş) dikdörtgen."""
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h


# ------------------------------------------------------------------ panel bileşenleri
class Widget:
    height = 0

    def layout(self, g, x, y, w):
        self.g, self.x, self.y, self.w = g, x, y, w

    def handle(self, ev):
        return False

    def hovering(self, pos):
        return False

    def update(self, dt):
        pass


class Slider(Widget):
    height = 48

    def __init__(self, label, minv, maxv, value, step, fmt):
        self.label, self.minv, self.maxv = label, minv, maxv
        self.value, self.step, self.fmt = value, step, fmt
        self.drag = False

    def layout(self, g, x, y, w):
        super().layout(g, x, y, w)
        self.track = pygame.Rect(x, y + g.S(30), w, max(3, g.S(4)))
        self.hit = self.track.inflate(g.S(18), g.S(26))

    def hovering(self, pos):
        return self.drag or self.hit.collidepoint(pos)

    def _set(self, mx):
        t = clamp((mx - self.track.x) / self.track.w, 0, 1)
        v = self.minv + t * (self.maxv - self.minv)
        self.value = clamp(round(v / self.step) * self.step, self.minv, self.maxv)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.hit.collidepoint(ev.pos):
            self.drag = True
            self._set(ev.pos[0])
            return True
        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.drag = False
        elif ev.type == pygame.MOUSEMOTION and self.drag:
            self._set(ev.pos[0])
            return True
        return False

    def draw(self, s):
        g = self.g
        lbl = g.text("label", self.label, TEXT)
        s.blit(lbl, (self.x, self.y))
        vt = g.text("value", self.fmt(self.value), CYAN)
        pw, ph = vt.get_width() + g.S(14), vt.get_height() + g.S(2)
        px, py = self.x + self.w - pw, self.y + (lbl.get_height() - ph) // 2
        s.blit(g.rr(pw, ph, ph // 2, (56, 189, 248, 30)), (px, py))
        s.blit(vt, (px + g.S(7), py + g.S(1)))
        tr = self.track
        s.blit(g.rr(tr.w, tr.h, tr.h // 2, (255, 255, 255, 26)), tr.topleft)
        t = (self.value - self.minv) / (self.maxv - self.minv)
        fill = g.grad_rr(tr.w, tr.h, tr.h // 2, CYAN, VIOLET)
        s.blit(fill, tr.topleft, pygame.Rect(0, 0, max(tr.h, int(tr.w * t)), tr.h))
        kx, kr = tr.x + int(tr.w * t), g.S(8)
        if self.hovering(pygame.mouse.get_pos()):
            gr = g.S(24)
            s.blit(g.glow(gr, mul(CYAN, 0.55)), (kx - gr, tr.centery - gr), special_flags=pygame.BLEND_RGB_ADD)
        s.blit(g.circle(kr, WHITE), (kx - kr, tr.centery - kr))


class Toggle(Widget):
    height = 34

    def __init__(self, label, value):
        self.label, self.value = label, value
        self.anim = 1.0 if value else 0.0

    def layout(self, g, x, y, w):
        super().layout(g, x, y, w)
        self.rect = pygame.Rect(x, y, w, g.S(28))
        sw, sh = g.S(40), g.S(22)
        self.sw = pygame.Rect(x + w - sw, y + (g.S(28) - sh) // 2, sw, sh)

    def hovering(self, pos):
        return self.rect.collidepoint(pos)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            self.value = not self.value
            return True
        return False

    def update(self, dt):
        self.anim += ((1.0 if self.value else 0.0) - self.anim) * min(1, dt * 14)

    def draw(self, s):
        g, sw = self.g, self.sw
        lbl = g.text("label", self.label, TEXT)
        s.blit(lbl, (self.x, self.rect.centery - lbl.get_height() // 2))
        s.blit(g.rr(sw.w, sw.h, sw.h // 2, (255, 255, 255, 30)), sw.topleft)
        on = g.grad_rr(sw.w, sw.h, sw.h // 2, CYAN, VIOLET)
        on.set_alpha(int(255 * self.anim))
        s.blit(on, sw.topleft)
        on.set_alpha(255)
        kr = (sw.h - g.S(6)) // 2
        kx = int(lerp(sw.x + g.S(3) + kr, sw.right - g.S(3) - kr, self.anim))
        s.blit(g.circle(kr, WHITE), (kx - kr, sw.centery - kr))


class Segmented(Widget):
    height = 46

    def __init__(self, options, index=0):
        self.options, self.index = options, index
        self.anim_x = None

    @property
    def value(self):
        return self.options[self.index]

    def layout(self, g, x, y, w):
        super().layout(g, x, y, w)
        self.rect = pygame.Rect(x, y, w, g.S(36))
        self.seg_w = w / len(self.options)
        self.anim_x = None

    def hovering(self, pos):
        return self.rect.collidepoint(pos)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            self.index = clamp(int((ev.pos[0] - self.x) / self.seg_w), 0, len(self.options) - 1)
            return True
        return False

    def update(self, dt):
        tx = self.x + self.index * self.seg_w
        self.anim_x = tx if self.anim_x is None else self.anim_x + (tx - self.anim_x) * min(1, dt * 16)

    def draw(self, s):
        g, r = self.g, self.rect
        s.blit(g.rr(r.w, r.h, g.S(10), (255, 255, 255, 13)), r.topleft)
        s.blit(g.ring(r.w, r.h, g.S(10), (255, 255, 255, 30), (255, 255, 255, 30), 1), r.topleft)
        pad = g.S(3)
        pw, ph = int(self.seg_w) - 2 * pad, r.h - 2 * pad
        ax = self.anim_x if self.anim_x is not None else self.x
        s.blit(g.grad_rr(pw, ph, g.S(8), CYAN, VIOLET), (int(ax) + pad, r.y + pad))
        for i, opt in enumerate(self.options):
            t = g.text("seg", opt, TEXT if i == self.index else MUTED)
            cx = int(self.x + self.seg_w * (i + 0.5))
            s.blit(t, t.get_rect(center=(cx, r.centery)))


class Button(Widget):
    height = 52

    def __init__(self, text_fn, icon_fn, callback, primary=True):
        self.text_fn, self.icon_fn, self.callback, self.primary = text_fn, icon_fn, callback, primary

    def layout(self, g, x, y, w):
        super().layout(g, x, y, w)
        self.rect = pygame.Rect(x, y, w, g.S(42))

    def hovering(self, pos):
        return self.rect.collidepoint(pos)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            self.callback()
            return True
        return False

    def draw(self, s):
        g, r = self.g, self.rect
        hover = self.hovering(pygame.mouse.get_pos())
        if self.primary:
            gs, p = g.glow_rect(r.w, r.h, g.S(12), g.S(18))
            gl = gs.copy()
            gl.fill(mul(VIOLET, 0.5 if hover else 0.28), special_flags=pygame.BLEND_RGB_MULT)
            s.blit(gl, (r.x - p, r.y - p + g.S(4)), special_flags=pygame.BLEND_RGB_ADD)
            s.blit(g.grad_rr(r.w, r.h, g.S(12), CYAN, VIOLET), r.topleft)
            if hover:
                s.blit(g.rr(r.w, r.h, g.S(12), (255, 255, 255, 26)), r.topleft)
        else:
            s.blit(g.rr(r.w, r.h, g.S(12), (255, 255, 255, 24 if hover else 12)), r.topleft)
            s.blit(g.ring(r.w, r.h, g.S(12), (255, 255, 255, 60), (255, 255, 255, 25), 1), r.topleft)
        t = g.text("button", self.text_fn(), WHITE)
        isz = g.S(13)
        total = isz + g.S(9) + t.get_width()
        x0 = r.centerx - total // 2
        g.icon(s, self.icon_fn(), x0 + isz // 2, r.centery, isz, WHITE)
        s.blit(t, (x0 + isz + g.S(9), r.centery - t.get_height() // 2))


# ------------------------------------------------------------------ oyun nesneleri
class Box:
    def __init__(self, word, meaning, x, y, w):
        self.word, self.meaning = word, meaning
        self.x, self.y, self.w, self.h = x, y, w, BOX_H
        self.cache = None


class Spark:
    def __init__(self, x, y, vx, vy, life, color, size):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max = life
        self.color, self.size = color, size

    def update(self, dt):
        self.vx -= self.vx * 3.2 * dt
        self.vy -= self.vy * 3.2 * dt
        self.vy += 260 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt


class Ring:
    def __init__(self, x, y, rmax, life, color, width):
        self.x, self.y, self.rmax, self.color, self.width = x, y, rmax, color, width
        self.life = self.max = life

    def update(self, dt):
        self.life -= dt


class Flash(Ring):
    pass


class Shard:
    def __init__(self, surf, x, y, vx, vy, va, life):
        self.surf, self.x, self.y, self.vx, self.vy = surf, x, y, vx, vy
        self.ang, self.va = 0.0, va
        self.life = self.max = life

    def update(self, dt):
        self.vy += 900 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.ang += self.va * dt
        self.life -= dt


class Floater:
    def __init__(self, surf, x, y, life, vy=-36):
        self.surf, self.x, self.y, self.vy = surf, x, y, vy
        self.life = self.max = life

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt


class Pop:
    def __init__(self, surf, x, y, life=1.15):
        self.surf, self.x, self.y = surf, x, y
        self.life = self.max = life

    def update(self, dt):
        self.life -= dt


# ------------------------------------------------------------------ oyun
class Game:
    def __init__(self):
        pygame.init()
        self.desktop = self.desktop_size()
        self.levels = dict(WORDS)
        custom = load_custom_words()
        if custom:
            self.levels["Özel"] = custom
        self.best = load_best()
        self.state = "ready"            # ready / play / pause / over
        self.time = 0.0
        self.full = False
        self.win = None
        self.drag_win = None
        self.last_title_click = 0
        self.cursor_kind = None
        self.cta_rect = None
        self.stars = [[random.random(), random.random(), random.uniform(0.004, 0.018),
                       random.uniform(1.2, 2.8), random.uniform(0, 6.28), random.uniform(0.6, 2.2),
                       random.choice([WHITE, CYAN, VIOLET, (200, 210, 255)])] for _ in range(70)]
        self.make_widgets()
        self.reset()
        self.clock = pygame.time.Clock()
        try:
            pygame.display.set_icon(self.make_icon())
        except Exception:
            pass
        pygame.display.set_caption("Kelime Yağmuru")
        self.set_display(False)
        pygame.key.set_repeat(350, 35)
        pygame.key.start_text_input()

    # ---------------------------------------------------------- pencere
    @staticmethod
    def desktop_size():
        try:
            return pygame.display.get_desktop_sizes()[0]
        except Exception:
            info = pygame.display.Info()
            return info.current_w, info.current_h

    def make_icon(self):
        s = masked(gradient(64, 64, CYAN, VIOLET), aa_rrect(64, 64, 16, WHITE))
        f = load_font(BLACK, 40)
        t = f.render("K", True, WHITE)
        s.blit(t, t.get_rect(center=(32, 33)))
        return s

    def set_display(self, full):
        dw, dh = self.desktop
        if full:
            w, h = dw, dh
        else:
            h = int(min(dh * 0.86, dw * 0.86 / 1.6))
            w = int(h * 1.6)
        self.screen = pygame.display.set_mode((w, h), pygame.NOFRAME)
        self.win = get_sdl_window()
        if self.win is not None:
            try:
                self.win.position = (0, 0) if full else ((dw - w) // 2, (dh - h) // 2)
            except Exception:
                pass
        self.full = full
        self.rebuild()

    def rebuild(self):
        self.W, self.H = self.screen.get_size()
        self.U = self.H / BASE_H
        self.BW = self.W / self.U
        self.cache = {}
        self.text_cache = {}
        mk = lambda specs, size: load_font(specs, max(8, int(round(size * self.U))))
        self.F = dict(
            brand=mk(SEMI, 14), brand2=mk(SANS, 12.5), h2=mk(SEMI, 21), sub=mk(SANS, 12.5),
            section=mk(SEMI, 10.5), label=mk(SANS, 13.5), value=mk(SEMI, 11.5), seg=mk(SEMI, 12.5),
            button=mk(SEMI, 14.5), hud_label=mk(SEMI, 10), hud_num=mk(NUM, 26), hud_mid=mk(NUM, 22),
            hud_small=mk(SEMI, 11), word=mk(SEMI, 21), input=mk(SEMI, 28), placeholder=mk(SANS, 17),
            title=mk(BLACK, 54), big=mk(BLACK, 42), body=mk(SANS, 15), body_semi=mk(SEMI, 15),
            float=mk(NUM, 24), mean=mk(SEMI, 15), mean_tr=mk(SANS, 15), combo=mk(BLACK, 40),
            tile_num=mk(NUM, 30), tile_lbl=mk(SEMI, 10), chip=mk(SEMI, 13.5), chip_tr=mk(SANS, 13.5),
            key=mk(SEMI, 10.5), hint=mk(SANS, 12), cta=mk(SEMI, 16), num_small=mk(SEMI, 13),
        )
        # yerleşim (tasarım birimleri)
        px0 = MARGIN + SIDE_W + MARGIN
        self.b_side = BRect(MARGIN, TITLE_H + 12, SIDE_W, BASE_H - TITLE_H - 12 - MARGIN)
        self.b_hud_y = TITLE_H + 12
        self.b_play = BRect(px0, self.b_hud_y + HUD_H + 12, self.BW - MARGIN - px0,
                            BASE_H - MARGIN - (self.b_hud_y + HUD_H + 12))
        cx = self.b_play.x + self.b_play.w / 2
        self.b_input = BRect(cx - INPUT_W / 2, BASE_H - 24 - INPUT_H, INPUT_W, INPUT_H)
        self.danger_b = self.b_input.y - 26
        self.r_side = self.R(self.b_side)
        self.r_play = self.R(self.b_play)
        self.r_input = self.R(self.b_input)
        self.add = pygame.Surface((self.W, self.H)).convert()
        self.bg_base = self.make_bg()
        self.bg_frame, self.bg_time = None, -1.0
        self.layout_widgets()
        for b in self.boxes:
            b.cache = None
        self.over_cache = None

    def S(self, v):
        return max(1, int(round(v * self.U)))

    def px(self, v):
        return int(round(v * self.U))

    def R(self, b):
        return pygame.Rect(self.px(b.x), self.px(b.y), self.px(b.w), self.px(b.h))

    # ---------------------------------------------------------- önbellekli çizim parçaları
    def cached(self, key, fn):
        v = self.cache.get(key)
        if v is None:
            v = self.cache[key] = fn()
        return v

    def text(self, font_key, txt, color):
        key = (font_key, txt, color)
        v = self.text_cache.get(key)
        if v is None:
            if len(self.text_cache) > 3000:
                self.text_cache.clear()
            v = self.text_cache[key] = self.F[font_key].render(txt, True, color)
        return v

    def rr(self, w, h, r, color, width=0):
        return self.cached(("rr", w, h, r, color, width), lambda: aa_rrect(w, h, r, color, width))

    def grad_rr(self, w, h, r, c1, c2, horizontal=True):
        return self.cached(("grr", w, h, r, c1, c2, horizontal),
                           lambda: masked(gradient(w, h, c1, c2, horizontal), aa_rrect(w, h, r, WHITE)))

    def ring(self, w, h, r, c1, c2, width, horizontal=False):
        return self.cached(("ring", w, h, r, c1, c2, width, horizontal),
                           lambda: masked(gradient(w, h, c1, c2, horizontal),
                                          aa_rrect(w, h, r, WHITE, max(1, width * self.U))))

    def glow(self, radius, color):
        radius = max(2, int(radius))
        color = tuple(int(c) for c in color[:3])

        def mk():
            s = pygame.transform.smoothscale(glow_base(), (radius * 2, radius * 2))
            s.fill(color, special_flags=pygame.BLEND_RGB_MULT)
            return s
        return self.cached(("glow", radius, color), mk)

    def glowq(self, radius, color, k):
        lvl = round(clamp(k, 0, 1) * 10) / 10
        return self.glow(radius, mul(color, lvl)) if lvl > 0 else None

    def circle(self, r, color):
        def mk():
            ss = 4
            big = pygame.Surface((r * 2 * ss, r * 2 * ss), pygame.SRCALPHA)
            big.fill((*color[:3], 0))
            pygame.draw.circle(big, rgba(color), (r * ss, r * ss), r * ss)
            return pygame.transform.smoothscale(big, (r * 2, r * 2))
        return self.cached(("circ", r, color), mk)

    def glow_rect(self, w, h, r, spread):
        def mk():
            s = pygame.Surface((w + 2 * spread, h + 2 * spread)).convert()
            s.fill((0, 0, 0))
            pygame.draw.rect(s, WHITE, (spread, spread, w, h), border_radius=r)
            return blur(s, max(2, spread // 5))
        return self.cached(("glr", w, h, r, spread), mk), spread

    def glow_text(self, txt, font, color=None, grad=None, glow_color=None, strength=2):
        t = font.render(txt, True, WHITE if grad else color)
        if grad:
            gsurf = gradient(t.get_width(), t.get_height(), grad[0], grad[1])
            gsurf.blit(t, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            t = gsurf
        gc = glow_color or (mix(grad[0], grad[1], 0.5) if grad else color)
        pad = self.S(16)
        canvas = pygame.Surface((t.get_width() + 2 * pad, t.get_height() + 2 * pad), pygame.SRCALPHA)
        tmp = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
        tmp.fill((*gc, 0))
        tmp.blit(font.render(txt, True, gc), (pad, pad))
        tmp = blur(tmp, max(3, pad // 4))
        for _ in range(strength):
            canvas.blit(tmp, (0, 0))
        canvas.blit(t, (pad, pad))
        return canvas

    def spaced(self, font_key, txt, color, spacing):
        def mk():
            chars = [self.F[font_key].render(c, True, color) for c in txt]
            w = sum(c.get_width() for c in chars) + spacing * (len(chars) - 1)
            surf = pygame.Surface((max(1, w), self.F[font_key].get_height()), pygame.SRCALPHA)
            x = 0
            for c in chars:
                surf.blit(c, (x, 0))
                x += c.get_width() + spacing
            return surf
        return self.cached(("sp", font_key, txt, color, spacing), mk)

    def icon(self, s, kind, cx, cy, size, color):
        h = size / 2
        if kind == "play":
            pygame.draw.polygon(s, color, [(cx - h * 0.7, cy - h), (cx - h * 0.7, cy + h), (cx + h, cy)])
        elif kind == "pause":
            bw = max(2, int(size * 0.28))
            pygame.draw.rect(s, color, (int(cx - h * 0.8), int(cy - h), bw, int(size)), border_radius=1)
            pygame.draw.rect(s, color, (int(cx + h * 0.8) - bw, int(cy - h), bw, int(size)), border_radius=1)
        elif kind == "restart":
            r = pygame.Rect(0, 0, int(size), int(size))
            r.center = (int(cx), int(cy))
            pygame.draw.arc(s, color, r, math.radians(60), math.radians(360), max(2, self.S(2)))
            ax, ay = cx + h * math.cos(math.radians(60)), cy - h * math.sin(math.radians(60))
            a = size * 0.35
            pygame.draw.polygon(s, color, [(ax + a * 0.5, ay - a * 0.6), (ax + a * 0.6, ay + a * 0.55),
                                           (ax - a * 0.55, ay + a * 0.1)])

    def make_bg(self):
        W, H = self.W, self.H
        bg = gradient(W, H, BG_TOP, BG_BOT, horizontal=False).convert()
        dots = pygame.Surface((W, H), pygame.SRCALPHA)
        step = max(12, self.S(30))
        dr = max(1, self.S(1.1))
        for y in range(step // 2, H, step):
            for x in range(step // 2, W, step):
                pygame.draw.circle(dots, (255, 255, 255, 10), (x, y), dr)
        bg.blit(dots, (0, 0))
        return bg

    # ---------------------------------------------------------- panel
    def make_widgets(self):
        self.s_speed = Slider("Düşme hızı", 15, 160, 45, 1, lambda v: f"{v:.0f} px/sn")
        self.s_spawn = Slider("Kart aralığı", 0.8, 5.0, 2.6, 0.1, lambda v: f"{v:.1f} sn")
        self.s_max = Slider("Ekrandaki en fazla kart", 2, 12, 6, 1, lambda v: f"{v:.0f}")
        self.s_lives = Slider("Can (yeni oyunda)", 1, 10, 5, 1, lambda v: f"{v:.0f}")
        self.c_level = Segmented(list(self.levels.keys()) + ["Karışık"], 0)
        self.t_case = Toggle("Büyük/küçük harf duyarlı", True)
        self.t_caps = Toggle("Rastgele büyük harf", False)
        self.t_hint = Toggle("İpucu (soluk yazı)", False)
        self.t_mean = Toggle("Türkçe anlamı göster", True)
        self.t_ramp = Toggle("Zamanla hızlan", True)
        self.t_shake = Toggle("Ekran sarsıntısı", True)
        self.btn_play = Button(self.play_label, self.play_icon, self.play_pressed, True)
        self.btn_reset = Button(lambda: "Yeniden Başlat", lambda: "restart", self.start_game, False)
        self.sections = [("OYUN", [self.s_speed, self.s_spawn, self.s_max, self.s_lives]),
                         ("KELİMELER", [self.c_level, self.t_case, self.t_caps]),
                         ("YARDIM VE EFEKTLER", [self.t_hint, self.t_mean, self.t_ramp, self.t_shake])]
        self.widgets = [w for _, ws in self.sections for w in ws] + [self.btn_play, self.btn_reset]

    def layout_widgets(self):
        x, w = self.b_side.x + 20, self.b_side.w - 40
        y = self.b_side.y + 74
        self.section_pos = []
        for label, ws in self.sections:
            self.section_pos.append((label, self.px(x), self.px(y)))
            y += 24
            for wd in ws:
                wd.layout(self, self.px(x), self.px(y), self.px(w))
                y += wd.height
            y += 4
        yb = self.b_side.bottom - 18 - 42
        self.btn_reset.layout(self, self.px(x), self.px(yb), self.px(w))
        self.btn_play.layout(self, self.px(x), self.px(yb - 52), self.px(w))

    def play_label(self):
        return {"ready": "Başlat", "play": "Duraklat", "pause": "Devam Et", "over": "Yeni Oyun"}[self.state]

    def play_icon(self):
        return "pause" if self.state == "play" else "play"

    def play_pressed(self):
        if self.state in ("ready", "over"):
            self.start_game()
        elif self.state == "play":
            self.state = "pause"
        else:
            self.state = "play"

    # ---------------------------------------------------------- oyun durumu
    def reset(self):
        self.boxes = []
        self.sparks, self.rings, self.flashes = [], [], []
        self.shards, self.floaters, self.pops = [], [], []
        self.input = ""
        self.score, self.disp_score = 0, 0.0
        self.combo = self.best_combo = 0
        self.lives = self.max_lives = int(self.s_lives.value)
        self.correct_words = self.missed_words = 0
        self.missed_list = []
        self.keys_ok = self.keys_total = self.correct_chars = 0
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.recent = deque(maxlen=12)
        self.target = None
        self.link_t = 0.0
        self.shake_amp = self.shake_t = self.shake_T = 0.0
        self.input_shake = 0.0
        self.miss_flash = 0.0
        self.danger_k = 0.0
        self.new_record = False
        self.over_cache = None

    def start_game(self):
        self.reset()
        self.state = "play"

    def game_over(self):
        self.state = "over"
        self.over_cache = None
        if self.score > self.best:
            self.best = self.score
            self.new_record = True
            save_best(self.best)

    @property
    def cs(self):
        return self.t_case.value

    def word_pool(self):
        lvl = self.c_level.value
        if lvl == "Karışık":
            return [w for lst in self.levels.values() for w in lst]
        return self.levels[lvl]

    def current_target(self):
        return max(self.boxes, key=lambda b: b.y) if self.boxes else None

    def speed_mult(self):
        return min(1 + self.elapsed / 90, 3.0) if self.t_ramp.value else 1.0

    def typing_ok(self):
        tgt = self.target
        if not tgt or not self.input:
            return None
        return normalize(tgt.word, self.cs).startswith(normalize(self.input, self.cs))

    # ---------------------------------------------------------- kart üretme
    def spawn(self):
        pool = self.word_pool()
        on_screen = {b.word.lower() for b in self.boxes}
        cands = [p for p in pool if p[0] not in self.recent and p[0].lower() not in on_screen]
        if not cands:
            cands = [p for p in pool if p[0].lower() not in on_screen] or pool
        en, tr = random.choice(cands)
        self.recent.append(en)
        if self.t_caps.value and random.random() < 0.45:
            en = en.capitalize() if random.random() < 0.7 else en.upper()
        w = max(104, self.F["word"].size(en)[0] / self.U + 48)
        y = self.b_play.y - BOX_H - 2
        bp = self.b_play
        for _ in range(30):
            x = random.uniform(bp.x + 22, bp.right - 22 - w)
            r = pygame.Rect(int(x), int(y), int(w), BOX_H).inflate(28, 40)
            if not any(r.colliderect(pygame.Rect(int(b.x), int(b.y), int(b.w), BOX_H)) for b in self.boxes):
                self.boxes.append(Box(en, tr, x, y, w))
                return True
        return False

    # ---------------------------------------------------------- yazma
    def on_text(self, text):
        if self.state != "play":
            return
        tgt = self.current_target()
        for ch in text:
            self.input += ch
            self.keys_total += 1
            if tgt and normalize(tgt.word, self.cs).startswith(normalize(self.input, self.cs)):
                self.keys_ok += 1
        self.input = self.input[:40]
        tgt = self.current_target()
        if tgt and normalize(self.input.strip(), self.cs) == normalize(tgt.word, self.cs):
            self.hit(tgt)

    def add_shake(self, amp, dur):
        if self.t_shake.value:
            self.shake_amp, self.shake_t, self.shake_T = amp, dur, dur

    def hit(self, b):
        self.explode(b, True)
        self.boxes.remove(b)
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)
        mult = 1 + self.combo // 5
        gain = (10 + 2 * len(b.word)) * mult
        self.score += gain
        self.correct_words += 1
        self.correct_chars += len(b.word) + 1
        cx, cy = b.x + b.w / 2, b.y + b.h / 2
        self.floaters.append(Floater(self.glow_text(f"+{gain}", self.F["float"], AMBER), cx, cy - 30, 1.0, -50))
        if self.t_mean.value and b.meaning:
            chip = self.meaning_chip(b.word, b.meaning)
            half = chip.get_width() / 2 / self.U
            x = clamp(cx, self.b_play.x + half + 8, self.b_play.right - half - 8)
            self.floaters.append(Floater(chip, x, cy + 8, 2.0, -26))
        if self.combo % 5 == 0:
            self.pops.append(Pop(self.glow_text(f"SERİ  ×{mult}", self.F["combo"], grad=(AMBER, PINK), strength=3),
                                 self.b_play.x + self.b_play.w / 2, self.b_play.y + self.b_play.h * 0.32))
        self.add_shake(3, 0.12)
        self.input = ""
        self.target = None

    def miss(self, b):
        self.explode(b, False)
        self.boxes.remove(b)
        self.lives -= 1
        self.combo = 0
        self.missed_words += 1
        self.missed_list.append((b.word, b.meaning))
        cx, cy = b.x + b.w / 2, b.y + b.h / 2
        self.floaters.append(Floater(self.glow_text("-1 can", self.F["float"], RED), cx, cy - 30, 1.1, -40))
        self.miss_flash = 0.4
        self.add_shake(9, 0.3)
        self.input = ""
        self.target = None
        if self.lives <= 0:
            self.game_over()

    def meaning_chip(self, word, meaning):
        a = self.F["mean"].render(word, True, CYAN)
        arrow = self.F["mean_tr"].render("  →  ", True, MUTED)
        m = self.F["mean_tr"].render(meaning, True, TEXT)
        padx, h = self.S(14), max(a.get_height(), m.get_height()) + self.S(10)
        w = a.get_width() + arrow.get_width() + m.get_width() + 2 * padx
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.blit(aa_rrect(w, h, h // 2, (14, 18, 40, 225)), (0, 0))
        s.blit(masked(gradient(w, h, rgba(CYAN, 150), rgba(VIOLET, 150)), aa_rrect(w, h, h // 2, WHITE, max(1, self.U))), (0, 0))
        x = padx
        for part in (a, arrow, m):
            s.blit(part, (x, (h - part.get_height()) // 2))
            x += part.get_width()
        return s

    def explode(self, b, success):
        cx, cy = b.x + b.w / 2, b.y + b.h / 2
        main = MINT if success else RED
        palette = [CYAN, VIOLET, MINT, WHITE] if success else [RED, PINK, (255, 150, 120)]
        for _ in range(40 if success else 28):
            a = random.uniform(0, 2 * math.pi)
            sp = random.uniform(140, 520 if success else 380)
            self.sparks.append(Spark(cx + random.uniform(-b.w / 3, b.w / 3), cy + random.uniform(-8, 8),
                                     math.cos(a) * sp, math.sin(a) * sp * 0.7 - 60,
                                     random.uniform(0.35, 0.8), random.choice(palette), random.uniform(1.5, 3.2)))
        self.rings.append(Ring(cx, cy, b.w * 0.75, 0.45, main, 3))
        self.rings.append(Ring(cx, cy, b.w * 1.15, 0.65, VIOLET if success else PINK, 2))
        self.flashes.append(Flash(cx, cy, 95, 0.25, mix(main, WHITE, 0.35), 0))
        # kartı parçalara ayır
        c = self.card_surfaces(b)
        surf = c["target"] if b is self.target else c["normal"]
        pad, w, h = c["pad"], c["w"], c["h"]
        cols = int(clamp(round(b.w / 22), 4, 12))
        rows = 3
        for i in range(cols):
            for j in range(rows):
                x0, x1 = w * i // cols, w * (i + 1) // cols
                y0, y1 = h * j // rows, h * (j + 1) // rows
                piece = surf.subsurface(pygame.Rect(pad + x0, pad + y0, max(1, x1 - x0), max(1, y1 - y0))).copy()
                pcx = b.x + (x0 + x1) / 2 / self.U
                pcy = b.y + (y0 + y1) / 2 / self.U
                self.shards.append(Shard(piece, pcx, pcy,
                                         (pcx - cx) * 4 + random.uniform(-70, 70),
                                         (pcy - cy) * 6 - random.uniform(120, 300),
                                         random.uniform(-420, 420), random.uniform(0.55, 0.85)))

    # ---------------------------------------------------------- kart görseli
    def card_surfaces(self, b):
        if b.cache:
            return b.cache
        w, h, r, pad = self.S(b.w), self.S(b.h), self.S(14), self.S(30)
        size = (w + 2 * pad, h + 2 * pad)
        shadow = pygame.Surface(size, pygame.SRCALPHA)
        shadow.blit(aa_rrect(w, h, r, (0, 0, 0, 150)), (pad, pad + self.S(7)))
        shadow = blur(shadow, max(3, pad // 5))
        mask = aa_rrect(w, h, r, WHITE)
        sheen = masked(gradient(w, h, (255, 255, 255, 26), (255, 255, 255, 0), False), mask)

        def body(top, bot, border):
            c = pygame.Surface(size, pygame.SRCALPHA)
            c.blit(shadow, (0, 0))
            c.blit(masked(gradient(w, h, top, bot, False), mask), (pad, pad))
            c.blit(sheen, (pad, pad))
            c.blit(border, (pad, pad))
            return c

        nb = masked(gradient(w, h, (255, 255, 255, 80), (255, 255, 255, 18), False),
                    aa_rrect(w, h, r, WHITE, max(1, 1.2 * self.U)))
        tb = masked(gradient(w, h, rgba(CYAN), rgba(VIOLET)), aa_rrect(w, h, r, WHITE, max(2, 2.2 * self.U)))
        glow, gp = self.glow_rect(w, h, r, pad)  # pad ile aynı
        b.cache = dict(
            normal=body((48, 56, 100, 235), (28, 32, 64, 235), nb),
            target=body((42, 70, 128, 245), (36, 34, 88, 245), tb),
            glow=glow, pad=pad, w=w, h=h,
            word=self.F["word"].render(b.word, True, TEXT),
            word_dim=self.F["word"].render(b.word, True, (196, 204, 232)),
        )
        return b.cache

    # ---------------------------------------------------------- olaylar
    def title_buttons(self):
        h, bw = self.S(TITLE_H), self.S(46)
        return [("close", pygame.Rect(self.W - bw, 0, bw, h)),
                ("max", pygame.Rect(self.W - 2 * bw, 0, bw, h)),
                ("min", pygame.Rect(self.W - 3 * bw, 0, bw, h))]

    def title_action(self, kind):
        if kind == "close":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif kind == "max":
            self.set_display(not self.full)
        elif kind == "min":
            pygame.display.iconify()

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for kind, r in self.title_buttons():
                if r.collidepoint(ev.pos):
                    self.title_action(kind)
                    return
            if ev.pos[1] < self.S(TITLE_H):
                now = pygame.time.get_ticks()
                if now - self.last_title_click < 350:
                    self.set_display(not self.full)
                    self.last_title_click = 0
                    return
                self.last_title_click = now
                if not self.full:
                    self.drag_win = ev.pos
                return
            if self.cta_rect and self.cta_rect.collidepoint(ev.pos):
                self.play_pressed()
                return
            for wd in self.widgets:
                if wd.handle(ev):
                    return
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.drag_win = None
            for wd in self.widgets:
                wd.handle(ev)
        elif ev.type == pygame.MOUSEMOTION:
            if self.drag_win and self.win is not None:
                try:
                    wx, wy = self.win.position
                    self.win.position = (wx + ev.pos[0] - self.drag_win[0], wy + ev.pos[1] - self.drag_win[1])
                except Exception:
                    self.drag_win = None
                return
            for wd in self.widgets:
                wd.handle(ev)
        elif ev.type == pygame.TEXTINPUT:
            self.on_text(ev.text)
        elif ev.type == pygame.KEYDOWN:
            self.handle_key(ev)

    def handle_key(self, ev):
        if ev.key == pygame.K_F11:
            self.set_display(not self.full)
        elif ev.key == pygame.K_ESCAPE:
            if self.state == "play":
                self.state = "pause"
            elif self.state == "pause":
                self.state = "play"
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.state in ("ready", "over"):
                self.start_game()
            elif self.state == "pause":
                self.state = "play"
            elif self.input:
                self.input_shake = 0.35
                self.input = ""
        elif ev.key == pygame.K_BACKSPACE and self.state == "play":
            self.input = "" if ev.mod & pygame.KMOD_CTRL else self.input[:-1]

    def update_cursor(self):
        pos = pygame.mouse.get_pos()
        hand = any(wd.hovering(pos) for wd in self.widgets) or \
            any(r.collidepoint(pos) for _, r in self.title_buttons()) or \
            (self.cta_rect is not None and self.cta_rect.collidepoint(pos))
        kind = "hand" if hand else "arrow"
        if kind != self.cursor_kind:
            self.cursor_kind = kind
            try:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hand else pygame.SYSTEM_CURSOR_ARROW)
            except Exception:
                pass

    # ---------------------------------------------------------- güncelleme
    def update(self, dt):
        for wd in self.widgets:
            wd.update(dt)
        for st in self.stars:
            st[1] -= st[2] * dt
            if st[1] < -0.02:
                st[0], st[1] = random.random(), 1.02
        if self.state == "pause":
            return
        for lst in (self.sparks, self.rings, self.flashes, self.shards, self.floaters, self.pops):
            for o in lst:
                o.update(dt)
            lst[:] = [o for o in lst if o.life > 0]
        self.disp_score += (self.score - self.disp_score) * min(1, dt * 9)
        self.shake_t = max(0.0, self.shake_t - dt)
        self.input_shake = max(0.0, self.input_shake - dt)
        self.miss_flash = max(0.0, self.miss_flash - dt)
        if self.state != "play":
            return

        self.elapsed += dt
        m = self.speed_mult()
        speed = self.s_speed.value * m
        for b in self.boxes:
            b.y += speed * dt

        self.spawn_timer -= dt
        if not self.boxes or (self.spawn_timer <= 0 and len(self.boxes) < int(self.s_max.value)):
            self.spawn_timer = self.s_spawn.value / math.sqrt(m) if self.spawn() else 0.15

        for b in list(self.boxes):
            if self.state == "play" and b.y + b.h >= self.danger_b:
                self.miss(b)

        tgt = self.current_target()
        if tgt is not self.target:
            self.target = tgt
            self.link_t = 0.0
        self.link_t = min(1.0, self.link_t + dt / 0.22)
        self.danger_k = max([clamp((b.y + b.h - (self.danger_b - 160)) / 160, 0, 1) for b in self.boxes] or [0])

    # ---------------------------------------------------------- çizim: arka plan ve cam
    def draw_background(self, s):
        if self.bg_frame is None or self.time - self.bg_time > 1 / 20:
            f = self.bg_base.copy()
            W, H, t = self.W, self.H, self.time
            blobs = [((70, 36, 150), 0.72, 0.22, 0.62, 0.11, 0.0),
                     ((16, 86, 150), 0.30, 0.78, 0.56, 0.09, 2.0),
                     ((120, 26, 96), 0.98, 0.92, 0.48, 0.13, 4.0),
                     ((24, 36, 110), 0.10, 0.12, 0.45, 0.07, 1.0)]
            for col, fx, fy, rf, sp, ph in blobs:
                r = int(H * rf)
                x = W * (fx + 0.07 * math.sin(t * sp + ph))
                y = H * (fy + 0.06 * math.cos(t * sp * 0.8 + ph))
                f.blit(self.glow(r, col), (int(x - r), int(y - r)), special_flags=pygame.BLEND_RGB_ADD)
            self.bg_frame, self.bg_time = f, self.time
        s.blit(self.bg_frame, (0, 0))
        for x, y, _, size, ph, tw, col in self.stars:
            k = 0.25 + 0.3 * (0.5 + 0.5 * math.sin(self.time * tw + ph))
            g = self.glowq(self.S(size * 2.2), col, k)
            if g:
                r = g.get_width() // 2
                s.blit(g, (int(x * self.W) - r, int(y * self.H) - r), special_flags=pygame.BLEND_RGB_ADD)

    def capture_blur(self):
        k = max(6, self.S(10))
        W, H = self.W, self.H
        small = pygame.transform.smoothscale(self.screen, (max(1, W // k), max(1, H // k)))
        tiny = pygame.transform.smoothscale(small, (max(1, W // (2 * k)), max(1, H // (2 * k))))
        self.blur_small = pygame.transform.smoothscale(tiny, small.get_size())
        self.blur_k = k

    def frost(self, rect, radius, tint=(18, 22, 46, 150), border=True):
        s, k, small = self.screen, self.blur_k, self.blur_small
        sr = pygame.Rect(rect.x // k, rect.y // k, rect.w // k + 2, rect.h // k + 2).clip(small.get_rect())
        if sr.w > 0 and sr.h > 0:
            piece = pygame.transform.smoothscale(small.subsurface(sr), (sr.w * k, sr.h * k))
            layer = pygame.Surface(rect.size, pygame.SRCALPHA)
            layer.blit(piece, (0, 0), pygame.Rect(rect.x - sr.x * k, rect.y - sr.y * k, rect.w, rect.h))
            layer.blit(self.rr(rect.w, rect.h, radius, WHITE), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            s.blit(layer, rect.topleft)
        s.blit(self.rr(rect.w, rect.h, radius, tint), rect.topleft)
        sh = max(1, rect.h // 3)
        s.blit(self.cached(("sheen", rect.w, sh, radius),
                           lambda: masked(gradient(rect.w, sh, (255, 255, 255, 14), (255, 255, 255, 0), False),
                                          aa_rrect(rect.w, sh, radius, WHITE))), rect.topleft)
        if border:
            s.blit(self.ring(rect.w, rect.h, radius, (255, 255, 255, 58), (255, 255, 255, 14), 1), rect.topleft)

    # ---------------------------------------------------------- çizim: oyun alanı
    def shake_offset(self):
        if self.shake_t <= 0:
            return 0, 0
        a = self.S(self.shake_amp * (self.shake_t / self.shake_T))
        return random.randint(-a, a), random.randint(-a, a)

    def draw_danger(self, s):
        rp = self.r_play
        yd = self.px(self.danger_b)
        k = 0.15 + 0.85 * self.danger_k ** 1.5
        bh = self.S(140)
        band = self.cached(("band", rp.w, bh), lambda: gradient(rp.w, bh, (0, 0, 0), (120, 14, 40), False).convert())
        b = band.copy()
        b.fill((int(255 * k),) * 3, special_flags=pygame.BLEND_RGB_MULT)
        s.blit(b, (rp.x, yd - bh), special_flags=pygame.BLEND_RGB_ADD)
        col = mix((110, 40, 72), RED, self.danger_k)
        dash, gap = self.S(12), self.S(9)
        for x in range(rp.x + self.S(14), rp.right - self.S(14), dash + gap):
            pygame.draw.line(s, col, (x, yd), (min(x + dash, rp.right - self.S(14)), yd), max(1, self.S(2)))

    def draw_link(self, s, ox, oy):
        tgt = self.target
        if not tgt or self.state == "over":
            return
        ok = self.typing_ok()
        c1 = CYAN if ok is None else (MINT if ok else RED)
        c2 = VIOLET if ok is None else c1
        sx, sy = self.px(self.b_input.x + INPUT_W / 2), self.px(self.b_input.y)
        ex, ey = self.px(tgt.x + tgt.w / 2) + ox, self.px(tgt.y + tgt.h) + oy
        d = ey - sy
        p0, p1, p2, p3 = (sx, sy), (sx, sy + d * 0.5), (ex, ey - d * 0.5), (ex, ey)
        tend = ease_out(self.link_t)
        N = 40
        pts = [bezier(p0, p1, p2, p3, tend * i / N) for i in range(N + 1)]
        A, rp = self.add, self.r_play
        A.fill((0, 0, 0), rp)
        for width, k in ((self.S(16), 0.10), (self.S(9), 0.2), (self.S(4), 0.5), (max(1, self.S(1.6)), 1.0)):
            for i in range(N):
                col = mix(c1, c2, i / N)
                if k == 1.0:
                    col = mix(col, WHITE, 0.45)
                pygame.draw.line(A, mul(col, k), pts[i], pts[i + 1], width)
        for i in range(6):
            f = (self.time * 0.75 + i / 6) % 1.0
            if f <= tend:
                x, y = bezier(p0, p1, p2, p3, f)
                g = self.glow(self.S(11), mul(mix(c1, c2, f), 0.9))
                A.blit(g, (int(x) - g.get_width() // 2, int(y) - g.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
        for (x, y), col in ((p0, c1), (pts[-1], c2)):
            g = self.glow(self.S(16), col)
            A.blit(g, (int(x) - g.get_width() // 2, int(y) - g.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
        s.blit(A, rp.topleft, rp, special_flags=pygame.BLEND_RGB_ADD)

    def draw_card(self, s, b, is_t, ox, oy):
        c = self.card_surfaces(b)
        pad, w, h = c["pad"], c["w"], c["h"]
        x, y = self.px(b.x) + ox, self.px(b.y) + oy
        fade = clamp((b.y - (self.b_play.y - BOX_H)) / (BOX_H * 1.6), 0, 1)
        if is_t:
            ok = self.typing_ok()
            col = CYAN if ok is None else (MINT if ok else RED)
            col = mix(col, RED, self.danger_k ** 2)
            k = (0.55 + 0.2 * math.sin(self.time * 5)) * fade
            g = c["glow"].copy()
            g.fill(mul(col, k), special_flags=pygame.BLEND_RGB_MULT)
            s.blit(g, (x - pad, y - pad + self.S(2)), special_flags=pygame.BLEND_RGB_ADD)
        surf = c["target" if is_t else "normal"]
        surf.set_alpha(int(255 * fade))
        s.blit(surf, (x - pad, y - pad))
        surf.set_alpha(255)

        if is_t and self.input:
            typed, wn = normalize(self.input, self.cs), normalize(b.word, self.cs)
            n = 0
            while n < len(typed) and n < len(wn) and typed[n] == wn[n]:
                n += 1
            p1 = self.text("word", b.word[:n], MINT)
            p2 = self.text("word", b.word[n:], TEXT)
            x0 = x + w // 2 - (p1.get_width() + p2.get_width()) // 2
            y0 = y + h // 2 - p1.get_height() // 2 - self.S(1)
            s.blit(p1, (x0, y0))
            s.blit(p2, (x0 + p1.get_width(), y0))
            bw, bh = w - self.S(30), max(2, self.S(3))
            bx, by = x + self.S(15), y + h - self.S(8)
            s.blit(self.rr(bw, bh, bh // 2, (255, 255, 255, 22)), (bx, by))
            if n:
                s.blit(self.grad_rr(bw, bh, bh // 2, MINT, CYAN), (bx, by), pygame.Rect(0, 0, int(bw * n / len(wn)), bh))
        else:
            t = c["word"] if is_t else c["word_dim"]
            t.set_alpha(int(255 * fade))
            s.blit(t, t.get_rect(center=(x + w // 2, y + h // 2 - self.S(1))))
            t.set_alpha(255)

    def draw_effects(self, s, ox, oy):
        A, rp = self.add, self.r_play
        A.fill((0, 0, 0), rp)
        P = lambda x, y: (self.px(x) + ox, self.px(y) + oy)
        for f in self.flashes:
            k = f.life / f.max
            g = self.glowq(self.S(f.rmax * (1.25 - 0.35 * k)), f.color, k)
            if g:
                cx, cy = P(f.x, f.y)
                A.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
        for r in self.rings:
            k = r.life / r.max
            rad = self.S(8 + r.rmax * ease_out(1 - k))
            pygame.draw.circle(A, mul(r.color, k), P(r.x, r.y), rad, max(1, self.S(r.width * k + 0.6)))
        for sp in self.sparks:
            k = clamp(sp.life / sp.max, 0, 1)
            head, tail = P(sp.x, sp.y), P(sp.x - sp.vx * 0.035, sp.y - sp.vy * 0.035)
            pygame.draw.line(A, mul(sp.color, k), tail, head, max(1, self.S(2)))
            g = self.glowq(self.S(sp.size * 2.4), sp.color, k * 0.9)
            if g:
                A.blit(g, (head[0] - g.get_width() // 2, head[1] - g.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
        s.blit(A, rp.topleft, rp, special_flags=pygame.BLEND_RGB_ADD)

        for sh in self.shards:
            k = clamp(sh.life / sh.max, 0, 1)
            img = pygame.transform.rotozoom(sh.surf, sh.ang, 0.3 + 0.7 * k)
            img.set_alpha(int(255 * min(1, k * 1.6)))
            cx, cy = P(sh.x, sh.y)
            s.blit(img, img.get_rect(center=(cx, cy)))
        for f in self.floaters:
            k = clamp(f.life / f.max, 0, 1)
            f.surf.set_alpha(int(255 * min(1, k * 2.2)))
            cx, cy = P(f.x, f.y)
            s.blit(f.surf, f.surf.get_rect(center=(cx, cy)))
        for p in self.pops:
            age = p.max - p.life
            sc = ease_out_back(min(1, age / 0.28))
            a = 1 if p.life > 0.4 else p.life / 0.4
            img = pygame.transform.rotozoom(p.surf, 0, max(0.05, sc))
            img.set_alpha(int(255 * a))
            s.blit(img, img.get_rect(center=P(p.x, p.y - age * 18)))

        if self.miss_flash > 0:
            vig = self.cached(("vig", rp.w, rp.h), lambda: self.make_vignette(rp.w, rp.h))
            v = vig.copy()
            v.fill(mul(RED, 0.75 * self.miss_flash / 0.4), special_flags=pygame.BLEND_RGB_MULT)
            s.blit(v, rp.topleft, special_flags=pygame.BLEND_RGB_ADD)

    @staticmethod
    def make_vignette(w, h):
        small = pygame.Surface((80, 50))
        small.fill(WHITE)
        pygame.draw.rect(small, (0, 0, 0), (9, 9, 62, 32), border_radius=10)
        return blur(pygame.transform.smoothscale(small, (w, h)), 10).convert()

    # ---------------------------------------------------------- çizim: arayüz
    def draw_titlebar(self, s):
        h = self.S(TITLE_H)
        s.blit(self.rr(self.W, 1, 0, (255, 255, 255, 14)), (0, h - 1))
        x, cy = self.S(16), h // 2
        ls = self.S(22)
        logo = self.cached(("logo", ls), lambda: self.make_logo(ls))
        s.blit(logo, (x, cy - ls // 2))
        t1 = self.text("brand", "Kelime Yağmuru", TEXT)
        s.blit(t1, (x + ls + self.S(10), cy - t1.get_height() // 2))
        t2 = self.text("brand2", "English Vocabulary", FAINT)
        s.blit(t2, (x + ls + self.S(20) + t1.get_width(), cy - t2.get_height() // 2))
        mpos = pygame.mouse.get_pos()
        lw = max(1, self.S(1.2))
        for kind, r in self.title_buttons():
            hover = r.collidepoint(mpos)
            if hover:
                s.blit(self.rr(r.w, r.h, 0, (232, 17, 35) if kind == "close" else (255, 255, 255, 22)), r.topleft)
            col = WHITE if hover else MUTED
            a = self.S(5)
            cx, cy2 = r.centerx, r.centery
            if kind == "close":
                pygame.draw.line(s, col, (cx - a, cy2 - a), (cx + a, cy2 + a), lw + 1)
                pygame.draw.line(s, col, (cx - a, cy2 + a), (cx + a, cy2 - a), lw + 1)
            elif kind == "min":
                pygame.draw.line(s, col, (cx - a, cy2), (cx + a, cy2), lw)
            else:
                if self.full:
                    pygame.draw.rect(s, col, (cx - a + self.S(2), cy2 - a - self.S(1), 2 * a - self.S(2), 2 * a - self.S(2)), lw, border_radius=2)
                    pygame.draw.rect(s, col, (cx - a, cy2 - a + self.S(2), 2 * a - self.S(2), 2 * a - self.S(2)), lw, border_radius=2)
                else:
                    pygame.draw.rect(s, col, (cx - a, cy2 - a, 2 * a, 2 * a), lw, border_radius=2)

    def make_logo(self, n):
        surf = masked(gradient(n, n, CYAN, VIOLET), aa_rrect(n, n, n // 3, WHITE))
        t = load_font(BLACK, int(n * 0.62)).render("K", True, WHITE)
        surf.blit(t, t.get_rect(center=(n // 2, n // 2 + 1)))
        return surf

    def draw_sidebar(self, s):
        r = self.r_side
        self.frost(r, self.S(22))
        s.blit(self.text("h2", "Ayarlar", TEXT), (r.x + self.S(20), r.y + self.S(18)))
        s.blit(self.text("sub", "Oyunu kendine göre düzenle", MUTED), (r.x + self.S(20), r.y + self.S(46)))
        for i, (label, x, y) in enumerate(self.section_pos):
            if i:
                s.blit(self.rr(r.w - self.S(40), 1, 0, (255, 255, 255, 16)), (x, y - self.S(6)))
            s.blit(self.spaced("section", label, FAINT, self.S(1.6)), (x, y + self.S(2)))
        for wd in self.widgets:
            wd.draw(s)

    def hud_pill(self, s, x, w, label):
        y, h = self.px(self.b_hud_y), self.S(HUD_H)
        r = pygame.Rect(x, y, w, h)
        self.frost(r, self.S(16))
        s.blit(self.spaced("hud_label", label, MUTED, self.S(1.4)), (x + self.S(16), y + self.S(10)))
        return r

    def draw_hud(self, s):
        x, gap = self.px(self.b_play.x), self.S(10)
        y0 = self.S(25)
        r = self.hud_pill(s, x, self.S(172), "PUAN")
        s.blit(self.text("hud_num", f"{int(round(self.disp_score))}", TEXT), (r.x + self.S(16), r.y + y0 - self.S(2)))
        rec = self.text("hud_small", f"Rekor {self.best}", FAINT)
        s.blit(rec, (r.right - self.S(14) - rec.get_width(), r.y + self.S(10)))
        x = r.right + gap

        r = self.hud_pill(s, x, self.S(172), "SERİ")
        mult = 1 + self.combo // 5
        s.blit(self.text("hud_mid", f"x{self.combo}", AMBER if self.combo else TEXT), (r.x + self.S(16), r.y + y0))
        badge = self.text("hud_small", f"×{mult} puan", AMBER if mult > 1 else MUTED)
        bw, bh = badge.get_width() + self.S(14), badge.get_height() + self.S(4)
        bx, by = r.right - self.S(14) - bw, r.y + self.S(8)
        s.blit(self.rr(bw, bh, bh // 2, (251, 191, 36, 34) if mult > 1 else (255, 255, 255, 16)), (bx, by))
        s.blit(badge, (bx + self.S(7), by + self.S(2)))
        tw, th = self.S(62), max(2, self.S(4))
        tx, ty = r.right - self.S(14) - tw, r.bottom - self.S(18)
        s.blit(self.rr(tw, th, th // 2, (255, 255, 255, 24)), (tx, ty))
        frac = (self.combo % 5) / 5
        if frac:
            s.blit(self.grad_rr(tw, th, th // 2, AMBER, PINK), (tx, ty), pygame.Rect(0, 0, int(tw * frac), th))
        x = r.right + gap

        wpm = (self.correct_chars / 5) / (self.elapsed / 60) if self.elapsed > 5 else 0
        acc = 100 * self.keys_ok / self.keys_total if self.keys_total else 100
        for label, val, w in (("DOĞRULUK", f"%{acc:.0f}", 108), ("WPM", f"{wpm:.0f}", 92),
                              ("SÜRE", f"{int(self.elapsed) // 60:02d}:{int(self.elapsed) % 60:02d}", 100)):
            r = self.hud_pill(s, x, self.S(w), label)
            s.blit(self.text("hud_mid", val, TEXT), (r.x + self.S(16), r.y + y0))
            x = r.right + gap

        # canlar
        hs = self.S(18)
        n = self.max_lives
        show = n if n <= 6 else 1
        w = self.S(32) + show * self.S(24) + (self.S(34) if n > 6 else 0)
        rx = self.px(self.b_play.right) - w
        y, h = self.px(self.b_hud_y), self.S(HUD_H)
        r = pygame.Rect(rx, y, w, h)
        self.frost(r, self.S(16))
        s.blit(self.spaced("hud_label", "CAN", MUTED, self.S(1.4)), (r.x + self.S(16), r.y + self.S(10)))
        full = self.cached(("heart", hs, RED), lambda: heart_sprite(hs, (251, 82, 112)))
        empty = self.cached(("heart", hs, "e"), lambda: heart_sprite(hs, (64, 70, 102)))
        for i in range(show):
            hx, hy = r.x + self.S(16) + i * self.S(24), r.y + self.S(29)
            alive = (self.lives > i) if n <= 6 else self.lives > 0
            if alive:
                g = self.glow(self.S(16), mul(PINK, 0.45))
                s.blit(g, (hx + hs // 2 - g.get_width() // 2, hy + hs // 2 - g.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
            s.blit(full if alive else empty, (hx, hy))
        if n > 6:
            t = self.text("hud_mid", f"×{max(self.lives, 0)}", TEXT)
            s.blit(t, (r.x + self.S(16) + self.S(26), r.y + self.S(25)))

    def draw_input(self, s):
        r = self.r_input.copy()
        if self.input_shake > 0:
            r.x += int(math.sin(self.input_shake * 70) * self.S(10) * (self.input_shake / 0.35))
        ok = self.typing_ok()
        bad = ok is False or self.input_shake > 0
        col = RED if bad else (MINT if ok else CYAN)
        gs, p = self.glow_rect(r.w, r.h, r.h // 2, self.S(26))
        g = gs.copy()
        g.fill(mul(col, 0.42 if (ok is not None or bad) else 0.16 + 0.06 * math.sin(self.time * 2)),
               special_flags=pygame.BLEND_RGB_MULT)
        s.blit(g, (r.x - p, r.y - p), special_flags=pygame.BLEND_RGB_ADD)
        self.frost(r, r.h // 2, tint=(20, 24, 52, 175), border=False)
        if bad:
            s.blit(self.ring(r.w, r.h, r.h // 2, RED, RED, 2), r.topleft)
        elif ok:
            s.blit(self.ring(r.w, r.h, r.h // 2, MINT, CYAN, 2, True), r.topleft)
        else:
            s.blit(self.ring(r.w, r.h, r.h // 2, rgba(CYAN, 170), rgba(VIOLET, 170), 1.5, True), r.topleft)

        f = self.F["input"]
        tw = f.size(self.input)[0]
        tgt = self.target
        hint = self.t_hint.value and tgt and ok is not False and self.state == "play"
        if hint:
            ghost = self.text("input", tgt.word, (78, 88, 128))
            tw = max(tw, ghost.get_width())
            s.blit(ghost, (r.centerx - tw // 2, r.centery - ghost.get_height() // 2))
        if self.input:
            t = self.text("input", self.input, TEXT)
            s.blit(t, (r.centerx - tw // 2, r.centery - t.get_height() // 2))
        elif not hint:
            ph = self.text("placeholder", "Kelimeyi yaz…", FAINT)
            s.blit(ph, ph.get_rect(center=r.center))
        if self.state == "play":
            a = 0.5 + 0.5 * math.sin(self.time * 7)
            cx = r.centerx - tw // 2 + f.size(self.input)[0] + self.S(3)
            if not self.input and not hint:
                cx = r.centerx - self.S(62)
            ch = self.S(15)
            pygame.draw.line(s, mix((60, 70, 110), CYAN, a), (cx, r.centery - ch), (cx, r.centery + ch), max(2, self.S(2)))

    def draw_hints(self, s):
        rows = [("Enter", "Yanlışı sil"), ("ESC", "Duraklat"), ("F11", "Tam ekran")]
        x = self.r_play.x + self.S(18)
        if x + self.S(180) > self.r_input.x:
            return
        y = self.r_input.y + self.S(2)
        for i, (k, lab) in enumerate(rows):
            yy = y + i * self.S(21)
            t = self.text("key", k, TEXT)
            kw, kh = t.get_width() + self.S(12), self.S(17)
            s.blit(self.rr(kw, kh, self.S(5), (255, 255, 255, 16)), (x, yy))
            s.blit(self.ring(kw, kh, self.S(5), (255, 255, 255, 60), (255, 255, 255, 25), 1), (x, yy))
            s.blit(t, t.get_rect(center=(x + kw // 2, yy + kh // 2)))
            l = self.text("hint", lab, FAINT)
            s.blit(l, (x + kw + self.S(8), yy + (kh - l.get_height()) // 2))

    # ---------------------------------------------------------- çizim: açılır kartlar
    def panel_card(self, s, r):
        p = self.S(40)
        sh = self.cached(("pshadow", r.w, r.h), lambda: self.make_shadow(r.w, r.h, p))
        s.blit(sh, (r.x - p, r.y - p + self.S(12)))
        self.frost(r, self.S(26), tint=(24, 28, 60, 185), border=False)
        s.blit(self.ring(r.w, r.h, self.S(26), rgba(CYAN, 150), rgba(PINK, 110), 1.3, True), r.topleft)

    def make_shadow(self, w, h, p):
        c = pygame.Surface((w + 2 * p, h + 2 * p), pygame.SRCALPHA)
        c.blit(aa_rrect(w, h, self.S(26), (0, 0, 0, 170)), (p, p))
        return blur(c, max(3, p // 5))

    def draw_cta(self, s, rect, label, icon):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        pulse = 0.5 + 0.5 * math.sin(self.time * 3)
        gs, p = self.glow_rect(rect.w, rect.h, rect.h // 2, self.S(26))
        g = gs.copy()
        g.fill(mul(VIOLET, 0.3 + 0.2 * pulse + (0.2 if hover else 0)), special_flags=pygame.BLEND_RGB_MULT)
        s.blit(g, (rect.x - p, rect.y - p + self.S(4)), special_flags=pygame.BLEND_RGB_ADD)
        s.blit(self.grad_rr(rect.w, rect.h, rect.h // 2, CYAN, VIOLET), rect.topleft)
        if hover:
            s.blit(self.rr(rect.w, rect.h, rect.h // 2, (255, 255, 255, 30)), rect.topleft)
        t = self.text("cta", label, WHITE)
        isz = self.S(13)
        total = isz + self.S(10) + t.get_width()
        x0 = rect.centerx - total // 2
        self.icon(s, icon, x0 + isz // 2, rect.centery, isz, WHITE)
        s.blit(t, (x0 + isz + self.S(10), rect.centery - t.get_height() // 2))
        self.cta_rect = rect

    def draw_ready(self, s):
        r = pygame.Rect(0, 0, self.S(620), self.S(430))
        r.center = self.r_play.center
        self.panel_card(s, r)
        title = self.cached(("title",), lambda: self.glow_text("KELİME YAĞMURU", self.F["title"], grad=(CYAN, PINK), strength=2))
        s.blit(title, title.get_rect(center=(r.centerx, r.y + self.S(70))))
        sub = self.text("body", "İngilizce kelime bilgini hızla ve eğlenerek geliştir", MUTED)
        s.blit(sub, sub.get_rect(center=(r.centerx, r.y + self.S(118))))
        steps = ["Düşen kartlardaki İngilizce kelimeleri yaz.",
                 "Hedef hep en alttaki karttır; ışık hattı onu gösterir.",
                 "Kart kırmızı çizgiye değmeden yaz, seriyle çarpanı artır."]
        y = r.y + self.S(160)
        cr = self.S(14)
        for i, txt in enumerate(steps):
            cx, cy = r.x + self.S(64), y + cr
            s.blit(self.cached(("stepc", cr), lambda: masked(gradient(2 * cr, 2 * cr, CYAN, VIOLET),
                                                               self.circle(cr, WHITE))), (cx - cr, cy - cr))
            n = self.text("num_small", str(i + 1), WHITE)
            s.blit(n, n.get_rect(center=(cx, cy)))
            t = self.text("body", txt, TEXT)
            s.blit(t, (cx + cr + self.S(16), cy - t.get_height() // 2))
            y += self.S(46)
        cta = pygame.Rect(0, 0, self.S(290), self.S(52))
        cta.midbottom = (r.centerx, r.bottom - self.S(52))
        self.draw_cta(s, cta, "Başlamak için ENTER", "play")
        foot = self.text("hint", f"Seviye: {self.c_level.value}   ·   Can: {int(self.s_lives.value)}   ·   Rekor: {self.best}", FAINT)
        s.blit(foot, foot.get_rect(center=(r.centerx, r.bottom - self.S(26))))

    def draw_pause(self, s):
        r = pygame.Rect(0, 0, self.S(440), self.S(270))
        r.center = self.r_play.center
        self.panel_card(s, r)
        cr = self.S(30)
        cx, cy = r.centerx, r.y + self.S(62)
        g = self.glow(self.S(60), mul(VIOLET, 0.45))
        s.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
        s.blit(self.cached(("pc", cr), lambda: masked(gradient(2 * cr, 2 * cr, CYAN, VIOLET), self.circle(cr, WHITE))),
               (cx - cr, cy - cr))
        self.icon(s, "pause", cx, cy, self.S(20), WHITE)
        t = self.text("h2", "Duraklatıldı", TEXT)
        s.blit(t, t.get_rect(center=(r.centerx, r.y + self.S(122))))
        t = self.text("body", "Kaldığın yerden devam etmek için ESC", MUTED)
        s.blit(t, t.get_rect(center=(r.centerx, r.y + self.S(152))))
        cta = pygame.Rect(0, 0, self.S(220), self.S(48))
        cta.midbottom = (r.centerx, r.bottom - self.S(28))
        self.draw_cta(s, cta, "Devam Et", "play")

    def build_over(self):
        chips = []
        seen = set()
        for w, m in reversed(self.missed_list):
            if w.lower() in seen:
                continue
            seen.add(w.lower())
            a = self.F["chip"].render(w, True, TEXT)
            b = self.F["chip_tr"].render(m, True, MUTED) if m else None
            padx, h = self.S(12), self.S(32)
            gap = self.S(8) if b else 0
            cw = a.get_width() + gap + (b.get_width() if b else 0) + 2 * padx
            c = pygame.Surface((cw, h), pygame.SRCALPHA)
            c.blit(aa_rrect(cw, h, h // 2, (255, 255, 255, 14)), (0, 0))
            c.blit(aa_rrect(cw, h, h // 2, (244, 63, 94, 110), max(1, self.U)), (0, 0))
            c.blit(a, (padx, (h - a.get_height()) // 2))
            if b:
                c.blit(b, (padx + a.get_width() + gap, (h - b.get_height()) // 2))
            chips.append(c)
            if len(chips) >= 12:
                break
        return chips

    def draw_over(self, s):
        if self.over_cache is None:
            self.over_cache = self.build_over()
        chips = self.over_cache
        cw = self.S(660)
        inner = cw - self.S(64)
        rows, rx, row_w = [[]], 0, []
        for c in chips:
            if rx + c.get_width() > inner and rows[-1]:
                row_w.append(rx - self.S(8))
                rows.append([])
                rx = 0
            if len(rows) > 3:
                rows.pop()
                break
            rows[-1].append(c)
            rx += c.get_width() + self.S(8)
        row_w.append(rx - self.S(8))
        n_rows = len([r for r in rows if r])
        ch = self.S((300 + 20 + 40 * n_rows) if n_rows else 270) + self.S(96)
        r = pygame.Rect(0, 0, cw, min(ch, self.r_play.h - self.S(20)))
        r.center = self.r_play.center
        self.panel_card(s, r)

        title = self.cached(("overt",), lambda: self.glow_text("Oyun Bitti", self.F["big"], grad=(RED, PINK)))
        s.blit(title, title.get_rect(center=(r.centerx, r.y + self.S(56))))
        y = r.y + self.S(96)
        if self.new_record:
            t = self.text("hud_small", "YENİ REKOR", (30, 20, 0))
            bw, bh = t.get_width() + self.S(22), t.get_height() + self.S(8)
            bx = r.centerx - bw // 2
            gl = self.glow(self.S(46), mul(AMBER, 0.4))
            s.blit(gl, (r.centerx - gl.get_width() // 2, y + bh // 2 - gl.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
            s.blit(self.grad_rr(bw, bh, bh // 2, AMBER, (251, 146, 60)), (bx, y))
            s.blit(t, (bx + self.S(11), y + self.S(4)))
        y = r.y + self.S(132)
        mins = max(self.elapsed / 60, 1e-6)
        acc = 100 * self.keys_ok / self.keys_total if self.keys_total else 100
        tiles = [("PUAN", str(self.score), AMBER), ("WPM", f"{(self.correct_chars / 5) / mins:.0f}", CYAN),
                 ("DOĞRULUK", f"%{acc:.0f}", MINT), ("EN İYİ SERİ", str(self.best_combo), PINK)]
        gap = self.S(12)
        tw = (inner - 3 * gap) // 4
        th = self.S(86)
        for i, (lab, val, col) in enumerate(tiles):
            tx = r.x + self.S(32) + i * (tw + gap)
            s.blit(self.rr(tw, th, self.S(16), (255, 255, 255, 12)), (tx, y))
            s.blit(self.ring(tw, th, self.S(16), (255, 255, 255, 46), (255, 255, 255, 10), 1), (tx, y))
            v = self.text("tile_num", val, col)
            s.blit(v, v.get_rect(center=(tx + tw // 2, y + self.S(36))))
            l = self.spaced("tile_lbl", lab, MUTED, self.S(1.2))
            s.blit(l, l.get_rect(center=(tx + tw // 2, y + self.S(66))))
        y += th + self.S(22)
        line = self.text("hint", f"Doğru {self.correct_words}   ·   Kaçan {self.missed_words}   ·   "
                                 f"Süre {int(self.elapsed) // 60:02d}:{int(self.elapsed) % 60:02d}   ·   "
                                 f"Rekor {self.best}", MUTED)
        s.blit(line, line.get_rect(center=(r.centerx, y)))
        y += self.S(30)
        if n_rows:
            lab = self.spaced("section", "TEKRAR ETMEN GEREKEN KELİMELER", FAINT, self.S(1.6))
            s.blit(lab, lab.get_rect(center=(r.centerx, y)))
            y += self.S(20)
            for row, w in zip(rows, row_w):
                if not row:
                    continue
                x = r.centerx - w // 2
                for c in row:
                    s.blit(c, (x, y))
                    x += c.get_width() + self.S(8)
                y += self.S(40)
        cta = pygame.Rect(0, 0, self.S(280), self.S(50))
        cta.midbottom = (r.centerx, r.bottom - self.S(28))
        self.draw_cta(s, cta, "Yeni oyun için ENTER", "restart")

    # ---------------------------------------------------------- ana çizim
    def draw(self):
        s = self.screen
        self.draw_background(s)
        ox, oy = self.shake_offset()
        s.set_clip(self.r_play)
        self.draw_danger(s)
        self.draw_link(s, ox, oy)
        for b in self.boxes:
            self.draw_card(s, b, b is self.target, ox, oy)
        self.draw_effects(s, ox, oy)
        s.set_clip(None)

        self.capture_blur()
        self.draw_sidebar(s)
        self.draw_hud(s)
        self.draw_input(s)
        self.draw_hints(s)
        self.draw_titlebar(s)

        self.cta_rect = None
        if self.state != "play":
            self.capture_blur()
            self.frost(self.r_play, self.S(22), tint=(8, 10, 26, 120), border=False)
            {"ready": self.draw_ready, "pause": self.draw_pause, "over": self.draw_over}[self.state](s)

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.time += dt
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(ev)
            self.update(dt)
            self.draw()
            self.update_cursor()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()