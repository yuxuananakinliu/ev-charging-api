# Changelog
All notable changes to this project will be documented here.

This project adheres to [Semantic Versioning](https://semver.org/) and follows the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

## [Unreleased]

## [0.2.0] - 2025-09-07
### Added
- Public deployment:
  - **API (Render):** `https://ev-charging-api-2djx.onrender.com`
  - **Docs:** `https://ev-charging-api-2djx.onrender.com/docs`
  - **UI (Netlify):** `https://ev-charger-api.netlify.app`
- README overhaul with API reference and run/deploy instructions.

### Changed
- `/stations` response fields standardized:
  - SQL aliases `station_id → id`, `station_name → name` to match the OpenAPI schema.
- UI polish: sidebar toggle fixed as floating control; clustering and list formatting improved.

### Fixed
- **ResponseValidationError** on Render caused by `id/name` mismatch.
- Spurious `GET /stations/undefined` (422) from UI by guarding detail fetch on missing IDs.
- CORS/config edges for production.

## [0.1.0] - 2025-09-05
### Added
- Initial MVP:
  - ETL from DOE AFDC CSV → SQLite schema (`stations`, `connectors`).
  - FastAPI backend: `GET /stations`, `GET /stations/{id}` with geospatial search & filters.
  - Leaflet single-file UI with clustering and connector badges.
  - Basic OpenAPI docs at `/docs`.

[Unreleased]: https://github.com/yuxuananakinliu/ev-charging-api/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/yuxuananakinliu/ev-charging-api/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yuxuananakinliu/ev-charging-api/releases/tag/v0.1.0
