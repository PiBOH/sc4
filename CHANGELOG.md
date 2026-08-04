# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added DBPF/RefPack inspection and repacking utilities in `.tools/translation-tools/locale_tools.py`.
- Added root ignore rules for `.ignore/`, `.bkp/`, and locale backup files with the `.BAK` extension.

### Changed

- Updated the localized `SimCityLocale.DAT` archives for Danish, Dutch, Finnish, French, German, Italian, Norwegian, Polish, Portuguese, Spanish, and Swedish.
- Updated 88 DBPF resources containing exact-match UI labels that were still identical to the English reference; proper names, filenames, URLs, technical tokens, HTML, and dynamic placeholders were preserved.
- Rebuilt the affected DBPF indexes and RefPack payloads without changing untouched resources; this remains a conservative pass and does not claim to translate every ambiguous English-looking proper name or technical term.
- Created and retained a `.BAK` copy beside each modified locale archive before applying changes.
- Performed a conservative wording audit of all entries changed by this project in every non-English archive, including Italian. The context-sensitive “Floating Population” wording was retained rather than replaced by an unverified semantic approximation; this is not a substitute for a complete native-speaker review of every historical archive entry.
- Added a complete project README and a GitHub Actions auto-release workflow driven by `.tools/version.txt`.

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
