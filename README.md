# SimCity 4 multilingual locale archives

Updated `SimCityLocale.dat` archives for **SimCity 4 Deluxe v1.1.610**, with community-maintained translations for the supported game languages.

> This repository contains localization data and maintenance tooling. It does not contain the SimCity 4 game executable or a license to redistribute the game.

## Supported languages

| Folder | Language | Locale file |
| --- | --- | --- |
| `Danish/` | Danish | `SimCityLocale.DAT` |
| `Dutch/` | Dutch | `SimCityLocale.DAT` |
| `Finnish/` | Finnish | `SimCityLocale.DAT` |
| `French/` | French | `SimCityLocale.DAT` |
| `German/` | German | `SimCityLocale.DAT` |
| `Italian/` | Italian | `SimCityLocale.dat` |
| `Norwgian/` | Norwegian | `SimCityLocale.DAT` |
| `Polish/` | Polish | `SimCityLocale.DAT` |
| `Portgese/` | Brazilian Portuguese | `SimCityLocale.DAT` |
| `Spanish/` | Spanish | `SimCityLocale.DAT` |
| `Swedish/` | Swedish | `SimCityLocale.DAT` |
| `English/` | English reference | `SimCityLocale.dat` |
| `UKEnglsh/` | English (UK reference) | `SimCityLocale.DAT` |

The historical folder spellings are retained for compatibility with the original game packages.

## Installation

1. Close SimCity 4.
2. Back up the original locale archive in your game installation.
3. Choose a language folder from this repository.
4. Copy its `SimCityLocale.dat` or `SimCityLocale.DAT` into the corresponding language folder in your SimCity 4 installation.
5. Start the game and select or use the language configuration appropriate for your installation.

Keep the original filename and extension spelling. See the [English installation guide](.website/install.html) for more detail.

## Website

The English static website is stored in [`.website/`](.website/) and includes:

- project overview;
- supported languages and downloads;
- installation instructions;
- DBPF/RefPack tooling notes;
- release history;
- licensing and attribution information;
- a custom 404 page.

The workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml) publishes only the selected files from `.website/`. Locale archives, `.BAK` backups, `.bkp/`, `.ignore/`, and internal tooling are not included in the Pages artifact.

To enable deployment, set **Settings → Pages → Source: GitHub Actions** in the GitHub repository.

## Translation and archive safety

The locale archives use Maxis DBPF resources and RefPack-compressed LTEXT data. The dependency-free Python utility at `.tools/translation-tools/locale_tools.py`:

- compares entries by Type/Group/Instance (TGI) identifiers;
- changes exact verified matches instead of performing broad binary replacements;
- preserves HTML, escape sequences, dynamic placeholders, names, URLs, filenames, and technical identifiers;
- updates LTEXT length fields and DBPF offsets together;
- rejects trailing, gapped, or overlapping payload data before repacking;
- reopens and decodes output resources during validation.

The English archive at `English/SimCityLocale.dat` is the comparison reference and is not modified by the localization process.

## Local validation

Python 3.10 or newer is recommended. No third-party Python packages are required.

```bash
python3 .tools/translation-tools/locale_tools.py inspect \
  English/SimCityLocale.dat Italian/SimCityLocale.dat

python3 .tools/translation-tools/locale_tools.py compare \
  English/SimCityLocale.dat Italian/SimCityLocale.dat
```

The audit performed for this project was conservative and focused on entries changed by the project. It does not replace a complete native-speaker review of every historical sentence in every original archive.

## Backups and ignored files

Working backups are kept beside modified archives with the `.BAK` suffix. Git ignores:

- `*.BAK` files;
- the root `.bkp/` directory;
- the root `.ignore/` directory;
- Python cache directories.

Do not delete these backups until the corresponding archive has been independently verified.

## Licensing and attribution

The repository's own source, documentation, website, and tooling are released under the **Unlicense**, as stated in [`LICENSE`](LICENSE).

That does **not** change the licensing or ownership of SimCity 4. SimCity 4, SimCity 4 Deluxe, Maxis/EA, the game's original localization data, and related trademarks/assets remain subject to their respective rights and terms. The repository includes original support and license reference materials under [`Support/`](Support/), including language-specific EULA files and the original support readme. A local `Maxis/Support/` mirror may exist in a working copy, but it is not part of this commit. These documents are provided for reference and do not grant additional rights to redistribute the game.

## Releases

The version is stored in `.tools/version.txt` (currently `0.0.3-stable`). The workflow [`.github/workflows/auto-release.yml`](.github/workflows/auto-release.yml) validates the archives, creates a clean source ZIP, generates a SHA-256 checksum, and publishes the GitHub Release.

Push commits to `main` whose message starts with `v` to trigger the automatic release job. The `v` is only a trigger marker; it is not included in the release tag or release name. Manual workflow dispatch is also supported.

## Contributing

Read [`DEVGUIDE.md`](DEVGUIDE.md) before changing archives, tooling, workflows, or the website. Keep changes focused, preserve backups, validate DBPF structure, and update `CHANGELOG.md` using the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
