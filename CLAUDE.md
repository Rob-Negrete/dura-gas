# DuraGas - Claude Code Context

## Project Overview

**DuraGas** is a Home Assistant custom integration for monitoring LP gas consumption and solar water heater savings, designed specifically for Mexican households.

### Key Purpose
- Track LP gas tank levels and consumption
- Predict when refills are needed
- Calculate solar water heater ROI
- Compare costs vs traditional gas cylinders

## Architecture

### File Structure
```
custom_components/dura_gas/
├── __init__.py          # Entry point, service registration
├── manifest.json        # Integration metadata
├── const.py            # Constants, enums (RefillStrategy, HeatingMode)
├── coordinator.py      # DataUpdateCoordinator - ALL calculations here
├── config_flow.py      # Multi-step configuration UI
├── sensor.py           # 24 sensor entities
├── binary_sensor.py    # 3 binary sensor entities
├── services.yaml       # Service definitions
├── strings.json        # English UI strings
└── translations/
    ├── en.json         # English translations
    └── es.json         # Mexican Spanish translations
```

### Design Patterns
- **ConfigEntry-based**: No YAML configuration
- **DataUpdateCoordinator**: All state management and calculations
- **CoordinatorEntity**: All entities inherit from this
- **Persistent Storage**: Using Home Assistant's Store API

## Key Components

### Coordinator (`coordinator.py`)
The brain of the integration. Handles:
- All calculations (consumption, projections, solar ROI)
- Persistent storage (refill history, solar tracking)
- Public methods for services

### Sensors (24 total)
1. **Tank State (4)**: level, liters, kg, value
2. **Consumption (4)**: daily, monthly, days since refill, liters consumed
3. **Projections (6)**: days/weeks remaining, next refill date, recommendations
4. **Last Refill (3)**: date, liters, cost
5. **Strategy (3)**: monthly cost, refills/month, vs cylinders
6. **Solar (4)**: efficiency, monthly savings, ROI, hot water consumption

### Services (5 total)
1. `record_refill` - Record gas refill
2. `update_level` - Manual level update
3. `update_price` - Update gas price
4. `set_heating_mode` - Change solar/gas mode
5. `set_strategy` - Change refill strategy

## Development Guidelines

### Code Standards
- Full type hints on all functions
- Async/await for all I/O
- Use `_LOGGER` for logging
- Follow Home Assistant 2025 patterns

### Key Constants
```python
LP_GAS_KG_TO_LITERS = 1.96  # Conversion factor
WATER_HEATING_BASE_PERCENTAGE = 40  # % of gas for hot water
CYLINDER_MONTHLY_COST = 584.0  # Baseline for comparison
SCAN_INTERVAL = 300  # 5 minutes
```

### Refill Strategies
- `fill_complete` - Fill to 80%
- `fixed_300/400/500/600` - Fixed MXN amounts
- `level_50/60/70` - Fill to specific level
- `custom` - User-defined amount

### Heating Modes
- `solar_gas_hybrid` - Solar + gas backup
- `solar_only` - Solar only
- `gas_only` - Gas only
- `none` - No water heating

## Testing

Run tests with:
```bash
pytest tests/
```

Key test areas:
- LP gas calculations
- Consumption tracking
- Solar ROI calculations
- Edge cases (zero values, no history)

## Common Tasks

### Adding a New Sensor
1. Add description to `SENSOR_DESCRIPTIONS` in `sensor.py`
2. Add translation keys to `strings.json` and translation files
3. Update coordinator if new calculation needed

### Adding a New Service
1. Add schema in `__init__.py`
2. Add handler function
3. Register service
4. Add to `services.yaml`
5. Add translations

### Modifying Calculations
All calculations are in `coordinator.py`:
- `_calculate_tank_state()` - Tank status
- `_calculate_consumption()` - Usage stats
- `_calculate_projection()` - Future predictions
- `_calculate_solar()` - Solar savings

## Mexican Context

### Tank Sizes (Standard)
- 120L - Small homes (2-3 people)
- 180L - Medium homes (4-6 people) - Most common
- 300L - Large homes
- 500L - Small commercial
- 1000L - Large commercial

### Typical Gas Prices
- Range: 8-20 MXN/L
- Default: 10.88 MXN/L

### Solar Water Heaters
- Typical cost: 15,000-25,000 MXN
- Efficiency: 60-80%
- Payback: 2-4 years
