# AI Development Context for DuraGas

## Quick Reference

### What is DuraGas?
A Home Assistant custom integration for monitoring LP gas consumption and solar water heater savings in Mexican households.

### Tech Stack
- Python 3.12+
- Home Assistant Core 2025.10+
- Async/await patterns
- DataUpdateCoordinator architecture

### Key Files to Understand
1. `coordinator.py` - All business logic and calculations
2. `sensor.py` - Entity definitions using descriptions pattern
3. `config_flow.py` - Multi-step configuration UI
4. `const.py` - All constants and enums

## Code Patterns

### Entity Creation Pattern
```python
@dataclass(frozen=True, kw_only=True)
class DuraGasSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    condition_fn: Callable[[dict[str, Any]], bool] | None = None
```

### Coordinator Data Structure
```python
{
    "config": {...},      # Configuration values
    "tank": {...},        # Current tank state
    "consumption": {...}, # Usage statistics
    "projection": {...},  # Future predictions
    "last_refill": {...}, # Last refill info
    "strategy": {...},    # Strategy analysis
    "solar": {...},       # Solar savings (optional)
}
```

### Service Registration Pattern
```python
hass.services.async_register(
    DOMAIN,
    SERVICE_NAME,
    handler_function,
    schema=SERVICE_SCHEMA,
)
```

## Common Tasks

### Add New Sensor
1. Create `DuraGasSensorEntityDescription` in `sensor.py`
2. Add to `SENSOR_DESCRIPTIONS` tuple
3. Add translations in `strings.json` and `translations/*.json`

### Add New Service
1. Define schema in `__init__.py`
2. Create async handler function
3. Register with `hass.services.async_register()`
4. Add to `services.yaml`
5. Add translations

### Modify Calculations
All calculations in `coordinator.py`:
- Tank state: `_calculate_tank_state()`
- Consumption: `_calculate_consumption()`
- Projections: `_calculate_projection()`
- Solar: `_calculate_solar()`

## Mexican Context

### Standard Tank Sizes
- 120L, 180L (most common), 300L, 500L, 1000L

### Gas Price Range
- 8-20 MXN per liter
- Default: 10.88 MXN/L

### Conversion Factor
- 1 kg LP gas = 1.96 liters

## Testing
```bash
pytest tests/test_calculations.py
```

## Translations
- English: `strings.json` and `translations/en.json`
- Spanish (Mexican): `translations/es.json`
- Use informal "tú" form for Spanish
- Use Mexican terminology (tanque, recarga, not cilindro, rellenado)
