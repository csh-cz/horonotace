#!/usr/bin/env python3
"""Horonotace — vrstva C (vykreslení), v0.2.

Z horonotace YAML generuje schématickou „elevaci" soukolí ve stylu Oechslinových
tabulí / strojírenských kinematických schémat:

  * hřídel        = svislice mezi deskami (rám = obrys se stojkami),
  * soustředné    = jeden sloupec (Stützrohr), kola nad sebou,
    hřídele (osa)
  * kolo/pastorek = uzel na hřídeli s ⌐ závorkou a počtem zubů,
  * záběr         = stupňovité ortogonální spojení,
  * podsystém     = popisek se svorkou nad deskami,
  * krok/kyvadlo/závaží/indikace = vlastní značky.

Usage:  python3 tools/render_svg.py examples/praga-orloj.yaml render/praga-orloj.svg
        python3 tools/render_svg.py --all
"""
import sys, os, html, math
from collections import deque, defaultdict
import yaml

PAPER = "#f4eedd"; INK = "#1f1c14"; THIN = "#6b6253"; HAIR = "#8d8473"
ACC = "#9a3b2e"      # spouštění / bití
DRV = "#705f31"      # pohon
OUT = "#33506b"      # indikace

GEARS = {"kolo", "pastorek", "krokove-kolo", "venec"}
OUTS  = {"rucka", "indikace"}
BICI  = {"zaverka", "rechen", "staffel", "vetrnik", "kladivko", "cimbal", "zvon"}
DRIVE_T = {"zavazi", "pero", "perovnik"}
COLW, ROWH = 168, 64
TOP_PLATE, Y0 = 168, 232
DCY = 96                 # střed ciferníku nad deskou
DIAL_R = 17
MESH_FACTOR = 1.4        # hustota: rozteč sloupců = středová vzdálenost záběru × MESH_FACTOR
                         #   1,0 = přímý záběr (roztečné kružnice se dotýkají), >1 = volnější


def esc(s): return html.escape(str(s), quote=True)


def build(doc):
    st = doc["stroj"]
    P = {p["id"]: p for p in st.get("prvky", [])}
    hridele = st.get("hridele", [])
    vazby = st.get("vazby", [])
    ust_name = {u["id"]: u.get("nazev", u["id"]) for u in st.get("ustroji", [])}

    arbor_of, arbor_elems, osa_of = {}, {}, {}
    for h in hridele:
        arbor_elems[h["id"]] = list(h.get("nese", []))
        osa_of[h["id"]] = h.get("osa", h["id"])      # sloupec = osa nebo sama hřídel
        for e in h.get("nese", []):
            arbor_of[e] = h["id"]

    meshes = [(v["z"], v["do"]) for v in vazby
              if v.get("typ") == "zaber" and v.get("z") in P and v.get("do") in P]

    def col_of(e):  return osa_of.get(arbor_of.get(e), None)
    def is_gear(e): return (e in P) and (P[e].get("typ") in GEARS or "zuby" in P[e])

    # sloupce (osa) -> hřídele, a pořadí gear prvků ve sloupci
    col_arbors = defaultdict(list)
    for h in hridele:
        col_arbors[osa_of[h["id"]]].append(h["id"])
    col_gears = {}
    for c, arbs in col_arbors.items():
        g = []
        for a in arbs:
            g += [e for e in arbor_elems[a] if is_gear(e)]
        col_gears[c] = g

    # --- root = kolo NA HŘÍDELI poháněné pohonem, jinak první kolo na hřídeli ---
    root = None
    for v in vazby:
        d = v.get("do")
        if v.get("typ") == "pohon" and is_gear(d) and arbor_of.get(d):
            root = d; break
    if root is None:
        for h in hridele:
            gg = [e for e in h.get("nese", []) if is_gear(e)]
            if gg: root = gg[0]; break

    # --- řádky (svislá pozice) ---
    row = {}
    if root is not None:
        row[root] = 0
        q = deque([root]); seen = {root}
        while q:
            u = q.popleft()
            # poháněná kola (u je hnací); soustředná skupina se stohuje
            kids = [d for z, d in meshes if z == u and d not in row]
            grp = defaultdict(list)
            for d in kids: grp[col_of(d)].append(d)
            for _, mem in grp.items():
                for i, d in enumerate(mem):
                    row[d] = row[u] + i
                    if d not in seen: seen.add(d); q.append(d)
            # hnací kola (u je hnané)
            for z, d in meshes:
                if d == u and z not in row:
                    row[z] = row[u]
                    if z not in seen: seen.add(z); q.append(z)
            # souosost v rámci JEDNÉ hřídele
            a = arbor_of.get(u)
            if a:
                seq = [e for e in arbor_elems[a] if is_gear(e)]
                if u in seq:
                    iu = seq.index(u)
                    for j, g in enumerate(seq):
                        if g not in row:
                            row[g] = row[u] + (j - iu)
                            if g not in seen: seen.add(g); q.append(g)
    # zbylá kola
    for c, gs in col_gears.items():
        base = max([row.get(g, -1) for g in gs] + [-1]) + 1
        k = 0
        for g in gs:
            if g not in row: row[g] = base + k; k += 1
    # ne-kola na hřídeli (kotva, šnek…) dědí řádek sousedního kola (ne pluje na 0)
    for a, seq in arbor_elems.items():
        last = None
        for e in seq:
            if e in row: last = row[e]
            elif last is not None: row[e] = last
        nxt = None
        for e in reversed(seq):
            if e in row: nxt = row[e]
            elif nxt is not None: row[e] = nxt

    # --- pořadí sloupců (x) = BFS přes sousednost danou záběry ---
    cadj = defaultdict(set)
    for z, d in meshes:
        cz, cd = col_of(z), col_of(d)
        if cz and cd and cz != cd: cadj[cz].add(cd); cadj[cd].add(cz)
    rootcol = col_of(root) if root else None
    corder, cs = [], set()
    def cbfs(s):
        qq = deque([s])
        while qq:
            c = qq.popleft()
            if c in cs: continue
            cs.add(c); corder.append(c)
            for b in sorted(cadj[c], key=lambda k: str(k)):
                if b not in cs: qq.append(b)
    if rootcol: cbfs(rootcol)
    for c in col_gears:
        if c not in cs: cbfs(c)

    return dict(doc=doc, P=P, vazby=vazby, meshes=meshes, ust_name=ust_name,
                arbor_of=arbor_of, arbor_elems=arbor_elems, col_of=col_of,
                col_arbors=col_arbors, col_gears=col_gears, corder=corder,
                row=row, is_gear=is_gear)


def render(B):
    P, row, vazby = B["P"], B["row"], B["vazby"]
    corder, col_gears, col_arbors = B["corder"], B["col_gears"], B["col_arbors"]
    hl = B["doc"].get("hlavicka", {})
    konstr = B["doc"]["stroj"].get("konstrukce", {})
    je_ram = konstr.get("typ", "").endswith("ram")

    LEFT = 150
    maxrow = max(list(row.values()) + [0])
    def gy(e): return Y0 + row.get(e, 0) * ROWH
    botPlate = Y0 + (maxrow + 1) * ROWH + 24

    # poloměr kola ∝ roztečnému průměru (konstantní modul ve stroji), škálováno per-stroj
    zs = [p["zuby"] for p in P.values() if isinstance(p.get("zuby"), int)]
    zmax = max(zs) if zs else 1
    def rad(z):
        return round(max(3.0, 62.0 * z / zmax), 1) if isinstance(z, int) else 10.0

    # --- rozteč sloupců = středová vzdálenost záběru × MESH_FACTOR (1,0 = přímý záběr) ---
    def mesh_cd(ca, cb):                        # středová vzdálenost záběru mezi dvěma sloupci
        best = None
        for z, d in B["meshes"]:
            if {B["col_of"](z), B["col_of"](d)} == {ca, cb}:
                v = rad(P[z].get("zuby")) + rad(P[d].get("zuby"))
                best = v if best is None else max(best, v)
        return best
    GAP_DEFAULT = 150
    cx = {}; x = float(LEFT)
    for i, c in enumerate(corder):
        if i:
            cd = mesh_cd(corder[i-1], c)
            x += max(30, (cd * MESH_FACTOR) if cd else GAP_DEFAULT)
        cx[c] = round(x, 1)
    REG_TYPES = ("pocetnik", "stupnice", "srdcovka", "posuvka", "vypousteci-kolo",
                 "vypousteci-paka", "zaverna-paka", "zapadka-pocetniku", "sberaci-palec",
                 "kladivko", "cimbal", "zvon")
    n_free = sum(1 for e in P if B["arbor_of"].get(e) is None and P[e].get("typ") in REG_TYPES)
    W = (max(cx.values()) if cx else LEFT) + 250 + (70 if n_free else 0)
    H = botPlate + 170

    # --- barvy podle funkčního ústrojí (tlumená paleta na krémový papír) ---
    PALETTE = ["#2f6b6b", "#9a3b2e", "#5b4b8a", "#b5702a", "#33506b",
               "#3f7d56", "#6f7a2a", "#8a4b6b", "#4a6a8a"]
    blocks = [u["id"] for u in B["doc"]["stroj"].get("ustroji", [])]
    bclr = {b: PALETTE[i % len(PALETTE)] for i, b in enumerate(blocks)}
    def ec(e):
        return bclr.get(P.get(e, {}).get("ustroji"), INK)
    def cc(col):
        bs = [P[g].get("ustroji") for g in col_gears[col]
              if g in P and P[g].get("ustroji")]
        return bclr.get(bs[0], THIN) if bs else THIN

    # --- soustředné trubky: poloměr každé trubky kolem společné osy ---
    arbor_of = B["arbor_of"]
    r_tube = {}                                # poloměr trubky (0 = střední osa)
    tube_top = {}                              # horní konec (čím vnitřnější, tím delší → výš)
    for c in corder:
        arbs = col_arbors[c]
        if len(arbs) > 1:
            kk = len(arbs)
            for i, a in enumerate(arbs):
                r_tube[a] = i * 6
                tube_top[a] = 120 - (kk - 1 - i) * 15
    def gx(e):                                 # kola jsou na společné ose (střed sloupce)
        c = B["col_of"](e)
        return cx[c] if c in cx else None

    # --- barva per hřídel/trubka (u soustředných osách každá trubka jinak) ---
    TUBEPAL = ["#2e5e8c", "#2f7d5a", "#9a5a2e", "#6b4b8a", "#8a3b3b", "#3f7d7d"]
    aclr = {}
    for c in corder:
        arbs = col_arbors[c]
        if len(arbs) > 1:
            for i, a in enumerate(arbs):
                aclr[a] = TUBEPAL[i % len(TUBEPAL)]
        elif arbs:
            aclr[arbs[0]] = cc(c)
    def acol(e):
        return aclr.get(arbor_of.get(e), ec(e))
    def is_tube(c):
        return len(col_arbors[c]) > 1

    # --- umístění ústrojí: uvnitř rámu vs. samostatně na straně ciferníku ---
    ust_um = {u["id"]: u.get("umisteni", "ram") for u in B["doc"]["stroj"].get("ustroji", [])}
    def in_frame(c):
        bs = [P[g].get("ustroji") for g in col_gears[c] if g in P and P[g].get("ustroji")]
        return not any(ust_um.get(b) == "cifernik" for b in bs)

    # --- typ kroku (pro odlišení krokového kola + štítek) ---
    krok_druh = next((p.get("druh") for p in P.values()
                      if p.get("typ") == "krok" and p.get("druh")), None)  # ber prvek s druhem, ne dle pořadí
    KROK_CS = {"vretenovy": "vřetenový", "foliotovy": "vřetenový (foliotový)",
               "kotvovy": "kotvový", "grahamuv": "Grahamův", "amantuv": "Amantův",
               "robertuv": "Robertův", "brocotuv": "Brocotův", "valeckovy": "cylindrový",
               "chronometrovy": "chronometrový", "volny-kotvovy": "volný kotvový", "hippuv": "Hippův"}

    s = []

    def L(*a): s.append("".join(str(x) for x in a))

    L(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
      f'font-family="Georgia,\'Times New Roman\',serif" role="img">')
    L(f'<title>{esc(hl.get("nazev",""))}</title><desc>Schématická elevace soukolí '
      f'(horonotace, vrstva C).</desc>')
    L(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
    L(f'<defs><marker id="ar" markerWidth="9" markerHeight="9" refX="7" refY="3" '
      f'orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="{OUT}"/></marker></defs>')

    # rohové razítko (titulek dole vpravo, jako v knize) + nahoře
    L(f'<text x="{LEFT}" y="44" font-size="21" fill="{INK}">{esc(hl.get("nazev",""))}</text>')
    sub = " · ".join(filter(None, [hl.get("autor",""), hl.get("datace","")]))
    if len(sub) > 92: sub = sub[:92].rsplit(" ", 1)[0] + "…"
    L(f'<text x="{LEFT}" y="66" font-size="12" fill="{THIN}">{esc(sub)}</text>')

    # --- desky / rám: jen kolem strojové části; komplikace na straně ciferníku jsou mimo ---
    inframe = [c for c in corder if in_frame(c)]
    outframe = [c for c in corder if not in_frame(c)]
    rx0 = LEFT - 70
    rx1 = ((max(cx[c] for c in inframe) + 92) if inframe
           else (cx[corder[-1]] + 95 if corder else rx0 + 200))
    if je_ram:
        L(f'<rect x="{rx0}" y="{TOP_PLATE}" width="{rx1-rx0}" height="{botPlate-TOP_PLATE}" '
          f'fill="none" stroke="{INK}" stroke-width="2.4"/>')
        for px in (rx0, rx1):
            L(f'<line x1="{px}" y1="{TOP_PLATE-6}" x2="{px}" y2="{botPlate+6}" stroke="{INK}" stroke-width="4.5"/>')
            L(f'<circle cx="{px}" cy="{TOP_PLATE-6}" r="4" fill="{INK}"/>')      # hlava závlačky
        lab = "Rám — klecový" if "klec" in konstr.get("typ","") else "Rám — flatbed"
        L(f'<text x="{rx0+4}" y="{TOP_PLATE-12}" font-size="12" fill="{THIN}" font-style="italic">{lab}</text>')
    else:
        for yy in (TOP_PLATE, botPlate):
            L(f'<line x1="{rx0}" y1="{yy}" x2="{rx1}" y2="{yy}" stroke="{INK}" stroke-width="2.2"/>')
            L(f'<text x="{rx1}" y="{yy-5}" font-size="12" fill="{THIN}" text-anchor="end" font-style="italic">Platine</text>')
    if outframe:                                  # oblast mimo rám (strana ciferníku)
        ox0 = rx1 + 18
        L(f'<line x1="{ox0}" y1="{TOP_PLATE-6}" x2="{ox0}" y2="{botPlate+6}" '
          f'stroke="{THIN}" stroke-width="1" stroke-dasharray="3 4"/>')
        oxr = max(cx[c] for c in outframe) + 95
        L(f'<text x="{(ox0+oxr)/2}" y="{TOP_PLATE-12}" font-size="11.5" fill="{THIN}" '
          f'font-style="italic" text-anchor="middle">na straně ciferníku (mimo rám)</text>')

    # --- svorky podsystémů nad deskou ---
    blk_cols = defaultdict(set)
    for c in corder:
        for g in col_gears[c]:
            u = P[g].get("ustroji")
            if u: blk_cols[u].add(c)
    band = TOP_PLATE - 30
    for blk, cols in blk_cols.items():
        xs = [cx[c] for c in cols if c in cx]
        if not xs: continue
        x0, x1 = min(xs) - 26, max(xs) + 26
        clr = bclr.get(blk, THIN)
        L(f'<path d="M{x0},{band+10} L{x0},{band} L{x1},{band} L{x1},{band+10}" '
          f'fill="none" stroke="{clr}" stroke-width="1.2"/>')
        L(f'<text x="{(x0+x1)/2}" y="{band-5}" font-size="12.5" fill="{clr}" '
          f'text-anchor="middle">{esc(B["ust_name"].get(blk, blk))}</text>')

    # --- hřídele / soustředné trubky (vnořené kolem společné osy) ---
    for c in corder:
        x = cx[c]; arbs = col_arbors[c]
        if len(arbs) > 1:                                     # soustředná sestava kolem osy
            rmax = max(r_tube[a] for a in arbs)
            for a in arbs:
                r = r_tube[a]; clr = aclr[a]; top = tube_top[a]    # různě dlouhé (teleskopicky)
                walls = (0,) if r == 0 else (-r, r)           # střední hřídel = jedna osa; ostatní = trubka (dvě stěny)
                for w in walls:
                    L(f'<line x1="{x+w}" y1="{botPlate}" x2="{x+w}" y2="{top}" '
                      f'stroke="{clr}" stroke-width="1.2"/>')
            for yy in (TOP_PLATE, botPlate):                  # společné ložisko sestavy
                L(f'<line x1="{x-rmax-2}" y1="{yy}" x2="{x+rmax+2}" y2="{yy}" stroke="{INK}" stroke-width="1.8"/>')
        else:                                                 # plný hřídel = jedna čára
            a = arbs[0]; clr = aclr.get(a, cc(c))
            L(f'<line x1="{x}" y1="{TOP_PLATE}" x2="{x}" y2="{botPlate}" '
              f'stroke="{clr}" stroke-opacity="0.6" stroke-width="1.2"/>')
            for yy in (TOP_PLATE, botPlate):
                L(f'<line x1="{x-4.5}" y1="{yy}" x2="{x+4.5}" y2="{yy}" stroke="{INK}" stroke-width="1.8"/>')

    # --- záběry: spoj od obvodu k obvodu (roztečná kružnice ke kružnici) ---
    for z, d in B["meshes"]:
        cz, cd = B["col_of"](z), B["col_of"](d)
        if cz not in cx or cd not in cx:        # kolo mimo hřídel — přeskoč
            continue
        x1, x2 = gx(z), gx(d)
        y1, y2 = gy(z), gy(d)
        r1, r2 = rad(P[z].get("zuby")), rad(P[d].get("zuby"))
        if x1 <= x2: sx, ex = x1 + r1, x2 - r2
        else:        sx, ex = x1 - r1, x2 + r2
        xm = (sx + ex) / 2
        L(f'<path d="M{sx},{y1} H{xm} V{y2} H{ex}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        L(f'<line x1="{xm-3}" y1="{(y1+y2)/2-3}" x2="{xm+3}" y2="{(y1+y2)/2+3}" stroke="{INK}" stroke-width="1"/>')

    # (hrany spouštění/blokování se kreslí níže — sjednoceně i s volnými prvky)

    # --- kola: úsečka = roztečný průměr (délka ∝ z), koncové čepy, náboj ---
    def gear(x, y, p, clr, escape=None):
        z = p.get("zuby"); r = rad(z)
        L(f'<line x1="{x-r}" y1="{y}" x2="{x+r}" y2="{y}" stroke="{clr}" stroke-width="1.9"/>')   # rozteč. úsečka
        for ex, sgn in ((x - r, 1), (x + r, -1)):                                                  # konce: čep / krokový zub / kolík
            if escape == "pin":                                                                    # kolíčkové kolo (Amant/Robert)
                L(f'<circle cx="{ex}" cy="{y}" r="2.3" fill="{clr}"/>')
            elif escape == "saw":                                                                  # krokové kolo — pilový hrot
                L(f'<path d="M{ex},{y+5} L{ex},{y-5} L{ex+sgn*6},{y-1}" fill="none" stroke="{clr}" stroke-width="1.4"/>')
            else:
                L(f'<line x1="{ex}" y1="{y-5}" x2="{ex}" y2="{y+5}" stroke="{clr}" stroke-width="1.3"/>')
        ny = (y + 15) if escape else (y - 8)            # u krokového kola číslo pod úsečkou (nad ní je kotva)
        if z is not None:
            L(f'<text x="{x}" y="{ny}" font-size="12.5" font-style="italic" fill="{INK}" text-anchor="middle">{z}</text>')
        else:
            L(f'<text x="{x+8}" y="{y+4}" font-size="11" font-style="italic" fill="{THIN}">?</text>')

    # ne-gear prvky na hřídeli (kotva, šnek…) -> drobná značka
    for c in corder:
        coax = len(col_arbors[c]) > 1
        x = cx[c]
        for a in col_arbors[c]:
            for e in B["arbor_elems"][a]:
                p = P.get(e, {})
                if B["is_gear"](e):
                    yy = gy(e); clr = acol(e)
                    es = ("pin" if krok_druh in ("amantuv", "robertuv") else "saw") \
                        if p.get("typ") == "krokove-kolo" else None
                    gear(x, yy, p, clr, es)
                    if coax:                             # klín na poloměru VLASTNÍ trubky (osa = jeden uprostřed)
                        rt = r_tube.get(a, 0)
                        for k in ((0,) if rt == 0 else (-rt, rt)):
                            L(f'<rect x="{x+k-3}" y="{yy-3}" width="6" height="6" fill="{clr}"/>')
                    else:                                # plný hřídel: náboj ve středu
                        L(f'<rect x="{x-3}" y="{yy-3}" width="6" height="6" fill="{clr}"/>')
                    if es:                               # štítek druhu kroku u krokového kola
                        lab = "krok: " + KROK_CS.get(krok_druh, krok_druh or "—")
                        L(f'<text x="{round(x+rad(p.get("zuby"))+8,1)}" y="{yy+3}" '
                          f'font-size="10" font-style="italic" fill="{clr}">{esc(lab)}</text>')
                elif p.get("typ") in ("kotva",):     # kotva NAD krokovým kolem (ramena + palety + čep)
                    y = gy(e)
                    L(f'<path d="M{x-9},{y-3} L{x},{y-17} L{x+9},{y-3}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
                    L(f'<line x1="{x-9}" y1="{y-6}" x2="{x-6}" y2="{y-1}" stroke="{INK}" stroke-width="2.3"/>')
                    L(f'<line x1="{x+9}" y1="{y-6}" x2="{x+6}" y2="{y-1}" stroke="{INK}" stroke-width="2.3"/>')
                    L(f'<circle cx="{x}" cy="{y-17}" r="1.8" fill="{INK}"/>')
                elif p.get("typ") == "snek":
                    y = gy(e)
                    L(f'<rect x="{x-4}" y="{y-7}" width="8" height="14" fill="none" stroke="{INK}" stroke-width="1.2"/>')
                    for t in range(-5, 6, 3):
                        L(f'<line x1="{x-4}" y1="{y+t}" x2="{x+4}" y2="{y+t+2}" stroke="{INK}" stroke-width="0.8"/>')
                    L(f'<text x="{x+9}" y="{y+3}" font-size="10.5" fill="{THIN}">šnek (fáze)</text>')
                elif p.get("typ") in BICI:
                    y = gy(e)
                    L(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="{INK}" stroke-width="1.3"/>')
                    L(f'<line x1="{x-5}" y1="{y}" x2="{x+5}" y2="{y}" stroke="{INK}" stroke-width="0.8"/>')
                    nm = p.get("druh") or p.get("typ")
                    L(f'<text x="{x+10}" y="{y+3}" font-size="10" fill="{THIN}">{esc(nm)}</text>')

    # --- ukazovací soustava: koaxiální trubky + vazba každého kola na jeho ukazatel ---
    out_by_col = defaultdict(list)
    for v in vazby:
        if v.get("typ") == "pohani":
            src = v.get("z")
            c = B["col_of"](src)
            if c in cx and src in row:
                out_by_col[c].append((src, P.get(v.get("do"), {}), v.get("do")))
    for c, outs in out_by_col.items():
        x = cx[c]
        outs.sort(key=lambda o: row.get(o[0], 0))
        k = len(outs)
        multi_tube = len(col_arbors[c]) > 1     # víc trubek na společné ose
        coax = multi_tube or k > 1
        if coax and not multi_tube:             # sdílený ciferník (jedno kolo → víc ukazatelů)
            L(f'<circle cx="{x}" cy="{DCY}" r="{DIAL_R}" fill="{PAPER}" stroke="{cc(c)}" stroke-width="1.3"/>')
            L(f'<circle cx="{x}" cy="{DCY}" r="2" fill="{cc(c)}"/>')
        for i, (src, tgt, tid) in enumerate(outs):
            scol = acol(src)                     # barva této dráhy (trubky)
            name = tgt.get("ukazuje") or tgt.get("druh") or tid
            if multi_tube:                       # ukazatel VYCHÁZÍ ze své trubky (z její stěny), ne ze středu
                a2 = arbor_of[src]; ty = tube_top[a2]; ox = x + r_tube[a2]
                L(f'<circle cx="{ox}" cy="{ty}" r="2.8" fill="{scol}"/>')                         # objímka na konci trubky
                L(f'<line x1="{ox}" y1="{ty}" x2="{ox+24}" y2="{ty}" stroke="{scol}" stroke-width="2"/>')  # ručka
                L(f'<path d="M{ox+24},{ty-3} l6,3 l-6,3 z" fill="{scol}"/>')                      # hrot
                L(f'<text x="{ox+34}" y="{ty+3}" font-size="10.5" fill="{scol}">{esc(name)}</text>')   # ukazatel
            elif coax:                           # jedno kolo, víc ukazatelů: ciferník s ručkami
                ang = math.radians(-90 + (i - (k - 1) / 2) * 44)
                hx, hy = x + (DIAL_R - 2) * math.cos(ang), DCY + (DIAL_R - 2) * math.sin(ang)
                dx = (i - (k - 1) / 2) * 8
                L(f'<line x1="{x+dx}" y1="{gy(src)}" x2="{x+dx}" y2="{DCY+DIAL_R}" stroke="{scol}" stroke-width="1.3"/>')
                L(f'<line x1="{x+dx}" y1="{DCY+DIAL_R}" x2="{x}" y2="{DCY}" stroke="{scol}" stroke-opacity="0.7" stroke-width="0.7"/>')
                L(f'<line x1="{x}" y1="{DCY}" x2="{round(hx,1)}" y2="{round(hy,1)}" stroke="{scol}" stroke-width="2"/>')
                lx, ly = x + (DIAL_R + 8) * math.cos(ang), DCY + (DIAL_R + 8) * math.sin(ang)
                rgt = math.cos(ang) >= 0
                L(f'<text x="{round(lx + (4 if rgt else -4),1)}" y="{round(ly+3,1)}" font-size="11" '
                  f'fill="{scol}" text-anchor="{"start" if rgt else "end"}">{esc(name)}</text>')
            else:
                L(f'<line x1="{x}" y1="{gy(src)}" x2="{x}" y2="{DCY+2}" stroke="{scol}" stroke-width="1.3"/>')
                L(f'<text x="{x}" y="{DCY-3}" font-size="11.5" fill="{scol}" text-anchor="middle">▲ {esc(name)}</text>')

    # --- kyvadlo / lihýř pod deskou (u sloupce s krokovým kolem) ---
    esc_col = None
    for c in corder:
        if any(P[g].get("typ") == "krokove-kolo" for g in col_gears[c]): esc_col = c
    osc = next((p for p in P.values() if p.get("typ") in ("kyvadlo","lihyr","foliot","setrvacka")), None)
    if osc and esc_col:
        x = cx[esc_col]; by = botPlate
        if osc.get("typ") in ("kyvadlo",):
            L(f'<line x1="{x}" y1="{by}" x2="{x}" y2="{by+74}" stroke="{INK}" stroke-width="1.3"/>')
            L(f'<circle cx="{x}" cy="{by+86}" r="11" fill="none" stroke="{INK}" stroke-width="1.6"/>')
            L(f'<text x="{x+17}" y="{by+90}" font-size="11" fill="{THIN}">kyvadlo {esc(osc.get("perioda",""))}</text>')
        else:
            L(f'<line x1="{x-24}" y1="{by+30}" x2="{x+24}" y2="{by+30}" stroke="{INK}" stroke-width="1.6"/>')
            L(f'<line x1="{x}" y1="{by}" x2="{x}" y2="{by+30}" stroke="{INK}" stroke-width="1.3"/>')
            for dx in (-24, 24):
                L(f'<rect x="{x+dx-4}" y="{by+26}" width="8" height="8" fill="{INK}"/>')
            L(f'<text x="{x+30}" y="{by+34}" font-size="11" fill="{THIN}">lihýř</text>')

    # --- pohon (závaží / pero) ---
    box_done = False
    for v in vazby:
        if v.get("typ") != "pohon": continue
        anchor = next((e for e in (v.get("do"), v.get("z"))
                       if e and B["col_of"](e) in cx), None)
        if anchor:
            col = B["col_of"](anchor); x = cx[col]
            # lanový buben na téže hřídeli (souosý s hnacím kolem)?
            drum = next((P[e] for a in col_arbors[col] for e in B["arbor_elems"][a]
                         if P.get(e, {}).get("typ") == "buben"), None)
            rope_top, wx = botPlate, x
            if drum:
                dy = botPlate - 40
                digits = "".join(ch for ch in str(drum.get("prumer", "")) if ch.isdigit())
                wd = max(18.0, min(46.0, int(digits) * 0.12)) if digits else 26.0
                # válec bubnu (řez) + návin lana (svislé čárky)
                L(f'<rect x="{round(x-wd/2,1)}" y="{dy-9}" width="{round(wd,1)}" height="18" rx="2" '
                  f'fill="none" stroke="{DRV}" stroke-width="1.5"/>')
                kk = max(3, int(wd / 4))
                for i in range(1, kk):
                    lx = round(x - wd/2 + i * wd / kk, 1)
                    L(f'<line x1="{lx}" y1="{dy-9}" x2="{lx}" y2="{dy+9}" stroke="{DRV}" stroke-opacity="0.55" stroke-width="0.7"/>')
                lab = "buben"
                if drum.get("prumer"): lab += f" ⌀{drum['prumer']}"
                if drum.get("otacky") is not None: lab += f", {drum['otacky']:g} ot."
                L(f'<text x="{round(x+wd/2+6,1)}" y="{dy+3}" font-size="9.5" fill="{DRV}">{esc(lab)}</text>')
                rope_top, wx = dy + 9, round(x - wd/2, 1)   # lano z okraje bubnu
            # lano dolů k závaží
            L(f'<line x1="{wx}" y1="{rope_top}" x2="{wx}" y2="{botPlate+30}" stroke="{DRV}" stroke-width="1.1"/>')
            L(f'<path d="M{wx-10},{botPlate+30} h20 l-3,26 h-14 z" fill="none" stroke="{DRV}" stroke-width="1.5"/>')
            for hy in range(36, 54, 5):
                L(f'<line x1="{wx-7}" y1="{botPlate+hy}" x2="{wx+7}" y2="{botPlate+hy}" stroke="{DRV}" stroke-width="0.7"/>')
            L(f'<text x="{wx}" y="{botPlate+72}" font-size="10.5" fill="{DRV}" text-anchor="middle">závaží</text>')
            # natahování: čtyřhran + klika na natahovacím čepu (vrch hnací hřídele) + rohatka/západka (drží nátah)
            wind = next((P[e] for a in col_arbors[col] for e in B["arbor_elems"][a]
                         if P.get(e, {}).get("typ") in ("klika", "natahovaci-ctyrhran", "natahovani")), None)
            if drum or wind:
                sqy = TOP_PLATE + 20
                L(f'<rect x="{x-4}" y="{sqy-4}" width="8" height="8" fill="none" stroke="{DRV}" '
                  f'stroke-width="1.2" transform="rotate(45 {x} {sqy})"/>')                       # čtyřhran
                L(f'<path d="M{x},{sqy} h26 v-20" fill="none" stroke="{DRV}" stroke-width="1.6"/>')  # klika (rameno + držadlo)
                L(f'<circle cx="{x+26}" cy="{sqy-20}" r="2.8" fill="{DRV}"/>')                     # rukojeť
                ry = sqy + 19                                                                      # rohatka + západka
                L(f'<circle cx="{x}" cy="{ry}" r="6.5" fill="none" stroke="{DRV}" stroke-width="1.1"/>')
                L(f'<path d="M{x-6},{ry-3} l2,-4 l2,4 l2,-4 l2,4 l2,-4" fill="none" stroke="{DRV}" stroke-width="0.9"/>')
                L(f'<circle cx="{x+12}" cy="{ry-9}" r="1.5" fill="{DRV}"/>')
                L(f'<path d="M{x+12},{ry-9} l-7,7" fill="none" stroke="{DRV}" stroke-width="1.2"/>')  # západka
                wlab = esc(wind["pozn"]) if (wind and wind.get("pozn")) else "natahování"
                L(f'<text x="{x+34}" y="{sqy-16}" font-size="9" fill="{DRV}">{wlab}</text>')
        elif not box_done:
            box_done = True
            x = LEFT - 110
            L(f'<line x1="{x+48}" y1="{Y0+6}" x2="{cx[corder[0]]-14}" y2="{Y0+6}" '
              f'stroke="{DRV}" stroke-width="1" stroke-dasharray="4 3"/>')
            L(f'<rect x="{x-30}" y="{Y0-14}" width="78" height="40" rx="3" fill="none" '
              f'stroke="{DRV}" stroke-width="1.2" stroke-dasharray="4 3"/>')
            L(f'<text x="{x+9}" y="{Y0+2}" font-size="10.5" fill="{DRV}" text-anchor="middle">jdoucí soukolí</text>')
            L(f'<text x="{x+9}" y="{Y0+16}" font-size="9" fill="{THIN}" text-anchor="middle">zuby nedoloženy</text>')

    # --- regulace bití: volné členy (páky) v bočním panelu + hrany spouštění/blokování ---
    REG_CS = {"pocetnik": "početník", "stupnice": "stupnice", "srdcovka": "srdcovka",
              "posuvka": "posůvka", "vypousteci-kolo": "vypouštěcí kolo",
              "vypousteci-paka": "vypouštěcí páka", "zaverna-paka": "závěrná páka",
              "zapadka-pocetniku": "západka početníku", "sberaci-palec": "sběrací palec",
              "kladivko": "kladivo", "cimbal": "cimbál", "zvon": "zvon"}
    def reg_glyph(t, gx2, gy2):                  # drobný symbol členu regulace
        if t in ("zaverka", "srdcovka", "stupnice"):
            L(f'<circle cx="{gx2}" cy="{gy2}" r="9" fill="none" stroke="{INK}" stroke-width="1.2"/>')
            L(f'<line x1="{gx2}" y1="{gy2-9}" x2="{gx2+2}" y2="{gy2-13}" stroke="{INK}" stroke-width="1"/>')
        elif t == "pocetnik":
            L(f'<circle cx="{gx2-9}" cy="{gy2-7}" r="1.8" fill="{INK}"/>')
            L(f'<path d="M{gx2-9},{gy2-7} Q{gx2},{gy2+2} {gx2+10},{gy2+6}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        elif t in ("kladivko",):
            L(f'<circle cx="{gx2-9}" cy="{gy2+6}" r="1.6" fill="{INK}"/>')
            L(f'<line x1="{gx2-9}" y1="{gy2+6}" x2="{gx2+7}" y2="{gy2-6}" stroke="{INK}" stroke-width="1.4"/>')
            L(f'<rect x="{gx2+5}" y="{gy2-10}" width="7" height="6" fill="{INK}"/>')
        elif t in ("cimbal", "zvon"):
            L(f'<path d="M{gx2-8},{gy2+6} q0,-14 8,-14 q8,0 8,14 z" fill="none" stroke="{INK}" stroke-width="1.4"/>')
            L(f'<line x1="{gx2-10}" y1="{gy2+6}" x2="{gx2+10}" y2="{gy2+6}" stroke="{INK}" stroke-width="1.2"/>')
        else:                                    # páky (vypouštěcí, závěrná, západka, palec)
            L(f'<circle cx="{gx2-9}" cy="{gy2-6}" r="1.8" fill="{INK}"/>')
            L(f'<path d="M{gx2-9},{gy2-6} L{gx2+9},{gy2+5} M{gx2-9},{gy2-6} L{gx2-5},{gy2+8}" '
              f'fill="none" stroke="{INK}" stroke-width="1.4"/>')

    free = [e for e in P if arbor_of.get(e) is None and P[e].get("typ") in REG_CS]
    fpos = {}

    def onarbor_pos(e):                          # poloha prvku na hřídeli (kolo) nebo bloku
        c = B["col_of"](e)
        if c in cx and e in row: return (cx[c], gy(e))
        gg = [g for cc2 in corder for g in col_gears[cc2] if P[g].get("ustroji") == e]
        if gg: return (cx[B["col_of"](gg[0])], gy(gg[0]))   # blok → první kolo bloku
        return None

    # in-situ (varianta C): každou páku/vačku umísti přímo k jejímu kolu;
    # kotvu odvodíme ze sousedství přes hrany spouštění/blokování.
    neigh = {e: [] for e in free}
    for v in vazby:
        if v.get("typ") in ("spousteni", "blokuje"):
            z, d = v.get("z"), v.get("do")
            if z in neigh and d != z: neigh[z].append(d)
            if d in neigh and z != d: neigh[d].append(z)
    placed = []
    def collide(x, y):
        return any(abs(x - px) < 72 and abs(y - py) < 24 for px, py in placed)
    remaining = list(free)
    for _ in range(len(free) + 1):
        for e in list(remaining):
            ap = next((onarbor_pos(n) for n in neigh[e] if onarbor_pos(n)), None)  # kotva na hřídeli má přednost
            if not ap:
                ap = next((fpos.get(n) for n in neigh[e] if fpos.get(n)), None)   # jinak k již umístěné páce
            if not ap: continue
            ex2, ey2 = ap[0] + 12, ap[1] - 34       # nad kotevním kolem, mírně vpravo
            while collide(ex2, ey2) and ey2 > TOP_PLATE - 26:
                ey2 -= 26
            fpos[e] = (ex2, ey2); placed.append((ex2, ey2)); remaining.remove(e)
    fx = (max(cx.values()) if cx else LEFT) + 70    # zbylé bez kotvy → stoh vpravo
    for i, e in enumerate(remaining):
        fpos[e] = (fx, TOP_PLATE + 30 + i * 40)
    for e in free:
        ex2, ey2 = fpos[e]
        reg_glyph(P[e].get("typ"), ex2, ey2)
        L(f'<text x="{ex2+13}" y="{ey2-3}" font-size="9" fill="{INK}">{esc(REG_CS.get(P[e]["typ"], P[e]["typ"]))}</text>')

    def pos2(e):                                 # poloha prvku: na hřídeli, volný (in-situ), nebo blok
        if e in fpos: return fpos[e]
        return onarbor_pos(e)
    for v in vazby:                              # hrany spouštění (aktuace) a blokování (zámek)
        t = v.get("typ")
        if t not in ("spousteni", "blokuje"): continue
        a, b = pos2(v.get("z")), pos2(v.get("do"))
        if not (a and b): continue
        if t == "spousteni":
            L(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" fill="none" stroke="{ACC}" '
              f'stroke-width="1.2" stroke-dasharray="5 3"/>')
        else:                                    # blokuje — čára + značka zámku
            mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
            L(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" fill="none" stroke="{ACC}" '
              f'stroke-width="1" stroke-dasharray="2 3"/>')
            L(f'<line x1="{mx-5}" y1="{my-4}" x2="{mx+5}" y2="{my+4}" stroke="{ACC}" stroke-width="2"/>')

    # --- legenda: vysvětlivky symbolů + razítko ---
    yy = H - 30
    L(f'<rect x="{LEFT}" y="{yy-9}" width="9" height="9" fill="{INK}"/>')
    L(f'<text x="{LEFT+14}" y="{yy}" font-size="11" fill="{THIN}">klíny = kolo spojené se svou dráhou</text>')
    cxl = LEFT + 250
    L(f'<line x1="{cxl}" y1="{yy-11}" x2="{cxl}" y2="{yy+2}" stroke="{THIN}" stroke-width="1.1"/>')        # osa (nejdelší)
    for dxl, dh in ((-3, 3), (3, 3), (-6, 6), (6, 6)):                                                     # kratší trubky
        L(f'<line x1="{cxl+dxl}" y1="{yy-11+dh}" x2="{cxl+dxl}" y2="{yy+2}" stroke="{THIN}" stroke-width="1"/>')
    L(f'<text x="{cxl+14}" y="{yy}" font-size="11" fill="{THIN}">osa (nejdelší) + kratší trubky → ukazatele</text>')
    L(f'<text x="{LEFT}" y="{H-12}" font-size="10" fill="{THIN}" font-style="italic">'
      f'barva = jednotlivá dráha (osa/trubka) · délka úsečky kola ∝ roztečnému průměru (∝ z)</text>')
    L(f'<text x="{W-30}" y="{H-14}" font-size="10" fill="{THIN}" text-anchor="end" '
      f'font-style="italic">horonotace · vrstva C</text>')
    L('</svg>')
    return "\n".join(s)


def run(src, out):
    B = build(yaml.safe_load(open(src)))
    svg = render(B)
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    open(out, "w").write(svg)
    nrows = (max(B['row'].values()) + 1) if B['row'] else 0
    print(f"→ {out}  ({len(B['corder'])} sloupců, {nrows} řádků)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in sys.argv[1:]:                      # --mesh=1.0 (přímý záběr) … vyšší = volnější
        if a.startswith("--mesh=") or a.startswith("--density="):
            MESH_FACTOR = float(a.split("=", 1)[1])
    if "--all" in sys.argv:
        for nm in ("praga-orloj", "vezni-pocitadlo", "vezni-jici-bici", "orloj-astrolab"):
            run(f"examples/{nm}.yaml", f"render/{nm}.svg")
    else:
        run(args[0], args[1])
