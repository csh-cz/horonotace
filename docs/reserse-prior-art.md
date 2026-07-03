# Rešerše prior-artu: notace pro popis hodinových strojů

> Podklad k návrhu horonotace. Rešerše proběhla ve třech směrech: hodinářská doména
> (web, EN/DE/FR), analogické strojově čitelné notace z jiných oborů, a primární
> literatura v Zotero knihovně ČSH.

## Verdikt

**Formální, strojově čitelná notace pro popis kompletních mechanických hodin
neexistuje.** Existují jen dílčí, vzájemně nepropojené konvence. Jde o reálnou,
neobsazenou mezeru — projekt nekonkuruje zavedenému formalismu, vyplňuje díru.
Žádný akademický článek navrhující formální/ontologickou notaci pro celé strojky
nebyl nalezen; horologické rozšíření CIDOC-CRM neexistuje (potvrzená mezera).

## 1. Co existuje v hodinářské doméně

| Konvence | Co umí | Kde končí |
|---|---|---|
| **Train count** (zuby/leaves, `Z/z`; Hajn 1953 `90—90—80—80 / 14—12—10—10`) | Přesný, počitatelný zápis převodů jdoucího soukolí | Jen aritmetika; každý autor jiné značení; nepokrývá krok/bití/indikace |
| **Beats/hour vzorec** (BHI/Britten/Daniels) | Jediný skutečně kanonický výpočetní artefakt | Výpočet, ne notace |
| **Blokové „skupinové" schéma** (Martínek & Řehoř 1964) | `hnací → soukolí → krok → oscilátor` + ukazovací větev; modulárně i pro bicí/budík/samonatah | Kreslicí konvence, ne kodifikovaná sada značek ani datový formát |
| **Schlagwerk taxonomie** (Schlossscheibe vs. Rechenschlagwerk) | Nejčistší slovník bicích strojů, nese i sémantiku (rack se samočinně koriguje) | Termíny balí chování+mechanismus do jednoho slova → nekomponovatelné |
| **ISO 2203 / ISO 3952** | Standard *kreslení* ozubených kol a kinematických symbolů | Kreslicí norma, ne datový model; bez kroku/bití |
| **ISO 6426 / NIHS / Getty AAT** | Autoritativní termíny; Getty AAT navíc strojově čitelné URI (SKOS/RDF, EN/DE/FR) | Thesaurus, ne model stroje — neřekne, *jak* prvky propojit |
| **Caliber DB** (Ranfft, Grail Watch, 17jewels, PocketWatchDatabase) | ~10–15 společných polí | Próza/HTML, žádné otevřené schéma ani API; Ranfft od 2022 mrtvý |

Astronomické indikace: kvazi-formální jádro je train-count aritmetika —
moon-phase 59zubé kolo (= 2×29,5), pražský orloj tři souosá kola **365 / 366 / 379**
na jednom pastorku (střední sluneční / hvězdný den / střední pohyb Měsíce).
Aproximace poměrů řetězovými zlomky je zavedená *praxe*, ne standard.

## 2. Primární literatura (Zotero ČSH)

Nejblíž formálnímu zápisu jsou jen dva tituly:

- **Martínek & Řehoř 1964, *Základy hodinářství*** (`LXZWE6KE`) — blokové „skupinové"
  schéma toku + algebra převodů `i = (Z₁/z₁)(Z₂/z₂)(Z₃/z₃)`, dělení na I. soukolí
  (krok→minutové kolo) a II. soukolí (hnací→minutový pastorek). **Hlavní předloha
  pro blokovou vrstvu a výpočet převodů.**
- **Hajn 1953, *Základy jemné mechaniky a hodinářství*** (`9MK4QIHS`) — řetězcový
  train-count, teorie záběru.

Vše ostatní (Sušický 1900 `M2MD5J34`, Boukal 1958 `KQVUX5CB`, Dietzschold 1905
`3BFA92ND`, Bassermann-Jordan 1914 `K2ZJJ8PR`) je próza + výpočet + číslované řezy.
Terminologická páteř: **Špatný 1882** (`W6VEJ854`, něm.-čes. slovník — Räderwerk,
Zähnezahl → české ekvivalenty).

## 3. Poučení z analogických notací

Konvergentní doporučení napříč chemií, hudbou, elektronikou a kinematikou:

1. **Dvě/tři vrstvy:** terse lineární forma k psaní (SMILES, ABC, FEN) **i** kanonický
   strukturní model k validaci/výměně (MOL/SDF, MusicXML/MEI). Neslučovat formát,
   který *píšu*, *cituji* a *vykresluji*.
2. **Jeden referenční kanonizátor**, jinak vznikne N dialektů (poučení SMILES vs.
   úspěch jediné implementace InChI).
3. **Graf se smyčkami, ne strom** — soukolí tvoří smyčky; URDF (strom) by selhal.
   Kanonický adjacency kód → test izomorfismu + citovatelné strukturní ID.
4. **Hřídel = sdílený „net", ne hrana** (SPICE: prvek drží terminály, záběr vzniká
   sdílením hřídele). Jeden přirozený datum = pohon/rám (jako SPICE uzel 0).
5. **Vrstvení po typu informace, hlubší vrstvy volitelné** (InChI) — neúplný stroj
   dá validní prefix, který stále sedí na známém soukolí.
6. **Topologie oddělená od kresby** — schéma generovat algoritmicky (Verovio/Mermaid
   model), volitelně dovolit explicitní souřadnice pro historický layout.
7. **Rozšířit existující sadu symbolů** ISO 3952 (linky, klouby, kola, vačky, západky,
   pružiny) — dodělat jen chybějící horologické glyfy (krok, bití).
8. **Povinná uspořádaná hlavička** (PGN Seven Tag Roster) — autor/místo/datace/inv. č.
   oddělené od těla → každý záznam je samostatně citovatelný a napojitelný na katalog.
9. **Citovatelnost přes Wikidata Q-čísla** (Orloj = Q729370) a provenience přes
   **CIDOC-CRM události** (výroba/oprava = `E12`), ne přes vlastní pole.

## 4. Stavební kameny, na nichž horonotace staví

| Potřeba | Nejlepší prior art | Co dodáváme |
|---|---|---|
| Termíny | Špatný 1882, ISO 6426, Getty AAT | Vlastní český slovník (v1), mapování na Getty/Wikidata (později) |
| Topologie soukolí | grafová teorie, train count | Graf prvků + hřídelí + záběrů, počitatelný |
| Funkční dekompozice | blokové schéma Martínek/Řehoř | Vrstva ústrojí + tok/spouštění |
| Bití | Schlagwerk taxonomie | Typovaný prvek `bici-soukoli` + `druh` |
| Citovatelnost | PGN hlavička, Wikidata, CIDOC-CRM | Hlavička stroje, později LOD export |

## Klíčové zdroje (URL)

- Train counting: <http://elgintime.blogspot.com/2013/04/train-counting.html>
- BHI DLC lekce: <https://bhi.co.uk/>
- ISO 2203 (zobrazení kol): <https://www.iso.org/standard/7006.html>
- ISO 3952 (kinematické symboly): <https://www.iso.org/standard/9603.html>
- ISO 6426 (horological vocabulary): <https://www.iso.org/standard/37066.html>
- Getty AAT (krok): <https://vocab.getty.edu/aat/300203656>
- CIDOC-CRM: <https://cidoc-crm.org/>
- Schlagwerk: <https://de.wikipedia.org/wiki/Schlagwerk_(Uhr)>
- Pražský orloj (peer-reviewed simulace): <https://www.mdpi.com/2076-3417/11/9/3989>
- SMILES / InChI / SELFIES; MusicXML / MEI / ABC; SPICE netlist; bond graphs;
  kinematic chain graphs; FEN/PGN; Graphviz DOT / Mermaid / GraphML — viz poučení výše.
