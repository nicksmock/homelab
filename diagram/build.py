"""Build homelab.svg from lab.toml.

Usage: python build.py [--png]

--png also renders homelab.png with headless Chrome or Edge, if one is installed.
Standard library only.
"""

import base64
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
DATA = HERE / "lab.toml"
OUT = HERE / "homelab.svg"
LOGOS = HERE / "logos"
WORDMARK = HERE / "brand" / "wordmark-dark.svg"

# Colour tokens from my brand assets, plus neutral steps between them.
BG = "#0A0E14"
SURFACE = "#161B22"
TILE = "#1C222B"
BORDER = "#262D37"
FG = "#E6EDF3"
MUTED = "#8B949E"
DIM = "#5C6570"
ACCENT = "#A855F7"

SANS = "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Mono', Consolas, ui-monospace, monospace"

W = 1440
M = 60
INNER = W - 2 * M
PAD = 24


def text(x, y, s, size=14, fill=FG, font=SANS, weight=400, anchor="start", spacing=0):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}>{escape(s)}</text>')


def eyebrow(x, y, s, fill=ACCENT, anchor="start"):
    return text(x, y, s.upper(), 11, fill, MONO, 500, anchor, 1.6)


def rect(x, y, w, h, fill=SURFACE, stroke=BORDER, rx=12, dash=None, sw=1):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, stroke=BORDER, sw=1.5, arrow=False):
    a = ' marker-end="url(#arrow)"' if arrow else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}"{a}/>')


def path(d, stroke=BORDER, sw=1.5):
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>'


def text_w(s, size):
    """Rough width of sans text. Good enough to size chips."""
    return len(s) * size * 0.54


# Icons ---------------------------------------------------------------------

missing_logos = set()


def logo_uri(slug):
    for ext, mime in (("svg", "image/svg+xml"), ("png", "image/png")):
        f = LOGOS / f"{slug}.{ext}"
        if f.exists():
            return f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()
    return None


def monogram(label):
    letters = re.sub(r"[^A-Za-z0-9]", "", label)
    return (letters[:1].upper() + letters[1:2].lower()) or "?"


def icon(cx, cy, size, slug, label):
    uri = logo_uri(slug)
    if uri:
        return (f'<image x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size}" '
                f'height="{size}" href="{uri}" preserveAspectRatio="xMidYMid meet"/>')
    missing_logos.add(slug)
    return (rect(cx - size / 2, cy - size / 2, size, size, BG, "#3B2A55", 7)
            + text(cx, cy + size * 0.17, monogram(label), size * 0.42, ACCENT, MONO, 600, "middle"))


# Cards ---------------------------------------------------------------------

TILE_H = 78
TILE_GAP = 8
GROUP_HEAD = 22
ROW_GAP = 14


def tile(x, y, w, t):
    out = [rect(x, y, w, TILE_H, TILE, BORDER, 9)]
    out.append(icon(x + w / 2, y + 24, 28, t.get("icon", t["id"]), t["label"]))
    out.append(text(x + w / 2, y + 54, t["label"], 12, FG, SANS, 500, "middle"))
    if t.get("note"):
        out.append(text(x + w / 2, y + 68, t["note"], 10, MUTED, SANS, 400, "middle"))
    if t.get("public"):
        out.append(public_badge(x + w - 12, y + 12))
    return "".join(out)


def public_badge(cx, cy):
    """Marks a service reachable from the internet."""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{ACCENT}" fill-opacity="0.18"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="{ACCENT}"/>')


def wifi(x, y, color=MUTED):
    """Small Wi-Fi glyph, (x, y) is the bottom dot."""
    return (f'<g fill="none" stroke="{color}" stroke-width="1.4" stroke-linecap="round">'
            f'<path d="M{x - 7:.1f},{y - 6:.1f} a10,10 0 0 1 14,0"/>'
            f'<path d="M{x - 4:.1f},{y - 3:.1f} a5.5,5.5 0 0 1 8,0"/></g>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.4" fill="{color}"/>')


def layout_groups(groups, cols):
    """Flow groups into rows of `cols` tiles, a blank column between neighbours."""
    rows, row, col = [], [], 0
    for g in groups:
        n = len(g["tiles"])
        need = n + (1 if row else 0)
        if row and (col + need > cols or g.get("section")):
            rows.append(row)
            row, col = [], 0
            need = n
        row.append((col + (1 if row else 0), g))
        col += need
    if row:
        rows.append(row)
    return rows


SECTION_H = 26


def groups_height(groups, cols):
    rows = layout_groups(groups, cols)
    h = 0
    for r in rows:
        named = any(g.get("name") for _, g in r)
        h += (SECTION_H if r[0][1].get("section") else 0)
        h += (GROUP_HEAD if named else 0) + TILE_H + ROW_GAP
    return h - ROW_GAP if rows else 0


def card_height(c, w):
    h = 20 + 16 + 40  # eyebrow, name
    if c.get("spec"):
        h += 26
    if c.get("storage"):
        h += 16 + 16 + 26 * len(c["storage"])
    h += 18
    h += groups_height(c.get("groups", []), c["cols"])
    return h + PAD


def section_counts(c):
    """Tile count per section. A group with no section belongs to the one above it."""
    counts, cur = {}, None
    for g in c.get("groups", []):
        cur = g.get("section", cur)
        counts[cur] = counts.get(cur, 0) + len(g["tiles"])
    return counts


def card(x, y, w, h, c):
    out = [rect(x, y, w, h)]
    out.append(f'<rect x="{x + PAD - 10}" y="{y + 26}" width="3" height="56" rx="1.5" fill="{ACCENT}"/>')
    cy = y + 38
    out.append(eyebrow(x + PAD, cy, c["eyebrow"]))
    if c.get("addr"):
        out.append(text(x + w - PAD, cy, c["addr"], 12, MUTED, MONO, 400, "end"))
    cy += 40
    out.append(text(x + PAD, cy, c["name"], 34, FG, SANS, 700, spacing=-0.5))
    if c.get("spec"):
        cy += 26
        out.append(text(x + PAD, cy, c["spec"], 14, MUTED))
    if c.get("storage"):
        cy += 16
        bh = 16 + 26 * len(c["storage"])
        out.append(rect(x + PAD, cy, w - 2 * PAD, bh, BG, BORDER, 9))
        for i, (k, v) in enumerate(c["storage"]):
            ry = cy + 28 + 26 * i
            out.append(text(x + PAD + 16, ry, k, 12, ACCENT, MONO, 500))
            out.append(text(x + PAD + 86, ry, v, 14, FG))
        cy += bh
    cy += 18
    cols = c["cols"]
    counts = section_counts(c)
    tw = (w - 2 * PAD - (cols - 1) * TILE_GAP) / cols
    for r in layout_groups(c.get("groups", []), cols):
        sec = r[0][1].get("section")
        if sec:
            cy += 14
            out.append(eyebrow(x + PAD, cy, sec))
            out.append(text(x + w - PAD, cy, str(counts[sec]), 11, MUTED, MONO, 500, "end"))
            cy += 12
        named = any(g.get("name") for _, g in r)
        if named:
            for col, g in r:
                if g.get("name"):
                    out.append(text(x + PAD + col * (tw + TILE_GAP), cy + 14, g["name"].upper(),
                                    10, MUTED, MONO, 500, spacing=1.2))
            cy += GROUP_HEAD
        for col, g in r:
            for i, t in enumerate(g["tiles"]):
                out.append(tile(x + PAD + (col + i) * (tw + TILE_GAP), cy, tw, t))
        cy += TILE_H + ROW_GAP
    return "".join(out)


# Sections ------------------------------------------------------------------

def header(d, counts):
    out = []
    # The wordmark is optional: without the file the header starts with the title.
    if WORDMARK.exists():
        wm = WORDMARK.read_text(encoding="utf-8")
        inner = re.search(r"<svg[^>]*>(.*)</svg>", wm, re.S).group(1)
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
        out.append(f'<svg x="{M - 12 * 30 / 82:.1f}" y="40" width="{294 * 30 / 82:.1f}" height="30" '
                   f'viewBox="0 0 294 82">{inner}</svg>')
    out.append(text(M, 124, d["meta"]["title"], 56, FG, SANS, 700, spacing=-1.5))
    stats = d["stats"]
    sw = 150
    for i, s in enumerate(stats):
        v = s["value"]
        if v.startswith("auto:"):
            v = f"{counts[v[5:]]:02d}"
        sx = W - M - (len(stats) - i) * sw + sw
        out.append(text(sx, 100, v, 44, ACCENT if i == 0 else FG, MONO, 600, "end", -1))
        out.append(text(sx, 126, s["label"].upper(), 11, MUTED, MONO, 500, "end", 1.6))
    return "".join(out)


def edge_row(d, y):
    h = 84
    out = []
    xs = []
    x = M
    widths = [250, 300]
    gap = 44
    for e, w in zip(d["edge"], widths):
        out.append(rect(x, y, w, h))
        out.append(eyebrow(x + 20, y + 28, e["eyebrow"]))
        out.append(text(x + 20, y + 54, e["name"], 20, FG, SANS, 600))
        out.append(text(x + 20, y + 72, e["sub"], 12, MUTED))
        if e.get("icon"):
            out.append(icon(x + w - 40, y + h / 2, 36, e["icon"], e["name"]))
        xs.append((x, w))
        x += w + gap
    for (x1, w1), (x2, _) in zip(xs, xs[1:] + [(x, 0)]):
        out.append(line(x1 + w1 + 6, y + h / 2, x2 - 8, y + h / 2, ACCENT, 1.5, True))
    g = d["edge_group"]
    gw = W - M - x
    out.append(rect(x, y, gw, h))
    out.append(eyebrow(x + 20, y + 28, g["eyebrow"]))
    iw = (gw - 40) / len(g["items"])
    for i, it in enumerate(g["items"]):
        ix = x + 20 + i * iw
        if it.get("icon"):
            out.append(icon(ix + 13, y + 61, 26, it["icon"], it["name"]))
            ix += 36
        out.append(text(ix, y + 54, it["name"], 17, FG, SANS, 600))
        out.append(text(ix, y + 72, it["sub"], 12, MUTED))
    return "".join(out), y + h, x + gw / 2


def network_row(d, y, drop_x):
    nets = d["networks"]
    gap = 14
    pw = (INNER - gap * (len(nets) - 1)) / len(nets)
    ph = 58
    bus_y = y + 24
    py = bus_y + 16
    centers = [M + i * (pw + gap) + pw / 2 for i in range(len(nets))]
    out = [line(drop_x, y, drop_x, bus_y), line(centers[0], bus_y, centers[-1], bus_y)]
    host_x = None
    for i, n in enumerate(nets):
        px = M + i * (pw + gap)
        hot = n.get("hosts")
        out.append(line(centers[i], bus_y, centers[i], py))
        out.append(rect(px, py, pw, ph, SURFACE, ACCENT if hot else BORDER, 10, sw=1.5 if hot else 1))
        out.append(text(px + 16, py + 25, n["name"], 15, FG, SANS, 600))
        out.append(text(px + pw - 16, py + 25, n["tag"], 12, ACCENT, MONO, 600, "end"))
        out.append(text(px + 16, py + 44, n["subnet"], 11, MUTED, MONO, 400))
        if n.get("ssid"):
            out.append(text(px + pw - 16, py + 44, n["ssid"], 12, FG, SANS, 500, "end"))
            out.append(wifi(px + pw - 26 - text_w(n["ssid"], 12), py + 43))
        if hot:
            host_x = centers[i]
    return "".join(out), py + ph, host_x


def flows(d, y):
    out = [eyebrow(M, y, "Data paths")]
    y += 18
    row_h = 46
    out.append(rect(M, y, INNER, 20 + row_h * len(d["flows"]), SURFACE))
    for i, f in enumerate(d["flows"]):
        ry = y + 10 + i * row_h
        if i:
            out.append(line(M + 20, ry, W - M - 20, ry, BORDER, 1))
        out.append(text(M + 24, ry + 28, f["name"].upper(), 11, ACCENT, MONO, 600, spacing=1.4))
        x = M + 190
        for j, step in enumerate(f["steps"]):
            for k, s in enumerate([step] if isinstance(step, str) else step):
                if k:
                    x += 8
                cw = text_w(s, 13) + 28
                out.append(rect(x, ry + 9, cw, 28, TILE, BORDER, 14))
                out.append(text(x + cw / 2, ry + 28, s, 13, FG, SANS, 500, "middle"))
                x += cw
            if j < len(f["steps"]) - 1:
                out.append(line(x + 5, ry + 23, x + 23, ry + 23, ACCENT, 1.5, True))
                x += 30
        if f.get("note"):
            out.append(text(W - M - 24, ry + 28, f["note"], 12, MUTED, SANS, 400, "end"))
    return "".join(out), y + 20 + row_h * len(d["flows"])


def schedule(d, y):
    sc = d["schedule"]
    out = [eyebrow(M, y, sc["title"])]
    y += 18
    h = 168
    out.append(rect(M, y, INNER, h, SURFACE))
    x0, x1 = M + 40, W - M - 40
    axis = y + 112

    def hx(hhmm):
        hh, mm = (int(v) for v in hhmm.split(":"))
        return x0 + (x1 - x0) * (hh * 60 + mm) / 1440

    out.append(line(x0, axis, x1, axis, BORDER, 1.5))
    for hh in range(0, 25, 3):
        tx = hx(f"{hh}:00")
        out.append(line(tx, axis, tx, axis + 5, DIM, 1))
        out.append(text(tx, axis + 20, f"{hh:02d}:00", 10, DIM, MONO, 400, "middle"))
    # Recurring jobs: a tick every N minutes on a lane under the axis.
    n = 1440 // sc["every"]
    for i in range(n):
        tx = x0 + (x1 - x0) * i / n
        out.append(line(tx, axis + 30, tx, axis + 36, ACCENT, 1))
    out.append(text(x0, axis + 50, sc["every_label"], 11, MUTED, SANS))
    out.append(text(x1, axis + 50, sc["monthly"], 11, MUTED, SANS, 400, "end"))
    # Daily events: one row of labels, pushed right so they never overlap,
    # each joined to its time by an angled leader.
    prev_end = 0
    for e in sorted(sc["events"], key=lambda e: e["at"]):
        ex = hx(e["at"])
        meta = f'{e["at"]}  {e["host"]}'
        lw = max(text_w(e["label"], 13), len(meta) * 6.6)
        lx = max(ex, prev_end + 28)
        prev_end = lx + lw
        color = DIM if e.get("muted") else ACCENT
        out.append(path(f"M{lx:.1f},{y + 22:.1f} V{y + 70:.1f} L{ex:.1f},{y + 90:.1f} V{axis:.1f}",
                        color, 1.2))
        out.append(f'<circle cx="{ex:.1f}" cy="{axis:.1f}" r="4" fill="{color}"/>')
        out.append(text(lx + 8, y + 34, meta, 10, color, MONO, 500, spacing=0.6))
        out.append(text(lx + 8, y + 52, e["label"], 13, MUTED if e.get("muted") else FG, SANS, 500))
    return "".join(out), y + h


def legend(y, show_public):
    out = []
    lx = M
    if show_public:
        out += [public_badge(M + 7, y - 4),
                text(M + 22, y, "Reachable from the internet through the Cloudflare tunnel, behind the app's own login",
                     12, MUTED)]
        lx = M + 640
    out.append(rect(lx, y - 12, 26, 16, SURFACE, ACCENT, 5, sw=1.5))
    out.append(text(lx + 36, y, "VLAN the servers sit on", 12, MUTED))
    lx += 230
    out.append(line(lx, y - 4, lx + 24, y - 4, ACCENT, 1.5, True))
    out.append(text(lx + 36, y, "Data or traffic flow", 12, MUTED))
    return "".join(out)


def build(d):
    cards = d["cards"]
    counts = {
        "hosts": sum(1 for c in cards if c.get("server")),
        "containers": sum(section_counts(c).get("Containers", 0) for c in cards),
        "networks": len(d["networks"]),
    }
    body = [header(d, counts)]

    s, y, drop_x = edge_row(d, 170)
    body.append(s)
    s, y, host_x = network_row(d, y, drop_x)
    body.append(s)

    main = [c for c in cards if c["column"] == "main"]
    side = [c for c in cards if c["column"] == "side"]
    mw = 850
    sx, sw = M + mw + 20, INNER - mw - 20
    gap = 20
    mh = [card_height(c, mw) for c in main]
    sh = [card_height(c, sw) for c in side]
    total = max(sum(mh) + gap * (len(mh) - 1), sum(sh) + gap * (len(sh) - 1))
    for hs, cs in ((mh, main), (sh, side)):
        spare = total - (sum(hs) + gap * (len(hs) - 1))
        for i, c in enumerate(cs):
            if c.get("stretch") or (spare and i == len(cs) - 1 and not any(k.get("stretch") for k in cs)):
                hs[i] += spare
                break

    top = y + 40
    bus_y = y + 20
    targets = [M + mw / 2, sx + sw / 2]
    body.append(line(host_x, y, host_x, bus_y))
    body.append(line(min(targets + [host_x]), bus_y, max(targets + [host_x]), bus_y))
    for tx in targets:
        body.append(line(tx, bus_y, tx, top))

    cy = top
    for c, h in zip(main, mh):
        body.append(card(M, cy, mw, h, c))
        cy += h + gap
    cy = top
    for c, h in zip(side, sh):
        body.append(card(sx, cy, sw, h, c))
        cy += h + gap

    s, y = flows(d, top + total + 48)
    body.append(s)
    if d.get("schedule"):
        s, y = schedule(d, y + 44)
        body.append(s)
    show_public = any(t.get("public") for c in cards for g in c.get("groups", []) for t in g["tiles"])
    body.append(legend(y + 40, show_public))

    fy = y + 70
    body.append(line(M, fy, W - M, fy, BORDER, 1))
    body.append(text(M, fy + 30, f"VERIFIED {d['meta']['verified']} · BUILT FROM lab.toml",
                     11, DIM, MONO, 500, spacing=1.4))
    body.append(text(W - M, fy + 30, d["meta"]["footer_right"], 12, DIM, SANS, 400, "end"))
    H = fy + 60

    defs = (f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{ACCENT}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
            f'width="100%" style="display:block" role="img" aria-label="{escape(d["meta"]["title"])} diagram">\n'
            f'<title>{escape(d["meta"]["title"])}</title>\n{defs}\n'
            f'<rect width="100%" height="100%" fill="{BG}"/>\n'
            + "\n".join(body) + "\n</svg>\n"), H


def render_png(svg_path, h):
    for exe in ("chrome", "msedge",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        found = shutil.which(exe) or (Path(exe).exists() and exe)
        if found:
            png = svg_path.with_suffix(".png")
            subprocess.run([found, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            f"--window-size={W},{int(h)}", "--default-background-color=0A0E14FF",
                            f"--screenshot={png}", svg_path.as_uri()],
                           check=True, capture_output=True)
            return png
    return None


def main():
    d = tomllib.loads(DATA.read_text(encoding="utf-8"))
    svg, h = build(d)
    OUT.write_bytes(svg.encode("utf-8"))
    print(f"wrote {OUT.name} ({W} x {h:.0f})")
    if missing_logos:
        print("no logo file, using monogram:", ", ".join(sorted(missing_logos)))
    if "--png" in sys.argv:
        png = render_png(OUT, h)
        print(f"wrote {png.name}" if png else "no Chrome or Edge found, skipped PNG")


if __name__ == "__main__":
    main()
