# DuraGas - LP Gas Tank Monitor for Home Assistant

**"Que tu gas dure más"** - Make your gas last longer

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.10+-blue.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Home Assistant custom integration for monitoring LP gas consumption and solar water heater savings, designed specifically for Mexican households.

[Leer en Español](README.es.md)

## Features

### Tank Monitoring
- Real-time tank level tracking (%, liters, kg)
- Current tank value in MXN
- Days and weeks remaining projections
- Next refill date prediction

### Consumption Analysis
- Daily and monthly consumption rates
- Track consumption since last refill
- Compare costs vs traditional cylinders

### Smart Refill Recommendations
- Multiple refill strategies (fill complete, fixed amounts, target levels)
- Recommended refill amounts based on your strategy
- Cost projections for next refill

### Solar Water Heater ROI (Optional)
- Track monthly savings from solar heating
- Accumulated ROI calculation
- Months to payback projection
- Hot water consumption estimates

### Alerts
- Low level alerts
- Refill recommended alerts
- Solar system status

## Installation

### Manual Installation
1. Download the latest release
2. Copy the `custom_components/dura_gas` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Go to Settings > Devices & Services > Add Integration
5. Search for "DuraGas"

### HACS Installation (Coming Soon)
1. Open HACS
2. Search for "DuraGas"
3. Install and restart Home Assistant

## Configuration

### Step 1: Tank Configuration
- **Tank Size**: Select from standard Mexican tank sizes (120L, 180L, 300L, 500L, 1000L) or enter a custom size
- **Usable Percentage**: Maximum safe fill level (80% recommended)
- **Initial Level**: Current tank level if known
- **Price per Liter**: Current LP gas price in MXN

### Step 2: Solar Water Heater (Optional)
- **Has Solar**: Enable solar water heater tracking
- **Installation Date**: When your solar heater was installed
- **Total Investment**: Cost including installation
- **Efficiency**: Estimated efficiency (70% typical)

### Step 3: Alerts & Strategy
- **Low Level Alert**: Alert threshold percentage
- **Refill Threshold**: Recommend refill below this level
- **Refill Strategy**: How you prefer to refill

## Sensors

### Tank State
| Sensor | Description | Unit |
|--------|-------------|------|
| Tank Level | Current fill percentage | % |
| Tank Liters | Current volume | L |
| Tank Kilograms | Current weight | kg |
| Tank Value | Current monetary value | MXN |

### Consumption
| Sensor | Description | Unit |
|--------|-------------|------|
| Daily Consumption | Average daily usage | L/day |
| Monthly Consumption | Average monthly usage | L/month |
| Days Since Refill | Days since last refill | days |
| Liters Consumed | Total consumed since refill | L |

### Projections
| Sensor | Description | Unit |
|--------|-------------|------|
| Days Remaining | Estimated days until empty | days |
| Weeks Remaining | Estimated weeks until empty | weeks |
| Next Refill Date | Projected refill date | timestamp |
| Recommended Liters | Suggested refill amount | L |
| Recommended Cost | Estimated refill cost | MXN |

### Solar (if enabled)
| Sensor | Description | Unit |
|--------|-------------|------|
| Solar Efficiency | Real efficiency percentage | % |
| Solar Savings Monthly | Monthly savings | MXN/month |
| Solar ROI Accumulated | Total accumulated savings | MXN |
| Hot Water Consumption | Daily hot water gas usage | L/day |

## Services

### `dura_gas.record_refill`
Record a new gas refill.

```yaml
service: dura_gas.record_refill
data:
  liters: 96
  price_per_liter: 10.88
  refill_date: "2024-01-15 10:30:00"  # Optional
```

### `dura_gas.update_level`
Manually update tank level.

```yaml
service: dura_gas.update_level
data:
  level_percent: 75
```

### `dura_gas.update_price`
Update current gas price.

```yaml
service: dura_gas.update_price
data:
  price_per_liter: 11.50
```

### `dura_gas.set_heating_mode`
Change water heating mode.

```yaml
service: dura_gas.set_heating_mode
data:
  mode: solar_gas_hybrid  # solar_gas_hybrid, solar_only, gas_only, none
```

### `dura_gas.set_strategy`
Change refill strategy.

```yaml
service: dura_gas.set_strategy
data:
  strategy: fill_complete  # fill_complete, fixed_300, fixed_400, etc.
  custom_amount: 450  # Only for custom strategy
```

## Dashboard Example

```yaml
type: entities
title: Gas LP Monitor
entities:
  - entity: sensor.duragas_tank_level
  - entity: sensor.duragas_tank_liters
  - entity: sensor.duragas_tank_value
  - entity: sensor.duragas_days_remaining
  - entity: sensor.duragas_next_refill_date
  - entity: binary_sensor.duragas_low_level
  - entity: binary_sensor.duragas_refill_recommended
```

## Automation Examples

### Low Level Notification
```yaml
automation:
  - alias: "Gas LP - Low Level Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.duragas_low_level
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Gas LP Bajo"
          message: >
            Nivel de gas: {{ states('sensor.duragas_tank_level') }}%
            Días restantes: {{ states('sensor.duragas_days_remaining') }}
```

### Weekly Summary
```yaml
automation:
  - alias: "Gas LP - Weekly Summary"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: notify.mobile_app
        data:
          title: "Resumen Semanal de Gas"
          message: >
            Nivel: {{ states('sensor.duragas_tank_level') }}%
            Consumo mensual: {{ states('sensor.duragas_monthly_consumption') }} L
            Costo mensual: ${{ states('sensor.duragas_monthly_cost') }} MXN
```

## FAQ

### What tank sizes are supported?
Standard Mexican sizes: 120L, 180L, 300L, 500L, 1000L, plus custom sizes from 50L to 5000L.

### Why is usable capacity 80%?
For safety, LP gas tanks should not be filled beyond 80% to allow for thermal expansion.

### How accurate are the projections?
Projections improve over time as more refill data is collected. Initial projections may be less accurate.

### Does it work without a solar water heater?
Yes! Solar tracking is optional. The integration works great for gas-only households.

## Troubleshooting

### Sensors show "Unknown"
This is normal before the first refill is recorded. Record a refill to start tracking.

### Projections seem wrong
Make sure you've recorded at least one refill and updated the current level accurately.

### Services not appearing
Restart Home Assistant after installation and check the logs for errors.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](.github/CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [Report Issues](https://github.com/Rob-Negrete/ha-dura-gas/issues)
- [Feature Requests](https://github.com/Rob-Negrete/ha-dura-gas/issues)
