#!/usr/bin/env python3
"""Horonotace — vrstva D (pohled na číselník).

Z indikačních prvků modelu (rucka/indikace + jejich ukazuje/druh) složí
SCHEMATICKÝ čelní pohled na ciferník — u astronomických hodin astroláb
(barevné pole den/noc/soumrak, ekliptika se zvěrokruhem, sluneční a měsíční
ručka s fází) a samostatné kalendárium. Polohy ručiček jsou ilustrativní.

Usage:  python3 tools/render_dial.py examples/praga-orloj.yaml render/praga-orloj-cifernik.svg
"""
import sys, os, math, html
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n

LANG = "cs"

PAPER = "#f4eedd"; INK = "#1f1c14"; THIN = "#6b6253"
GOLD = "#b0863a"; GOLD2 = "#7d5e26"
DAY = "#bcd3e2"; NIGHT = "#27384f"; DUSK = "#d2853a"
SUN = "#d8a32e"; MOON = "#d7d9d4"
ZOD = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
ROM = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
MES = ["led", "úno", "bře", "dub", "kvě", "čvn", "čvc", "srp", "zář", "říj", "lis", "pro"]


def esc(s): return html.escape(str(s), quote=True)


def pol(cx, cy, r, deg):                     # 0° = nahoru, po směru hodin
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def indicators(doc):
    out = []
    for p in doc["stroj"].get("prvky", []):
        if p.get("typ") in ("rucka", "indikace"):
            out.append((p.get("ukazuje") or p.get("druh") or p["id"], p.get("druh", "")))
    return out


def astrolabe(cx, cy, R, names):
    """Astroláb jako STEREOGRAFICKÁ PROJEKCE ZE SEVERNÍHO PÓLU (pražský orloj).

    Na rozdíl od běžného evropského astrolábu (projekce z jižního pólu) je orloj
    promítán ze severního nebeského pólu na rovinu rovníku. Důsledek:
      poloměr kružnice deklinace δ:  r(δ) = r_E·tan(45°+δ/2)
      → obratník Raka je VNĚJŠÍ (největší), Kozoroha VNITŘNÍ; střed = jižní pól.
    Ekliptika = excentrická kružnice tečná k oběma obratníkům (Rak nahoře, vnější);
    horizont a soumrak (−18°) = excentrické kružnice pro šířku Prahy. Den je vnější
    pole (kolem zenitu), noc středová (kolem nadiru / jižního pólu).
    """
    EPS = math.radians(23.44)              # sklon ekliptiky
    PHI = math.radians(50.087)             # zeměpisná šířka Prahy
    s = []
    rOut = R - 34                          # vnější obratník = obratník RAKA
    rE = rOut / math.tan(math.pi / 4 + EPS / 2)   # poloměr rovníku = měřítko projekce

    def rdel(d):                           # stereografický poloměr deklinace d — projekce ze SEV. pólu
        return rE * math.tan(math.pi / 4 + d / 2)

    rCan, rEq, rCap = rdel(EPS), rdel(0.0), rdel(-EPS)   # Rak (vnější), rovník, Kozoroh (vnitřní)
    k = (rCan ** 2 - rE ** 2) / (2 * rCan)        # excentricita ekliptiky (math: +y nahoru)
    eclY, Recl = cy - k, math.hypot(rE, k)        # SVG střed a poloměr ekliptiky (Rak nahoře)

    def alm(alt):                          # almukantarát výšky alt → (excentricita_math, poloměr)
        dS = PHI + alt - math.pi / 2       # jižní průsečík poledníku (deklinace)
        dN = math.pi / 2 - PHI + alt       # severní průsečík
        rS, rN = rdel(dS), rdel(dN)
        return (rS - rN) / 2.0, (rS + rN) / 2.0

    hC, hR = alm(0.0)                       # horizont (výška 0°)
    tC, tR = alm(math.radians(-18))        # astronomický soumrak (−18°)
    horY, twiY = cy - hC, cy - tC          # SVG středy (math +y nahoru → SVG nahoru); zde pod středem

    def eclpt(lon):                        # projekce bodu ekliptiky délky lon (°) → SVG (x,y)
        L = math.radians(lon)
        dec = math.asin(math.sin(EPS) * math.sin(L))
        ra = math.atan2(math.cos(EPS) * math.sin(L), math.cos(L))
        r = rdel(dec)
        return cx + r * math.cos(ra), cy - r * math.sin(ra)

    # --- pole den / soumrak / noc: den = VNĚ horizontu (zenit), noc = uvnitř soumraku (nadir) ---
    s.append(f'<clipPath id="disk"><circle cx="{cx}" cy="{cy}" r="{rCan:.1f}"/></clipPath>')
    s.append(f'<g clip-path="url(#disk)">')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{rCan:.1f}" fill="{DAY}"/>')                    # den (vně horizontu)
    s.append(f'<circle cx="{cx}" cy="{horY:.1f}" r="{hR:.1f}" fill="{DUSK}" opacity="0.92"/>')  # soumrak (uvnitř horizontu)
    s.append(f'<circle cx="{cx}" cy="{twiY:.1f}" r="{tR:.1f}" fill="{NIGHT}"/>')              # noc (uvnitř kruž. −18°)
    # obrysy: obratníky + rovník (soustředné kolem pólu), horizont + soumrak (excentrické)
    for rr, w in ((rCap, 0.8), (rEq, 1.0), (rCan, 1.2)):
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="{w}"/>')
    s.append(f'<circle cx="{cx}" cy="{horY:.1f}" r="{hR:.1f}" fill="none" stroke="{GOLD}" stroke-width="1.5"/>')      # horizont
    s.append(f'<circle cx="{cx}" cy="{twiY:.1f}" r="{tR:.1f}" fill="none" stroke="{GOLD}" stroke-opacity="0.7" stroke-width="1" stroke-dasharray="4 3"/>')  # soumrak
    s.append('</g>')
    # popisy pole (ortus vlevo, occasus vpravo — na průsečíku horizontu s rovníkem)
    s.append(f'<text x="{cx-rEq+4:.0f}" y="{cy-6}" font-size="9.5" fill="{GOLD}" font-style="italic">ortus</text>')
    s.append(f'<text x="{cx+rEq-4:.0f}" y="{cy-6}" font-size="9.5" fill="{GOLD}" text-anchor="end" font-style="italic">occasus</text>')
    s.append(f'<text x="{cx}" y="{cy-rCan*0.55:.0f}" font-size="9.5" fill="{GOLD2}" text-anchor="middle" font-style="italic">dies (den)</text>')
    s.append(f'<text x="{cx}" y="{cy+rCan*0.40:.0f}" font-size="9" fill="{DUSK}" text-anchor="middle" font-style="italic">crepusculum</text>')
    s.append(f'<text x="{cx}" y="{twiY+4:.0f}" font-size="9.5" fill="#9fb0c4" text-anchor="middle" font-style="italic">nox</text>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="1.8" fill="{GOLD2}"/>')   # střed = jižní pól (osa rotace réteu)

    # --- ekliptika (zvěrokruh): excentrická kružnice, znamení v projekci ---
    s.append(f'<circle cx="{cx}" cy="{eclY:.1f}" r="{Recl:.1f}" fill="none" stroke="{GOLD}" stroke-width="6" stroke-opacity="0.9"/>')
    s.append(f'<circle cx="{cx}" cy="{eclY:.1f}" r="{Recl+5:.1f}" fill="none" stroke="{GOLD2}" stroke-width="0.8"/>')
    s.append(f'<circle cx="{cx}" cy="{eclY:.1f}" r="{Recl-5:.1f}" fill="none" stroke="{GOLD2}" stroke-width="0.8"/>')
    for i, z in enumerate(ZOD):
        px, py = eclpt(i * 30)             # hranice znamení (stejné délkové úseky → nestejné na kružnici)
        ddx, ddy = px - cx, py - eclY
        dd = math.hypot(ddx, ddy) or 1
        s.append(f'<line x1="{px-ddx/dd*6:.1f}" y1="{py-ddy/dd*6:.1f}" x2="{px+ddx/dd*6:.1f}" y2="{py+ddy/dd*6:.1f}" stroke="{GOLD2}" stroke-width="0.7"/>')
        gx, gy = eclpt(i * 30 + 15)        # glyf doprostřed úseku
        s.append(f'<text x="{gx:.1f}" y="{gy+4:.1f}" font-size="11" fill="{GOLD2}" text-anchor="middle">{z}</text>')

    # --- prstenec římských (německých) hodin ---
    for i, n in enumerate(ROM):
        tx, ty = pol(cx, cy, R - 18, i * 30)
        s.append(f'<text x="{tx:.1f}" y="{ty+4:.1f}" font-size="12" fill="{INK}" text-anchor="middle">{n}</text>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-8}" fill="none" stroke="{GOLD2}" stroke-width="0.8"/>')

    # --- vnější prstenec staročeského času (24 dílků, otočný) ---
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{GOLD}" stroke-width="9" stroke-opacity="0.85"/>')
    for i in range(24):
        x1, y1 = pol(cx, cy, R - 4, i * 15); x2, y2 = pol(cx, cy, R + 4, i * 15)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{PAPER}" stroke-width="1.1"/>')
    if any("staro" in n.lower() for n, _ in names):
        s.append(f'<text x="{cx}" y="{cy-R-8}" font-size="10" fill="{GOLD2}" text-anchor="middle" font-style="italic">staročeský čas (otočný prsten)</text>')

    # --- ručky (poloha na ekliptice = stereografická projekce délky) ---
    def hand(lon, color, lab, kind=None):
        px, py = eclpt(lon)
        dx, dy = px - cx, py - cy
        d = math.hypot(dx, dy) or 1
        ex, ey = cx + dx / d * (R - 6), cy + dy / d * (R - 6)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="2.2"/>')
        if kind == "sun":
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="{SUN}" stroke="{GOLD2}"/>')
            for kk in range(8):
                rx1, ry1 = pol(px, py, 8, kk * 45); rx2, ry2 = pol(px, py, 12, kk * 45)
                s.append(f'<line x1="{rx1:.1f}" y1="{ry1:.1f}" x2="{rx2:.1f}" y2="{ry2:.1f}" stroke="{SUN}" stroke-width="1.2"/>')
        elif kind == "moon":
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7.5" fill="{MOON}" stroke="{GOLD2}"/>')
            s.append(f'<path d="M{px:.1f},{py-7.5:.1f} A7.5 7.5 0 0 0 {px:.1f},{py+7.5:.1f} Z" fill="{INK}"/>')
        lx, ly = cx + dx / d * (R + 14), cy + dy / d * (R + 14)
        anc = "start" if dx >= 0 else "end"
        s.append(f'<text x="{lx:.1f}" y="{ly+3:.1f}" font-size="11" fill="{color}" text-anchor="{anc}">{esc(lab)}</text>')

    has = " ".join(n.lower() for n, _ in names)
    if "slun" in has: hand(48, "#b8801f", "Slunce", kind="sun")                # ~začátek května (ilustrativně)
    if "měs" in has or "mesic" in has or "luna" in has: hand(232, GOLD2, "Měsíc", kind="moon")
    # hvězdná ručka s jarním bodem (počátek ekliptiky, λ=0 → rovník vlevo/vpravo)
    sx, sy = eclpt(0.0)
    dxh, dyh = sx - cx, sy - cy; dh = math.hypot(dxh, dyh) or 1
    s.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dxh/dh*(R-6):.1f}" y2="{cy+dyh/dh*(R-6):.1f}" stroke="{GOLD2}" stroke-width="1.6"/>')
    s.append(f'<text x="{cx+dxh/dh*(R+14):.1f}" y="{cy+dyh/dh*(R+14):.1f}" font-size="10" fill="{GOLD2}" text-anchor="end" font-style="italic">jarní bod</text>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{GOLD2}"/>')
    return s


def calendar(cx, cy, R, names):
    s = []
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{GOLD}" stroke-width="8" stroke-opacity="0.85"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-12}" fill="none" stroke="{GOLD2}" stroke-width="0.8"/>')
    for i in range(12):                        # měsíce
        x1, y1 = pol(cx, cy, R-12, i*30); x2, y2 = pol(cx, cy, R, i*30)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GOLD2}" stroke-width="0.8"/>')
        tx, ty = pol(cx, cy, R-24, i*30 + 15)
        s.append(f'<text x="{tx:.1f}" y="{ty+4:.1f}" font-size="10" fill="{INK}" text-anchor="middle">{MES[i]}</text>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-44}" fill="none" stroke="{GOLD2}" stroke-width="0.7"/>')  # prstenec medailonů
    for i in range(12):
        x1, y1 = pol(cx, cy, R-44, i*30); x2, y2 = pol(cx, cy, R-50, i*30)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GOLD2}" stroke-width="0.6"/>')
    # středový medailon (znak Starého Města — schematicky)
    s.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{PAPER}" stroke="{GOLD2}" stroke-width="1"/>')
    s.append(f'<path d="M{cx-14},{cy-12} h28 v14 q0,12 -14,18 q-14,-6 -14,-18 z" fill="none" stroke="{GOLD2}" stroke-width="1.2"/>')
    s.append(f'<rect x="{cx-5}" y="{cy-8}" width="10" height="14" fill="none" stroke="{GOLD2}" stroke-width="1"/>')
    # pevný index nahoře (kde se čte datum)
    s.append(f'<path d="M{cx-6},{cy-R-6} h12 l-6,12 z" fill="{DUSK}" stroke="{GOLD2}" stroke-width="0.8"/>')
    s.append(f'<text x="{cx}" y="{cy+R+22}" font-size="11" fill="{THIN}" text-anchor="middle" font-style="italic">kalendárium — 365 dílů, deska J. Mánes</text>')
    return s


def roman(n):
    out = ""
    for v, sym in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += sym; n -= v
    return out


def concentric(cx, cy, R, names):
    """Imaginární italský koncentrický číselník: tři soustředné stupnice —
    vnější 24 italských hodin (od západu Slunce), střední 12 „francouzských" hodin,
    vnitřní minutová; jedna dlouhá ruka italských hodin + minutová."""
    s = []
    # vnější prstenec — 24 italských hodin (I…XXIV)
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{GOLD}" stroke-width="8" stroke-opacity="0.85"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-16}" fill="none" stroke="{GOLD2}" stroke-width="0.8"/>')
    for i in range(24):
        a = i * 15
        x1, y1 = pol(cx, cy, R - 4, a); x2, y2 = pol(cx, cy, R + 4, a)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{PAPER}" stroke-width="1.1"/>')
        tx, ty = pol(cx, cy, R - 26, a)
        s.append(f'<text x="{tx:.1f}" y="{ty+4:.1f}" font-size="10.5" fill="{INK}" text-anchor="middle">{roman(i+1)}</text>')
    # střední prstenec — 12 hodin (ore francesi)
    R2 = R - 50
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R2}" fill="none" stroke="{GOLD2}" stroke-width="1"/>')
    for i in range(12):
        a = i * 30
        tx, ty = pol(cx, cy, R2 - 16, a)
        s.append(f'<text x="{tx:.1f}" y="{ty+4:.1f}" font-size="11" fill="{GOLD2}" text-anchor="middle">{ROM[i]}</text>')
    # vnitřní prstenec — minuty (60)
    R3 = R - 92
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R3}" fill="none" stroke="{GOLD2}" stroke-width="0.7"/>')
    for i in range(60):
        x1, y1 = pol(cx, cy, R3, i * 6); x2, y2 = pol(cx, cy, R3 - (6 if i % 5 == 0 else 3), i * 6)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GOLD2}" stroke-width="0.8"/>')
    # ruky: dlouhá italská (24 h) + minutová
    def hand(deg, ln, w, color):
        x2, y2 = pol(cx, cy, ln, deg)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"/>')
    hand(15 * 16 + 7, R - 18, 2.6, "#8a3a2a")     # italská ruka → ~16. hodina
    hand(42 * 6, R3 - 6, 1.8, INK)                # minutová → ~42. min
    s.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{GOLD2}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="{PAPER}"/>')
    # popisky stupnic
    s.append(f'<text x="{cx}" y="{cy+R2-2:.0f}" font-size="9" fill="{GOLD2}" text-anchor="middle" font-style="italic">ore francesi (12 h)</text>')
    s.append(f'<text x="{cx}" y="{cy+R+20}" font-size="11" fill="{THIN}" text-anchor="middle" font-style="italic">koncentrický číselník (imaginární italský stroj)</text>')
    return s


def render(doc):
    names = indicators(doc)
    has = " ".join(n.lower() for n, _ in names)
    astro = ("slun" in has) and ("měs" in has or "mesic" in has or "luna" in has)
    ital = ("ital" in has) or ("koncentr" in has)
    cal = "kalend" in has
    W, H = 940, 560
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
         f'font-family="Georgia,\'Times New Roman\',serif" role="img">',
         f'<defs></defs>', f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    hl = doc.get("hlavicka", {})
    s.append(f'<text x="40" y="44" font-size="21" fill="{INK}">{esc(hl.get("nazev",""))}</text>')
    if astro:
        sub = ("Pohled na číselník (vrstva D). Astroláb = stereografická projekce ZE SEV. pólu "
               "(Rak vnější, Kozoroh vnitřní); polohy ukazatelů ilustrativní.")
    elif ital:
        sub = "Pohled na číselník (vrstva D). Soustředné stupnice (italské + francouzské hodiny, minuty); polohy ilustrativní."
    else:
        sub = "Pohled na číselník (vrstva D) — schematicky. Polohy ukazatelů jsou ilustrativní."
    s.append(f'<text x="40" y="66" font-size="12" fill="{THIN}">{sub}</text>')
    # defs (clipy) musí být uvnitř svg; vložíme je z astrolabe() na začátek
    body = []
    if astro:
        body += astrolabe(280, 300, 218, names)
    elif ital:
        body += concentric(300 if cal else 470, 300, 218, names)
    if cal:
        body += calendar(710, 318, 150, names)
    if not astro and not ital and not cal:
        body.append(f'<text x="{W/2}" y="{H/2}" font-size="14" fill="{THIN}" text-anchor="middle">Pro tento stroj zatím není šablona číselníku.</text>')
    # clipPath musí být před použitím — astrolabe je vrací jako první prvky, OK
    s += body
    s.append(f'<text x="{W-30}" y="{H-16}" font-size="10" fill="{THIN}" text-anchor="end" font-style="italic">horonotace · vrstva D (číselník)</text>')
    s.append('</svg>')
    return "\n".join(s)


def run(src, out):
    doc = yaml.safe_load(open(src))
    svg = i18n.localize(render(doc), LANG)
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    open(out, "w").write(svg)
    print(f"→ {out}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        if a.startswith("--lang="):
            LANG = a.split("=", 1)[1]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) >= 2:
        run(args[0], args[1])
    else:
        run("examples/praga-orloj.yaml", "render/praga-orloj-cifernik.svg")
