# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2026-08-03

### Added

- Italian translation for 1,659 previously missing localization strings,
  covering interface labels, advisor messages, tutorial dialogs, mission text,
  building/vehicle names, and in-game help.
- Translations for short UI terms left in English (e.g. Train, Monorail,
  Subway, Road, Home, Accept).
- Localized version of the sample/error string present only in the English
  locale file.

### Fixed

- Corrected HTML tag loss in a long advisor dialog so all in-game links and
  placeholders render correctly.
- Restored exact preservation of dynamic placeholders (`#city#`, `#Advisor#`,
  `#mission_target#`, `#tuning_constants.*#`) and escape sequences in all
  translated strings.

### Changed

- Rebuilt `SimCityLocale.dat` as a valid DBPF archive with updated resource
  index and offsets.

## [0.0.1] - 2003-08-27

- Initial release with partial localization.

[0.0.2]: https://example.com/compare/0.0.1...0.0.2
[0.0.1]: https://example.com/tag/0.0.1
