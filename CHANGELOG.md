# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-dev.2](https://github.com/Rob-Negrete/dura-gas/compare/v0.1.0-dev.1...v0.1.0-dev.2) (2025-12-26)


### Features

* Select analytics period ([96fc467](https://github.com/Rob-Negrete/dura-gas/commit/96fc467b4d219909795da441a762f737d86fdf8c))
* Select analytics period ([dff44d3](https://github.com/Rob-Negrete/dura-gas/commit/dff44d32bebe25418768cee4e406093d486c2e03))

## [0.1.0-dev.1](https://github.com/Rob-Negrete/dura-gas/compare/v0.1.0-dev.0...v0.1.0-dev.1) (2025-12-26)


### Features

* Added dashboard for duragas analytics ([2b74831](https://github.com/Rob-Negrete/dura-gas/commit/2b74831791fe23243e674fc548b75ee710ae9a87))
* Added duragas dashboard ([89a2260](https://github.com/Rob-Negrete/dura-gas/commit/89a2260b46401f8a6bfee597444d92cefd071326))
* Added sensors for historical data ([43f185b](https://github.com/Rob-Negrete/dura-gas/commit/43f185b6629741573b70824f920bc9166f9f7342))
* use custom:button-card ([c0cad48](https://github.com/Rob-Negrete/dura-gas/commit/c0cad48541a0e3295c77b66d43faf32748cddefe))
* use input for litters and price per refill ([7a25b89](https://github.com/Rob-Negrete/dura-gas/commit/7a25b895eff68cb585195727004108455bcc9a8a))


### Bug Fixes

* fix timestamp conversions ([66d4f6d](https://github.com/Rob-Negrete/dura-gas/commit/66d4f6d034caa9eedd54674d1ae04e1e11326590))
* fix timestamp conversions part 2 ([c94fa1d](https://github.com/Rob-Negrete/dura-gas/commit/c94fa1d7cebad73bf3379a67de834a09302d73c4))
* Fixed sensor savings-vs-cylinders in dashboard ([02c7590](https://github.com/Rob-Negrete/dura-gas/commit/02c759072ed187e9c4b5f875481f996c61c8093e))
* Fixes sensor state_class for monetary ([158a624](https://github.com/Rob-Negrete/dura-gas/commit/158a62493c6826fd608fc885622efdc4f720be9e))
* numeric input format ([80eba71](https://github.com/Rob-Negrete/dura-gas/commit/80eba71ee98a66ef83c4f5dddca8480dbd989942))
* use default changelog type for first release ([607bfcd](https://github.com/Rob-Negrete/dura-gas/commit/607bfcd26c0d15769d5e8ecb62e92514e84179e5))
* use default changelog type for first release ([7340130](https://github.com/Rob-Negrete/dura-gas/commit/7340130c9a91dd785c2d7afc3347b34c361c1e41))

## [Unreleased]

### Added
- Historical analytics sensor for price tracking (`price_per_liter_tracking`)
- Analytics dashboard with consumption and cost trends (`custom_components/dura_gas/dashboards/analytics_dashboard.yaml`)
- Price per liter tracking over time (diagnostic sensor with graphing support)
- 6-month historical graphs for consumption, costs, and price trends

### Technical
- New sensor: `price_per_liter_tracking` with `device_class=None` and `state_class=MEASUREMENT` for proper graphing
- Analytics dashboard using native HA `history-graph` and `statistics-graph` cards
- No external dependencies required for analytics features

---

## [0.1.0] - Initial Release

### Added
- Initial implementation of DuraGas integration
- Tank monitoring sensors (level, liters, kg, value)
- Consumption analysis sensors (daily, monthly, since refill)
- Projection sensors (days/weeks remaining, next refill date)
- Refill history tracking (last 50 entries)
- Multiple refill strategies (fill complete, fixed amounts, target levels)
- Solar water heater ROI tracking
- Binary sensors for alerts (low level, refill recommended, solar active)
- 5 custom services (record_refill, update_level, update_price, set_heating_mode, set_strategy)
- Multi-step configuration flow
- Options flow for updating settings
- Full English and Mexican Spanish translations
- Persistent storage using Home Assistant's Store API
