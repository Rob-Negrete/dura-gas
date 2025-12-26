"""Select platform for DuraGas integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ANALYTICS_PERIOD_HOURS,
    DEFAULT_ANALYTICS_PERIOD,
    DOMAIN,
    VERSION,
    AnalyticsPeriod,
)
from .coordinator import DuraGasDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DuraGas select entities based on a config entry."""
    coordinator: DuraGasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([DuraGasAnalyticsPeriodSelect(coordinator, entry)])


class DuraGasAnalyticsPeriodSelect(
    CoordinatorEntity[DuraGasDataUpdateCoordinator], SelectEntity
):
    """Select entity for analytics period."""

    _attr_has_entity_name = True
    _attr_translation_key = "analytics_period"
    _attr_icon = "mdi:calendar-range"

    def __init__(
        self,
        coordinator: DuraGasDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_analytics_period"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="DuraGas Tank Monitor",
            manufacturer="DuraGas",
            model="LP Gas Tank",
            sw_version=VERSION,
        )
        self._attr_options = [period.value for period in AnalyticsPeriod]
        self._current_option = coordinator.data.get(
            "analytics_period", DEFAULT_ANALYTICS_PERIOD.value
        )

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.coordinator.data.get(
            "analytics_period", DEFAULT_ANALYTICS_PERIOD.value
        )

    @property
    def extra_state_attributes(self) -> dict[str, int]:
        """Return additional attributes with hours value for dashboard templates."""
        current = self.current_option or DEFAULT_ANALYTICS_PERIOD.value
        return {
            "hours_to_show": ANALYTICS_PERIOD_HOURS.get(current, 2160),
        }

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.async_set_analytics_period(option)
