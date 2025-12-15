"""Tests for DuraGas calculations."""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta

# Test LP gas conversion
LP_GAS_KG_TO_LITERS = 1.96
WATER_HEATING_BASE_PERCENTAGE = 40


class TestLPGasConversions:
    """Test LP gas conversion calculations."""

    def test_kg_to_liters_conversion(self) -> None:
        """Test kg to liters conversion."""
        kg = 10.0
        liters = kg * LP_GAS_KG_TO_LITERS
        assert liters == pytest.approx(19.6, rel=0.01)

    def test_liters_to_kg_conversion(self) -> None:
        """Test liters to kg conversion."""
        liters = 19.6
        kg = liters / LP_GAS_KG_TO_LITERS
        assert kg == pytest.approx(10.0, rel=0.01)

    def test_zero_conversion(self) -> None:
        """Test zero value conversion."""
        assert 0 * LP_GAS_KG_TO_LITERS == 0
        assert 0 / LP_GAS_KG_TO_LITERS == 0


class TestTankCapacityCalculations:
    """Test tank capacity calculations."""

    def test_usable_capacity_80_percent(self) -> None:
        """Test 80% usable capacity calculation."""
        capacity = 120.0
        usable_percentage = 80
        usable_capacity = capacity * (usable_percentage / 100)
        assert usable_capacity == pytest.approx(96.0, rel=0.01)

    def test_usable_capacity_different_sizes(self) -> None:
        """Test usable capacity for different tank sizes."""
        tank_sizes = [120, 180, 300, 500, 1000]
        usable_percentage = 80

        for capacity in tank_sizes:
            usable_capacity = capacity * (usable_percentage / 100)
            assert usable_capacity == pytest.approx(capacity * 0.8, rel=0.01)

    def test_current_liters_calculation(self) -> None:
        """Test current liters calculation from percentage."""
        usable_capacity = 96.0  # 120L tank at 80%
        current_level = 50  # 50% full
        current_liters = usable_capacity * (current_level / 100)
        assert current_liters == pytest.approx(48.0, rel=0.01)

    def test_current_value_calculation(self) -> None:
        """Test current tank value calculation."""
        current_liters = 48.0
        price_per_liter = 10.88
        current_value = current_liters * price_per_liter
        assert current_value == pytest.approx(522.24, rel=0.01)


class TestConsumptionCalculations:
    """Test consumption calculations."""

    def test_daily_consumption(self) -> None:
        """Test daily consumption calculation."""
        liters_consumed = 30.0
        days_since_refill = 10
        daily_consumption = liters_consumed / days_since_refill
        assert daily_consumption == pytest.approx(3.0, rel=0.01)

    def test_monthly_consumption(self) -> None:
        """Test monthly consumption calculation."""
        daily_consumption = 3.0
        monthly_consumption = daily_consumption * 30
        assert monthly_consumption == pytest.approx(90.0, rel=0.01)

    def test_days_remaining(self) -> None:
        """Test days remaining calculation."""
        current_liters = 48.0
        daily_consumption = 3.0
        days_remaining = current_liters / daily_consumption
        assert days_remaining == pytest.approx(16.0, rel=0.01)

    def test_zero_consumption_handling(self) -> None:
        """Test handling of zero consumption."""
        liters_consumed = 0.0
        days_since_refill = 10

        if days_since_refill > 0:
            daily_consumption = liters_consumed / days_since_refill
        else:
            daily_consumption = 0.0

        assert daily_consumption == 0.0

    def test_zero_days_handling(self) -> None:
        """Test handling of zero days (avoid division by zero)."""
        liters_consumed = 30.0
        days_since_refill = 0

        # Should handle zero days gracefully
        daily_consumption = liters_consumed / max(days_since_refill, 1)
        assert daily_consumption == pytest.approx(30.0, rel=0.01)


class TestRefillStrategyCalculations:
    """Test refill strategy calculations."""

    def test_fill_complete_strategy(self) -> None:
        """Test fill complete strategy."""
        usable_capacity = 96.0
        current_liters = 20.0
        recommended_liters = max(usable_capacity - current_liters, 0)
        assert recommended_liters == pytest.approx(76.0, rel=0.01)

    def test_fixed_amount_strategy(self) -> None:
        """Test fixed amount (MXN) strategy."""
        fixed_amount_mxn = 300.0
        price_per_liter = 10.88
        recommended_liters = fixed_amount_mxn / price_per_liter
        assert recommended_liters == pytest.approx(27.57, rel=0.01)

    def test_level_target_strategy(self) -> None:
        """Test target level strategy."""
        usable_capacity = 96.0
        current_liters = 20.0
        target_level = 50  # 50%

        target_liters = usable_capacity * (target_level / 100)
        recommended_liters = max(target_liters - current_liters, 0)
        assert recommended_liters == pytest.approx(28.0, rel=0.01)

    def test_already_above_target(self) -> None:
        """Test when current level is above target."""
        usable_capacity = 96.0
        current_liters = 60.0
        target_level = 50  # 50%

        target_liters = usable_capacity * (target_level / 100)
        recommended_liters = max(target_liters - current_liters, 0)
        assert recommended_liters == 0.0

    def test_resulting_level_calculation(self) -> None:
        """Test resulting level after refill."""
        usable_capacity = 96.0
        current_liters = 20.0
        recommended_liters = 50.0

        resulting_level = ((current_liters + recommended_liters) / usable_capacity) * 100
        assert resulting_level == pytest.approx(72.92, rel=0.1)


class TestSolarSavingsCalculations:
    """Test solar water heater savings calculations."""

    def test_base_water_heating_consumption(self) -> None:
        """Test base water heating consumption calculation."""
        monthly_consumption = 90.0
        base_water_heating = monthly_consumption * (WATER_HEATING_BASE_PERCENTAGE / 100)
        assert base_water_heating == pytest.approx(36.0, rel=0.01)

    def test_solar_hybrid_savings(self) -> None:
        """Test solar hybrid mode savings."""
        base_water_heating = 36.0
        solar_efficiency = 70  # 70%
        price_per_liter = 10.88

        coverage = solar_efficiency / 100
        liters_saved = base_water_heating * coverage
        savings_monthly = liters_saved * price_per_liter

        assert liters_saved == pytest.approx(25.2, rel=0.01)
        assert savings_monthly == pytest.approx(274.18, rel=0.1)

    def test_solar_only_savings(self) -> None:
        """Test solar only mode savings (100% coverage)."""
        base_water_heating = 36.0
        price_per_liter = 10.88

        coverage = 1.0  # 100%
        liters_saved = base_water_heating * coverage
        savings_monthly = liters_saved * price_per_liter

        assert liters_saved == pytest.approx(36.0, rel=0.01)
        assert savings_monthly == pytest.approx(391.68, rel=0.01)

    def test_gas_only_no_savings(self) -> None:
        """Test gas only mode (no savings)."""
        base_water_heating = 36.0
        price_per_liter = 10.88

        coverage = 0.0  # 0%
        liters_saved = base_water_heating * coverage
        savings_monthly = liters_saved * price_per_liter

        assert liters_saved == 0.0
        assert savings_monthly == 0.0

    def test_roi_percentage(self) -> None:
        """Test ROI percentage calculation."""
        roi_accumulated = 5000.0
        solar_investment = 15000.0

        roi_percentage = (roi_accumulated / solar_investment) * 100
        assert roi_percentage == pytest.approx(33.33, rel=0.1)

    def test_months_to_payback(self) -> None:
        """Test months to payback calculation."""
        solar_investment = 15000.0
        roi_accumulated = 5000.0
        savings_monthly = 274.18

        remaining = solar_investment - roi_accumulated
        months_to_payback = remaining / savings_monthly
        assert months_to_payback == pytest.approx(36.47, rel=0.1)

    def test_already_paid_back(self) -> None:
        """Test when investment is already paid back."""
        solar_investment = 15000.0
        roi_accumulated = 16000.0
        savings_monthly = 274.18

        if roi_accumulated >= solar_investment:
            months_to_payback = 0
        else:
            months_to_payback = (solar_investment - roi_accumulated) / savings_monthly

        assert months_to_payback == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_tank(self) -> None:
        """Test calculations with empty tank."""
        current_level = 0
        usable_capacity = 96.0
        current_liters = usable_capacity * (current_level / 100)

        assert current_liters == 0.0

    def test_full_tank(self) -> None:
        """Test calculations with full tank."""
        current_level = 100
        usable_capacity = 96.0
        current_liters = usable_capacity * (current_level / 100)

        assert current_liters == pytest.approx(96.0, rel=0.01)

    def test_no_refill_history(self) -> None:
        """Test calculations with no refill history."""
        refill_history = []

        if not refill_history:
            daily_consumption = 0.0
            monthly_consumption = 0.0
            days_since_refill = 0

        assert daily_consumption == 0.0
        assert monthly_consumption == 0.0
        assert days_since_refill == 0

    def test_zero_solar_investment(self) -> None:
        """Test ROI with zero investment."""
        roi_accumulated = 1000.0
        solar_investment = 0.0

        # Avoid division by zero
        if solar_investment > 0:
            roi_percentage = (roi_accumulated / solar_investment) * 100
        else:
            roi_percentage = 0

        assert roi_percentage == 0

    def test_very_low_consumption(self) -> None:
        """Test with very low consumption values."""
        daily_consumption = 0.1
        current_liters = 48.0

        days_remaining = current_liters / daily_consumption
        assert days_remaining == pytest.approx(480.0, rel=0.01)

    def test_high_consumption(self) -> None:
        """Test with high consumption values."""
        daily_consumption = 10.0
        current_liters = 48.0

        days_remaining = current_liters / daily_consumption
        assert days_remaining == pytest.approx(4.8, rel=0.01)


class TestCylinderComparison:
    """Test comparison with cylinder baseline."""

    CYLINDER_MONTHLY_COST = 584.0  # 29kg @ 20.15 MXN/kg

    def test_savings_vs_cylinders(self) -> None:
        """Test savings calculation vs cylinders."""
        monthly_consumption = 60.0
        price_per_liter = 10.88

        monthly_cost = monthly_consumption * price_per_liter
        vs_cylinders = self.CYLINDER_MONTHLY_COST - monthly_cost

        assert monthly_cost == pytest.approx(652.8, rel=0.01)
        assert vs_cylinders == pytest.approx(-68.8, rel=0.1)  # Negative means more expensive

    def test_cheaper_than_cylinders(self) -> None:
        """Test when stationary is cheaper than cylinders."""
        monthly_consumption = 40.0
        price_per_liter = 10.88

        monthly_cost = monthly_consumption * price_per_liter
        vs_cylinders = self.CYLINDER_MONTHLY_COST - monthly_cost

        assert monthly_cost == pytest.approx(435.2, rel=0.01)
        assert vs_cylinders == pytest.approx(148.8, rel=0.1)  # Positive means savings
