#!/usr/bin/env python3
"""Vrstva E — čelní pohled na soukolí (kola jako roztečné kružnice).

Doplněk k elevaci (vrstva C): druhá ortografická projekce stroje. Kolo = roztečná
kružnice (poloměr ∝ počtu zubů); záběr = dotyk kružnic; soustředná kola sdílejí
střed (hřídel/osa). Dva režimy:

  • schématický (default) — polohy hřídelí se dopočtou z počtů zubů (konstantní
    modul; meshující kružnice se dotýkají, sousední hřídele zigzag doprava),
  • věrný (depthing plán) — když KAŽDÁ ozubená hřídel má pole `poloha: [x, y]`
    (mm), kreslí se podle skutečných poloh (měřítko se dopočte tak, aby záběry
    seděly nejlépe).

Použití: python3 tools/render_front.py examples/x.yaml render/x-front.svg
"""
import os, sys, math, html
from collections import defaultdict, deque
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_svg import build, esc  # noqa: E402
import i18n  # noqa: E402

LANG = "cs"

PAPER, INK, THIN, ACC = "#f4eedd", "#1f1c14", "#8a8170", "#9a3b2e"
PAL = ["#2f6b6b", "#9a3b2e", "#5b4b8a", "#b5702a", "#33506b",   # shodná paleta s vrstvou C (render_svg)
       "#3f7d56", "#6f7a2a", "#8a4b6b", "#4a6a8a"]
R_MAX = 118.0          # poloměr největšího kola (px)
MARGIN, TITLE_H = 40, 70


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n else 0.0


def front(B):
    doc = B["doc"]
    P, meshes, col_of = B["P"], B["meshes"], B["col_of"]
    corder, col_gears = B["corder"], B["col_gears"]
    ust_name = B["ust_name"]

    gear_cols = [c for c in corder if col_gears[c]]
    allz = [P[e]["zuby"] for c in gear_cols for e in col_gears[c] if P[e].get("zuby")]
    zmax = max(allz) if allz else 60
    M = R_MAX / zmax                                   # px na zub (poloměr = M·zuby)

    def rad(e):
        z = P[e].get("zuby")
        return M * z if z else 9.0

    def colrad(c):                                     # největší kružnice ve sloupci
        return max((rad(e) for e in col_gears[c]), default=10.0)

    # barva podle ústrojí — stejné klíčování i pořadí jako vrstva C (barvy C↔E sedí)
    blocks = [u["id"] for u in doc["stroj"].get("ustroji", [])]
    uclr = {b: PAL[i % len(PAL)] for i, b in enumerate(blocks)}
    def color(e): return uclr.get(P[e].get("ustroji"), INK)
    present = {P[e].get("ustroji") for c in gear_cols for e in col_gears[c]}
    usts = [b for b in blocks if b in present]      # do legendy jen přítomné bloky, v pořadí modelu

    # adjacenční seznam sloupců přes záběry
    # (guard: přeskoč záběr s prvkem mimo hřídel → col_of je None; jinak KeyError v colrad)
    cadj = defaultdict(list)
    for z, d in meshes:
        cz, cd = col_of(z), col_of(d)
        if cz is None or cd is None or cz == cd:
            continue
        cadj[cz].append((cd, z, d))
        cadj[cd].append((cz, d, z))

    # polohy hřídelí (mm) → sloupce
    hridele = doc["stroj"].get("hridele", [])
    osa_of = {h["id"]: h.get("osa", h["id"]) for h in hridele}
    col_poloha = {}
    for h in hridele:
        if h.get("poloha"):
            col_poloha[osa_of[h["id"]]] = h["poloha"]
    faithful = bool(gear_cols) and all(c in col_poloha for c in gear_cols)
    if col_poloha and not faithful:            # částečné poloha → schématický režim, data se zahazují
        miss = [c for c in gear_cols if c not in col_poloha]
        print(f"⚠ poloha zadána jen u části hřídelí ({len(col_poloha)}/{len(gear_cols)}); "
              f"věrný režim vypnut, kreslím schématicky. Chybí: {', '.join(map(str, miss))}",
              file=sys.stderr)

    center = {}
    if faithful:                                       # věrný režim — skutečné polohy
        ratios = []
        for z, d in meshes:
            cz, cd = col_of(z), col_of(d)
            if cz in col_poloha and cd in col_poloha and cz != cd:
                (x1, y1), (x2, y2) = col_poloha[cz], col_poloha[cd]
                dmm = math.hypot(x2 - x1, y2 - y1)
                if dmm > 0:
                    ratios.append((rad(z) + rad(d)) / dmm)   # px na mm
        pxmm = median(ratios) or 1.0
        for c in gear_cols:
            x, y = col_poloha[c]
            center[c] = (x * pxmm, y * pxmm)
    else:                                              # schématický režim — BFS zigzag
        ALT = math.radians(24)
        counter = 0
        placed = set()
        comps = []                                     # samostatné stroje (jicí, bicí…) = komponenty
        for root in gear_cols:
            if root in placed:
                continue
            local = {root: (0.0, 0.0)}
            placed.add(root)
            q = deque([root])
            while q:
                c = q.popleft()
                for (cc, za, db) in cadj[c]:
                    if cc in placed:
                        continue
                    placed.add(cc)
                    cd = rad(za) + rad(db)             # středová vzdálenost = součet poloměrů
                    ang = ALT * (1 if counter % 2 == 0 else -1)
                    counter += 1
                    x, y = local[c]
                    local[cc] = (x + cd * math.cos(ang), y + cd * math.sin(ang))
                    q.append(cc)
            comps.append(local)
        ycur = 0.0                                     # komponenty pod sebe (bez překryvu)
        for local in comps:
            cys = [local[c][1] + s * colrad(c) for c in local for s in (-1, 1)]
            cxs = [local[c][0] + s * colrad(c) for c in local for s in (-1, 1)]
            lo, hi, lx = min(cys), max(cys), min(cxs)
            dy = ycur - lo
            for c in local:
                center[c] = (local[c][0] - lx, local[c][1] + dy)
            ycur += (hi - lo) + 60

    # normalizace do plátna
    xs = [center[c][0] + dx for c in gear_cols if c in center for dx in (-colrad(c), colrad(c))]
    ys = [center[c][1] + dy for c in gear_cols if c in center for dy in (-colrad(c), colrad(c))]
    minx, miny = (min(xs), min(ys)) if xs else (0, 0)
    ox, oy = MARGIN - minx, TITLE_H + MARGIN - miny
    def pt(c): x, y = center[c]; return (round(x + ox, 1), round(y + oy, 1))
    W = round(max((max(xs) - minx) + 2 * MARGIN if xs else 400, 600), 1)
    H = round((max(ys) - miny) + TITLE_H + 2 * MARGIN + 30, 1) if ys else 300

    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Georgia,\'Times New Roman\',serif">']
    A = out.append
    A(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
    h = doc.get("hlavicka", {})
    A(f'<text x="{MARGIN}" y="40" font-size="17" fill="{INK}">{esc(h.get("nazev","Soukolí"))} '
      f'<tspan font-size="12" fill="{THIN}">— čelní pohled</tspan></text>')
    rezim = "věrný (depthing plán)" if faithful else "schématický (z počtu zubů)"
    A(f'<text x="{MARGIN}" y="58" font-size="11" fill="{THIN}">kola = roztečné kružnice (⌀ ∝ zubům) · '
      f'záběr = dotyk kružnic · režim: {rezim}</text>')

    # spojnice středů (osa záběru)
    drawn = set()
    for z, d in meshes:
        cz, cd = col_of(z), col_of(d)
        if cz == cd or cz not in center or cd not in center:
            continue
        key = frozenset((cz, cd))
        if key in drawn:
            continue
        drawn.add(key)
        (x1, y1), (x2, y2) = pt(cz), pt(cd)
        A(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{THIN}" stroke-width="0.6" stroke-dasharray="2 3"/>')
        # bod záběru
        L = math.hypot(x2 - x1, y2 - y1) or 1
        t = rad(z) / L
        A(f'<circle cx="{round(x1+(x2-x1)*t,1)}" cy="{round(y1+(y2-y1)*t,1)}" r="2.4" '
          f'fill="none" stroke="{ACC}" stroke-width="1.1"/>')

    # kružnice kol
    for c in gear_cols:
        if c not in center:
            continue
        cx, cy = pt(c)
        for e in sorted(col_gears[c], key=lambda e: -rad(e)):
            r = rad(e); typ = P[e].get("typ"); clr = color(e); z = P[e].get("zuby")
            if typ == "krokove-kolo":
                A(f'<circle cx="{cx}" cy="{cy}" r="{round(r,1)}" fill="none" stroke="{clr}" stroke-width="1.5"/>')
                n = min(int(z or 24), 36)
                for k in range(n):
                    a0 = 2 * math.pi * k / n
                    x1 = cx + r * math.cos(a0); y1 = cy + r * math.sin(a0)
                    x2 = cx + (r + 4) * math.cos(a0 + 0.10); y2 = cy + (r + 4) * math.sin(a0 + 0.10)
                    A(f'<path d="M{round(x1,1)},{round(y1,1)} L{round(x2,1)},{round(y2,1)} '
                      f'L{round(cx+r*math.cos(a0+2*math.pi/n),1)},{round(cy+r*math.sin(a0+2*math.pi/n),1)}" '
                      f'fill="none" stroke="{clr}" stroke-width="0.7"/>')
            elif typ == "pastorek":
                A(f'<circle cx="{cx}" cy="{cy}" r="{round(r,1)}" fill="{clr}" fill-opacity="0.18" '
                  f'stroke="{clr}" stroke-width="1.3"/>')
            else:
                A(f'<circle cx="{cx}" cy="{cy}" r="{round(r,1)}" fill="none" stroke="{clr}" stroke-width="1.4"/>')
        # popisek největšího kola (počet zubů) na horním okraji
        big = max(col_gears[c], key=lambda e: rad(e))
        if P[big].get("zuby"):
            A(f'<text x="{cx}" y="{round(cy-rad(big)-4,1)}" font-size="11" fill="{color(big)}" '
              f'text-anchor="middle">{P[big]["zuby"]}</text>')
        # menší soustředná kola: čísla u středu (stohovaná, ať se nepřekrývají)
        i = 0
        for e in col_gears[c]:
            if e is big or not P[e].get("zuby"):
                continue
            A(f'<text x="{cx+6}" y="{round(cy+3+i*11,1)}" font-size="9" fill="{color(e)}">{P[e]["zuby"]}</text>')
            i += 1
        A(f'<circle cx="{cx}" cy="{cy}" r="2.2" fill="{INK}"/>')

    # legenda ústrojí
    ly = H - 16
    lx = MARGIN
    for u in usts:
        A(f'<circle cx="{lx+5}" cy="{ly-4}" r="5" fill="none" stroke="{uclr[u]}" stroke-width="1.4"/>')
        nm = esc(ust_name.get(u, u))
        A(f'<text x="{lx+15}" y="{ly}" font-size="10" fill="{THIN}">{nm}</text>')
        lx += 15 + 7 * len(nm) + 18
    A(f'<text x="{W-MARGIN}" y="40" font-size="10" fill="{THIN}" text-anchor="end" '
      f'font-style="italic">horonotace · vrstva E</text>')
    A('</svg>')
    return "\n".join(out)


def main():
    global LANG
    for a in sys.argv[1:]:
        if a.startswith("--lang="):
            LANG = a.split("=", 1)[1]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0] if args else "examples/ukazka-jednoduchy.yaml"
    dst = args[1] if len(args) > 1 else src.rsplit("/", 1)[-1].replace(".yaml", "-front.svg")
    if "/" not in dst:
        dst = "render/" + dst
    with open(src, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    B = build(doc)
    svg = i18n.localize(front(B), LANG)
    d = os.path.dirname(dst)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(svg)
    nc = len([c for c in B["corder"] if B["col_gears"][c]])
    print(f"→ {dst}  ({nc} hřídelí se soukolím)")


if __name__ == "__main__":
    main()
