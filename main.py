#!/usr/bin/env python3
"""THE WORLD IN ONE PAGE - a broadsheet front page for 26 November 2026.

Draws a 1024x1024 newspaper front page with a hand-built 5x7 bitmap
font and a from-scratch PNG encoder (zlib + struct, stdlib only).
No network, no randomness, no timestamps: two runs are byte-identical.
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 227)
INK = (17, 17, 17)
RED = (163, 31, 31)
GREY = (90, 86, 76)
LIGHT_GREY = (200, 194, 178)
SKY = (178, 205, 222)
CLOUD = (120, 130, 140)
BALLOON = (178, 44, 44)
BALLOON2 = (44, 90, 160)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

# ---------------------------------------------------------------- font
# My own 5x7 bitmap glyphs: each glyph is 7 strings of 5 characters,
# '#' = ink, '.' = blank.
GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ':': ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}

def clean(text):
    """Normalise to the glyph set: upper case, straight quotes/dashes."""
    repl = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
            "\u2014": "-", "\u2013": "-", "\u00a0": " ", "\u00e9": "E"}
    for k, v in repl.items():
        text = text.replace(k, v)
    return "".join(ch if ch in GLYPHS else " " for ch in text.upper())

def text_width(text, scale):
    return len(clean(text)) * 6 * scale - scale

def wrap(text, max_width, scale):
    """Greedy word wrap; returns list of lines fitting max_width."""
    words = clean(text).split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(col)

    def fill(self, x0, y0, x1, y1, col):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            row = bytes(col) * (x1 - x0)
            self.px[base:base + len(row)] = row

    def rect(self, x0, y0, x1, y1, col, thick=1):
        self.fill(x0, y0, x1, y0 + thick, col)
        self.fill(x0, y1 - thick, x1, y1, col)
        self.fill(x0, y0, x0 + thick, y1, col)
        self.fill(x1 - thick, y0, x1, y1, col)

    def hline(self, x0, x1, y, col, thick=1):
        self.fill(x0, y, x1, y + thick, col)

    def line(self, x0, y0, x1, y1, col):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, col):
        for y in range(cy - ry, cy + ry + 1):
            if ry == 0:
                continue
            t = 1.0 - ((y - cy) / ry) ** 2
            if t < 0:
                continue
            dx = int(rx * (t ** 0.5))
            self.fill(cx - dx, y, cx + dx + 1, y + 1, col)

    def ellipse_outline(self, cx, cy, rx, ry, col):
        steps = max(rx, ry) * 8
        for i in range(steps):
            import math
            a = 2 * math.pi * i / steps
            self.set(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), col)

    def glyph(self, x, y, ch, scale, col):
        rows = GLYPHS.get(ch, GLYPHS[' '])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == '1':
                    self.fill(x + c * scale, y + r * scale,
                              x + (c + 1) * scale, y + (r + 1) * scale, col)

    def text(self, x, y, s, scale, col):
        for ch in clean(s):
            self.glyph(x, y, ch, scale, col)
            x += 6 * scale
        return x

    def text_centred(self, cx, y, s, scale, col):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, col)

    def para(self, x, y, s, scale, col, max_width, leading=None):
        if leading is None:
            leading = 9 * scale
        for ln in wrap(s, max_width, scale):
            self.text(x, y, ln, scale, col)
            y += leading
        return y

# ---------------------------------------------------------------- page
def draw_page():
    c = Canvas(W, H, PAPER)
    M = 30                      # page margin
    right = W - M

    # ---- masthead ----
    c.text_centred(W // 2, 26, "THE WORLD IN ONE PAGE", 5, INK)
    c.hline(M, right, 108, INK, 4)
    c.hline(M, right, 116, INK, 1)
    c.text_centred(W // 2, 128, "THURSDAY, 26 NOVEMBER 2026", 2, RED)
    c.text_centred(W // 2, 150, "THE DAY'S NEWS FROM AROUND THE WORLD - ONE PAGE, EVERY STORY",
                   1, GREY)
    c.hline(M, right, 170, INK, 2)

    # ---- lead story ----
    lead_x, lead_w = M, 560
    y = 186
    c.text(lead_x, y, "LEAD STORY  *  NEW YORK", 1, RED)
    y = 208
    y = c.para(lead_x, y, "PARADE POSTPONED FOR THE FIRST TIME IN 100 YEARS",
               3, INK, lead_w, leading=28)
    y += 6
    y = c.para(lead_x, y,
               "The Macy's Thanksgiving Day Parade will not march today. "
               "A coastal storm bringing rain and gusts of up to 60 mph has "
               "forced organisers to move the centenary parade to Saturday, "
               "28 November - the first postponement in its 100-year history.",
               2, INK, lead_w)
    y += 4
    y = c.para(lead_x, y,
               "Giant balloons stay grounded when sustained winds pass "
               "23 mph, or gusts 34 mph. AAA expects 81.5 million Americans "
               "to travel for the holiday, with about 418,000 flights in the "
               "air over the Thanksgiving period.",
               2, INK, lead_w)

    # ---- lead illustration: storm over the parade route ----
    ix0, iy0, ix1, iy1 = 622, 186, right, 462
    c.rect(ix0, iy0, ix1, iy1, INK, 2)
    c.fill(ix0 + 2, iy0 + 2, ix1 - 2, iy1 - 2, SKY)
    # storm clouds
    c.ellipse(700, 235, 70, 22, CLOUD)
    c.ellipse(770, 220, 80, 26, (100, 110, 122))
    c.ellipse(880, 240, 75, 22, CLOUD)
    c.ellipse(950, 222, 55, 18, (100, 110, 122))
    # rain, slanting
    for k in range(14):
        rx = 650 + k * 24
        c.line(rx, 262, rx - 10, 292, (70, 90, 110))
        c.line(rx + 8, 300, rx - 2, 330, (70, 90, 110))
    # grounded balloon, sagging low over the street
    c.ellipse(760, 330, 62, 34, BALLOON2)
    c.ellipse(760, 322, 34, 16, (90, 140, 200))
    c.ellipse(830, 352, 100, 58, BALLOON)
    c.ellipse(830, 338, 58, 26, (205, 95, 95))
    c.line(745, 388, 715, 420, INK)
    c.line(830, 410, 830, 420, INK)
    c.line(905, 392, 930, 420, INK)
    # buildings and street
    c.fill(ix0 + 2, 420, 712, iy1 - 2, (70, 74, 82))
    c.fill(930, 402, ix1 - 2, iy1 - 2, (70, 74, 82))
    for wx in range(ix0 + 14, 700, 26):
        c.fill(wx, 424, wx + 10, 432, (210, 200, 140))
    c.fill(ix0 + 2, 448, ix1 - 2, iy1 - 2, (52, 52, 52))
    c.hline(ix0 + 2, ix1 - 2, 448, (230, 200, 60), 3)
    c.text(ix0 + 14, iy1 - 26, "GROUNDED: THE BALLOONS STAY DOWN", 1, WHITE)

    # ---- eight stories, two columns x four rows ----
    stories = [
        ("SPAIN", "RECORD DAY ON THE ATLANTIC ROUTE",
         "More than 2,100 migrants reached Spain's Canary Islands in 24 "
         "hours, a single-day record. Most landed on El Hierro; one person "
         "was found dead aboard a boat."),
        ("SPACE", "FIRST PAKISTANI ASTRONAUT REACHES TIANGONG",
         "Muhammad Zeeshan Ali flew aboard Shenzhou-24, becoming the first "
         "foreign astronaut to visit China's Tiangong space station."),
        ("CHINA", "BEIJING PROBES TOP SHANGHAI OFFICIAL",
         "China is investigating Chen Jining, a Politburo member and the "
         "Shanghai party chief, in a rare probe of a leader at that level."),
        ("KOREA", "PYONGYANG EXPELS SWISS ENVOY",
         "North Korea ordered Switzerland to close its newly opened "
         "diplomatic office in Pyongyang, citing sanctions."),
        ("YEMEN", "HOUTHIS VOW REVENGE AFTER PORT STRIKE",
         "Yemen's Houthis threatened retaliation after a port city was hit, "
         "raising fears of a new round of attacks on shipping."),
        ("BANGLADESH", "GARMENT WORKERS WIN 36% PAY RISE",
         "Bangladesh raised the minimum wage for entry-level garment "
         "workers by 36%, a big win for the industry's lowest-paid staff."),
        ("MERCURY", "EIGHT-YEAR VOYAGE ENDS AT MERCURY",
         "The joint Japanese-European BepiColombo mission reached Mercury "
         "after an eight-year journey across the Solar System."),
        ("TECH", "HUANG SAYS SORRY AFTER NVIDIA COMEBACK",
         "Nvidia chief Jensen Huang apologised to staff for 'terrible "
         "mistakes' after the board reinstated him as chief executive."),
    ]
    grid_y = 482
    c.hline(M, right, grid_y - 8, INK, 2)
    col_w = (right - M - 24) // 2
    row_h = 104
    for i, (kicker, head, body) in enumerate(stories):
        col = i % 2
        row = i // 2
        x = M + col * (col_w + 24)
        y = grid_y + row * row_h
        if col == 1:
            c.fill(x - 12, y, x - 11, y + row_h - 14, LIGHT_GREY)
        c.text(x, y, kicker, 1, RED)
        y += 14
        y = c.para(x, y, head, 2, INK, col_w, leading=17)
        y += 2
        c.para(x, y, body, 1, (40, 40, 40), col_w, leading=10)

    # ---- markets strip ----
    my = grid_y + 4 * row_h + 4
    c.fill(M, my, right, my + 44, BLACK)
    c.text(M + 12, my + 8, "MARKETS:", 2, (230, 200, 60))
    c.para(M + 12 + text_width("MARKETS: ", 2) + 8, my + 8,
           "NASDAQ DOWN NEARLY 4% ON AI FEARS  *  US JOBLESS CLAIMS 189,000  *  "
           "US Q3 GDP REVISED UP TO 4.3%",
           1, WHITE, right - M - 24 - text_width("MARKETS: ", 2) - 8, leading=10)

    # ---- briefs strip ----
    by = my + 44 + 10
    c.text(M, by, "ALSO TODAY:", 1, RED)
    c.para(M, by + 14,
           "Colombia troops free supermarket hostages  *  Australia and the "
           "Solomon Islands sign a security pact  *  Kuala Lumpur sues Google "
           "for $146m  *  Israeli judges urge dropping the gravest charges "
           "against Netanyahu.",
           1, INK, right - M, leading=11)
    c.hline(M, right, H - 26, INK, 2)
    c.text_centred(W // 2, H - 20, "THE WORLD IN ONE PAGE  -  THURSDAY, 26 NOVEMBER 2026",
                   1, GREY)
    return c

# ---------------------------------------------------------------- PNG
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out

def encode_png(c):
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[y * c.w * 3:(y + 1) * c.w * 3]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/entry.png")
    path = out_dir if out_dir.endswith(".png") else os.path.join(out_dir, "entry.png")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = encode_png(draw_page())
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")

if __name__ == "__main__":
    main()
