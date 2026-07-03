# Horonotace

Notace pro schématický popis celých hodinových strojů — pohonu, soukolí, kroku,
oscilátoru, bicího ústrojí a ukazovacích (indikačních) prvků. Cílem je zápis, který
je zároveň **strojově čitelný** (vhodný pro práci s AI a pro databáze),
**webově vykreslitelný** (SVG schéma) a **citovatelný v odborném textu**.

Projekt vzniká v kontextu Českého spolku horologického (ČSH).

## Stav

Verze **0.1** — návrh. Jádrem je strukturní datový model (vrstva A, YAML + JSON Schema).
Vykreslovací vrstvy existují jako **prototypy**: **C** elevace soukolí, **D** čelní pohled
na číselník, **E** čelní pohled na soukolí (kola jako kružnice). Lineární „terse" zápis
(vrstva B) je plánovaný. Přehled vrstev viz [spec/horonotace-0.1.md](spec/horonotace-0.1.md),
oponentní specifikace k připomínkám viz [spec/specifikace.md](spec/specifikace.md).

## Proč to vzniká

Důkladná rešerše ([docs/reserse-prior-art.md](docs/reserse-prior-art.md)) ukázala, že
**formální, strojově čitelná notace pro popis kompletních mechanických hodin
neexistuje**. Existují jen dílčí, nepropojené konvence: train-count aritmetika,
blokové „skupinové" schéma (Martínek & Řehoř 1964), německá Schlagwerk taxonomie,
kreslicí norma ISO 2203/3952, terminologické standardy (ISO 6426, Getty AAT) a
caliber databáze bez otevřeného schématu. Žádná z nich nepopíše celý stroj jako
validovatelný, vykreslitelný a počitatelný graf. Horonotace tu mezeru vyplňuje.

## Struktura repozitáře

| Cesta | Obsah |
|---|---|
| [spec/specifikace.md](spec/specifikace.md) | Oponentní specifikace v0.1 (k připomínkám) + `spec/specifikace.docx` |
| [spec/horonotace-0.1.md](spec/horonotace-0.1.md) | Technický model — vrstvy, datový model, výpočty |
| [spec/slovnik-typu.md](spec/slovnik-typu.md) | Řízený slovník `typ`/`role`/`druh` (cs/en/de) |
| [schema/horonotace.schema.json](schema/horonotace.schema.json) | JSON Schema (draft 2020-12) pro validaci |
| [examples/](examples/) | Funkční příklady (věžní stroj, italský stroj, orloj, Táborský 1570) |
| [tools/](tools/) | Renderery: `render_svg.py` (C), `render_dial.py` (D), `render_front.py` (E), `symboly.py` (list symbolů) |
| [render/](render/) | Vygenerovaná SVG schémata a list symbolů |
| [docs/](docs/) | Symboly, kroky, regulace bití, Oechslin/Roegel, rešerše |

## Rozsah v1

Pokrývá **věžní**, **stolní/nástěnné/skříňové** a **astronomické hodiny / orloje**.
Záměrně zatím neřeší svět kapesních/náramkových strojků a caliber databází.

## Licence

- **Kód a schéma** (`tools/`, `schema/`): [EUPL-1.2](LICENSES/EUPL-1.2.txt)
- **Dokumentace, příklady a vygenerovaná schémata** (`docs/`, `spec/`, `examples/`, `render/`, `README.md`): [CC-BY-4.0](LICENSES/CC-BY-4.0.txt)

© David Knespl / Český spolek horologický. Repozitář je [REUSE](https://reuse.software/)-kompatibilní
(viz `REUSE.toml`). Autorství: SPDX hlavičky, resp. `REUSE.toml` pro binární/generované soubory.
