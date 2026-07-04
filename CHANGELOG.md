# Changelog

Formát dle [Keep a Changelog](https://keepachangelog.com/cs/1.1.0/);
verzování [SemVer](https://semver.org/lang/cs/).

## [0.1] — 2026-07-03

První veřejné vydání.

### Přidáno
- **Datový model (vrstva A)** — YAML + JSON Schema (draft 2020-12): `prvky`, `hridele`,
  `vazby`, `ustroji`, `konstrukce`; graf se smyčkami, dvě úrovně granularity.
- **Řízený slovník** `typ`/`role`/`druh` (cs/en/de), ukotvený na hodinářský glosář.
- **Renderery**: elevace soukolí (vrstva C, `render_svg.py`), čelní pohled na číselník
  (D, `render_dial.py`), čelní pohled na soukolí — kola jako kružnice (E, `render_front.py`).
- **Sada 48 symbolů komponent** (`symboly.py`): pohon + natahování (klika/čtyřhran/klíček),
  soukolí, **typy krokových kol** (pilové / korunové / kolíčkové / cylindrové) a **typy
  kotev** (vratná / klidová Graham / vřeteno / páková / kolíková paleta / cylindr / detent),
  oscilátory, bicí soukolí + regulace (páky), ukazovací prvky.
- **Číselníky (vrstva D)**: stereografický astroláb (projekce ze severního pólu, obratník
  Raka vnější) a koncentrické stupnice (italské / francouzské hodiny).
- **Příklady**: věžní stroje (jicí + bicí), imaginární italský vřetenový stroj (korunové
  kolo + vřeteno + lihýř), Pražský orloj (astroláb + Táborského historická varianta 1570),
  jednoduchý závažový stroj.
- **Oponentní specifikace** v Markdownu i DOCX (k připomínkám).
- Licencování **EUPL-1.2** (kód, schéma) + **CC-BY-4.0** (dokumentace, příklady, render),
  REUSE 3.0.
- **Anglická verze**: `README.en.md`, `spec/specification.en.md` (+ EN docx), dvojjazyčné
  `description` v JSON Schema. **Lokalizace rendererů** (`--lang=en`, modul `tools/i18n.py`)
  — anglicky olabelovaná sada diagramů (`render/*-en.svg`); přepínače jazyků v README i spec.

### Plánováno
- Vrstva B (lineární „terse" zápis) a kanonizátor.
- Kalkulačka (převody, počet kmitů, drift astronomických indikací, délka chodu).
- Boční panel / integrace akčních členů regulace bití do elevace.
- Mapování slovníku na Getty AAT / Wikidata / CIDOC-CRM.
