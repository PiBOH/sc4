# Developer Guide

This file is the repository's contributor guide. Read it before changing locale archives, translation tooling, documentation, workflows, or the GitHub Pages website.

## Project scope

This repository maintains community localization archives for SimCity 4 Deluxe v1.1.610. It is not the game itself.

The repository's own files are released under the Unlicense in [`LICENSE`](LICENSE). SimCity 4, Maxis, Electronic Arts, the original game data, and related assets remain governed by their own ownership and license terms. Reference EULAs and original support notices are kept under [`Support/`](Support/); never describe the repository Unlicense as a license for the game. A local `Maxis/Support/` mirror is not automatically committed.

## Repository layout

- `Danish/`, `Dutch/`, `Finnish/`, `French/`, `German/`, `Italian/`, `Norwgian/`, `Polish/`, `Portgese/`, `Spanish/`, `Swedish/`: localized DBPF archives.
- `English/`: English comparison reference.
- `UKEnglsh/`: UK English reference archive.
- `Support/`: original support and license reference materials.
- `.tools/translation-tools/locale_tools.py`: dependency-free DBPF/RefPack utility.
- `.tools/version.txt`: release version source.
- `.website/`: English static GitHub Pages site.
- `.github/workflows/`: auto-release and Pages deployment workflows.
- `CHANGELOG.md`: Keep a Changelog project history.
- `.bkp/`, `.ignore/`, and `*.BAK`: local working material; these are ignored and must not be committed.

Root language file lists were intentionally removed because they are not required by the project workflow.

## Translation workflow

1. Work from a clean branch or a clearly documented working tree.
2. Keep the English reference archive unchanged.
3. Create or verify a `.BAK` copy before changing a localized archive.
4. Compare entries by TGI, not by raw text offsets.
5. Change only exact, verified entries. Do not replace broad substrings.
6. Preserve HTML tags, escape sequences, dynamic placeholders, names, URLs, filenames, and technical tokens.
7. Have target-language text reviewed by a fluent speaker when possible. Automated checks cannot certify idiomatic language quality.
8. Reopen the resulting archive and validate every LTEXT resource before replacing the original.
9. Update the changelog with the actual scope and count of changes.

Useful commands:

```bash
python3 .tools/translation-tools/locale_tools.py inspect \
  English/SimCityLocale.dat Italian/SimCityLocale.dat

python3 .tools/translation-tools/locale_tools.py compare \
  English/SimCityLocale.dat Italian/SimCityLocale.dat

python3 -m py_compile .tools/translation-tools/locale_tools.py
```

## DBPF safety requirements

The utility must refuse to repack archives with trailing data, gaps, or overlapping payloads. Any archive rewrite must preserve the TGI list and resource count. Validate RefPack decompression and reopen every generated archive.

Never edit a `.DAT`/`.dat` file with a generic text editor or broad binary replacement tool.

## Website development

The website is deliberately dependency-free and lives entirely in `.website/`:

- HTML pages use `lang="en"`.
- Shared styling belongs in `.website/styles.css`.
- Shared mobile navigation belongs in `.website/script.js`.
- Keep all pages linked through the common navigation.
- Use the existing skip link, visible keyboard focus, and custom 404 pattern.
- Do not place locale archives, `.BAK` files, `.bkp/`, `.ignore/`, or internal tools in `.website/`.

The Pages workflow explicitly copies the website files into `_site`; it does not publish the repository root. If adding a site asset, update `.github/workflows/deploy-pages.yml` and its validation checks.

## Workflows and releases

`auto-release.yml` reads `.tools/version.txt`. A push commit message beginning with `v` triggers the release job; the `v` is not added to the release tag or name. Manual dispatch is also supported.

`deploy-pages.yml` uses the official Pages actions and publishes the `.website/` artifact. Required Pages permissions are `contents: read`, `pages: write`, and `id-token: write`.

Do not use force-pushes. Do not commit generated artifacts, local backups, or secrets.

## Documentation and changelog

Write project documentation in English. Use Keep a Changelog headings and keep entries factual:

- `Added` for new tooling, pages, or workflows;
- `Changed` for updated archives or behavior;
- `Fixed` for corrected defects;
- `Removed` for intentionally removed files such as obsolete root file lists.

When describing licensing, always distinguish the repository's Unlicense from SimCity 4 and Maxis/EA licensing.

## Pre-commit checklist

```bash
git diff --check
python3 -m py_compile .tools/translation-tools/locale_tools.py
git status --short --untracked-files=all
```

Also verify that:

- all DBPF archives reopen successfully;
- `.BAK`, `.bkp/`, and `.ignore/` are not staged;
- the Pages workflow copies only `.website` files;
- site links and pages work after the directory move;
- `README.md`, `DEVGUIDE.md`, and `CHANGELOG.md` are updated when behavior changes.
