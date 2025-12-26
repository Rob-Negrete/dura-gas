"""Constants for DuraGas integration."""
from __future__ import annotations

from enum import StrEnum
from typing import Any, Final

# Integration domain
DOMAIN: Final = "dura_gas"
VERSION: Final = "0.1.0-dev.1"  # x-release-please-version

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

# Storage keys
STORAGE_KEY: Final = "dura_gas_data"
STORAGE_VERSION: Final = 1
MAX_REFILL_HISTORY: Final = 50

# Tank size presets (Mexican standard sizes)
TANK_SIZES: Final[dict[str, dict[str, Any]]] = {
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
        "autonomy": "Variable",
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


class AnalyticsPeriod(StrEnum):
    """Analytics period options for historical graphs."""

    MONTHS_3 = "3_months"
    MONTHS_6 = "6_months"
    MONTHS_9 = "9_months"
    MONTHS_12 = "12_months"


# Analytics period to hours mapping
ANALYTICS_PERIOD_HOURS: Final[dict[str, int]] = {
    AnalyticsPeriod.MONTHS_3: 2160,   # 90 days * 24 hours
    AnalyticsPeriod.MONTHS_6: 4320,   # 180 days * 24 hours
    AnalyticsPeriod.MONTHS_9: 6480,   # 270 days * 24 hours
    AnalyticsPeriod.MONTHS_12: 8760,  # 365 days * 24 hours
}

DEFAULT_ANALYTICS_PERIOD: Final = AnalyticsPeriod.MONTHS_3
