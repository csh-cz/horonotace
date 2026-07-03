#!/usr/bin/env python3
"""Horonotace — knihovna symbolů (vrstva C) + přehledový list.

Definuje schematický glyf pro každý typ komponenty notace a umí vykreslit
přehledový list (symbol sheet). Glyfy jsou v knižním stylu (papír + inkoust),
sjednocené s elevací soukolí (tools/render_svg.py).

Usage:  python3 tools/symboly.py --sheet render/symboly.svg
        python3 tools/symboly.py --table          # markdown tabulka na stdout
"""
import sys, os, math, html

PAPER = "#f4eedd"; INK = "#1f1c14"; THIN = "#6b6253"
DRV = "#705f31"; ACC = "#9a3b2e"; OUT = "#33506b"


def esc(s): return html.escape(str(s), quote=True)


def pol(cx, cy, r, deg):
    a = math.radians(deg); return cx + r * math.sin(a), cy - r * math.cos(a)


def spiral(cx, cy, r0, r1, turns, n=40, clr=INK, w=1.0):
    pts = []
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * t
        a = math.radians(360 * turns * t)
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{clr}" stroke-width="{w}"/>'


# ── glyfy (každý kreslí kolem středu (x,y), ~±18 px) ──
def g_zavazi(x, y):
    return [f'<path d="M{x-9},{y-12} h18 l-3,24 h-12 z" fill="none" stroke="{DRV}" stroke-width="1.6"/>'] + \
           [f'<line x1="{x-6}" y1="{y-12+6*i}" x2="{x+6}" y2="{y-12+6*i}" stroke="{DRV}" stroke-width="0.7"/>' for i in range(1, 4)]

def g_buben(x, y):
    return [f'<rect x="{x-16}" y="{y-9}" width="32" height="18" rx="2.5" fill="none" stroke="{DRV}" stroke-width="1.6"/>'] + \
           [f'<line x1="{x-12+6*i}" y1="{y-9}" x2="{x-12+6*i}" y2="{y+9}" stroke="{DRV}" stroke-opacity="0.55" stroke-width="0.7"/>' for i in range(6)]

def g_perovnik(x, y):
    return [f'<circle cx="{x}" cy="{y}" r="15" fill="none" stroke="{DRV}" stroke-width="1.6"/>',
            spiral(x, y, 2, 12, 2.2, clr=DRV, w=1.0)]

def g_pero(x, y):
    return [spiral(x, y, 1, 15, 2.6, clr=DRV, w=1.2)]

def g_snek(x, y):  # fusee — kužel se šroubovicí
    out = [f'<path d="M{x-12},{y+14} L{x-7},{y-14} L{x+7},{y-14} L{x+12},{y+14} z" fill="none" stroke="{DRV}" stroke-width="1.6"/>']
    for i in range(5):
        yy = y - 11 + i * 6
        out.append(f'<line x1="{x-9+ i*0.7}" y1="{yy}" x2="{x+9- i*0.7}" y2="{yy+3}" stroke="{DRV}" stroke-width="0.7"/>')
    return out

def g_retizek(x, y):  # fusee chain
    out = []
    for i in range(4):
        yy = y - 13 + i * 8
        out.append(f'<ellipse cx="{x}" cy="{yy}" rx="3" ry="4.5" fill="none" stroke="{DRV}" stroke-width="1.1"/>')
    return out

def g_rohatka(x, y):  # ratchet wheel + pawl
    out = [f'<circle cx="{x}" cy="{y}" r="13" fill="none" stroke="{INK}" stroke-width="1.3"/>']
    for k in range(12):
        x1, y1 = pol(x, y, 13, k * 30); x2, y2 = pol(x, y, 17, k * 30 + 14)
        out.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} L{pol(x,y,13,k*30+30)[0]:.1f},{pol(x,y,13,k*30+30)[1]:.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}"/>')
    return out

def g_zapadka(x, y):  # pawl / click
    return [f'<circle cx="{x-12}" cy="{y-8}" r="2" fill="{INK}"/>',
            f'<path d="M{x-12},{y-8} L{x+8},{y+4} l-3,-6" fill="none" stroke="{INK}" stroke-width="1.4"/>']

def g_klika(x, y):  # winding crank — čtyřhran + rameno + rukojeť
    return [f'<rect x="{x-13}" y="{y-4}" width="8" height="8" fill="none" stroke="{INK}" stroke-width="1.3" transform="rotate(45 {x-9} {y})"/>',
            f'<path d="M{x-9},{y} L{x+10},{y} L{x+10},{y-13}" fill="none" stroke="{INK}" stroke-width="1.7"/>',
            f'<circle cx="{x+10}" cy="{y-15}" r="3" fill="{INK}"/>']

def g_natahovaci_ctyrhran(x, y):  # winding square (Vierkant) na natahovacím čepu
    return [f'<line x1="{x-15}" y1="{y}" x2="{x+4}" y2="{y}" stroke="{INK}" stroke-width="1.6"/>',
            f'<rect x="{x+4}" y="{y-6}" width="12" height="12" fill="none" stroke="{INK}" stroke-width="1.4" transform="rotate(45 {x+10} {y})"/>']

def g_klicek(x, y):  # winding key — klíček (pružinové stroje)
    return [f'<rect x="{x-13}" y="{y-5}" width="10" height="10" fill="none" stroke="{INK}" stroke-width="1.4"/>',
            f'<line x1="{x-3}" y1="{y}" x2="{x+9}" y2="{y}" stroke="{INK}" stroke-width="1.6"/>',
            f'<ellipse cx="{x+14}" cy="{y}" rx="5" ry="7" fill="none" stroke="{INK}" stroke-width="1.4"/>']

def g_kolo(x, y):
    return [f'<line x1="{x-17}" y1="{y}" x2="{x+17}" y2="{y}" stroke="{INK}" stroke-width="1.9"/>',
            f'<line x1="{x-17}" y1="{y-5}" x2="{x-17}" y2="{y+5}" stroke="{INK}" stroke-width="1.3"/>',
            f'<line x1="{x+17}" y1="{y-5}" x2="{x+17}" y2="{y+5}" stroke="{INK}" stroke-width="1.3"/>',
            f'<rect x="{x-3}" y="{y-3}" width="6" height="6" fill="{INK}"/>']

def g_pastorek(x, y):
    return [f'<line x1="{x-7}" y1="{y}" x2="{x+7}" y2="{y}" stroke="{INK}" stroke-width="1.9"/>',
            f'<line x1="{x-7}" y1="{y-5}" x2="{x-7}" y2="{y+5}" stroke="{INK}" stroke-width="1.3"/>',
            f'<line x1="{x+7}" y1="{y-5}" x2="{x+7}" y2="{y+5}" stroke="{INK}" stroke-width="1.3"/>',
            f'<rect x="{x-3}" y="{y-3}" width="6" height="6" fill="{INK}"/>']

def g_cevkovy(x, y):  # lantern pinion — klec
    out = [f'<line x1="{x-6}" y1="{y-11}" x2="{x-6}" y2="{y+11}" stroke="{INK}" stroke-width="1.3"/>',
           f'<line x1="{x+6}" y1="{y-11}" x2="{x+6}" y2="{y+11}" stroke="{INK}" stroke-width="1.3"/>']
    for i in range(4):
        yy = y - 9 + i * 6
        out.append(f'<line x1="{x-6}" y1="{yy}" x2="{x+6}" y2="{yy}" stroke="{INK}" stroke-width="0.9"/>')
    return out

def g_krokove_kolo(x, y):  # escape wheel
    out = [f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{INK}" stroke-width="1.2"/>']
    for k in range(15):
        x1, y1 = pol(x, y, 12, k * 24); x2, y2 = pol(x, y, 17, k * 24 - 8)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<rect x="{x-2.5}" y="{y-2.5}" width="5" height="5" fill="{INK}"/>')
    return out

def g_kotva(x, y):  # anchor
    return [f'<path d="M{x-13},{y+9} L{x},{y-12} L{x+13},{y+9}" fill="none" stroke="{INK}" stroke-width="1.7"/>',
            f'<path d="M{x-13},{y+4} l-3,5" stroke="{INK}" stroke-width="2.4"/>',
            f'<path d="M{x+13},{y+4} l3,5" stroke="{INK}" stroke-width="2.4"/>',
            f'<circle cx="{x}" cy="{y-12}" r="2" fill="{INK}"/>']

def g_paleta(x, y):
    return [f'<path d="M{x-9},{y+5} l6,-12 l12,4 l-6,12 z" fill="none" stroke="{INK}" stroke-width="1.4"/>']

# --- typy krokových kol ---
def g_korunove_kolo(x, y):  # crown wheel — vřetenový krok s lihýřem (boční pohled)
    cy = y + 3                               # střed věnce (bubínku)
    out = [f'<ellipse cx="{x}" cy="{cy}" rx="13" ry="5" fill="none" stroke="{INK}" stroke-width="1.3"/>',
           f'<line x1="{x-13}" y1="{cy}" x2="{x-13}" y2="{cy+8}" stroke="{INK}" stroke-width="1"/>',
           f'<line x1="{x+13}" y1="{cy}" x2="{x+13}" y2="{cy+8}" stroke="{INK}" stroke-width="1"/>',
           f'<path d="M{x-13},{cy+8} A13 5 0 0 0 {x+13},{cy+8}" fill="none" stroke="{INK}" stroke-width="1.3"/>',
           f'<line x1="{x}" y1="{cy+8}" x2="{x}" y2="{cy+15}" stroke="{INK}" stroke-width="1.2"/>']  # osa dolů (nezasahuje do zubů)
    for k in range(8):                       # pilové (šikmé) zuby axiálně na horním věnci
        t = -1 + 2 * k / 7.0
        bx = x + t * 12.5; by = cy - 5 * math.sqrt(max(0.0, 1 - t * t))
        out.append(f'<path d="M{bx:.1f},{by:.1f} l1.3,-5 l2.4,5" fill="none" stroke="{INK}" stroke-width="0.8"/>')
    return out

def g_kolickove_kolo(x, y):  # pin wheel — Amantův krok (kolíky místo zubů)
    out = [f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{INK}" stroke-width="1.2"/>']
    for k in range(12):
        px, py = pol(x, y, 12, k * 30)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="{INK}"/>')
    out.append(f'<rect x="{x-2.5}" y="{y-2.5}" width="5" height="5" fill="{INK}"/>')
    return out

def g_cylindrove_kolo(x, y):  # cylinder escape wheel — zuby na nožkách
    out = [f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{INK}" stroke-width="1.2"/>']
    for k in range(12):
        sx, sy = pol(x, y, 9, k * 30); ex, ey = pol(x, y, 13, k * 30); tx, ty = pol(x, y, 16, k * 30 - 7)
        out.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{INK}" stroke-width="0.7"/>')
        out.append(f'<path d="M{ex:.1f},{ey:.1f} L{tx:.1f},{ty:.1f}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(f'<rect x="{x-2.5}" y="{y-2.5}" width="5" height="5" fill="{INK}"/>')
    return out

# --- typy kotev / regulace kroku ---
def g_kotva_grahamova(x, y):  # deadbeat (Graham) — klidové (válcové) palety
    return [f'<path d="M{x-13},{y+7} L{x},{y-12} L{x+13},{y+7}" fill="none" stroke="{INK}" stroke-width="1.6"/>',
            f'<path d="M{x-16},{y+9} a5 5 0 0 1 6,-7" fill="none" stroke="{INK}" stroke-width="2.2"/>',
            f'<path d="M{x+16},{y+9} a5 5 0 0 0 -6,-7" fill="none" stroke="{INK}" stroke-width="2.2"/>',
            f'<circle cx="{x}" cy="{y-12}" r="2" fill="{INK}"/>']

def g_vreteno(x, y):  # verge — vřeteno se dvěma kolmými paletami (pro korunové kolo)
    return [f'<line x1="{x}" y1="{y-15}" x2="{x}" y2="{y+15}" stroke="{INK}" stroke-width="1.6"/>',
            f'<path d="M{x},{y-8} l-10,-4 l0,4 z" fill="{INK}"/>',
            f'<path d="M{x},{y+8} l10,4 l0,-4 z" fill="{INK}"/>',
            f'<circle cx="{x}" cy="{y-15}" r="1.8" fill="{INK}"/>']

def g_kotva_pakova(x, y):  # lever — volný kotvový (pákový) krok: ramena + vidlice
    return [f'<path d="M{x-12},{y+6} L{x},{y-9} L{x+12},{y+6}" fill="none" stroke="{INK}" stroke-width="1.6"/>',
            f'<line x1="{x}" y1="{y-9}" x2="{x}" y2="{y-19}" stroke="{INK}" stroke-width="1.3"/>',
            f'<path d="M{x-3.5},{y-19} l3.5,4 l3.5,-4" fill="none" stroke="{INK}" stroke-width="1.2"/>',
            f'<circle cx="{x}" cy="{y-9}" r="1.8" fill="{INK}"/>',
            f'<circle cx="{x}" cy="{y-22}" r="1.6" fill="{INK}"/>']

def g_paleta_kolikova(x, y):  # pin-pallet — Amantův krok: palety jako kolíky
    return [f'<path d="M{x-12},{y+5} L{x},{y-11} L{x+12},{y+5}" fill="none" stroke="{INK}" stroke-width="1.6"/>',
            f'<circle cx="{x-12}" cy="{y+5}" r="2.6" fill="{INK}"/>',
            f'<circle cx="{x+12}" cy="{y+5}" r="2.6" fill="{INK}"/>',
            f'<circle cx="{x}" cy="{y-11}" r="2" fill="{INK}"/>']

def g_cylindr(x, y):  # cylinder — válcový (cylindrový) krok
    return [f'<line x1="{x-6}" y1="{y-13}" x2="{x-6}" y2="{y+13}" stroke="{INK}" stroke-width="1.4"/>',
            f'<line x1="{x+6}" y1="{y-13}" x2="{x+6}" y2="{y+13}" stroke="{INK}" stroke-width="1.4"/>',
            f'<path d="M{x-6},{y-13} a6 3 0 0 1 12,0" fill="none" stroke="{INK}" stroke-width="1.1"/>',
            f'<path d="M{x-6},{y+13} a6 3 0 0 0 12,0" fill="none" stroke="{INK}" stroke-width="1.1"/>',
            f'<path d="M{x+6},{y-3} a6 3 0 0 1 0,8" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="2 2"/>']

def g_detent(x, y):  # chronometer detent — pružná zarážka s blokovacím kamenem
    return [f'<line x1="{x-15}" y1="{y+12}" x2="{x+12}" y2="{y-9}" stroke="{INK}" stroke-width="1.5"/>',
            f'<rect x="{x+9}" y="{y-13}" width="5" height="5" fill="{INK}"/>',
            f'<path d="M{x-15},{y+12} q-4,-3 -2,-8" fill="none" stroke="{INK}" stroke-width="1"/>',
            f'<path d="M{x-1},{y+1} l7,-4" stroke="{INK}" stroke-width="0.8"/>']

def g_kyvadlo(x, y):
    return [f'<line x1="{x}" y1="{y-16}" x2="{x}" y2="{y+8}" stroke="{INK}" stroke-width="1.4"/>',
            f'<circle cx="{x}" cy="{y+13}" r="6" fill="none" stroke="{INK}" stroke-width="1.7"/>']

def g_lihyr(x, y):
    return [f'<line x1="{x-16}" y1="{y}" x2="{x+16}" y2="{y}" stroke="{INK}" stroke-width="1.7"/>',
            f'<line x1="{x}" y1="{y-10}" x2="{x}" y2="{y}" stroke="{INK}" stroke-width="1.3"/>',
            f'<rect x="{x-19}" y="{y-4}" width="7" height="8" fill="{INK}"/>',
            f'<rect x="{x+12}" y="{y-4}" width="7" height="8" fill="{INK}"/>']

def g_setrvacka(x, y):  # balance
    return [f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{INK}" stroke-width="1.7"/>',
            f'<line x1="{x-14}" y1="{y}" x2="{x+14}" y2="{y}" stroke="{INK}" stroke-width="1.1"/>',
            f'<line x1="{x}" y1="{y-14}" x2="{x}" y2="{y+14}" stroke="{INK}" stroke-width="1.1"/>',
            f'<circle cx="{x}" cy="{y}" r="2.4" fill="{INK}"/>']

def g_vlasek(x, y):
    return [spiral(x, y, 1.5, 14, 3.2, clr=INK, w=1.0)]

def g_zaverka(x, y):  # locking plate / count wheel — disk s nepravidelnými zářezy
    out = [f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{INK}" stroke-width="1.4"/>']
    for k, d in enumerate([0, 40, 95, 150, 210, 285]):
        x1, y1 = pol(x, y, 14, d); x2, y2 = pol(x, y, 9, d)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="1.1"/>')
    out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}"/>')
    return out

def g_pocetnik(x, y):  # rack — ozubený oblouk + čep
    out = [f'<circle cx="{x-15}" cy="{y+12}" r="2" fill="{INK}"/>']
    pts = []
    for k in range(9):
        a = -60 + k * 12
        xx, yy = pol(x - 15, y + 12, 26, a)
        pts.append((xx, yy))
    out.append(f'<polyline points="{" ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    # zoubky dovnitř (k čepu)
    for (xx, yy) in pts:
        dx, dy = (x-15) - xx, (y+12) - yy
        L = (dx*dx+dy*dy) ** 0.5 or 1
        out.append(f'<line x1="{xx:.1f}" y1="{yy:.1f}" x2="{xx+dx/L*4:.1f}" y2="{yy+dy/L*4:.1f}" stroke="{INK}" stroke-width="1"/>')
    return out

def g_stupnice(x, y):  # snail cam
    pts = []
    for i in range(13):
        a = math.radians(i / 12 * 360)
        r = 4 + 11 * (i / 12)
        pts.append(f"{x + r*math.cos(a):.1f},{y + r*math.sin(a):.1f}")
    return [f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="1.5"/>',
            f'<line x1="{pts[-1].split(",")[0]}" y1="{pts[-1].split(",")[1]}" x2="{pts[0].split(",")[0]}" y2="{pts[0].split(",")[1]}" stroke="{INK}" stroke-width="1.1"/>',
            f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}"/>']

def g_srdcovka(x, y):  # warning / hoop wheel — kolo s jedním zářezem
    return [f'<circle cx="{x}" cy="{y}" r="13" fill="none" stroke="{INK}" stroke-width="1.4"/>',
            f'<path d="M{x},{y-13} l-3,5 l6,0 z" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>',
            f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}"/>']

def g_posuvka(x, y):  # lifting cam — vačka
    return [f'<ellipse cx="{x+2}" cy="{y}" rx="13" ry="9" fill="none" stroke="{INK}" stroke-width="1.5"/>',
            f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}"/>',
            f'<line x1="{x}" y1="{y}" x2="{x+15}" y2="{y}" stroke="{INK}" stroke-width="0.7" stroke-dasharray="2 2"/>']

def g_vypousteci(x, y):  # let-off — kolo s kolíkem + zarážka
    return [f'<circle cx="{x-4}" cy="{y}" r="11" fill="none" stroke="{INK}" stroke-width="1.3"/>',
            f'<circle cx="{pol(x-4,y,11,40)[0]:.1f}" cy="{pol(x-4,y,11,40)[1]:.1f}" r="2.2" fill="{INK}"/>',
            f'<path d="M{x+14},{y-12} L{x+6},{y+2}" fill="none" stroke="{ACC}" stroke-width="1.5"/>',
            f'<circle cx="{x+14}" cy="{y-12}" r="2" fill="{ACC}"/>']

def g_vetrnik(x, y):  # fly
    return [f'<line x1="{x}" y1="{y-15}" x2="{x}" y2="{y+15}" stroke="{INK}" stroke-width="1.3"/>',
            f'<rect x="{x-16}" y="{y-12}" width="11" height="9" fill="none" stroke="{INK}" stroke-width="1.3"/>',
            f'<rect x="{x+5}" y="{y+3}" width="11" height="9" fill="none" stroke="{INK}" stroke-width="1.3"/>']

def g_kladivko(x, y):  # hammer
    return [f'<circle cx="{x-13}" cy="{y+10}" r="2" fill="{INK}"/>',
            f'<line x1="{x-13}" y1="{y+10}" x2="{x+10}" y2="{y-8}" stroke="{INK}" stroke-width="1.5"/>',
            f'<rect x="{x+8}" y="{y-13}" width="9" height="7" rx="1.5" fill="{INK}"/>']

def g_cimbal(x, y):  # bell
    return [f'<path d="M{x-12},{y+9} q0,-20 12,-20 q12,0 12,20 z" fill="none" stroke="{INK}" stroke-width="1.6"/>',
            f'<line x1="{x-14}" y1="{y+9}" x2="{x+14}" y2="{y+9}" stroke="{INK}" stroke-width="1.4"/>',
            f'<circle cx="{x}" cy="{y+12}" r="2" fill="{INK}"/>']

def g_cifernik(x, y):  # dial
    return [f'<circle cx="{x}" cy="{y}" r="15" fill="none" stroke="{INK}" stroke-width="1.5"/>',
            f'<text x="{x}" y="{y-6}" font-size="6" fill="{INK}" text-anchor="middle">XII</text>',
            f'<line x1="{x}" y1="{y}" x2="{x+7}" y2="{y-4}" stroke="{INK}" stroke-width="1.2"/>',
            f'<circle cx="{x}" cy="{y}" r="1.6" fill="{INK}"/>']

def g_rucka(x, y):  # hand
    return [f'<circle cx="{x-13}" cy="{y+6}" r="2.4" fill="{OUT}"/>',
            f'<line x1="{x-13}" y1="{y+6}" x2="{x+11}" y2="{y-8}" stroke="{OUT}" stroke-width="2"/>',
            f'<path d="M{x+11},{y-8} l-6,1 l3,4 z" fill="{OUT}"/>']

def g_indikace(x, y):
    return [f'<line x1="{x}" y1="{y+12}" x2="{x}" y2="{y-6}" stroke="{OUT}" stroke-width="1.5"/>',
            f'<path d="M{x-4},{y-6} l4,-7 l4,7 z" fill="{OUT}"/>',
            f'<circle cx="{x}" cy="{y+12}" r="2" fill="{OUT}"/>']

def g_remontoir(x, y):  # remontoár — pomocná zpruha + páčka
    return [spiral(x-6, y, 1, 8, 1.8, clr=ACC, w=1.1),
            f'<line x1="{x+2}" y1="{y}" x2="{x+15}" y2="{y-9}" stroke="{ACC}" stroke-width="1.5"/>',
            f'<circle cx="{x+15}" cy="{y-9}" r="2" fill="{ACC}"/>',
            f'<text x="{x+2}" y="{y+15}" font-size="8" fill="{ACC}" text-anchor="middle" font-style="italic">R</text>']

def g_maintaining(x, y):  # údržbový pohon (Harrison) — kolo + pružná západka
    return [f'<circle cx="{x-4}" cy="{y}" r="11" fill="none" stroke="{INK}" stroke-width="1.3"/>',
            spiral(x+10, y+4, 1, 5, 1.6, clr=ACC, w=1.0),
            f'<path d="M{x+10},{y+4} L{x-1},{y-3}" fill="none" stroke="{ACC}" stroke-width="1.4"/>']


def g_vypousteci_paka(x, y):  # lifting piece — zalomená páka zvedaná kolíkem
    return [f'<circle cx="{x-13}" cy="{y-6}" r="2" fill="{INK}"/>',
            f'<path d="M{x-13},{y-6} L{x+10},{y+4} M{x-13},{y-6} L{x-9},{y+10}" fill="none" stroke="{INK}" stroke-width="1.5"/>',
            f'<circle cx="{x-9}" cy="{y+11}" r="1.6" fill="{INK}"/>']  # nos zvedaný kolíkem

def g_zaverna_paka(x, y):  # locking lever — páka s nosem (padá do výřezu = zámek)
    return [f'<circle cx="{x+12}" cy="{y-8}" r="2" fill="{INK}"/>',
            f'<path d="M{x+12},{y-8} L{x-10},{y+4} l0,7 l4,0" fill="none" stroke="{INK}" stroke-width="1.5"/>']

def g_zapadka_pocetniku(x, y):  # rack hook — západka držící početník
    out = [f'<circle cx="{x+10}" cy="{y-9}" r="2" fill="{INK}"/>',
           f'<path d="M{x+10},{y-9} L{x-8},{y+6} l5,-1" fill="none" stroke="{INK}" stroke-width="1.5"/>']
    for i in range(3):  # zuby početníku, do kterých zapadá
        out.append(f'<path d="M{x-14+i*5},{y+10} l3,-4 l3,4" fill="none" stroke="{THIN}" stroke-width="0.9"/>')
    return out

def g_sberaci_palec(x, y):  # gathering pallet — kotouč s palcem (sbírá početník)
    return [f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{INK}" stroke-width="1.3"/>',
            f'<path d="M{x},{y} L{x+15},{y-7}" fill="none" stroke="{INK}" stroke-width="1.6"/>',
            f'<rect x="{x-2.5}" y="{y-2.5}" width="5" height="5" fill="{INK}"/>']


# slug, cs, en, de, kategorie, fn
SYM = [
    ("zavazi", "závaží", "weight", "Gewicht", "Pohon", g_zavazi),
    ("buben", "lanový buben", "drum", "Trommel", "Pohon", g_buben),
    ("perovnik", "perovník", "mainspring barrel", "Federhaus", "Pohon", g_perovnik),
    ("pero", "péro tažné", "mainspring", "Zugfeder", "Pohon", g_pero),
    ("snek", "závitek / šnek", "fusee", "Schnecke", "Pohon", g_snek),
    ("retizek-snekovy", "řetízek šnekový", "fusee chain", "Schneckenkette", "Pohon", g_retizek),
    ("rohatka", "rohatka", "ratchet wheel", "Sperrad", "Pohon", g_rohatka),
    ("zapadka", "západka", "pawl / click", "Sperrklinke", "Pohon", g_zapadka),
    ("klika", "natahovací klika", "winding crank", "Aufzugskurbel", "Pohon", g_klika),
    ("natahovaci-ctyrhran", "natahovací čtyřhran", "winding square", "Aufzugsvierkant", "Pohon", g_natahovaci_ctyrhran),
    ("klicek", "natahovací klíček", "winding key", "Aufzugschlüssel", "Pohon", g_klicek),
    ("kolo", "ozubené kolo", "wheel", "Zahnrad", "Soukolí", g_kolo),
    ("pastorek", "pastorek", "pinion", "Trieb", "Soukolí", g_pastorek),
    ("cevkovy-pastorek", "cévkový pastorek", "lantern pinion", "Laternengetriebe", "Soukolí", g_cevkovy),
    ("krokove-kolo", "krokové kolo (pilové)", "escape wheel", "Hemmungsrad", "Krokové kolo", g_krokove_kolo),
    ("korunove-kolo", "korunové kolo", "crown wheel", "Kronrad", "Krokové kolo", g_korunove_kolo),
    ("kolickove-kolo", "kolíčkové krokové kolo", "pin escape wheel", "Stiftenrad", "Krokové kolo", g_kolickove_kolo),
    ("cylindrove-kolo", "cylindrové (válcové) kolo", "cylinder escape wheel", "Zylinderrad", "Krokové kolo", g_cylindrove_kolo),
    ("kotva", "kotva vratná", "recoil anchor", "Ankerrad-Anker", "Kotva / krok", g_kotva),
    ("kotva-grahamova", "kotva klidová (Graham)", "deadbeat anchor", "ruhender Anker", "Kotva / krok", g_kotva_grahamova),
    ("vreteno", "vřeteno", "verge", "Spindel", "Kotva / krok", g_vreteno),
    ("kotva-pakova", "kotva páková (volná)", "lever", "Ankerhebel", "Kotva / krok", g_kotva_pakova),
    ("paleta-kolikova", "paleta kolíková (Amant)", "pin pallet", "Stiftpalette", "Kotva / krok", g_paleta_kolikova),
    ("cylindr", "cylindr (válec)", "cylinder", "Zylinder", "Kotva / krok", g_cylindr),
    ("detent", "zarážka chronometru", "detent", "Chronometerdetent", "Kotva / krok", g_detent),
    ("paleta", "paleta", "pallet", "Palette", "Kotva / krok", g_paleta),
    ("kyvadlo", "kyvadlo", "pendulum", "Pendel", "Oscilátor", g_kyvadlo),
    ("lihyr", "lihýř / foliot", "foliot", "Waag", "Oscilátor", g_lihyr),
    ("setrvacka", "setrvačka", "balance", "Unruhe", "Oscilátor", g_setrvacka),
    ("vlasek", "vlásek", "hairspring", "Spirale", "Oscilátor", g_vlasek),
    ("zaverka", "závěrka / počitadlo", "locking plate / count wheel", "Schloßscheibe", "Bicí", g_zaverka),
    ("pocetnik", "početník", "rack", "Schlagrechen", "Bicí", g_pocetnik),
    ("stupnice", "stupnice", "snail", "Staffel", "Bicí", g_stupnice),
    ("srdcovka", "srdcovka", "warning / hoop wheel", "Herzscheibe", "Bicí", g_srdcovka),
    ("posuvka", "posůvka", "lifting cam", "Hebenocke", "Bicí", g_posuvka),
    ("vypousteci-kolo", "vypouštěcí kolo", "let-off / release", "Auslösung", "Bicí", g_vypousteci),
    ("vypousteci-paka", "vypouštěcí páka", "lifting piece", "Auslösehebel", "Bicí", g_vypousteci_paka),
    ("zaverna-paka", "závěrná páka", "locking lever", "Sperrhebel", "Bicí", g_zaverna_paka),
    ("zapadka-pocetniku", "západka početníku", "rack hook", "Rechenfanghebel", "Bicí", g_zapadka_pocetniku),
    ("sberaci-palec", "sběrací palec", "gathering pallet", "Hebedaumen", "Bicí", g_sberaci_palec),
    ("vetrnik", "větrník", "fly / fan", "Windfang", "Bicí", g_vetrnik),
    ("kladivko", "kladivo", "hammer", "Hammer", "Bicí", g_kladivko),
    ("cimbal", "cimbál / zvon", "bell", "Glocke", "Bicí", g_cimbal),
    ("cifernik", "ciferník", "dial", "Zifferblatt", "Ukazovací", g_cifernik),
    ("rucka", "ručka", "hand", "Zeiger", "Ukazovací", g_rucka),
    ("indikace", "indikace", "indication", "Anzeige", "Ukazovací", g_indikace),
    ("remontoir", "remontoár", "remontoire", "Remontoir", "Speciální", g_remontoir),
    ("udrzbovy-pohon", "údržbový pohon", "maintaining power", "Erhaltungsantrieb", "Speciální", g_maintaining),
]


def sheet():
    CW, CH, COLS = 248, 104, 4
    cats = []
    for s in SYM:
        if not cats or cats[-1][0] != s[4]: cats.append([s[4], []])
        cats[-1][1].append(s)
    W = 60 + COLS * CW
    # spočítej výšku
    rows = sum(((len(items) + COLS - 1) // COLS) for _, items in cats)
    H = 110 + len(cats) * 34 + rows * CH + 40
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Georgia,\'Times New Roman\',serif" role="img">',
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
           f'<text x="40" y="48" font-size="22" fill="{INK}">Horonotace — list symbolů (vrstva C)</text>',
           f'<text x="40" y="72" font-size="12" fill="{THIN}">Schematické značky komponent. Slug = hodnota pole typ; termín dle glosáře horologicka-terminologie.</text>']
    yy = 104
    for cat, items in cats:
        out.append(f'<text x="40" y="{yy+16}" font-size="14" fill="{ACC}">{esc(cat)}</text>')
        out.append(f'<line x1="40" y1="{yy+22}" x2="{W-40}" y2="{yy+22}" stroke="{ACC}" stroke-opacity="0.4" stroke-width="0.8"/>')
        yy += 34
        for i, (slug, cs, en, de, _, fn) in enumerate(items):
            col = i % COLS; rowstart = (i // COLS)
            cx = 40 + col * CW + CW // 2 - 60
            cyr = yy + rowstart * CH
            out += fn(cx, cyr + 30)
            out.append(f'<text x="{cx}" y="{cyr+66}" font-size="11" fill="{INK}" text-anchor="middle" font-family="monospace">{esc(slug)}</text>')
            out.append(f'<text x="{cx}" y="{cyr+82}" font-size="11" fill="{THIN}" text-anchor="middle">{esc(cs)}</text>')
        yy += ((len(items) + COLS - 1) // COLS) * CH + 6
    out.append(f'<text x="{W-40}" y="{H-16}" font-size="10" fill="{THIN}" text-anchor="end" font-style="italic">horonotace · list symbolů</text>')
    out.append("</svg>")
    return "\n".join(out)


def table():
    lines = ["| Symbol (slug) | Komponenta (cs) | en | de | Kategorie |",
             "|---|---|---|---|---|"]
    for slug, cs, en, de, kat, _ in SYM:
        lines.append(f"| `{slug}` | {cs} | {en} | {de} | {kat} |")
    return "\n".join(lines)


if __name__ == "__main__":
    if "--table" in sys.argv:
        print(table())
    else:
        out = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else "render/symboly.svg"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w").write(sheet())
        print(f"→ {out}  ({len(SYM)} symbolů)")
