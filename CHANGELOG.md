# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
