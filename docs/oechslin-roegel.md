# Oechslin & Roegel — metoda zápisu astronomických soukolí

> Doplněk k [reserse-prior-art.md](reserse-prior-art.md). Cílené prověření notace,
> kterou ve svých knihách používá **Ludwig Oechslin** (kurátor MIH La Chaux-de-Fonds,
> Ulysse Nardin Trilogy of Time / Freak, Ochs und Junior).

## Co Oechslinova „notace" je — a co není

**Není** uzavřený symbolický formalismus s vlastní gramatikou. **Je** to dvojice
provázaných věcí:

1. **Dokumentační disciplína** — kompletní train-count (`kolo/pastorek` se zuby) →
   **exaktní racionální poměr** (zlomek, ne desetinné číslo) → **porovnání se
   skutečnou astronomickou periodou** (tropický rok, synodický/drakonický měsíc,
   siderický den) → **chyba aproximace a drift** (za kolik staletí rozejití o 1 den).
2. **Návrhová metoda** — aproximace racionálních poměrů (= metoda řetězových zlomků),
   hledání *syntetického* řešení: jediné (často epicyklické) soukolí pro víc indikací
   s minimem dílů (např. fáze Měsíce přesná na 3478 let z 5 dílů vč. ciferníku).

## Moderní strojová formalizace — Denis Roegel

**Denis Roegel** (LORIA Nancy; kapitola o astronomických hodinách v *General History
of Horology*, OUP 2022) formalizoval Oechslinova data v companionu
*roegel2025oechslin* — <https://roegeld.github.io/oechslin/> (32 PDF kapitol, v0.18,
říjen 2025). **Pozor: Roegel explicitně zakazuje zrcadlení/indexaci textu (jen osobní
studium).**

Notační konvence (přesně vzor pro naši astronomickou vrstvu):

```
V_out  = V_in × ∏(z_hnaný / z_hnací)          řetězec záběrů (poměr úhl. rychlostí)
V_abs  = V_rel + V_carrier                      epicyklické soukolí (superpozice)
P_<i>  = exaktní zlomek  +  rozklad na h/m/s    perioda hřídele/indikace
```

- `V<index>` = poměr úhlové rychlosti hřídele / trubky / rámu; **znaménko** = smysl
  otáčení.
- **Horní index (prime)** = vztažná soustava — nezbytné pro epicyklika (relativně
  k unášeči vs. absolutně).
- `P<index>` = perioda jako **exaktní zlomek** + desetinný rozklad na h/m/s.

Reprodukovaný příklad (Kleinovy geografické hodiny, Praha ~1732, z Roegelovy kapitoly):

```
V10' = −2                                  (trubka 10: otáčka za 12 h)
V11' = V10' × (36/72) = 1                  (arbor 11: otáčka za den)
V14' = V11' × (1/5) × (1/73) = 1/365       (P = 365 dní)
ekliptika (siderický den):
V9'  = V20' × (366/365)
P9'  = −365/366 = −23 h 56 m 3,9344… s
```

## Grafická notace (tabule v Priestermechaniker)

Oechslin v *Priestermechaniker* (1996) doprovází text **velkoformátovými tabulemi**
se schématickým zápisem celého soukolí (z fotografií knihy — světový stroj typu
Hahn: planetárium, soustavy měsíců Jupitera a Saturna, Sonne/Mond Tages- i
Jahressystem). Princip notace:

- **Vodorovné linky = desky stroje** (`Platine`, `Doppelplatine`), kreslené nad
  sebou jako základní roviny; prostor mezi dvěma deskami = úroveň, kde sedí kola.
- **Svislé linky = hřídele/osy** (arbory) kolmo mezi deskami.
- **Číslo v pravoúhlé závorce (⌐) na svislici = kolo/pastorek** s daným počtem zubů
  v dané axiální výšce. **Více závorek nad sebou na téže svislici = souosá kola na
  jedné hřídeli** — přesně náš sdílený *net*.
- **Záběr** = kola na sousedních svislicích ve stejné výšce spojená vodorovně.
- **Výstupy = pojmenované indikace** (`Sonne`, `Mond`, `Merkur`…`Uranus`, měsíce
  planet `1.–5. Mond`, `Mondknoten` = uzly Měsíce, `Mond Apsidenlinie` = přímka
  apsid, `Ekliptik`). Souosé výstupy (více ručiček na jedné ose) přes soustředné
  trubky — `Stützrohr` (opěrná trubka), `Brücke` (můstek).
- **Dvojí číslování:** *kurzivní* větší čísla u indikací = pořadové číslo dílu
  (Bauteil-Nr., odpovídá Roegelovu `V<index>`); *drobná čísla v závorkách* = počty
  zubů (Zähnezahl).
- **Funkční dekompozice:** každý podsystém má vlastní titulek —
  `Planetarium heliozentrisch`, `Sonne/Mond Jahressystem`, `Sonne/Mond Tagessystem`,
  `Saturn Mondsystem`, `Jupiter Mondsystem`, `24-Stunden mit Bahnausgleich`.

Jde o **schematickou „elevaci"/řez stohem kol mezi deskami**: svislá osa = axiální
stohování, vodorovná = sousedství/záběr; abstraktní kinematické schéma, ne měřítkový
výkres. **To je cílová podoba naší vrstvy C** a zároveň silné potvrzení vrstvy A:
Oechslinova svislice = naše `hridel`, závorka = `prvek` se `zuby`, vodorovné spojení
= `zaber`, pojmenovaný výstup = indikace, titulkovaný blok = `ustroji`.

Mapování:

| Oechslin (grafika) | horonotace (vrstva A) |
|---|---|
| Svislice (osa) | `hridel` |
| Závorka s počtem zubů | `prvek` `kolo`/`pastorek` + `zuby` |
| Závorky nad sebou | prvky sdílející jednu `hridel` |
| Vodorovné spojení kol | `vazba` `zaber` |
| Pojmenovaný výstup | `prvek` `indikace`/`rucka` |
| Titulkovaný podsystém | `ustroji`/`komplikace` |
| Kurzivní díl-číslo | `id` prvku |

**Převzít navíc do modelu:** **typ konstrukce** (`stroj.konstrukce.typ`); **axiální
rozsah hřídele**; **soustředné trubky** (`Stützrohr`) pro souosé vícenásobné výstupy
ručiček.

> **Pozor — platí pro plotnové stroje.** Oechslinova elevace mezi deskami je vázaná
> na **interiérové/astronomické stroje s plotnami** (`Platine`/`Doppelplatine`).
> **Věžní stroje** mají místo ploten **rám** — `klecový rám` (birdcage) nebo
> `flatbed rám` — a kola jsou uložena v rámových sloupcích/příčníkách. Abstraktní
> graf (hřídele + záběry) je týž, ale **vrstva C podle `stroj.konstrukce.typ` volí
> jiný layout**: desková elevace vs. rámové schéma. Desky tedy nejsou univerzální
> referencí, jen jednou z konstrukčních variant.

## Dopad na horonotace

| Co převzít | Jak |
|---|---|
| Poměry jako **exaktní zlomky**, ne desetinná čísla | `perioda` a převody ukládat racionálně (čitatel/jmenovatel) |
| **Astronomický cíl + chyba** | u indikace volitelné pole `cil` (cílová perioda) + dopočtená `chyba`/`drift` |
| **Epicyklika: vztažná soustava** | model umožní unášeč (`carrier`) a relativní vs. absolutní rychlost; `V_abs = V_rel + V_carrier` |
| **Znaménko = smysl otáčení** | u period/převodů evidovat orientaci |

**Limity (stejné narazíme i my):** Oechslin/Roegel řeší *jen* kinematiku převodů a
indikací — ne krok, pohon ani bití (to náš model pokrývá navíc). Nelineární indikace
(excentrická kola, vačky, eliptická soukolí) jsou i u Oechslina **mimo čistou
zlomkovou notaci** — nejtěžší část, řešit později.

## Zdroje

- Oechslin, *Astronomische Uhren und Welt-Modelle der Priestermechaniker im 18. Jh.*
  (1996, Antoine Simonin, Neuchâtel; Habilitace ETH) — Zotero `L7VJGYCT` (bez PDF).
  **Hlavní nositel metody.** Sv. II = tooth-counts a převody „přes stránky vzorců".
- Oechslin, *Die Farnesianische Uhr* (1982, Bibl. Apostolica Vaticana, Studi e testi
  300–302) — disertace, ~462 dílů.
- Patent astronomických hodinek UN (Oechslin/Giger/Spöring) — Zotero `JCYTW4XB`
  (jen abstrakt).
- Roegel, companion 2025 — <https://roegeld.github.io/oechslin/> (necitovat veřejně).
- Recenze: Mueller-Maerki (NAWCC), <https://mb.nawcc.org/threads/rewiew-oechslin-priestermechaniker-1996-repost.9033/>
- Knespl, *Ochs und Junior: Důsledná jednoduchost* (2014) — Zotero `3U6FBYFX`.
