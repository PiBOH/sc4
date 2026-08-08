# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `CONTRIBUTING.md`, an English contributor guide covering archive safety, website maintenance, workflows, documentation, and licensing boundaries.
- Added the English static website under `.website/` with language, installation, tools, releases, licensing, and 404 pages.
- Added a Pages deployment workflow that publishes only the selected `.website/` files.
- Added DBPF/RefPack inspection and repacking utilities in `.tools/translation-tools/locale_tools.py`.
- Added root ignore rules for `.ignore/`, `.bkp/`, and locale backup files with the `.BAK` extension.
- Documented the existing `Support/` EULA and support reference materials, which remain subject to the game's original licensing terms.
- Documented the Semantic Versioning 2.0.0 convention while preserving the existing `.tools/version.txt` format (`0.0.3-stable`).
- Added per-language locale ZIPs as release assets (`Danish.zip`, `Italian.zip`, …), each with a SHA-256 checksum, so users can download a single language without cloning the repository.
- Added direct download links for every language ZIP on the website languages page, including English and UK English reference archives.
- Improved automated release notes to include a file-change summary from the previous tag when a version section is not yet present in the changelog.
- Redesigned the website to match the NirSoft aesthetic: Arial font, white background, minimal header with pipe-separated text links, no decorative boxes, standard browser link colors, plain tables.
- Added restrained old-web colors to the existing site structure: pale blue sidebar/header/footer backgrounds, dark blue headings, and a light blue table header without changing the layout.
- Documented archive compatibility up to SimCity 4 v1.1.641 across README, developer guide, website, and Jekyll config.
- Added a `Plugins/` folder with plugins tested and working with SimCity 4 Deluxe Edition: SC4 Disable FPS Limits v0.2.3 and the SimCity 4 Extra Cheats Plugin.
- Added a Plugins page to the website with plugin descriptions, installation instructions (including the explicit `%USERPROFILE%\Documents\SimCity 4\Plugins` destination), licensing notes, and a direct download link, noting that the Extra Cheats Plugin is optional but highly recommended on SimCity 4 versions prior to v1.1.641.
- Added `Plugins.zip` with its SHA-256 checksum as a release asset alongside the per-language ZIPs.
- Redesigned the website with the Jarock catalogue style: centered column with subtle shadow, serif headings, header brand block, top navigation bar, boxed sidebar with notes, breadcrumbs, catalog tables with captions, status chips, download boxes, and notice boxes.
- Added a small `script.js` for the responsive mobile menu toggle.

### Changed

- Updated the localized `SimCityLocale.DAT` archives for Danish, Dutch, Finnish, French, German, Italian, Norwegian, Polish, Portuguese, Spanish, and Swedish.
- Updated 88 DBPF resources containing exact-match UI labels that were still identical to the English reference; proper names, filenames, URLs, technical tokens, HTML, and dynamic placeholders were preserved.
- Rebuilt the affected DBPF indexes and RefPack payloads without changing untouched resources; this remains a conservative pass and does not claim to translate every ambiguous English-looking proper name or technical term.
- Created and retained a `.BAK` copy beside each modified locale archive before applying changes.
- Performed a conservative wording audit of all entries changed by this project in every non-English archive, including Italian. The context-sensitive “Floating Population” wording was retained rather than replaced by an unverified semantic approximation; this is not a substitute for a complete native-speaker review of every historical archive entry.
- Added a complete project README and a GitHub Actions auto-release workflow driven by `.tools/version.txt`.
- Moved the static GitHub Pages site from the repository root into `.website/` and simplified its styling to a plain, no-framework design.
- Updated `.github/workflows/deploy-pages.yml` to publish only the selected `.website/` files (now including `script.js`), excluding locale archives, backups, and private tool directories.
- Replaced the NirSoft-inspired flat layout with the Jarock catalogue design across every site page.
- Recreated and expanded `README.md` with the website, contributor guide, and the distinction between the repository Unlicense and SimCity 4/Maxis/EA licensing.

### Removed

- Removed obsolete root language file lists that are not required by the project workflow.

## [0.0.2] - 2026-08-03

### Added (`Italian/SimCityLocale.dat`)

- Italian translation for 1,659 previously missing localization strings,
  covering interface labels, advisor messages, tutorial dialogs, mission text,
  building/vehicle names, and in-game help.
- Translations for short UI terms left in English (e.g. Train, Monorail,
  Subway, Road, Home, Accept).
- Localized version of the sample/error string present only in the English
  locale file.

### Fixed (`Italian/SimCityLocale.dat`)

- Corrected HTML tag loss in a long advisor dialog so all in-game links and
  placeholders render correctly.
- Restored exact preservation of dynamic placeholders (`#city#`, `#Advisor#`,
  `#mission_target#`, `#tuning_constants.*#`) and escape sequences in all
  translated strings.

### Changed (`Italian/SimCityLocale.dat`)

- Rebuilt `SimCityLocale.dat` as a valid DBPF archive with updated resource
  index and offsets.

## [0.0.1] - 2003-08-27

- Initial release with partial localization.

[0.0.2]: https://example.com/compare/0.0.1...0.0.2
[0.0.1]: https://example.com/tag/0.0.1
