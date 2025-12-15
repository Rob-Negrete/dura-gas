"""Config flow for DuraGas integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_HAS_SOLAR,
    CONF_INITIAL_LEVEL,
    CONF_LOW_THRESHOLD,
    CONF_PRICE_PER_LITER,
    CONF_REFILL_STRATEGY,
    CONF_REFILL_THRESHOLD,
    CONF_SOLAR_EFFICIENCY,
    CONF_SOLAR_INSTALLATION_DATE,
    CONF_SOLAR_INVESTMENT,
    CONF_TANK_CAPACITY_CUSTOM,
    CONF_TANK_SIZE,
    CONF_USABLE_PERCENTAGE,
    DEFAULT_PRICE_PER_LITER,
    DEFAULT_SOLAR_EFFICIENCY,
    DEFAULT_USABLE_PERCENTAGE,
    DOMAIN,
    RefillStrategy,
)

_LOGGER = logging.getLogger(__name__)

TANK_SIZE_OPTIONS = [
    selector.SelectOptionDict(value="120", label="120L - Casa pequeña (2-3 personas)"),
    selector.SelectOptionDict(
        value="180", label="180L - Casa mediana (4-6 personas) ⭐"
    ),
    selector.SelectOptionDict(
        value="300", label="300L - Casa grande / Comercio pequeño"
    ),
    selector.SelectOptionDict(value="500", label="500L - Comercio mediano"),
    selector.SelectOptionDict(value="1000", label="1000L - Comercio grande"),
    selector.SelectOptionDict(value="custom", label="Personalizado"),
]

REFILL_STRATEGY_OPTIONS = [
    selector.SelectOptionDict(value="fill_complete", label="Llenar completo (80%)"),
    selector.SelectOptionDict(value="fixed_300", label="Monto fijo: $300 MXN"),
    selector.SelectOptionDict(value="fixed_400", label="Monto fijo: $400 MXN"),
    selector.SelectOptionDict(value="fixed_500", label="Monto fijo: $500 MXN"),
    selector.SelectOptionDict(value="fixed_600", label="Monto fijo: $600 MXN"),
    selector.SelectOptionDict(value="level_50", label="Llenar hasta 50%"),
    selector.SelectOptionDict(value="level_60", label="Llenar hasta 60%"),
    selector.SelectOptionDict(value="level_70", label="Llenar hasta 70%"),
    selector.SelectOptionDict(value="custom", label="Personalizado"),
]


class DuraGasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DuraGas."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> DuraGasOptionsFlow:
        """Get the options flow for this handler."""
        return DuraGasOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - tank configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, "120")

            if tank_size == "custom":
                custom_capacity = user_input.get(CONF_TANK_CAPACITY_CUSTOM)
                if custom_capacity is None or custom_capacity < 50 or custom_capacity > 5000:
                    errors["base"] = "invalid_capacity"

            if not errors:
                self._data.update(user_input)
                return await self.async_step_solar()

        schema = vol.Schema(
            {
                vol.Required(CONF_TANK_SIZE, default="120"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=TANK_SIZE_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_TANK_CAPACITY_CUSTOM): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=50,
                        max=5000,
                        step=1,
                        unit_of_measurement="L",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_USABLE_PERCENTAGE, default=DEFAULT_USABLE_PERCENTAGE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=70,
                        max=90,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(CONF_INITIAL_LEVEL, default=0): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(
                    CONF_PRICE_PER_LITER, default=DEFAULT_PRICE_PER_LITER
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=8.0,
                        max=20.0,
                        step=0.01,
                        unit_of_measurement="MXN/L",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_solar(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the solar configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_alerts()

        schema = vol.Schema(
            {
                vol.Required(CONF_HAS_SOLAR, default=False): selector.BooleanSelector(),
                vol.Optional(CONF_SOLAR_INSTALLATION_DATE): selector.DateSelector(),
                vol.Optional(
                    CONF_SOLAR_INVESTMENT, default=15000
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100000,
                        step=100,
                        unit_of_measurement="MXN",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_SOLAR_EFFICIENCY, default=DEFAULT_SOLAR_EFFICIENCY
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="solar",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_alerts(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the alerts and strategy configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            low_threshold = user_input.get(CONF_LOW_THRESHOLD, 20)
            refill_threshold = user_input.get(CONF_REFILL_THRESHOLD, 30)

            if refill_threshold < low_threshold:
                errors["base"] = "invalid_thresholds"

            if not errors:
                self._data.update(user_input)
                return self.async_create_entry(
                    title="DuraGas Tank Monitor",
                    data=self._data,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_LOW_THRESHOLD, default=20): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=10,
                        max=50,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(
                    CONF_REFILL_THRESHOLD, default=30
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=10,
                        max=50,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(
                    CONF_REFILL_STRATEGY, default=RefillStrategy.FILL_COMPLETE
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=REFILL_STRATEGY_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="alerts",
            data_schema=schema,
            errors=errors,
        )


class DuraGasOptionsFlow(OptionsFlow):
    """Handle DuraGas options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._data: dict[str, Any] = dict(config_entry.data)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow - tank configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, "120")

            if tank_size == "custom":
                custom_capacity = user_input.get(CONF_TANK_CAPACITY_CUSTOM)
                if custom_capacity is None or custom_capacity < 50 or custom_capacity > 5000:
                    errors["base"] = "invalid_capacity"

            if not errors:
                self._data.update(user_input)
                return await self.async_step_solar()

        current_data = self._config_entry.data

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_TANK_SIZE, default=current_data.get(CONF_TANK_SIZE, "120")
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=TANK_SIZE_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_TANK_CAPACITY_CUSTOM,
                    default=current_data.get(CONF_TANK_CAPACITY_CUSTOM),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=50,
                        max=5000,
                        step=1,
                        unit_of_measurement="L",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_USABLE_PERCENTAGE,
                    default=current_data.get(
                        CONF_USABLE_PERCENTAGE, DEFAULT_USABLE_PERCENTAGE
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=70,
                        max=90,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(
                    CONF_PRICE_PER_LITER,
                    default=current_data.get(
                        CONF_PRICE_PER_LITER, DEFAULT_PRICE_PER_LITER
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=8.0,
                        max=20.0,
                        step=0.01,
                        unit_of_measurement="MXN/L",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_solar(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the solar configuration step."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_alerts()

        current_data = self._config_entry.data

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HAS_SOLAR, default=current_data.get(CONF_HAS_SOLAR, False)
                ): selector.BooleanSelector(),
                vol.Optional(
                    CONF_SOLAR_INSTALLATION_DATE,
                    default=current_data.get(CONF_SOLAR_INSTALLATION_DATE),
                ): selector.DateSelector(),
                vol.Optional(
                    CONF_SOLAR_INVESTMENT,
                    default=current_data.get(CONF_SOLAR_INVESTMENT, 15000),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100000,
                        step=100,
                        unit_of_measurement="MXN",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_SOLAR_EFFICIENCY,
                    default=current_data.get(
                        CONF_SOLAR_EFFICIENCY, DEFAULT_SOLAR_EFFICIENCY
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="solar",
            data_schema=schema,
        )

    async def async_step_alerts(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the alerts and strategy configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            low_threshold = user_input.get(CONF_LOW_THRESHOLD, 20)
            refill_threshold = user_input.get(CONF_REFILL_THRESHOLD, 30)

            if refill_threshold < low_threshold:
                errors["base"] = "invalid_thresholds"

            if not errors:
                self._data.update(user_input)
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data=self._data,
                )
                return self.async_create_entry(title="", data={})

        current_data = self._config_entry.data

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOW_THRESHOLD,
                    default=current_data.get(CONF_LOW_THRESHOLD, 20),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=10,
                        max=50,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(
                    CONF_REFILL_THRESHOLD,
                    default=current_data.get(CONF_REFILL_THRESHOLD, 30),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=10,
                        max=50,
                        step=1,
                        unit_of_measurement="%",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required(
                    CONF_REFILL_STRATEGY,
                    default=current_data.get(
                        CONF_REFILL_STRATEGY, RefillStrategy.FILL_COMPLETE
                    ),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=REFILL_STRATEGY_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="alerts",
            data_schema=schema,
            errors=errors,
        )
