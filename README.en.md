# Horonotace

*[Čeština](README.md) · English*

🔭 **Live gallery:** <https://csh-cz.github.io/horonotace/> · **live editor** (YAML → SVG in the browser): <https://csh-cz.github.io/horonotace/editor.html>

A notation for the schematic description of complete mechanical clock movements — drive,
gear trains, escapement, oscillator, striking work, and indication (display) elements.
The goal is a description that is at once **machine-readable** (suitable for AI work and
databases), **web-renderable** (SVG schematics), and **citable in scholarly text**.

The project is developed in the context of the Czech Horological Society (Český spolek
horologický, ČSH).

## Status

Version **0.1** — draft. The core is a structured data model (layer A, YAML + JSON
Schema). The rendering layers exist as **prototypes**: **C** gear elevation, **D** dial
face, **E** gear front view (wheels as circles). A linear "terse" notation (layer B) is
planned. Overview of the layers: [spec/horonotace-0.1.md](spec/horonotace-0.1.md); the
reviewer-facing specification (Czech): [spec/specifikace.md](spec/specifikace.md), English:
[spec/specification.en.md](spec/specification.en.md).

## Why it exists

A thorough survey ([docs/reserse-prior-art.md](docs/reserse-prior-art.md), in Czech)
showed that **no formal, machine-readable notation for describing complete mechanical
clocks exists**. There are only partial, unconnected conventions: train-count arithmetic,
block "group" schematics (Martínek & Řehoř 1964), German Schlagwerk taxonomy, the ISO
2203/3952 drawing standards, terminological standards (ISO 6426, Getty AAT), and caliber
databases without an open schema. None of them describes a whole movement as a
validatable, renderable, computable graph. Horonotace fills that gap.

## Repository structure

| Path | Contents |
|---|---|
| [spec/specifikace.md](spec/specifikace.md) / [spec/specification.en.md](spec/specification.en.md) | Reviewer-facing specification v0.1 + `spec/specifikace.docx` |
| [spec/horonotace-0.1.md](spec/horonotace-0.1.md) | Technical model — layers, data model, computations |
| [spec/slovnik-typu.md](spec/slovnik-typu.md) | Controlled vocabulary `typ`/`role`/`druh` (cs/en/de) |
| [schema/horonotace.schema.json](schema/horonotace.schema.json) | JSON Schema (draft 2020-12) for validation |
| [examples/](examples/) | Working examples (tower clock, Italian clock, Prague Orloj, Táborský 1570) |
| [tools/](tools/) | Renderers: `render_svg.py` (C), `render_dial.py` (D), `render_front.py` (E), `symboly.py` (symbol sheet) |
| [render/](render/) | Generated SVG schematics and the symbol sheet |
| [docs/](docs/) | Symbols, escapements, striking regulation, Oechslin/Roegel, prior-art survey |

## Scope (v1)

Covers **tower**, **table/wall/longcase** interior movements, and **astronomical clocks /
astronomical dials (orloj)**. Deliberately does not (yet) address pocket/wristwatch
movements or caliber databases.

## Licence

- **Code and schema** (`tools/`, `schema/`): [EUPL-1.2](LICENSES/EUPL-1.2.txt)
- **Documentation, examples, generated schematics** (`docs/`, `spec/`, `examples/`, `render/`, `README.md`): [CC-BY-4.0](LICENSES/CC-BY-4.0.txt)

© David Knespl / Czech Horological Society. The repository is
[REUSE](https://reuse.software/)-compliant (see `REUSE.toml`); see also [LICENSE.md](LICENSE.md).
