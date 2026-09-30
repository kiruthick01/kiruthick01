#!/usr/bin/env python3
"""Generate the lab-notebook README graphics (light + dark variants).

Writes to assets/: banner, info-card, experiments, elements. Featured project
numbers come from scripts/projects.json (a snapshot of the portfolio data), so
every figure on the profile matches the portfolio.

Usage: python make_lab_readme.py
"""
import json
import os
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)
PROJECTS = json.loads((Path(__file__).parent / "projects.json").read_text(encoding="utf8"))

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
JP = "'Noto Serif JP','Yu Mincho','Hiragino Mincho ProN','MS Mincho',serif"

THEMES = {
    "light": dict(paper="#f2ecdd", card="#fbf8f0", ink="#1c1b18", ink2="#57544b",
                  line="#c9c9c2", grid="#344e82", grid_op="0.10", hanko="#d2402a",
                  hi="#f5df73", blue="#2c4d9c", green="#2c7a58", border="#bdb6a3",
                  hi_text="#1c1b18"),
    "dark": dict(paper="#0a0f0d", card="#111a16", ink="#dbe9e1", ink2="#8fa89b",
                 line="#1f3a2d", grid="#7cffb2", grid_op="0.07", hanko="#ff5a45",
                 hi="#ffb454", blue="#6fb3ff", green="#7cffb2", border="#24402f",
                 hi_text="#0a0f0d"),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fade(delay: float, dy: int = 10) -> str:
    """SMIL fade+rise-in that freezes on the last frame."""
    return (
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" additive="sum" '
        f'from="0 {dy}" to="0 0" begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>'
    )


def grid_defs(t, uid):
    return (
        f'<pattern id="g{uid}" width="32" height="32" patternUnits="userSpaceOnUse">'
        f'<path d="M32 0H0V32" fill="none" stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}" stroke-width="1"/></pattern>'
        f'<pattern id="G{uid}" width="128" height="128" patternUnits="userSpaceOnUse">'
        f'<path d="M128 0H0V128" fill="none" stroke="{t["grid"]}" stroke-opacity="{float(t["grid_op"]) * 1.6:.3f}" stroke-width="1.2"/></pattern>'
    )


def paper(t, w, h, uid):
    return (
        f'<rect width="{w}" height="{h}" rx="14" fill="{t["paper"]}"/>'
        f'<rect width="{w}" height="{h}" rx="14" fill="url(#g{uid})"/>'
        f'<rect width="{w}" height="{h}" rx="14" fill="url(#G{uid})"/>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{t["border"]}"/>'
    )


def tape(t, x, y, rot=-4, w=70, h=20):
    return (
        f'<g transform="translate({x} {y}) rotate({rot})"><rect width="{w}" height="{h}" fill="{t["hi"]}" opacity="0.72"/>'
        f'<rect width="{w}" height="{h}" fill="none" stroke="#000" stroke-opacity="0.08"/></g>'
    )


def hanko(t, cx, cy, size=64, rot=8, top="実験", bottom="室"):
    s = size
    return (
        f'<g transform="translate({cx} {cy}) rotate({rot})" opacity="0.92">'
        f'<rect x="{-s/2}" y="{-s/2}" width="{s}" height="{s}" rx="{s*0.16}" fill="none" stroke="{t["hanko"]}" stroke-width="3"/>'
        f'<rect x="{-s/2+4}" y="{-s/2+4}" width="{s-8}" height="{s-8}" rx="{s*0.1}" fill="none" stroke="{t["hanko"]}" stroke-width="1"/>'
        f'<text x="0" y="{-s*0.04}" text-anchor="middle" font-family="{JP}" font-weight="700" font-size="{s*0.36}" fill="{t["hanko"]}">{top}</text>'
        f'<text x="0" y="{s*0.33}" text-anchor="middle" font-family="{JP}" font-weight="700" font-size="{s*0.36}" fill="{t["hanko"]}">{bottom}</text>'
        f'</g>'
    )


def svg(w, h, body, uid, t, title):
    # Static by default: SMIL fade-ins can render blank where SMIL is paused or
    # unsupported. Set ANIMATE=1 to emit the staggered fade-in version.
    if not os.environ.get("ANIMATE"):
        body = re.sub(r"<animate[^>]*/>|<animateTransform[^>]*/>", "", body)
        body = body.replace(' opacity="0"', "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">'
        f'<title>{esc(title)}</title><defs>{grid_defs(t, uid)}</defs>{paper(t, w, h, uid)}{body}</svg>'
    )


# ------------------------------------------------------------------ banner
def banner(t, name):
    w, h = 900, 290
    b = tape(t, 46, 22, -3)
    b += (f'<text x="48" y="64" font-family="{MONO}" font-size="12" letter-spacing="2.4" fill="{t["ink2"]}">'
          f'LAB NOTEBOOK  ·  <tspan fill="{t["hanko"]}">VOL. 01</tspan>  ·  FIELD NOTES OF M KIRUTHICK KANNAA</text>')
    lines = [("I build systems, then measure", 118, 640), ("how far they can be trusted.", 172, 600)]
    hx = 48 + 600 * 20 / 28
    b += f'<rect x="{hx - 4:.0f}" y="146" width="{600 * 8 / 28 + 8:.0f}" height="24" fill="{t["hi"]}" opacity="0.75"/>'
    for i, (txt, y, tl) in enumerate(lines):
        b += (f'<g opacity="0">{fade(0.1 + i * 0.25, 14)}<text x="48" y="{y}" font-family="{SERIF}" font-size="46" font-weight="700" '
              f'fill="{t["ink"]}" textLength="{tl}" lengthAdjust="spacingAndGlyphs">{esc(txt)}</text></g>')
    b += (f'<g opacity="0">{fade(0.7, 8)}<text x="48" y="222" font-family="{SANS}" font-size="16" fill="{t["ink2"]}">'
          f'AI · embedded systems · research engineering  —  Chennai <tspan fill="{t["hanko"]}">→</tspan> Japan</text>'
          f'<text x="48" y="250" font-family="{JP}" font-size="15" fill="{t["hanko"]}">キルティック</text>'
          f'<text x="150" y="250" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{t["ink2"]}">EVERY PROJECT BELOW LISTS WHAT IT PROVES AND WHAT IT DOES NOT</text></g>')
    b += hanko(t, 810, 96, 88, 8)
    return svg(w, h, b, "b" + name, t, "Lab notebook: I build systems, then measure how far they can be trusted")


# --------------------------------------------------------------- info card
ROWS = [
    ("NOW", "ML Engineer | Sensor Fusion and Hydrological Systems"),
    ("PREV", "Full Stack Dev Intern @ ATPAR UI Technology"),
    ("STACK", "Python · Next.js · Solidity · FastAPI"),
    ("HIGHLIGHT", "Marine Ecosystem Monitoring System"),
]


def info_card(t, name):
    w, h = 490, 385
    b = f'<rect x="20" y="30" width="450" height="{h - 60}" rx="6" fill="{t["card"]}" stroke="{t["border"]}"/>'
    b += tape(t, 40, 20, -3, 64, 18)
    b += f'<text x="44" y="70" font-family="{MONO}" font-size="11" letter-spacing="2.2" fill="{t["ink2"]}">SPECIMEN CARD  ·  kiruthick01@github</text>'
    y = 112
    for i, (k, v) in enumerate(ROWS):
        wrapped = textwrap.wrap(v, 40)
        b += f'<g opacity="0">{fade(0.15 + i * 0.2, 8)}'
        b += f'<text x="44" y="{y}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.6" fill="{t["hanko"]}">{k}</text>'
        for j, line in enumerate(wrapped):
            b += f'<text x="140" y="{y + j * 20}" font-family="{SERIF}" font-size="15" fill="{t["ink"]}">{esc(line)}</text>'
        yy = y + (len(wrapped) - 1) * 20 + 16
        b += f'<line x1="44" y1="{yy}" x2="446" y2="{yy}" stroke="{t["line"]}" stroke-dasharray="3 4"/></g>'
        y = yy + 28
    b += f'<g opacity="0">{fade(1.0, 6)}<rect x="44" y="{h - 68}" width="228" height="26" rx="13" fill="{t["hi"]}"/>'
    b += f'<text x="158" y="{h - 51}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1" fill="{t["hi_text"]}">OPEN TO RESEARCH &amp; ENGINEERING</text>'
    b += f'<text x="286" y="{h - 51}" font-family="{JP}" font-size="14" fill="{t["ink2"]}">学習中 · 日本語</text></g>'
    b += hanko(t, 420, 62, 46, 9, "実験", "室")
    return svg(w, h, b, "i" + name, t, "Specimen card: current role, previous role, stack and highlight")


# ------------------------------------------------------------ experiments
STATUS = {"Shipped": "SHIPPED", "Working prototype": "PROTOTYPE",
          "Simulation-validated": "SIMULATED", "In development": "IN DEV"}
TONE = {"Shipped": "green", "Working prototype": "blue", "Simulation-validated": "blue", "In development": "hanko"}


def clip(lines, n):
    if len(lines) <= n:
        return lines
    out = lines[:n]
    out[-1] = out[-1].rstrip(" .,") + "…"
    return out


def experiments(t, name):
    feats = [p for p in PROJECTS if p["featured"]]
    w = 900
    cw, ch, gap, x0, y0 = 272, 214, 24, 18, 78
    rows = (len(feats) + 2) // 3
    h = y0 + rows * (ch + gap) + 10
    b = f'<text x="34" y="46" font-family="{JP}" font-size="24" font-weight="700" fill="{t["hanko"]}">実験</text>'
    b += f'<text x="92" y="44" font-family="{MONO}" font-size="12" letter-spacing="2.4" fill="{t["ink2"]}">EXPERIMENTS  ·  FEATURED  ·  FIGURES COPIED FROM EACH REPO</text>'
    b += f'<line x1="34" y1="58" x2="{w - 34}" y2="58" stroke="{t["line"]}"/>'
    for i, p in enumerate(feats):
        col, row = i % 3, i // 3
        x = x0 + col * (cw + gap) + 6
        y = y0 + row * (ch + gap)
        rot = [-1.1, 0.8, -0.5, 0.9, -0.7, 0.6][i % 6]
        m = p["impact"][0]
        title = clip(textwrap.wrap(p["title"], 22), 2)
        label = clip(textwrap.wrap(m["label"], 34), 2)
        tone = t[TONE[p["status"]]]
        g = f'<g opacity="0" transform="translate({x} {y})">{fade(0.1 + i * 0.12)}<g transform="rotate({rot} {cw/2} {ch/2})">'
        g += f'<rect width="{cw}" height="{ch}" rx="5" fill="{t["card"]}" stroke="{t["border"]}"/>'
        g += tape(t, 26, -9, -3 + (i % 3) * 3, 62, 18)
        g += f'<text x="18" y="38" font-family="{MONO}" font-size="10.5" letter-spacing="1.4" fill="{t["ink2"]}">EXP-{i + 1:02d} · {p["year"]}</text>'
        sw = len(STATUS[p["status"]]) * 6.6 + 14
        g += (f'<g transform="translate({cw - 16 - sw} 24) rotate(-3)"><rect width="{sw}" height="18" rx="2" fill="none" stroke="{tone}" stroke-width="1.6"/>'
              f'<text x="{sw/2}" y="12.5" text-anchor="middle" font-family="{MONO}" font-size="9.5" font-weight="700" letter-spacing="1" fill="{tone}">{STATUS[p["status"]]}</text></g>')
        for j, line in enumerate(title):
            g += f'<text x="18" y="{68 + j * 22}" font-family="{SERIF}" font-size="18" font-weight="700" fill="{t["ink"]}">{esc(line)}</text>'
        g += f'<line x1="18" y1="118" x2="{cw - 18}" y2="118" stroke="{t["line"]}" stroke-dasharray="3 4"/>'
        for j, line in enumerate(label):
            g += f'<text x="18" y="{138 + j * 13}" font-family="{MONO}" font-size="9.5" letter-spacing="0.6" fill="{t["ink2"]}">{esc(line.upper())}</text>'
        g += f'<text x="18" y="196" font-family="{SERIF}" font-size="38" font-weight="700" fill="{t["hanko"]}">{esc(m["value"])}</text>'
        g += '</g></g>'
        b += g
    return svg(w, h, b, "e" + name, t, "Featured experiments with headline figures"), h


# ---------------------------------------------------------------- elements
ELEMENTS = [
    ("Py", "Python", "ai", 3), ("Pt", "PyTorch / ML", "ai", 2), ("Fft", "Signal proc.", "ai", 2),
    ("Nlp", "NLP / BERTopic", "ai", 2), ("Gis", "DEM / geospatial", "ai", 2), ("C++", "C / C++", "emb", 2),
    ("Esp", "ESP32", "emb", 3), ("Rpi", "Raspberry Pi", "emb", 2), ("Mq", "MQTT / I2S", "emb", 2),
    ("Ts", "TypeScript", "web", 3), ("Nx", "Next.js / React", "web", 3), ("Fa", "FastAPI", "web", 2),
    ("So", "Solidity", "web", 2), ("Gt", "Git / CI", "tool", 2), ("Vs", "VS Code ext.", "tool", 2),
    ("Ja", "日本語 (learning)", "tool", 1),
]
GROUPS = {"ai": ("AI & SIGNALS", "blue"), "emb": ("EMBEDDED", "hanko"),
          "web": ("FULL-STACK", "green"), "tool": ("TOOLS & TONGUES", "hi")}


def elements(t, name):
    w, h = 900, 330
    tw, th, gap = 96, 96, 12
    x0 = (w - (8 * tw + 7 * gap)) / 2
    b = f'<text x="34" y="46" font-family="{JP}" font-size="24" font-weight="700" fill="{t["hanko"]}">元素</text>'
    b += f'<text x="92" y="44" font-family="{MONO}" font-size="12" letter-spacing="2.4" fill="{t["ink2"]}">PERIODIC TABLE OF SKILLS  ·  THICKER BORDER = MORE TIME IN THE FIELD</text>'
    b += f'<line x1="34" y1="58" x2="{w - 34}" y2="58" stroke="{t["line"]}"/>'
    for i, (sym, nm, grp, lvl) in enumerate(ELEMENTS):
        x = x0 + (i % 8) * (tw + gap)
        y = 76 + (i // 8) * (th + gap)
        c = t[GROUPS[grp][1]]
        b += f'<g opacity="0" transform="translate({x} {y})">{fade(0.05 + i * 0.04, 6)}'
        b += f'<rect width="{tw}" height="{th}" rx="5" fill="{t["card"]}" stroke="{c}" stroke-width="{lvl + 0.5}"/>'
        b += f'<text x="8" y="16" font-family="{MONO}" font-size="9" fill="{t["ink2"]}">{i + 1:02d}</text>'
        b += f'<text x="{tw/2}" y="56" text-anchor="middle" font-family="{SERIF}" font-size="32" font-weight="700" fill="{t["ink"]}">{esc(sym)}</text>'
        b += f'<text x="{tw/2}" y="82" text-anchor="middle" font-family="{SANS}" font-size="9.5" fill="{t["ink2"]}">{esc(nm)}</text></g>'
    lx = x0
    for key, (label, ck) in GROUPS.items():
        b += f'<rect x="{lx}" y="{h - 30}" width="11" height="11" rx="2" fill="none" stroke="{t[ck]}" stroke-width="2.2"/>'
        b += f'<text x="{lx + 18}" y="{h - 21}" font-family="{MONO}" font-size="10" letter-spacing="1.4" fill="{t["ink2"]}">{esc(label)}</text>'
        lx += 40 + len(label) * 7.6
    return svg(w, h, b, "n" + name, t, "Periodic table of skills")


def main():
    for name, t in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(banner(t, name), encoding="utf8")
        (OUT / f"info-card-{name}.svg").write_text(info_card(t, name), encoding="utf8")
        (OUT / f"experiments-{name}.svg").write_text(experiments(t, name)[0], encoding="utf8")
        (OUT / f"elements-{name}.svg").write_text(elements(t, name), encoding="utf8")
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs to", OUT)


if __name__ == "__main__":
    main()
