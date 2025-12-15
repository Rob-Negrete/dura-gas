# GitHub Copilot Instructions for DuraGas

## Project Context
DuraGas is a Home Assistant custom integration for LP gas monitoring. When suggesting code:

## Code Style Requirements

### Type Hints
Always include complete type hints:
```python
async def async_record_refill(
    self,
    liters: float,
    price_per_liter: float,
    refill_date: datetime | None = None,
) -> None:
```

### Async Patterns
All I/O operations must be async:
```python
# Correct
await self._store.async_save(data)
await coordinator.async_refresh()

# Wrong - Never use sync I/O
self._store.save(data)  # Don't do this
```

### Entity Patterns
Use the description dataclass pattern:
```python
@dataclass(frozen=True, kw_only=True)
class DuraGasSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
```

### Logging
Use module-level logger:
```python
_LOGGER = logging.getLogger(__name__)
_LOGGER.info("Message with %s", value)
```

## Domain Knowledge

### LP Gas Constants
- Conversion: 1 kg = 1.96 liters
- Usable capacity: typically 80% of tank
- Water heating: ~40% of gas consumption

### Mexican Context
- Standard tanks: 120L, 180L, 300L, 500L, 1000L
- Price range: 8-20 MXN/L
- Cylinder baseline: 29kg @ 20.15 MXN/kg = 584 MXN/month

### Solar Water Heaters
- Typical investment: 15,000-25,000 MXN
- Efficiency: 60-80%
- Payback period: 2-4 years

## File Responsibilities

### coordinator.py
- ALL calculations go here
- Persistent storage management
- Service method implementations

### sensor.py / binary_sensor.py
- Entity definitions only
- Get values from coordinator.data
- No calculations in entities

### config_flow.py
- Multi-step configuration
- Input validation
- Options flow for updates

## Translations
- English is primary (strings.json)
- Mexican Spanish in es.json
- Use informal "tú" form
- Mexican terminology: tanque, recarga, litros

## Common Imports
```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
```
