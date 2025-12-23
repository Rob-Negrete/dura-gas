"""Number platform for DuraGas integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.const import CURRENCY_DOLLAR
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PRICE_PER_LITER, DEFAULT_PRICE_PER_LITER, DOMAIN, VERSION
from .coordinator import DuraGasDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class DuraGasNumberEntityDescription(NumberEntityDescription):
    """Describes DuraGas number entity."""

    storage_key: str


NUMBER_DESCRIPTIONS: tuple[DuraGasNumberEntityDescription, ...] = (
    DuraGasNumberEntityDescription(
        key="refill_liters_input",
        translation_key="refill_liters_input",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        native_min_value=10,
        native_max_value=200,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:gas-station",
        storage_key="input_refill_liters",
    ),
    DuraGasNumberEntityDescription(
        key="price_per_liter_input",
        translation_key="price_per_liter_input",
        native_unit_of_measurement=CURRENCY_DOLLAR,
        native_min_value=8,
        native_max_value=25,
        native_step=0.01,
        mode=NumberMode.BOX,
        icon="mdi:currency-usd",
        storage_key="input_price_per_liter",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DuraGas number entities based on a config entry."""
    coordinator: DuraGasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[DuraGasNumber] = [
        DuraGasNumber(coordinator, entry, description)
        for description in NUMBER_DESCRIPTIONS
    ]

    async_add_entities(entities)


class DuraGasNumber(CoordinatorEntity[DuraGasDataUpdateCoordinator], NumberEntity):
    """Representation of a DuraGas number input."""

    entity_description: DuraGasNumberEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DuraGasDataUpdateCoordinator,
        entry: ConfigEntry,
        description: DuraGasNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
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
        self._entry = entry

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        storage_key = self.entity_description.storage_key
        stored_value = self.coordinator.get_input_value(storage_key)

        if stored_value is not None:
            return stored_value

        # Default values
        if storage_key == "input_refill_liters":
            # Default to usable capacity
            return self.coordinator.data.get("tank", {}).get("usable_capacity", 96)
        if storage_key == "input_price_per_liter":
            # Default to configured price
            return self._entry.data.get(CONF_PRICE_PER_LITER, DEFAULT_PRICE_PER_LITER)

        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.coordinator.async_set_input_value(
            self.entity_description.storage_key, value
        )
