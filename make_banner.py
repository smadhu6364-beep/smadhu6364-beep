"""
Builds light.svg and dark.svg: an F1-style profile banner with animated
start lights (five reds come on one by one, then go out: lights out).
Run: python make_banner.py
"""

THEMES = {
    "dark": dict(bg="#0b0d10", panel="#15181d", text="#f2f4f7", sub="#9aa4b2",
                 line="#2a2f37", kerb_a="#e10600", kerb_b="#f2f4f7", off="#3a1010"),
    "light": dict(bg="#f6f7f9", panel="#ffffff", text="#111418", sub="#5b6573",
                  line="#d9dee5", kerb_a="#e10600", kerb_b="#111418", off="#e8c9c9"),
}

W, H = 1200, 340
FONT = "'Titillium Web','Segoe UI','Helvetica Neue',Arial,sans-serif"


def checkered(x, y, cols, rows, size, a, b):
    out = []
    for r in range(rows):
        for c in range(cols):
            col = a if (r + c) % 2 == 0 else b
            out.append(f'<rect x="{x + c * size}" y="{y + r * size}" width="{size}" height="{size}" fill="{col}"/>')
    return "".join(out)


def kerb(y, t):
    seg = []
    for i in range(0, W, 40):
        col = t["kerb_a"] if (i // 40) % 2 == 0 else t["kerb_b"]
        seg.append(f'<polygon points="{i},{y} {i + 40},{y} {i + 30},{y + 12} {i - 10},{y + 12}" fill="{col}"/>')
    return "".join(seg)


def lights(t):
    """Five start lights. Each turns red in sequence (0.6 s apart), all go
    out together at 3.6 s, cycle repeats every 7 s."""
    out = []
    cx0, cy = 870, 118
    for i in range(5):
        cx = cx0 + i * 58
        on = 0.6 * (i + 1)
        # keyTimes over a 7 s loop: off -> on at `on` -> off at 3.6
        k_on, k_off = on / 7, 3.6 / 7
        out.append(
            f'<rect x="{cx - 24}" y="{cy - 46}" width="48" height="92" rx="10" fill="{t["panel"]}" stroke="{t["line"]}"/>'
            f'<circle cx="{cx}" cy="{cy - 20}" r="15" fill="{t["off"]}"/>'
            f'<circle cx="{cx}" cy="{cy + 20}" r="15" fill="{t["off"]}">'
            f'<animate attributeName="fill" dur="7s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{k_on:.4f};{k_off:.4f}" values="{t["off"]};#ff1e00;{t["off"]}"/></circle>'
        )
    out.append(f'<text x="{cx0 + 116}" y="{cy + 78}" text-anchor="middle" font-family="{FONT}" font-size="15" '
               f'font-weight="700" letter-spacing="4" fill="{t["sub"]}">LIGHTS OUT AND AWAY WE GO'
               f'<animate attributeName="opacity" dur="7s" repeatCount="indefinite" calcMode="discrete" '
               f'keyTimes="0;{3.6 / 7:.4f};{6.4 / 7:.4f}" values="0;1;0"/></text>')
    return "".join(out)


def banner(name):
    t = THEMES[name]
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Madhu Sudhan, MSc Business Analytics at DCU, data and analytics">',
         f'<rect width="{W}" height="{H}" rx="22" fill="{t["bg"]}"/>',
         # speed lines
         *[f'<rect x="{-200 + i * 37}" y="{40 + i * 22}" width="{260 - i * 14}" height="3" rx="1.5" fill="{t["line"]}">'
           f'<animate attributeName="x" from="{-300}" to="{W}" dur="{2.4 + i * 0.35:.2f}s" repeatCount="indefinite"/></rect>'
           for i in range(8)],
         kerb(H - 30, t),
         checkered(W - 150, 20, 6, 2, 20, t["text"], t["bg"]),
         # timing-tower name plate
         f'<rect x="48" y="62" width="10" height="150" fill="#e10600"/>',
         f'<text x="78" y="120" font-family="{FONT}" font-size="58" font-weight="800" fill="{t["text"]}">MADHU SUDHAN</text>',
         f'<text x="80" y="160" font-family="{FONT}" font-size="22" font-weight="600" fill="{t["sub"]}">'
         f'MSc Business Analytics · Dublin City University</text>',
         f'<text x="80" y="196" font-family="{FONT}" font-size="20" fill="{t["sub"]}">'
         f'SQL · Python · Power BI · ML evaluation · 3 yrs travel operations</text>',
         # position / interval style chips
         f'<rect x="80" y="226" width="172" height="40" rx="8" fill="#e10600"/>',
         f'<text x="166" y="252" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="#ffffff">P1 · DATA ANALYST</text>',
         f'<rect x="264" y="226" width="236" height="40" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>',
         f'<text x="382" y="252" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="{t["text"]}">GRID: DUBLIN, IRELAND</text>',
         lights(t),
         '</svg>']
    return "".join(s)


if __name__ == "__main__":
    for name in THEMES:
        with open(f"{name}.svg", "w", encoding="utf-8") as f:
            f.write(banner(name))
    print("written light.svg, dark.svg")
