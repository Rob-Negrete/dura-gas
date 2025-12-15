"""Binary sensor platform for DuraGas integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION, HeatingMode
from .coordinator import DuraGasDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class DuraGasBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes DuraGas binary sensor entity."""

    is_on_fn: Callable[[dict[str, Any]], bool]
    condition_fn: Callable[[dict[str, Any]], bool] | None = None
    extra_attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


BINARY_SENSOR_DESCRIPTIONS: tuple[DuraGasBinarySensorEntityDescription, ...] = (
    DuraGasBinarySensorEntityDescription(
        key="low_level",
        translation_key="low_level",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert",
        is_on_fn=lambda data: (
            data.get("tank", {}).get("current_level", 100)
            < data.get("config", {}).get("low_threshold", 20)
        ),
        extra_attrs_fn=lambda data: {
            "current_level": data.get("tank", {}).get("current_level"),
            "threshold": data.get("config", {}).get("low_threshold"),
        },
    ),
    DuraGasBinarySensorEntityDescription(
        key="refill_recommended",
        translation_key="refill_recommended",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:gas-station",
        is_on_fn=lambda data: (
            data.get("tank", {}).get("current_level", 100)
            < data.get("config", {}).get("refill_threshold", 30)
        ),
        extra_attrs_fn=lambda data: {
            "current_level": data.get("tank", {}).get("current_level"),
            "threshold": data.get("config", {}).get("refill_threshold"),
            "recommended_liters": data.get("projection", {}).get("recommended_liters"),
            "recommended_cost": data.get("projection", {}).get("recommended_cost"),
        },
    ),
    DuraGasBinarySensorEntityDescription(
        key="solar_active",
        translation_key="solar_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:solar-power-variant",
        is_on_fn=lambda data: (
            data.get("solar", {}).get("heating_mode", HeatingMode.GAS_ONLY)
            != HeatingMode.GAS_ONLY
            if data.get("solar")
            else False
        ),
        condition_fn=lambda data: data.get("config", {}).get("has_solar", False),
        extra_attrs_fn=lambda data: {
            "heating_mode": data.get("solar", {}).get("heating_mode"),
            "savings_monthly": data.get("solar", {}).get("savings_monthly"),
        }
        if data.get("solar")
        else {},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DuraGas binary sensors based on a config entry."""
    coordinator: DuraGasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[DuraGasBinarySensor] = []

    for description in BINARY_SENSOR_DESCRIPTIONS:
        if description.condition_fn is None or description.condition_fn(coordinator.data):
            entities.append(DuraGasBinarySensor(coordinator, entry, description))

    async_add_entities(entities)


class DuraGasBinarySensor(
    CoordinatorEntity[DuraGasDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of a DuraGas binary sensor."""

    entity_description: DuraGasBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DuraGasDataUpdateCoordinator,
        entry: ConfigEntry,
        description: DuraGasBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.entity_description.extra_attrs_fn is not None:
            return self.entity_description.extra_attrs_fn(self.coordinator.data)
        return None
