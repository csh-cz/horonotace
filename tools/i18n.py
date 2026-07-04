#!/usr/bin/env python3
"""Lokalizace vykreslených SVG (horonotace). CZ je zdroj; EN se získá:
- u render_svg / render_dial / render_front post-zpracováním textových uzlů (`localize`),
- u symboly.py přímo z pole `en` v datech (žádná kolize slug×termín).

Slovník `TR` mapuje ZOBRAZOVANÝ český řetězec → anglický. Slugy (ASCII kebab-case)
zde NEJSOU, takže zůstávají beze změny.
"""
import re

CAT = {
    "Pohon": "Drive", "Soukolí": "Gearing", "Krokové kolo": "Escape wheel",
    "Kotva / krok": "Anchor / escapement", "Oscilátor": "Oscillator",
    "Bicí": "Striking", "Ukazovací": "Indication", "Speciální": "Special",
    "Krok": "Escapement",
}

TR = {
    # --- nadpisy / podtituly ---
    "Věžní hodiny — typický stroj (jicí + bicí)": "Tower clock — typical movement (going + striking)",
    "Italský věžní stroj (imaginární)": "Italian tower movement (imaginary)",
    "Staroměstský orloj — astronomický číselník": "Prague Old-Town astronomical dial",
    "Horonotace — list symbolů (vrstva C)": "Horonotace — sheet of symbols (layer C)",
    "19. století": "19th century",
    "ilustrativní (sloh 16.–17. stol.)": "illustrative (16th–17th c. style)",
    "Pohled na číselník (vrstva D). Astroláb = stereografická projekce ZE SEV. pólu (Rak vnější, Kozoroh vnitřní); polohy ukazatelů ilustrativní.":
        "Dial view (layer D). Astrolabe = stereographic projection FROM THE NORTH pole (Cancer outer, Capricorn inner); indicator positions are illustrative.",
    "Pohled na číselník (vrstva D). Soustředné stupnice (italské + francouzské hodiny, minuty); polohy ilustrativní.":
        "Dial view (layer D). Concentric scales (Italian + French hours, minutes); positions illustrative.",
    "Schematické značky komponent. Slug = hodnota pole typ; termín dle glosáře horologicka-terminologie.":
        "Schematic component symbols. Slug = value of the typ field; term per the horologicka-terminologie glossary.",
    "kola = roztečné kružnice (⌀ ∝ zubům) · záběr = dotyk kružnic · režim: schématický (z počtu zubů)":
        "wheels = pitch circles (⌀ ∝ teeth) · mesh = circles touching · mode: schematic (from tooth counts)",
    "— čelní pohled": "— front view",
    # --- rám / legenda / elevace ---
    "Rám — flatbed": "Frame — flatbed", "Rám — klecový": "Frame — birdcage",
    "barva = jednotlivá dráha (osa/trubka) · délka úsečky kola ∝ roztečnému průměru (∝ z)":
        "colour = individual path (arbor/tube) · wheel-bar length ∝ pitch diameter (∝ z)",
    "klíny = kolo spojené se svou dráhou": "squares = wheel fixed to its path",
    "osa (nejdelší) + kratší trubky → ukazatele": "axis (longest) + shorter tubes → indicators",
    "jdoucí soukolí": "going train", "zuby nedoloženy": "tooth counts undocumented",
    "na straně ciferníku (mimo rám)": "on the dial side (outside the frame)",
    "Regulace bití": "Striking regulation",
    "závaží": "weight", "kyvadlo 2 s": "pendulum 2 s", "kyvadlo": "pendulum",
    "natahování": "winding", "natahování klikou": "winding by crank",
    "krok: kotvový": "escapement: recoil anchor",
    "krok: vřetenový (foliotový)": "escapement: verge (foliot)",
    "▲ minuty": "▲ minutes", "▲ fáze Měsíce": "▲ Moon phase",
    # --- ústrojí (názvy bloků z modelu) + kategorie sdílené ---
    "Jicí soukolí": "Going train", "Bicí soukolí (počitadlové)": "Striking train (count-wheel)",
    "Astroláb (Slunce / Měsíc / zvěrokruh)": "Astrolabe (Sun / Moon / zodiac)",
    "Fáze Měsíce (polostříbřená koule)": "Moon phase (semi-silvered sphere)",
    "Kalendárium (deska, R. Božek)": "Calendarium (plate, R. Božek)",
    "Slunce": "Sun", "Měsíc": "Moon", "zvěrokruh": "zodiac", "kalendář": "calendar",
    # --- číselník (astroláb / koncentrický) ---
    "dies (den)": "dies (day)", "jarní bod": "vernal point",
    "staročeský čas": "Old Bohemian time", "staročeský čas (otočný prsten)": "Old Bohemian time (rotating ring)",
    "koncentrický číselník (imaginární italský stroj)": "concentric dial (imaginary Italian movement)",
    "kalendárium — 365 dílů, deska J. Mánes": "calendarium — 365 divisions, plate by J. Mánes",
    # --- razítka ---
    "horonotace · vrstva C": "horonotace · layer C",
    "horonotace · vrstva D (číselník)": "horonotace · layer D (dial)",
    "horonotace · vrstva E": "horonotace · layer E",
    "horonotace · list symbolů": "horonotace · symbol sheet",
    # --- regulace bití (popisky pák v elevaci) ---
    "vypouštěcí páka": "lifting piece", "závěrná páka": "locking lever",
    "kladivo": "hammer", "cimbál": "bell", "početník": "rack",
    # --- měsíce (kalendárium) ---
    "led": "Jan", "úno": "Feb", "bře": "Mar", "dub": "Apr", "kvě": "May", "čvn": "Jun",
    "čvc": "Jul", "srp": "Aug", "zář": "Sep", "říj": "Oct", "lis": "Nov", "pro": "Dec",
    # --- <desc> (přístupnost) ---
    "Schématická elevace soukolí (horonotace, vrstva C).": "Schematic gear elevation (horonotace, layer C).",
    # --- názvy bloků / štítky bez diakritiky (ID prvků, kategorie jako názvy ústrojí) ---
    "Krok": "Escapement", "Oscilátor": "Oscillator", "Pohon": "Drive", "Soukolí": "Gearing",
    "Bicí": "Striking", "Ukazovací": "Indication", "Speciální": "Special",
    "Oscilátor (kyvadlo)": "Oscillator (pendulum)", "Vřetenový krok": "Verge escapement",
    "vetrnik": "fly", "pocitadlo": "count wheel", "going": "going wheel",
    "Mikuláš z Kadaně; výpočet Jan Šindel (1410). Rekonstr. Romuald Božek (1865–66) · 1410 (s…":
        "Mikuláš of Kadaň; calc. Jan Šindel (1410). Reconstr. Romuald Božek (1865–66) · 1410 (s…",
}


def localize(svg, lang):
    """Post-zpracování: přeloží obsah textových uzlů dle TR (jen pro EN)."""
    if lang != "en":
        return svg

    def repl(m):
        s = m.group(1)
        core = s.strip()                                  # tolerance k okrajovým mezerám
        lead = s[:len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()):]
        if core in TR:
            return ">" + lead + TR[core] + trail + "<"
        if core.startswith("buben ⌀"):                    # dynamický popisek bubnu
            return ">" + lead + core.replace("buben ⌀", "drum ⌀").replace(" ot.", " turns") + trail + "<"
        if core.startswith("krok: "):                     # nezachycený druh kroku
            return ">" + lead + "escapement: " + core[6:] + trail + "<"
        return m.group(0)

    return re.sub(r'>([^<>]+)<', repl, svg)
