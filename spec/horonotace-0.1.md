# Horonotace — specifikace 0.1

Status: **návrh**. Tento dokument popisuje strukturní datový model (vrstva A).

## 1. Architektura vrstev

Horonotace záměrně odděluje reprezentace téhož stroje (poučení z SMILES vs. MOL,
ABC vs. MEI). Jádrem v0.1 je vrstva A (strukturní model); **B** (lineární zápis) je
plánovaná, **C/D/E** (vykreslení) existují jako prototypy (`render_svg.py`,
`render_dial.py`, `render_front.py`).

| Vrstva | Forma | Role | Stav |
|---|---|---|---|
| **A — strukturní model** | YAML / JSON + JSON Schema | Zdroj pravdy. Graf prvků, hřídelí a vazeb. Validovatelný, počitatelný. | **v0.1 (zde)** |
| **B — lineární zápis** | kompaktní řetězec | Psaní rukou, vložení do textu, citace. Generuje se z A jedním kanonizátorem. | plán |
| **C — elevace soukolí** | SVG (web), symboly dle ISO 3952 + horologické glyfy | Schéma stroje. Generuje se z A. Podoba: **Oechslinova „elevace mezi deskami"** (vodorovné = desky `Platine`, svislice = hřídel, závorka = kolo se zuby, vodorovně = záběr) — viz [docs/oechslin-roegel.md](../docs/oechslin-roegel.md). Prototyp: `tools/render_svg.py`. Sada symbolů komponent: [docs/symboly.md](../docs/symboly.md) + `tools/symboly.py` (list `render/symboly.svg`). | prototyp |
| **D — pohled na číselník** | SVG (web) | Schematický **čelní pohled na ciferník** — jak ukazatele opravdu vypadají (zejm. astronomické hodiny: astroláb s polem den/noc, ekliptika, sluneční/měsíční ručka s fází; kalendárium). Generuje se z indikačních prvků A. Prototyp: `tools/render_dial.py`. | prototyp |
| **E — čelní pohled na soukolí** | SVG (web) | **Čelní pohled na soukolí** — kola jako roztečné kružnice (⌀ ∝ zubům), záběr = dotyk, soustředná kola sdílejí střed. Planární uspořádání hřídelí (obdoba depthing plánu); ortografický doplněk elevace C. Schématický režim z počtů zubů, věrný režim z pole `poloha`. Prototyp: `tools/render_front.py`. | prototyp |

Vrstva A je **graf se smyčkami**, ne strom — soukolí i spřažení jdoucího a bicího
ústrojí tvoří smyčky.

## 2. Datový model

Dokument má tři části: `horonotace` (verze), `hlavicka` (metadata, citace) a
`stroj` (vlastní mechanismus).

```yaml
horonotace: "0.1"
hlavicka: { … }      # kdo, kde, kdy, typ, inv. č. — viz §2.1
stroj:
  ustroji: [ … ]     # úroveň 1: funkční ústrojí (blokové schéma)
  prvky:   [ … ]     # úroveň 2: kola, pastorky, krok, kyvadlo, cimbály, ručky…
  hridele: [ … ]     # sdílené „nety" — souosé prvky
  vazby:   [ … ]     # hrany: záběr, tok, spouštění, pohon, pohání
  konstrukce: { … }  # typ nosné konstrukce: desky (plotny) / klecový rám / flatbed rám
```

> **Konstrukce ≠ topologie.** Abstraktní graf (`prvky`/`hridele`/`vazby`) je nezávislý
> na typu konstrukce. Hřídele (osy) a záběry existují stejně u plotnového i rámového
> stroje; **typ rámu ovlivňuje jen prostorové vykreslení (vrstva C), ne výpočet
> převodů**. Pozor: **věžní hodiny mají rám** (klecový / flatbed), kola jsou uložena
> v rámových sloupcích a příčníkách — **ne mezi plotnami** jako interiérové stroje.

Stroj se popisuje na **dvou vnořených úrovních**:

- **Úroveň 1 (blokové schéma)** — uzly jsou `ustroji` (pohon, jdoucí soukolí, krok,
  oscilátor, bicí soukolí, ukazovací ústrojí, komplikace), hrany jsou vazby typu
  `tok` a `spousteni`. Stačí samo o sobě (graceful partial spec à la InChI) — když
  detaily kol neznáme, popíšeme jen ústrojí a tok mezi nimi.
- **Úroveň 2 (kola/pastorky)** — `prvky` se zuby, `hridele` jako sdílené nety a
  `vazby` typu `zaber`. Z toho se počítá převod a počet kmitů.

Každý `prvek` odkazuje svým polem `ustroji` na blok, do něhož patří → obě úrovně
jsou propojené a renderer umí mezi nimi přepínat (rozklik bloku na kola).

### 2.1 Hlavička (citace)

Uspořádaná, oddělená od těla stroje (PGN model) → každý záznam je samostatně
citovatelný.

```yaml
hlavicka:
  nazev: "Věžní hodiny, kostel sv. …"
  autor: "Jan Prokeš ze Sobotky"     # výrobce / firma
  misto: "Sobotka"
  datace: "1868"                      # rok nebo rozsah „1860–1870"
  typ: vezni                          # vezni|stolni|nastenne|skrinove|astronomicke|orloj|jine
  inv: "H-1234"                       # inventární číslo
  sbirka: "Hodinárium ČSH"
  wikidata: Q729370                   # volitelně, pro citaci (plán: i CIDOC-CRM)
  pozn: "…"
```

### 2.2 Prvek (`prvky[]`)

Vše hmotné je typovaný prvek. Společná pole `id`, `typ`; další pole závisí na typu
(model je úmyslně rozšiřitelný — `additionalProperties` povolené).

```yaml
- id: stredni-kolo
  typ: kolo
  role: stredni          # funkční role (volitelně)
  ustroji: jdouci        # příslušnost k bloku úrovně 1
  zuby: 90               # u kol/pastorků
  pozn: "nese minutovou ručku"
```

#### Slovník typů — kanonický v [slovnik-typu.md](slovnik-typu.md)

Řízený slovník `typ`/`role`/`druh` je **ukotvený na hodinářský glosář** (skill
`horologicka-terminologie`, prameny Špatný 1882 / Sušický 1900 / Sladkovský 1947 /
Dietzschold 1905). Plná tabulka cs/en/de viz [slovnik-typu.md](slovnik-typu.md).
Stručně:

**Pohon:** `zavazi`, `buben` (`prumer`,`otacky`,`lano`), `pero`, `perovnik`, `snek`/`zavitek` (fusee), `retizek-snekovy`, `rohatka`, `zapadka`
**Soukolí:** `kolo` (`zuby`, `role`: `hlavni|spodni|minutove|mezitimni|sekundove|kolickove|stridne|hodinove`), `pastorek` (`zuby`), `cevkovy-pastorek`
**Krok:** `krok` (`druh`: `vretenovy|kotvovy|grahamuv|amantuv|robertuv|brocotuv|valeckovy|chronometrovy|volny-kotvovy|hippuv|…` — katalog se symboly [docs/kroky.md](../docs/kroky.md)), `krokove-kolo`, `kotva`, `paleta`
**Oscilátor:** `kyvadlo` (`perioda`, `kompenzace`: `rostove|rtutove|invarove`), `lihyr`/`foliot`, `setrvacka`, `vlasek`
**Bicí:** `zaverka` (závěrka), `pocitadlo`, `pocetnik` (rack), `stupnice` (snail), `srdcovka`, `posuvka`, `vypousteci-kolo`, `vetrnik`, `kladivko`, `cimbal`/`zvon` (`pocet`)
**Ukazovací / indikace:** `cifernik`, `rucka` (`ukazuje`: `hodiny|minuty|vteriny|datum|mesic|…`), `soukoli-rucek` (kvadratura), `indikace` (`druh`: `kalendar|lunace|faze-mesice|equation|astrolab|tellurium|planetarium|…`)

> Změna proti dřívějšku: německé slugy **`rechen` → `pocetnik`**, **`staffel` → `stupnice`**
> (kanonický český termín z glosáře).

> `druh` u `krok` ať odkazuje na slug katalogu kroků (`/kroky/<slug>`), aby web
> propojil schéma s heslem o daném kroku.

### 2.3 Hřídel (`hridele[]`) — sdílený net

Souosé prvky (kolo + pastorek na téže hřídeli) sdílí hřídel. Záběr pak vzniká
*mezi prvky na různých hřídelích*. Hřídel je první-třídní uzel grafu (SPICE model).

```yaml
- id: h-stredni
  nese: [stredni-kolo, p-treti]    # kola/pastorky na téže ose
  perioda: "1 h"                   # doba 1 otáčky (volitelně; např. minutové kolo)
- id: h-slunce
  osa: os-astrolab                 # soustředné trubky (Stützrohr) sdílí osu →
  nese: [kolo-slunce, rucka-slunce] #   vrstva C je kreslí v jednom sloupci nad sebou
```

Pole `osa` značí **soustředné hřídele** (trubky na společné ose, např. ručky Slunce
/ Měsíce / zvěrokruhu na pražském orloji). Vrstva C je vykreslí jako jeden sloupec.

Volitelné pole `poloha: [x, y]` (mm) udává **skutečnou polohu hřídele v plotně/rámu**.
Použije ji **čelní pohled (vrstva E)** pro věrný depthing plán; bez ní se polohy
hřídelí dopočtou schématicky z počtů zubů.

### 2.4 Vazba (`vazby[]`) — hrany

```yaml
- typ: zaber                 # záběr: hnací kolo → hnaný pastorek
  z: stredni-kolo
  do: p-treti
  # prevod = zuby(z)/zuby(do) se dopočítá
```

| `typ` | Význam | `z` → `do` |
|---|---|---|
| `pohon` | pohon roztáčí první kolo | pohon → kolo |
| `zaber` | záběr ozubení | hnací → hnaný (kolo i pastorek) |
| `tok` | tok síly/pohybu mezi ústrojími (úroveň 1) | ústrojí → ústrojí |
| `spousteni` | jdoucí soukolí spouští bicí; páka uvolní páku (let-off / aktuace) | prvek/ústrojí → prvek/ústrojí |
| `blokuje` | člen zamyká/blokuje druhý (zámek bicího stroje, západka) | páka/kolo → soukolí/prvek |
| `pohani` | soukolí pohání ukazovací prvek | prvek → rucka/indikace |

## 3. Co se z modelu počítá

- **Celkový převod** soukolí = součin `zuby(kolo)/zuby(pastorek)` po cestě záběrů
  (Martínek/Řehoř `i = (Z₁/z₁)(Z₂/z₂)…`).
- **Počet kmitů za hodinu** oscilátoru z převodu mezi minutovým a krokovým kolem a
  počtu zubů krokového kola (BHI/Britten vzorec).
- **Indikační poměry** (astronomické): poměr period souosých kol — např. orloj
  365 / 366 / 379 na společném pastorku. Po vzoru **Oechslina/Roegela** (viz
  [docs/oechslin-roegel.md](../docs/oechslin-roegel.md)) ukládat poměry i periody
  jako **exaktní zlomky** (ne desetinná čísla), se znaménkem = smyslem otáčení;
  u indikace volitelně **cílová astronomická perioda** a dopočtená **chyba/drift**.
- **Epicyklická soukolí**: relativní vs. absolutní rychlost přes vztažnou soustavu
  (unášeč), `V_abs = V_rel + V_carrier`. Plné řešení až v0.2 (viz §5.3).
- **Kontrola konzistence:** každý `zaber` musí spojovat prvky na různých hřídelích;
  každé `id` ve `vazby` musí existovat v `prvky`/`ustroji`/`hridele`.

## 4. Příklady

- [examples/vezni-pocitadlo.yaml](../examples/vezni-pocitadlo.yaml) — věžní stroj se
  závažovým pohonem, kotvovým krokem, vteřinovým kyvadlem a počitadlovým hodinovým
  bitím; obě úrovně granularity.
- [examples/vezni-jici-bici.yaml](../examples/vezni-jici-bici.yaml) — **typický věžní
  stroj**: flatbed rám, plné **jicí soukolí** (96→96→90→krok. kolo 30, vteřinové
  kyvadlo) i **bicí soukolí** (96→84→kolíkové 48→větrník, počitadlo 78), spouštění
  bití z jicího stroje, dvě závaží.
- [examples/orloj-astrolab.yaml](../examples/orloj-astrolab.yaml) — zjednodušená
  astronomická indikace s převody 365/366/379 a fází Měsíce.
- [examples/praga-orloj.yaml](../examples/praga-orloj.yaml) — **Staroměstský orloj**:
  věrný zápis astrolábu (společný pastorek 24 z → kola 365/366/379), fáze Měsíce
  (57z věnec + dvouchodý šnek), kalendárium a staročeský čas; kovaný klecový rám.
  Doložené počty zubů (Horský & Procházka 1964, orloj.eu).

## 5. Otevřené otázky pro v0.2

1. Lineární zápis (vrstva B) — návrh gramatiky a kanonizátoru.
2. Sada symbolů (vrstva C) — které ISO 3952 glyfy převzít, které horologické dodělat.
3. Epicyklická/planetová soukolí — Willisova rovnice, zápis unášeče; převzít
   Oechslin/Roegel model `V_abs = V_rel + V_carrier` + vztažnou soustavu (prime).
   Periody/převody jako exaktní zlomky, indikace s polem `cil` (cílová perioda) a
   dopočtenou `chyba`. Viz [docs/oechslin-roegel.md](../docs/oechslin-roegel.md).
4. Mapování slovníku na Getty AAT URI a hlavičky na CIDOC-CRM / Wikidata.
5. Identita stroje — kanonický hash topologie (InChIKey analogie) pro deduplikaci.
6. **Konstrukční rám a vykreslení podle typu** — axiální/prostorová reference NENÍ
   univerzálně „deska". Plotnové stroje (interiérové, stolní, astronomické) mají
   **desky** (`Platine`/`Doppelplatine`) → Oechslinova elevace mezi deskami. **Věžní
   stroje** mají naopak **rám** — `klecový rám` (birdcage) nebo `flatbed rám` — kola
   jsou uložena v rámových sloupcích/příčníkách. Model proto nese **typ konstrukce**
   (`stroj.konstrukce.typ`) a vrstva C podle něj volí layout: desková elevace
   (Oechslin) vs. rámové schéma. Dále: axiální rozsah hřídele (mezi kterými
   deskami/příčníky vede) a soustředné `Stützrohr` pro souosé výstupy ručiček. Viz
   [docs/oechslin-roegel.md](../docs/oechslin-roegel.md).
