# Kroky (escapements) — typy a komponenty

Notace eviduje **typ kroku** v poli `krok.druh` (řízený slovník). Ve schématech
**nekreslíme samostatné konstrukční obrázky každého kroku** — místo toho krok skládáme
z **komponentních symbolů**: typu **krokového kola** a typu **zachycujícího členu
(kotvy)**. Tyto symboly jsou v listu [render/symboly.svg](../render/symboly.svg)
(kategorie *Krokové kolo* a *Kotva / krok*), generuje [tools/symboly.py](../tools/symboly.py).

Termíny a datace dle glosáře `horologicka-terminologie` (Gros 1913, Saunier 1887,
Dietzschold 1905, Sladkovský 1947).

## Zápis v notaci

Krok = prvek `typ: krok` s polem `druh` + příslušné komponenty:

```yaml
prvky:
  # vřetenový krok (starý věžní / italský stroj)
  - { id: krok,  typ: krok, druh: vretenovy, ustroji: krok }
  - { id: koruna, typ: korunove-kolo, ustroji: krok, zuby: 15 }
  - { id: vreteno, typ: vreteno, ustroji: krok }
  - { id: lihyr, typ: lihyr, ustroji: oscilator }     # foliot
```

Pole `druh` odkazuje na heslo katalogu kroků na webu (`/kroky/<slug>`), takže schéma
stroje se propojí s výkladem daného kroku.

## Komponenty podle druhu kroku (symboly)

| `druh` | krokové kolo (`typ`) | zachycující člen (`typ`) | oscilátor |
|---|---|---|---|
| `vretenovy` | `korunove-kolo` | `vreteno` | `lihyr` / `foliot` |
| `kotvovy` | `krokove-kolo` | `kotva` (vratná) | `kyvadlo` |
| `grahamuv` | `krokove-kolo` | `kotva-grahamova` | `kyvadlo` |
| `amantuv` | `kolickove-kolo` | `paleta-kolikova` | `kyvadlo` |
| `robertuv` | `kolickove-kolo` | `kotva` (středová) | `kyvadlo` |
| `brocotuv` | `krokove-kolo` | `paleta` (achátové) | `kyvadlo` |
| `valeckovy` | `cylindrove-kolo` | `cylindr` | `setrvacka` |
| `chronometrovy` | `krokove-kolo` | `detent` | `setrvacka` |
| `volny-kotvovy` | `krokove-kolo` | `kotva-pakova` | `setrvacka` |
| `hippuv` | `krokove-kolo` | (přerušovač) | `kyvadlo` |

Symboly: krokové kolo — `krokove-kolo` (pilové), `korunove-kolo` (crown), `kolickove-kolo`
(kolíkové), `cylindrove-kolo`; kotva — `kotva` (vratná), `kotva-grahamova` (klidová),
`vreteno`, `kotva-pakova` (páková), `paleta-kolikova`, `cylindr`, `detent`, `paleta`.

## Krokové kolo v kinematické elevaci (vrstva C)

V kinematickém schématu (elevace soukolí) se krokové kolo kreslí jako **úsečka
(roztečná kružnice) jako ostatní kola** (délka ∝ počtu zubů), jen **jemně odlišená na
koncích**:

- **pilový hrot** na koncích — krokové kolo s ozubením (kotvový, Grahamův, Brocotův,
  cylindrový, chronometrový, volný kotvový),
- **tečka (kolík)** na koncích — **kolíčkové kolo** (`amantuv`, `robertuv`).

Nad krokovým kolem se kreslí kotva, pod kolem počet zubů a vpravo **štítek druhu**
(`krok: <cs>`) z `krok.druh`. Krokové kolo tak zapadá do soukolí jako ostatní kola.
Implementace `tools/render_svg.py` (`gear(..., escape="saw"|"pin")`).

## Tabulka hlavních typů

| `druh` | Krok (cs) | en | de | Datace | Konstrukce (klíčový rys) |
|---|---|---|---|---|---|
| `vretenovy` | vřetenový krok | verge | Spindelhemmung | ~13. stol. | korunové kolo + vřeteno se dvěma paletami (~90°) |
| `kotvovy` | kotvový (vratný) krok | recoil anchor | Ankerhemmung | Clement ~1670 | kotva se šikmými paletami, mírný **zpětný pohyb** (recoil) |
| `grahamuv` | Grahamův (klidový) krok | deadbeat | Graham-Hemmung | Graham 1715 | klidové (souosé) plošky palet — **bez zpětného pohybu** |
| `amantuv` | Amantův kolíčkový krok | pin-pallet | Stiftenhemmung | Amant ~1741 | **kolíčkové kolo** (kolíky místo zubů) + úzké palety |
| `robertuv` | Robertův krok | Robert | Älterer Stiftengang | Robert 1852 | kolíčkové kolo + **středová kotva** v jednom kuse s kyvadlem |
| `brocotuv` | Brocotův krok | Brocot | Brocot-Hemmung | Brocot ~1850 | viditelný krok; club zuby (30) + **půlkruhové achátové palety** |
| `valeckovy` | válečkový / cylindrový | cylinder | Zylinderhemmung | Graham ~1720 | dutý **cylindr** na hřídeli setrvačky; zuby na nožkách |
| `chronometrovy` | chronometrový krok | detent | Chronometerhemmung | Earnshaw ~1780 | **detent** (pružná zarážka), impuls jen v jednom směru kyvu |
| `volny-kotvovy` | volný kotvový (pákový) | detached lever | freie Ankerhemmung | Mudge 1759 | **vidlička** oddělená od setrvačky vyjma impulsu; club zuby |
| `hippuv` | Hippův přerušovač | Hipp toggle | Hipp-Hemmung | Hipp 1843 | elektromechanický; kyvadlo + **přerušovač** + cívka |

## Poznámky ke konstrukci (z glosáře)

- **vřetenový** — nejstarší; vertikální vřeteno se dvěma „vlajkami" zachycuje korunové
  kolo. U věžních hodin a kapesních cibulí do počátku 19. stol.
- **kotvový vs. Grahamův** — oba mají kotvu nad krokovým kolem; rozdíl je v tvaru
  palety: vratný (recoil) tlačí kolo zpět, klidový (deadbeat, soustředné plošky) ne.
- **Amantův / Robertův** — kolíčkové kolo (Stiftengang). Robert přidává středovou kotvu
  jednolitou s kyvadlem; v Čechách výhradně Jan Prokeš ze Sobotky (od 1868).
- **Brocotův** — „viditelný krok" francouzských pendule de Paris; palety z achátu.
- **cylindrový** — klidový krok kapesních hodinek 18. stol.; dutý cylindr na ose setrvačky.
- **chronometrový** — nejpřesnější (lodní chronometry); detent drží kolo, impuls jen
  jedním směrem.
- **volný kotvový (pákový)** — standard moderních hodinek; vidlička je „volná" mezi impulsy.
- **Hippův** — elektromechanický (master-clock); kyvadlo má vlastní pohon přes elektromagnet.

Plný výklad viz glosář `horologicka-terminologie/reference/glosar.yaml` a
`spec/slovnik-typu.md`.

## Údržba

Nový typ krokového kola nebo kotvy = přidat glyf a položku do `SYM` v
[tools/symboly.py](../tools/symboly.py) (kategorie *Krokové kolo* / *Kotva / krok*) a
řádek do mapovací tabulky výše + do `spec/slovnik-typu.md`. Pro spornost ověřit
v Zotero (Gros 1913, Saunier 1887, Dietzschold 1905).
