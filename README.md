# SimCity 4 multilingual locale archives

Updated `SimCityLocale.dat` archives for **SimCity 4 Deluxe v1.1.610**, with translations for the supported game languages.

> This repository contains localization data, not the game itself. SimCity 4 and its original localization files remain the property of their respective rights holders.

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

The folder names reflect the original SimCity 4 installation/package names and are intentionally retained.

## Installation

1. Close SimCity 4.
2. Make a backup of the original locale archive in your game installation.
3. Choose the language folder you want.
4. Copy its `SimCityLocale.dat` or `SimCityLocale.DAT` into the corresponding language folder in your SimCity 4 installation, replacing the original file.
5. Start the game and select/use that language as appropriate for your installation.

Keep the archive extension and filename spelling exactly as supplied. Windows filesystems are usually case-insensitive, but the original game package names are preserved for compatibility.

## What is included

- Updated DBPF locale archives.
- `.tools/translation-tools/locale_tools.py`, a small dependency-free Python utility for inspecting, comparing, extracting, validating, and safely repacking the archives.
- Per-language file lists, readmes, EULAs, and fonts from the original localization package.
- `CHANGELOG.md` with the project history.

## Translation and archive safety

The locale archives use Maxis DBPF resources and RefPack-compressed LTEXT data. The translation utility:

- compares entries by their Type/Group/Instance (TGI) identifiers;
- changes exact matching text only, rather than performing broad binary replacements;
- preserves HTML, escape sequences, dynamic placeholders, names, URLs, filenames, and technical identifiers;
- updates the LTEXT length field and DBPF offsets when a string changes;
- rejects archives with trailing, gapped, or overlapping payload data before repacking;
- validates the resulting archive by reopening it and decoding its LTEXT resources.

The English archive at `English/SimCityLocale.dat` is the comparison reference. The English reference files are not modified by the localization process.

## Local validation

Python 3.10 or newer is recommended. No third-party Python packages are required.

Inspect archives:

```bash
python3 .tools/translation-tools/locale_tools.py inspect \
  English/SimCityLocale.dat Italian/SimCityLocale.dat
```

Compare a language with the English reference:

```bash
python3 .tools/translation-tools/locale_tools.py compare \
  English/SimCityLocale.dat Italian/SimCityLocale.dat
```

The tool also supports extraction and conservative translation candidates. The project audit checked all entries changed by this project; it does not claim to replace a complete native-speaker review of every historical sentence in the original archives. Any archive rewrite should be performed on a copy first and validated before replacement.

## Backups and ignored files

Working backups are kept beside modified archives with the `.BAK` suffix. The following are intentionally ignored by Git:

- `.BAK` files;
- the root `.bkp/` directory;
- the root `.ignore/` directory;
- Python cache directories.

Do not delete these backups unless you have independently verified the corresponding archive.

## Releases

The release version is stored in `.tools/version.txt` (currently `0.0.3-stable`). The GitHub Actions workflow at `.github/workflows/auto-release.yml` can create a GitHub Release from that version and attach a clean source ZIP containing tracked project files.

The workflow runs automatically on pushes to `main` only when the commit message starts with `v`; the `v` is only the trigger marker and is not included in the release tag or name. The workflow can also be started manually from the **Actions** tab. Versions ending in `-stable` are published as stable releases; other suffixes are marked as prereleases.

## License

The repository's original project content is released under the terms in [`LICENSE`](LICENSE). SimCity 4 remains a trademark and copyrighted product of its respective owners.
