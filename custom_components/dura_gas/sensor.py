"""Sensor platform for DuraGas integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, VERSION
from .coordinator import DuraGasDataUpdateCoordinator


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    """Parse a datetime value from string or return as-is if already datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        parsed = datetime.fromisoformat(value)
        # Ensure timezone awareness
        if parsed.tzinfo is None:
            parsed = dt_util.as_local(parsed)
        return parsed
    except (ValueError, TypeError):
        return None


@dataclass(frozen=True, kw_only=True)
class DuraGasSensorEntityDescription(SensorEntityDescription):
    """Describes DuraGas sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]
    extra_attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    condition_fn: Callable[[dict[str, Any]], bool] | None = None


SENSOR_DESCRIPTIONS: tuple[DuraGasSensorEntityDescription, ...] = (
    # Tank State (4 sensors)
    DuraGasSensorEntityDescription(
        key="tank_level",
        translation_key="tank_level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:propane-tank",
        value_fn=lambda data: data.get("tank", {}).get("current_level"),
        extra_attrs_fn=lambda data: {
            "capacity": data.get("tank", {}).get("capacity"),
            "usable_capacity": data.get("tank", {}).get("usable_capacity"),
        },
    ),
    DuraGasSensorEntityDescription(
        key="tank_liters",
        translation_key="tank_liters",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:propane-tank",
        value_fn=lambda data: data.get("tank", {}).get("current_liters"),
    ),
    DuraGasSensorEntityDescription(
        key="tank_kilograms",
        translation_key="tank_kilograms",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:weight-kilogram",
        value_fn=lambda data: data.get("tank", {}).get("current_kg"),
    ),
    DuraGasSensorEntityDescription(
        key="tank_value",
        translation_key="tank_value",
        native_unit_of_measurement="MXN",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        icon="mdi:cash",
        value_fn=lambda data: data.get("tank", {}).get("current_value"),
    ),
    # Consumption Analysis (4 sensors)
    DuraGasSensorEntityDescription(
        key="daily_consumption",
        translation_key="daily_consumption",
        native_unit_of_measurement="L/day",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:fire",
        value_fn=lambda data: data.get("consumption", {}).get("daily"),
    ),
    DuraGasSensorEntityDescription(
        key="monthly_consumption",
        translation_key="monthly_consumption",
        native_unit_of_measurement="L/month",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:calendar-month",
        value_fn=lambda data: data.get("consumption", {}).get("monthly"),
    ),
    DuraGasSensorEntityDescription(
        key="days_since_refill",
        translation_key="days_since_refill",
        native_unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:calendar-clock",
        value_fn=lambda data: data.get("consumption", {}).get("days_since_refill"),
    ),
    DuraGasSensorEntityDescription(
        key="liters_consumed",
        translation_key="liters_consumed",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        icon="mdi:counter",
        value_fn=lambda data: data.get("consumption", {}).get("liters_consumed"),
    ),
    # Projections (6 sensors)
    DuraGasSensorEntityDescription(
        key="days_remaining",
        translation_key="days_remaining",
        native_unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:calendar-arrow-right",
        value_fn=lambda data: data.get("projection", {}).get("days_remaining"),
    ),
    DuraGasSensorEntityDescription(
        key="weeks_remaining",
        translation_key="weeks_remaining",
        native_unit_of_measurement="weeks",
        icon="mdi:calendar-week",
        value_fn=lambda data: data.get("projection", {}).get("weeks_remaining"),
    ),
    DuraGasSensorEntityDescription(
        key="next_refill_date",
        translation_key="next_refill_date",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:calendar-alert",
        value_fn=lambda data: _parse_datetime(data.get("projection", {}).get("next_refill_date")),
    ),
    DuraGasSensorEntityDescription(
        key="recommended_liters",
        translation_key="recommended_liters",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        suggested_display_precision=1,
        icon="mdi:gas-station",
        value_fn=lambda data: data.get("projection", {}).get("recommended_liters"),
    ),
    DuraGasSensorEntityDescription(
        key="recommended_cost",
        translation_key="recommended_cost",
        native_unit_of_measurement="MXN",
        device_class=SensorDeviceClass.MONETARY,
        suggested_display_precision=2,
        icon="mdi:cash-plus",
        value_fn=lambda data: data.get("projection", {}).get("recommended_cost"),
    ),
    DuraGasSensorEntityDescription(
        key="resulting_level",
        translation_key="resulting_level",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        icon="mdi:propane-tank-outline",
        value_fn=lambda data: data.get("projection", {}).get("resulting_level"),
    ),
    # Last Refill (3 sensors)
    DuraGasSensorEntityDescription(
        key="last_refill_date",
        translation_key="last_refill_date",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:calendar-check",
        value_fn=lambda data: _parse_datetime(data.get("last_refill", {}).get("date")),
    ),
    DuraGasSensorEntityDescription(
        key="last_refill_liters",
        translation_key="last_refill_liters",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        suggested_display_precision=1,
        icon="mdi:gas-station",
        value_fn=lambda data: data.get("last_refill", {}).get("liters"),
    ),
    DuraGasSensorEntityDescription(
        key="last_refill_cost",
        translation_key="last_refill_cost",
        native_unit_of_measurement="MXN",
        device_class=SensorDeviceClass.MONETARY,
        suggested_display_precision=2,
        icon="mdi:cash",
        value_fn=lambda data: data.get("last_refill", {}).get("total_cost"),
    ),
    # Strategy Analysis (3 sensors)
    DuraGasSensorEntityDescription(
        key="monthly_cost",
        translation_key="monthly_cost",
        native_unit_of_measurement="MXN/month",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        icon="mdi:cash-multiple",
        value_fn=lambda data: data.get("strategy", {}).get("monthly_cost"),
    ),
    DuraGasSensorEntityDescription(
        key="refills_per_month",
        translation_key="refills_per_month",
        native_unit_of_measurement="refills/month",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:counter",
        value_fn=lambda data: data.get("strategy", {}).get("refills_per_month"),
    ),
    DuraGasSensorEntityDescription(
        key="vs_cylinders",
        translation_key="vs_cylinders",
        native_unit_of_measurement="MXN/month",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        icon="mdi:compare-horizontal",
        value_fn=lambda data: data.get("strategy", {}).get("vs_cylinders"),
        extra_attrs_fn=lambda data: {
            "cylinder_baseline": 584.0,
            "description": "Positive means you save vs cylinders",
        },
    ),
    # Solar Analysis (4 sensors - only if has_solar)
    DuraGasSensorEntityDescription(
        key="solar_efficiency_real",
        translation_key="solar_efficiency_real",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:solar-power",
        value_fn=lambda data: data.get("solar", {}).get("efficiency_real")
        if data.get("solar")
        else None,
        condition_fn=lambda data: data.get("config", {}).get("has_solar", False),
    ),
    DuraGasSensorEntityDescription(
        key="solar_savings_monthly",
        translation_key="solar_savings_monthly",
        native_unit_of_measurement="MXN/month",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:piggy-bank",
        value_fn=lambda data: data.get("solar", {}).get("savings_monthly")
        if data.get("solar")
        else None,
        condition_fn=lambda data: data.get("config", {}).get("has_solar", False),
    ),
    DuraGasSensorEntityDescription(
        key="solar_roi_accumulated",
        translation_key="solar_roi_accumulated",
        native_unit_of_measurement="MXN",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        icon="mdi:chart-line",
        value_fn=lambda data: data.get("solar", {}).get("roi_accumulated")
        if data.get("solar")
        else None,
        extra_attrs_fn=lambda data: {
            "percentage": data.get("solar", {}).get("roi_percentage"),
            "months_to_payback": data.get("solar", {}).get("months_to_payback"),
        }
        if data.get("solar")
        else {},
        condition_fn=lambda data: data.get("config", {}).get("has_solar", False),
    ),
    DuraGasSensorEntityDescription(
        key="hot_water_consumption",
        translation_key="hot_water_consumption",
        native_unit_of_measurement="L/day",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:water-thermometer",
        value_fn=lambda data: data.get("solar", {}).get("hot_water_consumption")
        if data.get("solar")
        else None,
        condition_fn=lambda data: data.get("config", {}).get("has_solar", False),
    ),
    # Historical Analytics (diagnostic sensors for graphing)
    DuraGasSensorEntityDescription(
        key="price_per_liter_tracking",
        translation_key="price_per_liter_tracking",
        native_unit_of_measurement="MXN/L",
        device_class=None,  # CRITICAL: No MONETARY to allow MEASUREMENT state_class
        state_class=SensorStateClass.MEASUREMENT,  # Enables historical graphing
        suggested_display_precision=2,
        icon="mdi:chart-line-variant",
        entity_category=EntityCategory.DIAGNOSTIC,  # Hidden by default in UI
        value_fn=lambda data: data.get("config", {}).get("price_per_liter"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DuraGas sensors based on a config entry."""
    coordinator: DuraGasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[DuraGasSensor] = []

    for description in SENSOR_DESCRIPTIONS:
        if description.condition_fn is None or description.condition_fn(coordinator.data):
            entities.append(DuraGasSensor(coordinator, entry, description))

    async_add_entities(entities)


class DuraGasSensor(CoordinatorEntity[DuraGasDataUpdateCoordinator], SensorEntity):
    """Representation of a DuraGas sensor."""

    entity_description: DuraGasSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DuraGasDataUpdateCoordinator,
        entry: ConfigEntry,
        description: DuraGasSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="DuraGas Tank Monitor",
            manufacturer="DuraGas",
            model="LP Gas Tank",
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.entity_description.extra_attrs_fn is not None:
            return self.entity_description.extra_attrs_fn(self.coordinator.data)
        return None
