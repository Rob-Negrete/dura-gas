"""DuraGas - LP Gas Tank Monitor for Home Assistant."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, HeatingMode, RefillStrategy
from .coordinator import DuraGasDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

SERVICE_RECORD_REFILL = "record_refill"
SERVICE_UPDATE_LEVEL = "update_level"
SERVICE_UPDATE_PRICE = "update_price"
SERVICE_SET_HEATING_MODE = "set_heating_mode"
SERVICE_SET_STRATEGY = "set_strategy"

ATTR_LITERS = "liters"
ATTR_PRICE_PER_LITER = "price_per_liter"
ATTR_REFILL_DATE = "refill_date"
ATTR_LEVEL_PERCENT = "level_percent"
ATTR_MODE = "mode"
ATTR_STRATEGY = "strategy"
ATTR_CUSTOM_AMOUNT = "custom_amount"

SERVICE_RECORD_REFILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_LITERS): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=200)
        ),
        vol.Required(ATTR_PRICE_PER_LITER): vol.All(
            vol.Coerce(float), vol.Range(min=8, max=20)
        ),
        vol.Optional(ATTR_REFILL_DATE): cv.datetime,
    }
)

SERVICE_UPDATE_LEVEL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_LEVEL_PERCENT): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=100)
        ),
    }
)

SERVICE_UPDATE_PRICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PRICE_PER_LITER): vol.All(
            vol.Coerce(float), vol.Range(min=8, max=20)
        ),
    }
)

SERVICE_SET_HEATING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MODE): vol.In(
            [mode.value for mode in HeatingMode]
        ),
    }
)

SERVICE_SET_STRATEGY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_STRATEGY): vol.In(
            [strategy.value for strategy in RefillStrategy]
        ),
        vol.Optional(ATTR_CUSTOM_AMOUNT): vol.All(
            vol.Coerce(float), vol.Range(min=100, max=2000)
        ),
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DuraGas from a config entry."""
    coordinator = DuraGasDataUpdateCoordinator(hass, entry)

    await coordinator.async_load_stored_data()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await _async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        if not hass.data[DOMAIN]:
            _async_unregister_services(hass)

    return unload_ok


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register DuraGas services."""

    async def _get_coordinator() -> DuraGasDataUpdateCoordinator | None:
        """Get the first available coordinator."""
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No DuraGas integration configured")
            return None
        entry_id = next(iter(hass.data[DOMAIN]))
        return hass.data[DOMAIN][entry_id]

    async def handle_record_refill(call: ServiceCall) -> None:
        """Handle record_refill service call."""
        coordinator = await _get_coordinator()
        if coordinator is None:
            return

        liters: float = call.data[ATTR_LITERS]
        price_per_liter: float = call.data[ATTR_PRICE_PER_LITER]
        refill_date: datetime | None = call.data.get(ATTR_REFILL_DATE)

        await coordinator.async_record_refill(liters, price_per_liter, refill_date)

        _LOGGER.info(
            "Service record_refill called: %.2f L at %.2f MXN/L",
            liters,
            price_per_liter,
        )

    async def handle_update_level(call: ServiceCall) -> None:
        """Handle update_level service call."""
        coordinator = await _get_coordinator()
        if coordinator is None:
            return

        level_percent: float = call.data[ATTR_LEVEL_PERCENT]

        await coordinator.async_update_level(level_percent)

        _LOGGER.info("Service update_level called: %.1f%%", level_percent)

    async def handle_update_price(call: ServiceCall) -> None:
        """Handle update_price service call."""
        coordinator = await _get_coordinator()
        if coordinator is None:
            return

        price_per_liter: float = call.data[ATTR_PRICE_PER_LITER]

        await coordinator.async_update_price(price_per_liter)

        _LOGGER.info("Service update_price called: %.2f MXN/L", price_per_liter)

    async def handle_set_heating_mode(call: ServiceCall) -> None:
        """Handle set_heating_mode service call."""
        coordinator = await _get_coordinator()
        if coordinator is None:
            return

        mode_str: str = call.data[ATTR_MODE]
        mode = HeatingMode(mode_str)

        await coordinator.async_set_heating_mode(mode)

        _LOGGER.info("Service set_heating_mode called: %s", mode)

    async def handle_set_strategy(call: ServiceCall) -> None:
        """Handle set_strategy service call."""
        coordinator = await _get_coordinator()
        if coordinator is None:
            return

        strategy_str: str = call.data[ATTR_STRATEGY]
        strategy = RefillStrategy(strategy_str)
        custom_amount: float | None = call.data.get(ATTR_CUSTOM_AMOUNT)

        await coordinator.async_set_strategy(strategy, custom_amount)

        _LOGGER.info("Service set_strategy called: %s", strategy)

    if not hass.services.has_service(DOMAIN, SERVICE_RECORD_REFILL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RECORD_REFILL,
            handle_record_refill,
            schema=SERVICE_RECORD_REFILL_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_LEVEL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_UPDATE_LEVEL,
            handle_update_level,
            schema=SERVICE_UPDATE_LEVEL_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_PRICE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_UPDATE_PRICE,
            handle_update_price,
            schema=SERVICE_UPDATE_PRICE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_HEATING_MODE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_HEATING_MODE,
            handle_set_heating_mode,
            schema=SERVICE_SET_HEATING_MODE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_STRATEGY):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_STRATEGY,
            handle_set_strategy,
            schema=SERVICE_SET_STRATEGY_SCHEMA,
        )


def _async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister DuraGas services."""
    hass.services.async_remove(DOMAIN, SERVICE_RECORD_REFILL)
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_LEVEL)
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_PRICE)
    hass.services.async_remove(DOMAIN, SERVICE_SET_HEATING_MODE)
    hass.services.async_remove(DOMAIN, SERVICE_SET_STRATEGY)
