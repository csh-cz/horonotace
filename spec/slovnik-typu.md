# Řízený slovník typů a rolí (horonotace)

Kontrolovaný slovník hodnot `prvek.typ`, `prvek.role` a dalších enumerací notace,
**ukotvený na hodinářský glosář** skillu `horologicka-terminologie`
(`reference/glosar.yaml`, cs/en/de/fr). Cíl: stabilní, jednoznačné slugy navázané
na zavedenou českou terminologii (Špatný 1882, Sušický 1900, Sladkovský 1947,
Dietzschold 1905), aby se notace nemusela přepisovat při růstu.

Slug = ASCII kebab-case (bez diakritiky). Český termín = preferovaný tvar z glosáře.

## 1. Pohon (`pohon`, `pohon-b`, …)

| `typ` | cs (glosář) | en | de | poznámka |
|---|---|---|---|---|
| `zavazi` | závaží | weight | Gewicht | tažné závaží |
| `buben` | buben (lanový / řetězový) | drum / barrel | Trommel | pole `prumer`, `otacky`, `lano` |
| `pero` | péro tažné / pohonná zpruha | mainspring | Zugfeder | |
| `perovnik` | perovník | mainspring barrel | Federhaus | var. *bubínek pérový* (Sušický) |
| `snek` / `zavitek` | závitek / šnek | fusee | Schnecke | vyrovnává tah pera; POZOR: „šnek" = i šnekový převod (níže) |
| `retizek-snekovy` | řetízek šnekový | fusee chain | Schneckenkette | |
| `rohatka` | rohatka | ratchet wheel | Sperrad | s západkou drží nátah |
| `zapadka` | západka | pawl / click | Sperrklinke | var. *základka* (Sušický) |
| `klika` | natahovací klika | winding crank | Aufzugskurbel | klika na čtyřhranu, natahuje závaží |
| `natahovaci-ctyrhran` | natahovací čtyřhran | winding square | Aufzugsvierkant | čtyřhran na natahovacím čepu |
| `klicek` | natahovací klíček | winding key | Aufzugschlüssel | pružinové/menší stroje |

Natahování: v elevaci se na hnacím (natahovacím) čepu kreslí čtyřhran + klika
a rohatka se západkou (drží nátah). Pro pružinové stroje `klicek` místo `klika`.

## 2. Soukolí — kola a pastorky (`kolo`, `pastorek`)

`typ: kolo` + `role:` udává funkci kola. Role jsou z glosáře (Sušický/Sladkovský):

| `role` | cs (glosář) | en | de | poznámka |
|---|---|---|---|---|
| `hlavni` | hlavní / hnací kolo | great wheel | Grundrad | u věžních na hřídeli bubnu |
| `spodni` | kolo spodní / hřídelové | barrel wheel | Federhausrad | synonymum hlavního na perovníku |
| `minutove` | kolo minutové | center wheel | Minutenrad | 1 ot./h, nese minutovou ručku |
| `mezitimni` | kolo mezitimní | third wheel | Zwischenrad | var. *mezilehlé* |
| `sekundove` | kolo sekundové / vteřinové | fourth wheel | Sekundenrad | nese vteřinovou ručku |
| `kolickove` | kolíčkové kolo | pin wheel | Stiftenrad | krokové n. bicí (zvedá kladivo) |
| `stridne` | kolo střídné | minute wheel (kvadratura) | Wechselrad | v převodu ručiček 12:1 |
| `hodinove` | kolo hodinové | hour wheel | Stundenrad | nese hodinovou ručku |

| `typ` | cs | en | de | poznámka |
|---|---|---|---|---|
| `pastorek` | pastorek | pinion | Trieb | `zuby` = počet ceví/listů |
| `cevkovy-pastorek` | cévkový pastorek | lantern pinion | Laternengetriebe | tradiční u věžních |

**Role indikačních / astronomických kol** (u orlojů a astronomických strojů; `role` je
volný string, tabulka pojmenovává doložené hodnoty):

| `role` | cs | poznámka |
|---|---|---|
| `ekliptika` | kolo ekliptiky / zvěrokruhu | nese zvěrokruh, 1 ot./hvězdný (siderický) den |
| `slunce` | sluneční kolo | pohon sluneční ručky, 1 ot./24 h |
| `mesic` | měsíční kolo | pohon měsíční ručky / fáze |
| `venec` | věnec (vnitřní ozubení) | prstencové kolo, např. koule fáze Měsíce |
| `kalendar` | kalendářní kolo | 1 ot./rok (365/366) |
| `hvezdny` / `slunecni` / `mesicni` | (siderický / solární / lunární běh) | rozlišení period souosých kol astrolábu (365/366/379) |

## 3. Krok (`krok`) — `druh:`

Slug `druh` u kroku odkazuje na katalog `/kroky/<slug>`. Krok se ve schématech skládá
z **komponentních symbolů** (typ krokového kola + typ kotvy), ne ze samostatných
obrázků každého kroku — mapování druh → komponenty viz [docs/kroky.md](../docs/kroky.md).
Z glosáře:

| `druh` | cs (glosář) | en | de |
|---|---|---|---|
| `vretenovy` | vřetenový krok | verge | Spindelhemmung |
| `kotvovy` | kotvový (vratný) krok | anchor / recoil | Ankerhemmung |
| `grahamuv` | Grahamův krok | deadbeat | ruhende Hemmung |
| `amantuv` | Amantův krok | pin-pallet (Amant) | Stiftenhemmung Amant |
| `robertuv` | Robertův krok | Robert | Älterer Stiftengang |
| `brocotuv` | Brocotův krok | Brocot | Brocot-Hemmung |
| `valeckovy` | válečkový / cylindrový | cylinder | Zylinderhemmung |
| `chronometrovy` | chronometrový krok | chronometer / detent | Chronometerhemmung |
| `volny-kotvovy` | volný kotvový (pákový) krok | detached lever | freie Ankerhemmung |
| `hippuv` | Hippův přerušovač | Hipp toggle | Hipp-Hemmung |

Součásti kroku — **typy krokových kol**: `krokove-kolo` (pilové, Hemmungsrad),
`korunove-kolo` (crown / Kronrad — vřetenový krok s lihýřem), `kolickove-kolo`
(pin / Stiftenrad — Amant), `cylindrove-kolo` (cylinder / Zylinderrad).
**Typy kotev / zachycujících členů**: `kotva` (vratná / recoil), `kotva-grahamova`
(klidová / deadbeat), `vreteno` (verge / Spindel), `kotva-pakova` (páková / lever),
`paleta-kolikova` (pin pallet / Amant), `cylindr` (cylinder), `detent` (chronometr),
`paleta` (pallet; `paleta-vstupni`, `paleta-vystupni`). Mapování na `druh` viz docs/kroky.md.

## 4. Oscilátor (`oscilator`)

| `typ` | cs | en | de | poznámka |
|---|---|---|---|---|
| `kyvadlo` | kyvadlo | pendulum | Pendel | `perioda`, `kompenzace` (roštové/rtuťové/invarové) |
| `lihyr` / `foliot` | lihýř / foliot | foliot | Waag | předkyvadlový vyvažovač |
| `setrvacka` | setrvačka | balance | Unruhe | NE „balanc" jako primární |
| `vlasek` | vlásek | hairspring | Spirale | |

## 5. Bicí soukolí (`bici`) — Sladkovský 1947

| `typ` | cs (glosář) | en | de | poznámka |
|---|---|---|---|---|
| `zaverka` | závěrka | locking plate | Schloßscheibe | počitadlové bití |
| `pocitadlo` | počitadlo / početník | count wheel | Zählrad | ~synonymum závěrky |
| `pocetnik` | početník (rack) | rack | Schlagrechen | rack-and-snail bití |
| `stupnice` | stupnice | snail | Staffel | 12 schůdků, určuje počet úhozů |
| `srdcovka` | srdcovka | warning / hoop wheel | Herzscheibe | zastaví bicí stroj |
| `posuvka` | posůvka | lifting cam | Hebenocke | posune početník o zub |
| `vypousteci-kolo` | vypouštěcí kolo / vypouštění | let-off / release | Auslösung | uvolní bicí v celou hodinu |
| `vypousteci-paka` | vypouštěcí páka | lifting piece | Auslösehebel | zvedaná kolíkem jicího soukolí → uvolní zámek |
| `zaverna-paka` | závěrná páka | locking lever | Sperrhebel | nos padá do výřezu závěrky = zámek |
| `zapadka-pocetniku` | západka početníku | rack hook | Rechenfanghebel | drží početník proti zpětnému pohybu |
| `sberaci-palec` | sběrací palec | gathering pallet | Hebedaumen | sbírá početník po jednom zubu / úhozu |
| `vetrnik` | větrník | fly / fan | Windfang | vzdušná brzda rychlosti |

Hrany regulace bití: `spousteni` (uvolnění/aktuace, např. vypouštěcí páka → závěrná
páka), `blokuje` (zámek — závěrná páka / početník blokuje bicí soukolí).
| `kladivko` | kladivo | hammer | Hammer | |
| `cimbal` / `zvon` | cimbál / zvon | bell / gong | Glocke | `pocet` = počet |

> **Aliasy → kanonický slug:** `rechen` → **`pocetnik`**, `staffel` → **`stupnice`**
> (dřívější německé slugy nahrazeny českými z glosáře).

## 6. Ukazovací ústrojí a indikace (`ukazovaci`, `komplikace`)

| `typ` | cs | en | de | poznámka |
|---|---|---|---|---|
| `cifernik` | ciferník | dial | Zifferblatt | |
| `rucka` | ručka / ručička | hand | Zeiger | `ukazuje:` hodiny/minuty/… |
| `soukoli-rucek` | kvadratura (převod ručiček) | motion work | Wechselgetriebe | 12:1 |
| `indikace` | indikace | indication | Anzeige | `druh:` viz níže |

Hodnoty `indikace.druh` (řízené, rozšiřitelné): `kalendar`, `lunace`, `faze-mesice`,
`astrolab`, `tellurium`, `planetarium`, `equation` (rovnice času), `zverokruh`,
`staroceske-hodiny`, `italske-hodiny`, `francouzske-hodiny`, `automat` (pohyblivé figury).

## 7. Konstrukce (`stroj.konstrukce.typ`)

| `typ` | cs (glosář) | en | de |
|---|---|---|---|
| `desky` | plotny / desky | plates | Platinen |
| `klecovy-ram` | klecový rám | birdcage / posted frame | Vogelkäfig-Gestell |
| `flatbed-ram` | flatbed rám | flatbed frame | Flachbett-Gestell |

## Zdroj a údržba

Kanonické termíny pocházejí z `horologicka-terminologie/reference/glosar.yaml`.
Při sporu o termín ověřit v Zotero (Špatný 1882 `W6VEJ854`, Sušický 1900 `M2MD5J34`,
Sladkovský 1947 `VIBRCUZT`, Dietzschold 1905 `3BFA92ND`) — ne na retailových webech.
Nové typy přidávat sem **i** s cs/en/de a zdrojem.
