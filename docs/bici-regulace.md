# Regulace bití — početník, závěrkové kolo, páky

Bicí soukolí (`soukoli-bici`) jen pohání kladivo přes kolíkové kolo a větrník;
**kolik úhozů** zazní a **kdy se zastaví** řídí samostatná sestava — *regulace bití*.
Notace rozlišuje dva systémy (terminologie dle glosáře `horologicka-terminologie`,
Sladkovský 1947).

Symboly všech členů: [render/symboly.svg](../render/symboly.svg) (kategorie Bicí).

## A — Počitadlové (závěrkové) bití · Schloßscheibe

Členy:

| prvek | `typ` | role |
|---|---|---|
| závěrkové kolo | `zaverka` | disk s nestejnými výřezy (1+2+…+12 = 78) |
| závěrná páka | `zaverna-paka` | nos jede po obvodu; padne do **hlubokého** výřezu → zámek |
| vypouštěcí páka | `vypousteci-paka` | zvedaná kolíkem jicího soukolí → uvolní závěrnou páku |
| kolíkové kolo | `kolo` (`role: kolickove`) | zvedá kladivo |
| větrník, kladivo, cimbál | `vetrnik`, `kladivko`, `cimbal` | |

```yaml
prvky:
  - { id: zaverka, typ: zaverka, druh: pocitadlo, ustroji: bici, pozn: "výřezy 1+2+…+12 = 78" }
  - { id: zaverna, typ: zaverna-paka, ustroji: bici }
  - { id: vypousteci, typ: vypousteci-paka, ustroji: bici }
vazby:
  - { typ: spousteni, z: jdouci, do: vypousteci, pozn: "kolík v celou hodinu zvedne páku" }
  - { typ: spousteni, z: vypousteci, do: zaverna, pozn: "uvolní závěrnou páku → bije" }
  - { typ: blokuje, z: zaverka, do: zaverna, pozn: "výřezy řídí, kdy nos padne = počet úhozů" }
  - { typ: blokuje, z: zaverna, do: bici, pozn: "nos v hlubokém výřezu = zámek" }
```

Vlastnost: závěrka **nemá zpětnou vazbu na ručky** — když se přeskočí úhoz, rozejde
se s časem (nutná ruční korekce).

## B — Rack-and-snail · Rechenschlagwerk

Členy:

| prvek | `typ` | role |
|---|---|---|
| stupnice (snail) | `stupnice` | 12 schůdků na hodinové ose; výška schůdku = počet úhozů |
| početník (rack) | `pocetnik` | ozubené rameno, padne na schůdek stupnice |
| západka početníku | `zapadka-pocetniku` | drží početník proti zpětnému pohybu |
| sběrací palec | `sberaci-palec` | sbírá početník po jednom zubu / úhozu |
| vypouštěcí páka | `vypousteci-paka` | uvolní v celou hodinu |

```yaml
prvky:
  - { id: stupnice, typ: stupnice, ustroji: bici, pozn: "12 schůdků na hodinové ose" }
  - { id: pocetnik, typ: pocetnik, ustroji: bici }
  - { id: zapadka, typ: zapadka-pocetniku, ustroji: bici }
  - { id: palec, typ: sberaci-palec, ustroji: bici }
  - { id: vypousteci, typ: vypousteci-paka, ustroji: bici }
vazby:
  - { typ: spousteni, z: jdouci, do: vypousteci }
  - { typ: spousteni, z: vypousteci, do: pocetnik, pozn: "početník padne na schůdek" }
  - { typ: blokuje, z: stupnice, do: pocetnik, pozn: "výška schůdku = počet zubů = úhozů" }
  - { typ: spousteni, z: palec, do: pocetnik, pozn: "sbírá po jednom zubu / úhozu" }
  - { typ: blokuje, z: pocetnik, do: bici, pozn: "po vyčerpání zubů → zámek" }
```

Vlastnost: rack je **samočinně korekční** — počet úhozů vždy odpovídá poloze stupnice
(tj. hodinové ručky).

## Vazby regulace

- **`spousteni`** — aktuace / uvolnění (kolík → vypouštěcí páka → závěrná páka /
  početník; sběrací palec → početník). V elevaci čárkovaně (akcentně).
- **`blokuje`** — zámek (závěrná páka / početník / závěrka blokuje bicí soukolí).
  Nová hrana ve schématu ([schema](../schema/horonotace.schema.json)).

## Jak se to kreslí v elevaci (implementováno — layout „in-situ")

Klíčové: regulace bití jde do **jednoho** kinematického schématu s jicím
i ukazovacím soukolím, ne zvlášť. Zvolený layout = **in-situ** (každá páka přímo
u svého kola, bez samostatného panelu — mechanicky nejvěrnější):

- Bicí **soukolí** je v elevaci jako schodovité kolo→pastorek (jako jicí).
- **Páky a vačky** (vypouštěcí / závěrná páka, početník, sběrací palec, kladivo,
  cimbál) jsou **volné prvky** — nejsou v žádné `nese`. Renderer každou umístí
  **k jejímu kolu**: kotvu odvodí ze sousedství přes hrany `spousteni`/`blokuje`
  (přednost má soused **na hřídeli** před volným), umístí glyf mírně nad kolo
  a kolize řeší svislým posunem.
- **Hrany** `spousteni` (čárkovaně) a `blokuje` (tečkovaně + značka zámku) se kreslí
  **sjednoceně** přes funkci `pos2()` (poloha prvku = hřídel / volný in-situ / blok →
  první kolo bloku). Tím se propojí jicí soukolí (kolík minutového kola) → vypouštěcí
  páka → závěrná páka → zámek hnacího kola bicího v jednom obrázku.

Ukázka: [examples/vezni-jici-bici.yaml](../examples/vezni-jici-bici.yaml) →
[render/vezni-jici-bici.svg](../render/vezni-jici-bici.svg). Vypouštěcí páka sedí
u minutového kola, závěrná u hnacího kola bicího (dlouhá spojka = reálná táhlová
vazba), kladivo + cimbál u kolíkového kola.

Layout byl vybrán ze čtyř variant (A boční panel s diagonálami, B spodní pás,
C in-situ, D boční panel s ortogonální sběrnicí); zvolena **C**.

Známá omezení: u kolíkového kola se členy (kladivo, cimbál, větrník) shlukují
(daň za in-situ hustotu); volný prvek na hřídeli bez záběru (počitadlo) nedostane
sloupec → jeho hrana `blokuje` se zatím nevykreslí.

## Údržba

Termíny ověřeny v glosáři (Sladkovský 1947: srdcovka, posůvka, stupnice, početník,
západka, základka; Šumavský 1851: zdvihací kolo / Heberad). Pro sporné páky
(sběrací palec, závěrná páka) ověřit u autora / v Zotero — německé ekvivalenty
(Hebedaumen, Sperrhebel, Rechenfanghebel) jsou doplněny jako orientační.
