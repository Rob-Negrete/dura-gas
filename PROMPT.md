# DuraGas - Home Assistant Custom Integration
## Complete Production-Ready Code Generation Request

You are tasked with generating a complete, production-ready Home Assistant custom integration called **DuraGas**. This integration monitors LP gas consumption and solar water heater savings for Mexican households.

---

## CRITICAL REQUIREMENTS

### Target Environment
- **Home Assistant Core:** 2025.10.1
- **Python Version:** 3.12+
- **Pattern:** ConfigEntry-based (no YAML config)
- **Architecture:** DataUpdateCoordinator
- **Update Interval:** 5 minutes
- **Dependencies:** None (HA standard library only)

### Code Quality Standards
- ✅ **Full async/await** - No synchronous I/O operations
- ✅ **Complete type hints** - Every function parameter and return value
- ✅ **Python 3.12+ syntax** - Use modern features (StrEnum, proper unions)
- ✅ **Proper logging** - Use `_LOGGER` with appropriate levels
- ✅ **Error handling** - Try/except with specific exceptions
- ✅ **Entity categories** - CONFIG, DIAGNOSTIC, or None as appropriate
- ✅ **State classes** - MEASUREMENT, TOTAL, or TOTAL_INCREASING
- ✅ **Device classes** - MONETARY, TIMESTAMP, etc. where applicable
- ✅ **Unique IDs** - All entities must have permanent unique_id
- ✅ **Device info** - Link all entities to single device
- ✅ **Bilingual** - Full English and Spanish (Mexican) translations

---

## PROJECT OVERVIEW

### Purpose
Help Mexican households:
1. Track how long their LP gas lasts
2. Measure real solar water heater ROI
3. Optimize gas refill timing and amounts
4. Compare costs: stationary tank vs cylinders

### Target Users
- Mexican households with 120L-1000L stationary LP gas tanks
- Optional: Solar water heater systems
- Home Assistant OS installation

### Key Features
- **24+ sensor entities** tracking tank state, consumption, projections
- **3 binary sensors** for low level and refill alerts
- **5 custom services** for refill recording, level updates, mode changes
- **Multiple refill strategies** (fill complete, fixed amounts, target levels)
- **Solar ROI tracking** with monthly savings accumulation
- **Bilingual UI** (English + Mexican Spanish)

---

## FILE GENERATION ORDER

Generate the following files in this exact order:

### 0. AI Context Documentation
**File:** `CLAUDE.md`
**Purpose:** Comprehensive project context for Claude Code and AI assistants
**Content:** [See CLAUDE.md template below]

### 1. Integration Metadata
**File:** `custom_components/dura_gas/manifest.json`
```json
{
  "domain": "dura_gas",
  "name": "DuraGas",
  "codeowners": ["@Rob-Negrete"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/Rob-Negrete/ha-dura-gas",
  "integration_type": "device",
  "iot_class": "calculated",
  "issue_tracker": "https://github.com/Rob-Negrete/ha-dura-gas/issues",
  "requirements": [],
  "version": "1.0.0",
  "homeassistant": "2025.10.0"
}
```

### 2. Constants and Configuration
**File:** `custom_components/dura_gas/const.py`

**Content:**
```python
"""Constants for DuraGas integration."""
from __future__ import annotations

from typing import Final
from enum import StrEnum

# Integration domain
DOMAIN: Final = "dura_gas"
VERSION: Final = "1.0.0"

# Gas LP physics
LP_GAS_KG_TO_LITERS: Final = 1.96

# Default values
DEFAULT_TANK_SIZE: Final = "120"
DEFAULT_USABLE_PERCENTAGE: Final = 80
DEFAULT_PRICE_PER_LITER: Final = 10.88
DEFAULT_SOLAR_EFFICIENCY: Final = 70

# Constants for calculations
WATER_HEATING_BASE_PERCENTAGE: Final = 40  # ~40% of gas goes to hot water
CYLINDER_MONTHLY_COST: Final = 584.0  # Baseline: 29kg @ 20.15 MXN/kg

# Update interval
SCAN_INTERVAL: Final = 300  # 5 minutes in seconds

# Configuration keys
CONF_TANK_SIZE: Final = "tank_size"
CONF_TANK_CAPACITY_CUSTOM: Final = "tank_capacity_custom"
CONF_USABLE_PERCENTAGE: Final = "usable_percentage"
CONF_INITIAL_LEVEL: Final = "initial_level"
CONF_PRICE_PER_LITER: Final = "price_per_liter"
CONF_HAS_SOLAR: Final = "has_solar"
CONF_SOLAR_INSTALLATION_DATE: Final = "solar_installation_date"
CONF_SOLAR_INVESTMENT: Final = "solar_investment"
CONF_SOLAR_EFFICIENCY: Final = "solar_efficiency"
CONF_LOW_THRESHOLD: Final = "low_threshold"
CONF_REFILL_THRESHOLD: Final = "refill_threshold"
CONF_REFILL_STRATEGY: Final = "refill_strategy"

# Tank size presets (Mexican standard sizes)
TANK_SIZES: Final[dict[str, dict[str, any]]] = {
    "120": {
        "capacity": 120,
        "label": "120L - Casa pequeña (2-3 personas)",
        "description": "Departamentos, casas pequeñas",
        "autonomy": "4-8 semanas",
    },
    "180": {
        "capacity": 180,
        "label": "180L - Casa mediana (4-6 personas) ⭐ Más común",
        "description": "Familias promedio",
        "autonomy": "6-12 semanas",
    },
    "300": {
        "capacity": 300,
        "label": "300L - Casa grande / Comercio pequeño",
        "description": "Familias grandes, alto consumo",
        "autonomy": "10-20 semanas",
    },
    "500": {
        "capacity": 500,
        "label": "500L - Comercio mediano",
        "description": "Panaderías, lavanderías",
        "autonomy": "Variable según consumo",
    },
    "1000": {
        "capacity": 1000,
        "label": "1000L - Comercio grande",
        "description": "Restaurantes grandes, industria",
        "autonomy": "Variable según consumo",
    },
    "custom": {
        "capacity": 0,
        "label": "Personalizado",
        "description": "Ingresa capacidad manualmente",
    },
}


class RefillStrategy(StrEnum):
    """Refill strategy options."""

    FILL_COMPLETE = "fill_complete"
    FIXED_300 = "fixed_300"
    FIXED_400 = "fixed_400"
    FIXED_500 = "fixed_500"
    FIXED_600 = "fixed_600"
    LEVEL_50 = "level_50"
    LEVEL_60 = "level_60"
    LEVEL_70 = "level_70"
    CUSTOM = "custom"


class HeatingMode(StrEnum):
    """Water heating mode options."""

    SOLAR_GAS_HYBRID = "solar_gas_hybrid"
    SOLAR_ONLY = "solar_only"
    GAS_ONLY = "gas_only"
    NONE = "none"
```

### 3. Data Update Coordinator
**File:** `custom_components/dura_gas/coordinator.py`

**Requirements:**
- Extend `DataUpdateCoordinator`
- Update every 5 minutes (SCAN_INTERVAL)
- Calculate ALL derived values (don't make sensors do calculations)
- Manage persistent storage for:
  - Refill history (last 50 entries)
  - Solar investment tracking
  - Current state
- Provide data structure:
```python
{
    "config": {
        "tank_size": str,
        "capacity": float,
        "usable_capacity": float,
        "price_per_liter": float,
        "has_solar": bool,
        "solar_investment": float,
        "heating_mode": HeatingMode,
        "refill_strategy": RefillStrategy,
    },
    "tank": {
        "capacity": float,
        "usable_capacity": float,
        "current_level": float,  # percentage
        "current_liters": float,
        "current_kg": float,
        "current_value": float,  # MXN
    },
    "consumption": {
        "daily": float,  # L/day
        "monthly": float,  # L/month
        "days_since_refill": int,
        "liters_consumed": float,
    },
    "projection": {
        "days_remaining": float,
        "weeks_remaining": float,
        "next_refill_date": datetime,
        "recommended_liters": float,
        "recommended_cost": float,
        "resulting_level": float,  # percentage after recommended refill
    },
    "last_refill": {
        "date": datetime,
        "liters": float,
        "price_per_liter": float,
        "total_cost": float,
    },
    "strategy": {
        "current": RefillStrategy,
        "monthly_cost": float,
        "refills_per_month": float,
        "vs_cylinders": float,  # difference vs baseline
    },
    "solar": {  # Only if has_solar
        "efficiency_real": float,
        "savings_monthly": float,
        "roi_accumulated": float,
        "roi_percentage": float,
        "months_to_payback": float,
        "hot_water_consumption": float,
        "heating_mode": HeatingMode,
    },
    "refill_history": [
        {
            "date": datetime,
            "liters": float,
            "price_per_liter": float,
            "total_cost": float,
            "level_before": float,
            "level_after": float,
        }
    ],
}
```

**Key Calculations:**
```python
# Tank state
usable_capacity = capacity * (usable_percentage / 100)
current_liters = usable_capacity * (current_level / 100)
current_kg = current_liters / LP_GAS_KG_TO_LITERS
current_value = current_liters * price_per_liter

# Consumption (requires refill history)
daily_consumption = liters_consumed / days_since_refill
monthly_consumption = daily_consumption * 30
days_remaining = current_liters / daily_consumption

# Strategy-based recommendations
if strategy == FILL_COMPLETE:
    recommended_liters = usable_capacity - current_liters
elif strategy == FIXED_300:
    recommended_liters = 300 / price_per_liter
elif strategy == LEVEL_50:
    target_liters = usable_capacity * 0.5
    recommended_liters = target_liters - current_liters
# ... etc

# Solar savings (if has_solar)
base_water_heating = monthly_consumption * WATER_HEATING_BASE_PERCENTAGE / 100
if heating_mode == SOLAR_GAS_HYBRID:
    coverage = solar_efficiency / 100
elif heating_mode == SOLAR_ONLY:
    coverage = 1.0
else:
    coverage = 0.0

liters_saved = base_water_heating * coverage
solar_savings_monthly = liters_saved * price_per_liter

# ROI tracking
roi_accumulated += solar_savings_monthly  # Updated monthly
roi_percentage = (roi_accumulated / solar_investment) * 100
months_to_payback = (solar_investment - roi_accumulated) / solar_savings_monthly
```

**Public Methods:**
```python
async def async_record_refill(
    self,
    liters: float,
    price_per_liter: float,
    refill_date: datetime | None = None,
) -> None:
    """Record a new refill."""

async def async_update_level(self, level_percent: float) -> None:
    """Update current tank level."""

async def async_update_price(self, price_per_liter: float) -> None:
    """Update gas price."""

async def async_set_heating_mode(self, mode: HeatingMode) -> None:
    """Set water heating mode."""

async def async_set_strategy(
    self,
    strategy: RefillStrategy,
    custom_amount: float | None = None,
) -> None:
    """Set refill strategy."""
```

### 4. Configuration Flow
**File:** `custom_components/dura_gas/config_flow.py`

**Requirements:**
- Multi-step configuration flow
- Options flow for updates
- Proper input validation
- Conditional field display

**Steps:**

**Step 1: Tank Configuration**
```python
DATA_SCHEMA_TANK = vol.Schema({
    vol.Required(CONF_TANK_SIZE, default="120"): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                {"value": "120", "label": "120L - Casa pequeña (2-3 personas)"},
                {"value": "180", "label": "180L - Casa mediana (4-6 personas) ⭐"},
                {"value": "300", "label": "300L - Casa grande / Comercio pequeño"},
                {"value": "500", "label": "500L - Comercio mediano"},
                {"value": "1000", "label": "1000L - Comercio grande"},
                {"value": "custom", "label": "Personalizado"},
            ],
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    ),
    # Show only if tank_size == "custom"
    vol.Optional(CONF_TANK_CAPACITY_CUSTOM): vol.All(
        vol.Coerce(float),
        vol.Range(min=50, max=5000)
    ),
    vol.Required(CONF_USABLE_PERCENTAGE, default=80): vol.All(
        vol.Coerce(int),
        vol.Range(min=70, max=90)
    ),
    vol.Required(CONF_INITIAL_LEVEL, default=0): vol.All(
        vol.Coerce(int),
        vol.Range(min=0, max=100)
    ),
    vol.Required(CONF_PRICE_PER_LITER, default=10.88): vol.All(
        vol.Coerce(float),
        vol.Range(min=8.0, max=20.0)
    ),
})
```

**Step 2: Solar Configuration (Optional)**
```python
DATA_SCHEMA_SOLAR = vol.Schema({
    vol.Required(CONF_HAS_SOLAR, default=False): bool,
    # Show only if has_solar == True
    vol.Optional(CONF_SOLAR_INSTALLATION_DATE): selector.DateSelector(),
    vol.Optional(CONF_SOLAR_INVESTMENT, default=15000): vol.All(
        vol.Coerce(float),
        vol.Range(min=0, max=100000)
    ),
    vol.Optional(CONF_SOLAR_EFFICIENCY, default=70): vol.All(
        vol.Coerce(int),
        vol.Range(min=0, max=100)
    ),
})
```

**Step 3: Alerts & Strategy**
```python
DATA_SCHEMA_ALERTS = vol.Schema({
    vol.Required(CONF_LOW_THRESHOLD, default=20): vol.All(
        vol.Coerce(int),
        vol.Range(min=10, max=50)
    ),
    vol.Required(CONF_REFILL_THRESHOLD, default=30): vol.All(
        vol.Coerce(int),
        vol.Range(min=10, max=50)
    ),
    vol.Required(CONF_REFILL_STRATEGY, default=RefillStrategy.FILL_COMPLETE): 
        selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    {"value": "fill_complete", "label": "Llenar completo (80%)"},
                    {"value": "fixed_300", "label": "Monto fijo: $300 MXN"},
                    {"value": "fixed_400", "label": "Monto fijo: $400 MXN"},
                    {"value": "fixed_500", "label": "Monto fijo: $500 MXN"},
                    {"value": "fixed_600", "label": "Monto fijo: $600 MXN"},
                    {"value": "level_50", "label": "Llenar hasta 50%"},
                    {"value": "level_60", "label": "Llenar hasta 60%"},
                    {"value": "level_70", "label": "Llenar hasta 70%"},
                    {"value": "custom", "label": "Personalizado"},
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
})
```

**Options Flow:**
- Allow updating all settings post-setup
- Same schemas as initial config
- Trigger coordinator refresh after changes

### 5. Sensor Platform
**File:** `custom_components/dura_gas/sensor.py`

**Requirements:**
- Extend `CoordinatorEntity` and `SensorEntity`
- 24+ sensors organized in categories
- Proper device_class, state_class, entity_category
- All linked to same device

**Sensor Entities (24 total):**

**Tank State (4 sensors):**
1. `duragas_tank_level` - % (MEASUREMENT)
2. `duragas_tank_liters` - L (MEASUREMENT)
3. `duragas_tank_kilograms` - kg (MEASUREMENT)
4. `duragas_tank_value` - MXN (MONETARY, MEASUREMENT)

**Consumption Analysis (4 sensors):**
5. `duragas_daily_consumption` - L/day (MEASUREMENT)
6. `duragas_monthly_consumption` - L/month (MEASUREMENT)
7. `duragas_days_since_refill` - days (DIAGNOSTIC)
8. `duragas_liters_consumed` - L (TOTAL_INCREASING)

**Projections (6 sensors):**
9. `duragas_days_remaining` - days
10. `duragas_weeks_remaining` - weeks
11. `duragas_next_refill_date` - TIMESTAMP
12. `duragas_recommended_liters` - L
13. `duragas_recommended_cost` - MXN (MONETARY)
14. `duragas_resulting_level` - %

**Last Refill (3 sensors - DIAGNOSTIC):**
15. `duragas_last_refill_date` - TIMESTAMP
16. `duragas_last_refill_liters` - L
17. `duragas_last_refill_cost` - MXN (MONETARY)

**Strategy Analysis (3 sensors):**
18. `duragas_monthly_cost` - MXN/month (MONETARY)
19. `duragas_refills_per_month` - count
20. `duragas_vs_cylinders` - MXN/month (MONETARY)

**Solar Analysis (4 sensors - only if has_solar):**
21. `duragas_solar_efficiency_real` - % (MEASUREMENT)
22. `duragas_solar_savings_monthly` - MXN/month (MONETARY)
23. `duragas_solar_roi_accumulated` - MXN (TOTAL)
    - Attributes: percentage, months_to_payback
24. `duragas_hot_water_consumption` - L/day (MEASUREMENT)

**Example Sensor Implementation:**
```python
class DuraGasTankLevelSensor(CoordinatorEntity, SensorEntity):
    """Tank level percentage sensor."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: DuraGasDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_tank_level"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="DuraGas Tank Monitor",
            manufacturer="DuraGas",
            model="LP Gas Tank",
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("tank", {}).get("current_level")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        tank_data = self.coordinator.data.get("tank", {})
        return {
            "capacity": tank_data.get("capacity"),
            "usable_capacity": tank_data.get("usable_capacity"),
        }
```

### 6. Binary Sensor Platform
**File:** `custom_components/dura_gas/binary_sensor.py`

**Binary Sensors (3 total):**

1. `duragas_low_level` - PROBLEM, ON when < low_threshold
2. `duragas_refill_recommended` - PROBLEM, ON when < refill_threshold
3. `duragas_solar_active` - ON when heating_mode != GAS_ONLY (if has_solar)

**Example:**
```python
class DuraGasLowLevelBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Low level alert binary sensor."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        """Return true if tank level is low."""
        current_level = self.coordinator.data.get("tank", {}).get("current_level", 100)
        threshold = self.coordinator.data.get("config", {}).get("low_threshold", 20)
        return current_level < threshold
```

### 7. Services
**File:** `custom_components/dura_gas/services.yaml`

**5 Services:**
```yaml
record_refill:
  name: Record Gas Refill
  description: Record a new gas refill with liters and price
  fields:
    liters:
      name: Liters
      description: Amount of gas added in liters
      required: true
      example: 96
      selector:
        number:
          min: 0
          max: 200
          step: 0.1
          unit_of_measurement: "L"
    price_per_liter:
      name: Price per Liter
      description: Price paid per liter in MXN
      required: true
      example: 10.88
      selector:
        number:
          min: 8
          max: 20
          step: 0.01
          unit_of_measurement: "MXN/L"
    refill_date:
      name: Refill Date
      description: Date and time of refill (optional, defaults to now)
      required: false
      selector:
        datetime:

update_level:
  name: Update Tank Level
  description: Manually update the current tank level percentage
  fields:
    level_percent:
      name: Level Percentage
      description: Current tank level in percentage
      required: true
      example: 75
      selector:
        number:
          min: 0
          max: 100
          step: 1
          unit_of_measurement: "%"

update_price:
  name: Update Gas Price
  description: Update the current gas price per liter
  fields:
    price_per_liter:
      name: Price per Liter
      description: New price per liter in MXN
      required: true
      example: 10.88
      selector:
        number:
          min: 8
          max: 20
          step: 0.01
          unit_of_measurement: "MXN/L"

set_heating_mode:
  name: Set Water Heating Mode
  description: Change the water heating mode (solar/gas/hybrid)
  fields:
    mode:
      name: Heating Mode
      description: Water heating mode
      required: true
      example: "solar_gas_hybrid"
      selector:
        select:
          options:
            - label: "Solar + Gas (Hybrid)"
              value: "solar_gas_hybrid"
            - label: "Solar Only"
              value: "solar_only"
            - label: "Gas Only"
              value: "gas_only"
            - label: "None"
              value: "none"

set_strategy:
  name: Set Refill Strategy
  description: Change the refill recommendation strategy
  fields:
    strategy:
      name: Strategy
      description: Refill strategy
      required: true
      example: "fill_complete"
      selector:
        select:
          options:
            - label: "Fill Complete (80%)"
              value: "fill_complete"
            - label: "Fixed: $300 MXN"
              value: "fixed_300"
            - label: "Fixed: $400 MXN"
              value: "fixed_400"
            - label: "Fixed: $500 MXN"
              value: "fixed_500"
            - label: "Fixed: $600 MXN"
              value: "fixed_600"
            - label: "Fill to 50%"
              value: "level_50"
            - label: "Fill to 60%"
              value: "level_60"
            - label: "Fill to 70%"
              value: "level_70"
            - label: "Custom Amount"
              value: "custom"
    custom_amount:
      name: Custom Amount
      description: Custom amount in MXN (only for custom strategy)
      required: false
      example: 450
      selector:
        number:
          min: 100
          max: 2000
          step: 10
          unit_of_measurement: "MXN"
```

### 8. Integration Entry Point
**File:** `custom_components/dura_gas/__init__.py`

**Requirements:**
- Setup platforms (sensor, binary_sensor)
- Register services with proper handlers
- Handle entry unload
- Proper error handling
```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DuraGas from a config entry."""
    
    # Create coordinator
    coordinator = DuraGasDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "binary_sensor"]
    )
    
    # Register services
    async def handle_record_refill(call: ServiceCall) -> None:
        """Handle record_refill service call."""
        # Implementation
    
    async def handle_update_level(call: ServiceCall) -> None:
        """Handle update_level service call."""
        # Implementation
    
    # ... register all 5 services
    
    hass.services.async_register(DOMAIN, "record_refill", handle_record_refill)
    # ... etc
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor"]
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
```

### 9. UI Strings
**File:** `custom_components/dura_gas/strings.json`

**Requirements:**
- Complete English strings for all UI elements
- Config flow steps and options
- Service descriptions
- Sensor names and descriptions
- Error messages

**Key Sections:**
```json
{
  "config": {
    "step": {
      "tank": {
        "title": "Tank Configuration",
        "description": "Configure your LP gas tank. Most Mexican homes use 120L or 180L.",
        "data": {
          "tank_size": "Tank Size",
          "tank_capacity_custom": "Custom Capacity (liters)",
          "usable_percentage": "Usable Percentage (%)",
          "initial_level": "Initial Level (%)",
          "price_per_liter": "Price per Liter (MXN)"
        },
        "data_description": {
          "tank_size": "Select your tank size. Choose 'Custom' for non-standard sizes.",
          "usable_percentage": "Maximum safe fill level (80% recommended)",
          "initial_level": "Current tank level if known, otherwise leave at 0"
        }
      },
      "solar": { ... },
      "alerts": { ... }
    },
    "error": {
      "invalid_capacity": "Tank capacity must be between 50 and 5000 liters",
      "invalid_percentage": "Percentage must be between {min} and {max}",
      "invalid_price": "Price must be between 8 and 20 MXN per liter"
    }
  },
  "entity": {
    "sensor": {
      "tank_level": {
        "name": "Tank Level"
      },
      "tank_liters": {
        "name": "Tank Liters"
      },
      // ... all sensors
    }
  },
  "services": {
    "record_refill": {
      "name": "Record Refill",
      "description": "Record a new gas refill"
    },
    // ... all services
  }
}
```

### 10. English Translations
**File:** `custom_components/dura_gas/translations/en.json`

**Content:** Identical to strings.json (full English translations)

### 11. Spanish Translations
**File:** `custom_components/dura_gas/translations/es.json`

**Requirements:**
- Mexican Spanish (tú form, informal)
- Cultural adaptations
- "Tanque" not "cilindro"
- "Recarga" not "rellenado"

**Example:**
```json
{
  "config": {
    "step": {
      "tank": {
        "title": "Configuración del Tanque",
        "description": "Configura tu tanque de gas LP. La mayoría de hogares mexicanos usan 120L o 180L.",
        "data": {
          "tank_size": "Tamaño del Tanque",
          "tank_capacity_custom": "Capacidad Personalizada (litros)",
          "usable_percentage": "Porcentaje Utilizable (%)",
          "initial_level": "Nivel Inicial (%)",
          "price_per_liter": "Precio por Litro (MXN)"
        },
        "data_description": {
          "tank_size": "Selecciona el tamaño de tu tanque. Elige 'Personalizado' para tamaños especiales.",
          "usable_percentage": "Nivel máximo de llenado seguro (80% recomendado)",
          "initial_level": "Nivel actual del tanque si lo conoces, de lo contrario deja en 0"
        }
      }
    }
  }
}
```

### 12-15. GitHub AI Context Files

**File 12:** `.github/ai-context.md` - General AI development context
**File 13:** `.github/copilot-instructions.md` - GitHub Copilot specific
**File 14:** `.cursorrules` - Cursor IDE rules
**File 15:** `.github/CONTRIBUTING.md` - Contribution guidelines

[Content for each file provided in previous conversation]

### 16. README (English)
**File:** `README.md`

**Sections:**
- Project overview with "Que tu gas dure más" tagline
- Features list
- Installation instructions (manual + HACS ready)
- Configuration walkthrough with screenshots descriptions
- Dashboard examples with YAML
- Automation examples
- Service usage examples
- FAQ
- Troubleshooting
- Contributing
- License

### 17. README (Spanish)
**File:** `README.es.md`

**Requirements:**
- Complete Spanish translation of README.md
- Mexican cultural adaptations
- Natural phrasing for Mexican users

### 18. License
**File:** `LICENSE`

**Content:** MIT License

### 19. Basic Tests
**File:** `tests/test_calculations.py`

**Test Cases:**
- LP gas kg to liters conversion
- Tank capacity calculations
- Daily/monthly consumption calculations
- Refill strategy calculations
- Solar savings calculations
- Edge cases (zero division, null values)

### 20. Git Ignore
**File:** `.gitignore`

**Content:**
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
.env
.venv
venv/
*.log
.DS_Store
.vscode/
.idea/
```

---

## CRITICAL INSTRUCTIONS

### Code Quality
1. **Every function must have full type hints**
2. **All I/O operations must be async**
3. **Use proper logging levels** (debug, info, warning, error)
4. **Handle errors gracefully** with try/except
5. **Follow Home Assistant 2025 coding standards**

### Entity Requirements
1. **All entities must have unique_id** based on entry_id
2. **All entities must link to same device**
3. **Set appropriate entity_category** (CONFIG/DIAGNOSTIC/None)
4. **Set appropriate state_class** (MEASUREMENT/TOTAL)
5. **Use device_class** where applicable (MONETARY, TIMESTAMP)

### Translations
1. **Complete English in strings.json**
2. **Complete Mexican Spanish in es.json**
3. **All config steps, errors, entities, services must be translated**
4. **Use Mexican terminology and informal tú form**

### Storage & Data
1. **Use ConfigEntry for configuration**
2. **Use DataUpdateCoordinator for state management**
3. **Store refill history (max 50 entries)**
4. **Store solar investment tracking**
5. **All calculations in coordinator, not sensors**

### Testing
1. **Include basic pytest tests**
2. **Test calculations and edge cases**
3. **Verify no division by zero**
4. **Test with missing data (no refill history yet)**

---

## OUTPUT FORMAT

For each file, output: