"""DataUpdateCoordinator for DuraGas integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

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
    CYLINDER_MONTHLY_COST,
    DEFAULT_PRICE_PER_LITER,
    DEFAULT_SOLAR_EFFICIENCY,
    DEFAULT_USABLE_PERCENTAGE,
    DOMAIN,
    LP_GAS_KG_TO_LITERS,
    MAX_REFILL_HISTORY,
    SCAN_INTERVAL,
    STORAGE_KEY,
    STORAGE_VERSION,
    TANK_SIZES,
    WATER_HEATING_BASE_PERCENTAGE,
    HeatingMode,
    RefillStrategy,
)

_LOGGER = logging.getLogger(__name__)


class DuraGasDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching DuraGas data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.config_entry = entry
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}"
        )
        self._stored_data: dict[str, Any] = {}

    async def async_load_stored_data(self) -> None:
        """Load stored data from disk."""
        stored = await self._store.async_load()
        if stored:
            self._stored_data = stored
        else:
            self._stored_data = {
                "current_level": self.config_entry.data.get(CONF_INITIAL_LEVEL, 0),
                "refill_history": [],
                "solar_roi_accumulated": 0.0,
                "heating_mode": HeatingMode.SOLAR_GAS_HYBRID
                if self.config_entry.data.get(CONF_HAS_SOLAR, False)
                else HeatingMode.GAS_ONLY,
                "refill_strategy": self.config_entry.data.get(
                    CONF_REFILL_STRATEGY, RefillStrategy.FILL_COMPLETE
                ),
                "custom_strategy_amount": None,
                "last_solar_update": None,
            }

    async def _async_save_stored_data(self) -> None:
        """Save stored data to disk."""
        await self._store.async_save(self._stored_data)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the integration."""
        try:
            if not self._stored_data:
                await self.async_load_stored_data()

            config = self._build_config()
            tank = self._calculate_tank_state(config)
            consumption = self._calculate_consumption(tank)
            projection = self._calculate_projection(config, tank, consumption)
            last_refill = self._get_last_refill()
            strategy = self._calculate_strategy(config, consumption)
            solar = self._calculate_solar(config, consumption) if config["has_solar"] else None

            await self._update_solar_roi(solar)

            return {
                "config": config,
                "tank": tank,
                "consumption": consumption,
                "projection": projection,
                "last_refill": last_refill,
                "strategy": strategy,
                "solar": solar,
                "refill_history": self._stored_data.get("refill_history", []),
            }
        except Exception as err:
            _LOGGER.error("Error updating DuraGas data: %s", err)
            raise UpdateFailed(f"Error updating data: {err}") from err

    def _build_config(self) -> dict[str, Any]:
        """Build configuration dictionary."""
        entry_data = self.config_entry.data
        tank_size = entry_data.get(CONF_TANK_SIZE, "120")

        if tank_size == "custom":
            capacity = float(entry_data.get(CONF_TANK_CAPACITY_CUSTOM, 120))
        else:
            capacity = float(TANK_SIZES.get(tank_size, TANK_SIZES["120"])["capacity"])

        usable_percentage = entry_data.get(CONF_USABLE_PERCENTAGE, DEFAULT_USABLE_PERCENTAGE)
        usable_capacity = capacity * (usable_percentage / 100)

        return {
            "tank_size": tank_size,
            "capacity": capacity,
            "usable_capacity": usable_capacity,
            "usable_percentage": usable_percentage,
            "price_per_liter": entry_data.get(CONF_PRICE_PER_LITER, DEFAULT_PRICE_PER_LITER),
            "has_solar": entry_data.get(CONF_HAS_SOLAR, False),
            "solar_investment": entry_data.get(CONF_SOLAR_INVESTMENT, 0),
            "solar_efficiency": entry_data.get(CONF_SOLAR_EFFICIENCY, DEFAULT_SOLAR_EFFICIENCY),
            "solar_installation_date": entry_data.get(CONF_SOLAR_INSTALLATION_DATE),
            "heating_mode": HeatingMode(
                self._stored_data.get("heating_mode", HeatingMode.GAS_ONLY)
            ),
            "refill_strategy": RefillStrategy(
                self._stored_data.get("refill_strategy", RefillStrategy.FILL_COMPLETE)
            ),
            "low_threshold": entry_data.get(CONF_LOW_THRESHOLD, 20),
            "refill_threshold": entry_data.get(CONF_REFILL_THRESHOLD, 30),
        }

    def _calculate_tank_state(self, config: dict[str, Any]) -> dict[str, Any]:
        """Calculate current tank state."""
        current_level = self._stored_data.get("current_level", 0)
        usable_capacity = config["usable_capacity"]
        price_per_liter = config["price_per_liter"]

        current_liters = usable_capacity * (current_level / 100)
        current_kg = current_liters / LP_GAS_KG_TO_LITERS
        current_value = current_liters * price_per_liter

        return {
            "capacity": config["capacity"],
            "usable_capacity": usable_capacity,
            "current_level": current_level,
            "current_liters": round(current_liters, 2),
            "current_kg": round(current_kg, 2),
            "current_value": round(current_value, 2),
        }

    def _calculate_consumption(self, tank: dict[str, Any]) -> dict[str, Any]:
        """Calculate consumption statistics."""
        refill_history = self._stored_data.get("refill_history", [])

        if not refill_history:
            return {
                "daily": 0.0,
                "monthly": 0.0,
                "days_since_refill": 0,
                "liters_consumed": 0.0,
            }

        last_refill = refill_history[-1]
        last_refill_date = datetime.fromisoformat(last_refill["date"])
        now = dt_util.now()
        days_since_refill = max((now - last_refill_date).days, 1)

        level_after_refill = last_refill.get("level_after", 100)
        current_level = self._stored_data.get("current_level", 0)
        usable_capacity = tank["usable_capacity"]

        liters_at_refill = usable_capacity * (level_after_refill / 100)
        current_liters = usable_capacity * (current_level / 100)
        liters_consumed = max(liters_at_refill - current_liters, 0)

        daily_consumption = liters_consumed / days_since_refill if days_since_refill > 0 else 0
        monthly_consumption = daily_consumption * 30

        return {
            "daily": round(daily_consumption, 2),
            "monthly": round(monthly_consumption, 2),
            "days_since_refill": days_since_refill,
            "liters_consumed": round(liters_consumed, 2),
        }

    def _calculate_projection(
        self,
        config: dict[str, Any],
        tank: dict[str, Any],
        consumption: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate projections."""
        daily_consumption = consumption["daily"]
        current_liters = tank["current_liters"]
        usable_capacity = tank["usable_capacity"]
        price_per_liter = config["price_per_liter"]
        strategy = config["refill_strategy"]

        if daily_consumption > 0:
            days_remaining = current_liters / daily_consumption
            weeks_remaining = days_remaining / 7
            next_refill_date = dt_util.now() + timedelta(days=days_remaining)
        else:
            days_remaining = float("inf")
            weeks_remaining = float("inf")
            next_refill_date = None

        recommended_liters = self._calculate_recommended_liters(
            strategy, usable_capacity, current_liters, price_per_liter
        )
        recommended_cost = recommended_liters * price_per_liter
        resulting_level = ((current_liters + recommended_liters) / usable_capacity) * 100

        return {
            "days_remaining": round(days_remaining, 1) if days_remaining != float("inf") else None,
            "weeks_remaining": round(weeks_remaining, 1)
            if weeks_remaining != float("inf")
            else None,
            "next_refill_date": next_refill_date.isoformat() if next_refill_date else None,
            "recommended_liters": round(recommended_liters, 2),
            "recommended_cost": round(recommended_cost, 2),
            "resulting_level": round(min(resulting_level, 100), 1),
        }

    def _calculate_recommended_liters(
        self,
        strategy: RefillStrategy,
        usable_capacity: float,
        current_liters: float,
        price_per_liter: float,
    ) -> float:
        """Calculate recommended liters based on strategy."""
        match strategy:
            case RefillStrategy.FILL_COMPLETE:
                return max(usable_capacity - current_liters, 0)
            case RefillStrategy.FIXED_300:
                return 300 / price_per_liter
            case RefillStrategy.FIXED_400:
                return 400 / price_per_liter
            case RefillStrategy.FIXED_500:
                return 500 / price_per_liter
            case RefillStrategy.FIXED_600:
                return 600 / price_per_liter
            case RefillStrategy.LEVEL_50:
                target = usable_capacity * 0.5
                return max(target - current_liters, 0)
            case RefillStrategy.LEVEL_60:
                target = usable_capacity * 0.6
                return max(target - current_liters, 0)
            case RefillStrategy.LEVEL_70:
                target = usable_capacity * 0.7
                return max(target - current_liters, 0)
            case RefillStrategy.CUSTOM:
                custom_amount = self._stored_data.get("custom_strategy_amount", 400)
                return (custom_amount or 400) / price_per_liter
            case _:
                return max(usable_capacity - current_liters, 0)

    def _get_last_refill(self) -> dict[str, Any]:
        """Get last refill information."""
        refill_history = self._stored_data.get("refill_history", [])

        if not refill_history:
            return {
                "date": None,
                "liters": None,
                "price_per_liter": None,
                "total_cost": None,
            }

        last = refill_history[-1]
        return {
            "date": last.get("date"),
            "liters": last.get("liters"),
            "price_per_liter": last.get("price_per_liter"),
            "total_cost": last.get("total_cost"),
        }

    def _calculate_strategy(
        self,
        config: dict[str, Any],
        consumption: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate strategy analysis."""
        monthly_consumption = consumption["monthly"]
        price_per_liter = config["price_per_liter"]

        monthly_cost = monthly_consumption * price_per_liter
        vs_cylinders = CYLINDER_MONTHLY_COST - monthly_cost

        usable_capacity = config["usable_capacity"]
        if monthly_consumption > 0:
            refills_per_month = monthly_consumption / usable_capacity
        else:
            refills_per_month = 0

        return {
            "current": config["refill_strategy"],
            "monthly_cost": round(monthly_cost, 2),
            "refills_per_month": round(refills_per_month, 2),
            "vs_cylinders": round(vs_cylinders, 2),
        }

    def _calculate_solar(
        self,
        config: dict[str, Any],
        consumption: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate solar savings."""
        monthly_consumption = consumption["monthly"]
        price_per_liter = config["price_per_liter"]
        solar_efficiency = config["solar_efficiency"]
        solar_investment = config["solar_investment"]
        heating_mode = config["heating_mode"]

        base_water_heating = monthly_consumption * (WATER_HEATING_BASE_PERCENTAGE / 100)

        match heating_mode:
            case HeatingMode.SOLAR_GAS_HYBRID:
                coverage = solar_efficiency / 100
            case HeatingMode.SOLAR_ONLY:
                coverage = 1.0
            case _:
                coverage = 0.0

        liters_saved = base_water_heating * coverage
        savings_monthly = liters_saved * price_per_liter

        roi_accumulated = self._stored_data.get("solar_roi_accumulated", 0.0)
        roi_percentage = (roi_accumulated / solar_investment * 100) if solar_investment > 0 else 0

        if savings_monthly > 0 and solar_investment > roi_accumulated:
            months_to_payback = (solar_investment - roi_accumulated) / savings_monthly
        else:
            months_to_payback = 0 if roi_accumulated >= solar_investment else float("inf")

        hot_water_consumption = base_water_heating / 30 if monthly_consumption > 0 else 0

        return {
            "efficiency_real": solar_efficiency,
            "savings_monthly": round(savings_monthly, 2),
            "roi_accumulated": round(roi_accumulated, 2),
            "roi_percentage": round(roi_percentage, 2),
            "months_to_payback": round(months_to_payback, 1)
            if months_to_payback != float("inf")
            else None,
            "hot_water_consumption": round(hot_water_consumption, 2),
            "heating_mode": heating_mode,
        }

    async def _update_solar_roi(self, solar: dict[str, Any] | None) -> None:
        """Update solar ROI monthly."""
        if not solar:
            return

        now = dt_util.now()
        last_update = self._stored_data.get("last_solar_update")

        if last_update:
            last_update_date = datetime.fromisoformat(last_update)
            if now.month != last_update_date.month or now.year != last_update_date.year:
                self._stored_data["solar_roi_accumulated"] += solar["savings_monthly"]
                self._stored_data["last_solar_update"] = now.isoformat()
                await self._async_save_stored_data()
        else:
            self._stored_data["last_solar_update"] = now.isoformat()
            await self._async_save_stored_data()

    async def async_record_refill(
        self,
        liters: float,
        price_per_liter: float,
        refill_date: datetime | None = None,
    ) -> None:
        """Record a new refill."""
        if refill_date is None:
            refill_date = dt_util.now()

        config = self._build_config()
        usable_capacity = config["usable_capacity"]

        level_before = self._stored_data.get("current_level", 0)
        liters_before = usable_capacity * (level_before / 100)
        liters_after = liters_before + liters
        level_after = min((liters_after / usable_capacity) * 100, 100)

        refill_entry = {
            "date": refill_date.isoformat(),
            "liters": liters,
            "price_per_liter": price_per_liter,
            "total_cost": round(liters * price_per_liter, 2),
            "level_before": round(level_before, 1),
            "level_after": round(level_after, 1),
        }

        refill_history = self._stored_data.get("refill_history", [])
        refill_history.append(refill_entry)

        if len(refill_history) > MAX_REFILL_HISTORY:
            refill_history = refill_history[-MAX_REFILL_HISTORY:]

        self._stored_data["refill_history"] = refill_history
        self._stored_data["current_level"] = level_after

        await self._async_save_stored_data()
        await self.async_refresh()

        _LOGGER.info(
            "Recorded refill: %.2f L at %.2f MXN/L, level: %.1f%% -> %.1f%%",
            liters,
            price_per_liter,
            level_before,
            level_after,
        )

    async def async_update_level(self, level_percent: float) -> None:
        """Update current tank level."""
        level_percent = max(0, min(100, level_percent))
        self._stored_data["current_level"] = level_percent

        await self._async_save_stored_data()
        await self.async_refresh()

        _LOGGER.info("Updated tank level to %.1f%%", level_percent)

    async def async_update_price(self, price_per_liter: float) -> None:
        """Update gas price."""
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data={**self.config_entry.data, CONF_PRICE_PER_LITER: price_per_liter},
        )
        await self.async_refresh()

        _LOGGER.info("Updated gas price to %.2f MXN/L", price_per_liter)

    async def async_set_heating_mode(self, mode: HeatingMode) -> None:
        """Set water heating mode."""
        self._stored_data["heating_mode"] = mode

        await self._async_save_stored_data()
        await self.async_refresh()

        _LOGGER.info("Set heating mode to %s", mode)

    async def async_set_strategy(
        self,
        strategy: RefillStrategy,
        custom_amount: float | None = None,
    ) -> None:
        """Set refill strategy."""
        self._stored_data["refill_strategy"] = strategy
        if strategy == RefillStrategy.CUSTOM and custom_amount is not None:
            self._stored_data["custom_strategy_amount"] = custom_amount

        await self._async_save_stored_data()
        await self.async_refresh()

        _LOGGER.info("Set refill strategy to %s", strategy)
