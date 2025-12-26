# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Historical analytics sensor for price tracking (`price_per_liter_tracking`)
- Analytics dashboard with consumption and cost trends (`dashboards/analytics_dashboard.yaml`)
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
