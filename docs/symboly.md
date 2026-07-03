# Symboly a komponenty (vrstva C)

Schematické značky pro komponenty hodinového stroje. Každá komponenta má **slug**
(= hodnota pole `prvek.typ`), **český termín** (z glosáře skillu
`horologicka-terminologie`) a **glyf**. Vizuální přehledový list:
[render/symboly.svg](../render/symboly.svg) — generuje se z [tools/symboly.py](../tools/symboly.py).

```
python3 tools/symboly.py --sheet render/symboly.svg   # přehledový list
python3 tools/symboly.py --table                       # tato tabulka
```

Slug je ASCII kebab-case; český termín a en/de jsou ukotvené na glosář (prameny
Špatný 1882, Sušický 1900, Sladkovský 1947, Dietzschold 1905). Plné mapování typů
a rolí viz [spec/slovnik-typu.md](../spec/slovnik-typu.md).

## Tabulka podporovaných symbolů

| Symbol (slug) | Komponenta (cs) | en | de | Kategorie |
|---|---|---|---|---|
| `zavazi` | závaží | weight | Gewicht | Pohon |
| `buben` | lanový buben | drum | Trommel | Pohon |
| `perovnik` | perovník | mainspring barrel | Federhaus | Pohon |
| `pero` | péro tažné | mainspring | Zugfeder | Pohon |
| `snek` | závitek / šnek | fusee | Schnecke | Pohon |
| `retizek-snekovy` | řetízek šnekový | fusee chain | Schneckenkette | Pohon |
| `rohatka` | rohatka | ratchet wheel | Sperrad | Pohon |
| `zapadka` | západka | pawl / click | Sperrklinke | Pohon |
| `klika` | natahovací klika | winding crank | Aufzugskurbel | Pohon |
| `natahovaci-ctyrhran` | natahovací čtyřhran | winding square | Aufzugsvierkant | Pohon |
| `klicek` | natahovací klíček | winding key | Aufzugschlüssel | Pohon |
| `kolo` | ozubené kolo | wheel | Zahnrad | Soukolí |
| `pastorek` | pastorek | pinion | Trieb | Soukolí |
| `cevkovy-pastorek` | cévkový pastorek | lantern pinion | Laternengetriebe | Soukolí |
| `krokove-kolo` | krokové kolo (pilové) | escape wheel | Hemmungsrad | Krokové kolo |
| `korunove-kolo` | korunové kolo | crown wheel | Kronrad | Krokové kolo |
| `kolickove-kolo` | kolíčkové krokové kolo | pin escape wheel | Stiftenrad | Krokové kolo |
| `cylindrove-kolo` | cylindrové (válcové) kolo | cylinder escape wheel | Zylinderrad | Krokové kolo |
| `kotva` | kotva vratná | recoil anchor | Ankerrad-Anker | Kotva / krok |
| `kotva-grahamova` | kotva klidová (Graham) | deadbeat anchor | ruhender Anker | Kotva / krok |
| `vreteno` | vřeteno | verge | Spindel | Kotva / krok |
| `kotva-pakova` | kotva páková (volná) | lever | Ankerhebel | Kotva / krok |
| `paleta-kolikova` | paleta kolíková (Amant) | pin pallet | Stiftpalette | Kotva / krok |
| `cylindr` | cylindr (válec) | cylinder | Zylinder | Kotva / krok |
| `detent` | zarážka chronometru | detent | Chronometerdetent | Kotva / krok |
| `paleta` | paleta | pallet | Palette | Kotva / krok |
| `kyvadlo` | kyvadlo | pendulum | Pendel | Oscilátor |
| `lihyr` | lihýř / foliot | foliot | Waag | Oscilátor |
| `setrvacka` | setrvačka | balance | Unruhe | Oscilátor |
| `vlasek` | vlásek | hairspring | Spirale | Oscilátor |
| `zaverka` | závěrka / počitadlo | locking plate / count wheel | Schloßscheibe | Bicí |
| `pocetnik` | početník | rack | Schlagrechen | Bicí |
| `stupnice` | stupnice | snail | Staffel | Bicí |
| `srdcovka` | srdcovka | warning / hoop wheel | Herzscheibe | Bicí |
| `posuvka` | posůvka | lifting cam | Hebenocke | Bicí |
| `vypousteci-kolo` | vypouštěcí kolo | let-off / release | Auslösung | Bicí |
| `vypousteci-paka` | vypouštěcí páka | lifting piece | Auslösehebel | Bicí |
| `zaverna-paka` | závěrná páka | locking lever | Sperrhebel | Bicí |
| `zapadka-pocetniku` | západka početníku | rack hook | Rechenfanghebel | Bicí |
| `sberaci-palec` | sběrací palec | gathering pallet | Hebedaumen | Bicí |
| `vetrnik` | větrník | fly / fan | Windfang | Bicí |
| `kladivko` | kladivo | hammer | Hammer | Bicí |
| `cimbal` | cimbál / zvon | bell | Glocke | Bicí |
| `cifernik` | ciferník | dial | Zifferblatt | Ukazovací |
| `rucka` | ručka | hand | Zeiger | Ukazovací |
| `indikace` | indikace | indication | Anzeige | Ukazovací |
| `remontoir` | remontoár | remontoire | Remontoir | Speciální |
| `udrzbovy-pohon` | údržbový pohon | maintaining power | Erhaltungsantrieb | Speciální |

## Ukázky zápisu

### Pohon přes šnek (fusee) — vyrovnání tahu pera

```yaml
prvky:
  - { id: perovnik, typ: perovnik, ustroji: pohon }
  - { id: snek, typ: snek, ustroji: pohon, pozn: "vyrovnává nestejný tah pera" }
  - { id: retizek, typ: retizek-snekovy, ustroji: pohon }
  - { id: hlavni-kolo, typ: kolo, role: hlavni, ustroji: jdouci, zuby: 64 }
hridele:
  - { id: h-snek, nese: [snek, hlavni-kolo] }     # šnek souosý s hnacím kolem
  - { id: h-perovnik, nese: [perovnik] }
vazby:
  - { typ: pohon, z: perovnik, do: snek, pozn: "řetízek z bubnu na šnek" }
```

### Rack-and-snail bití (početník + stupnice)

```yaml
prvky:
  - { id: pocetnik, typ: pocetnik, ustroji: bici, pozn: "rozeklané rameno, padá na schůdek" }
  - { id: stupnice, typ: stupnice, ustroji: bici, pozn: "12 schůdků, určuje počet úhozů" }
  - { id: srdcovka, typ: srdcovka, ustroji: bici }
  - { id: vetrnik, typ: vetrnik, ustroji: bici }
  - { id: kladivo, typ: kladivko, ustroji: bici }
  - { id: zvon, typ: cimbal, pocet: 1, ustroji: bici }
vazby:
  - { typ: spousteni, z: jdouci, do: bici, pozn: "vypouštění v celou hodinu" }
  - { typ: spousteni, z: stupnice, do: pocetnik, pozn: "rameno padá na schůdek → počet úhozů" }
```

### Remontoár a údržbový pohon (maintaining power)

```yaml
prvky:
  - { id: remontoar, typ: remontoir, ustroji: jdouci, pozn: "pomocné péro napínané hl. pohonem, žene krok stejnoměrně" }
  - { id: udrzba, typ: udrzbovy-pohon, ustroji: pohon, pozn: "Harrison; drží chod během natahování" }
```

## Co se kreslí v elevaci vs. jen v listu

Vrstva C (elevace soukolí, `tools/render_svg.py`) zatím kreslí glyfy pro prvky
**na hřídeli** (kola, pastorky, krokové kolo, kotva, větrník, závěrka/počitadlo,
buben, …). Prvky, které **nesedí na hřídeli** nebo jsou to akční členy (kladivo,
cimbál, početník, stupnice, srdcovka, posůvka, vypouštěcí páka, remontoár), jsou
zatím definované jen jako **symboly v listu** a v modelu — jejich začlenění do
elevace je další krok (typicky jako boční sestava „regulace bití"). Knihovna
symbolů ([tools/symboly.py](../tools/symboly.py)) je sdílená, takže až se zapojí do
elevace, použijí se tytéž glyfy.

## Údržba

Nový symbol = přidat položku do `SYM` v `tools/symboly.py` (slug, cs, en, de,
kategorie, kreslicí funkce) **a** řádek do [spec/slovnik-typu.md](../spec/slovnik-typu.md)
se zdrojem termínu. Pro spornost termínu ověřit v Zotero (Špatný/Sušický/Sladkovský).
