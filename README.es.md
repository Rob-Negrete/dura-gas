# DuraGas - Monitor de Tanque de Gas LP para Home Assistant

**"Que tu gas dure más"**

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.10+-blue.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Una integración personalizada de Home Assistant para monitorear el consumo de gas LP y los ahorros del calentador solar de agua, diseñada específicamente para hogares mexicanos.

[Read in English](README.md)

## Características

### Monitoreo del Tanque
- Seguimiento del nivel del tanque en tiempo real (%, litros, kg)
- Valor actual del tanque en MXN
- Proyecciones de días y semanas restantes
- Predicción de fecha de próxima recarga

### Análisis de Consumo
- Tasas de consumo diario y mensual
- Seguimiento del consumo desde la última recarga
- Comparación de costos vs cilindros tradicionales

### Recomendaciones Inteligentes de Recarga
- Múltiples estrategias de recarga (llenar completo, montos fijos, niveles objetivo)
- Cantidades recomendadas según tu estrategia
- Proyecciones de costo para la próxima recarga

### ROI del Calentador Solar (Opcional)
- Seguimiento de ahorros mensuales por calentamiento solar
- Cálculo de ROI acumulado
- Proyección de meses para recuperar inversión
- Estimaciones de consumo de agua caliente

### Alertas
- Alertas de nivel bajo
- Alertas de recarga recomendada
- Estado del sistema solar

## Instalación

### Instalación Manual
1. Descarga la última versión
2. Copia la carpeta `custom_components/dura_gas` al directorio `custom_components` de tu Home Assistant
3. Reinicia Home Assistant
4. Ve a Configuración > Dispositivos y Servicios > Agregar Integración
5. Busca "DuraGas"

### Instalación via HACS (Próximamente)
1. Abre HACS
2. Busca "DuraGas"
3. Instala y reinicia Home Assistant

## Configuración

### Paso 1: Configuración del Tanque
- **Tamaño del Tanque**: Selecciona de los tamaños estándar mexicanos (120L, 180L, 300L, 500L, 1000L) o ingresa un tamaño personalizado
- **Porcentaje Utilizable**: Nivel máximo de llenado seguro (80% recomendado)
- **Nivel Inicial**: Nivel actual del tanque si lo conoces
- **Precio por Litro**: Precio actual del gas LP en MXN

### Paso 2: Calentador Solar de Agua (Opcional)
- **Tengo Solar**: Activa el seguimiento del calentador solar
- **Fecha de Instalación**: Cuándo se instaló tu calentador solar
- **Inversión Total**: Costo incluyendo instalación
- **Eficiencia**: Eficiencia estimada (70% es típico)

### Paso 3: Alertas y Estrategia
- **Alerta de Nivel Bajo**: Porcentaje de umbral de alerta
- **Umbral de Recarga**: Recomendar recarga por debajo de este nivel
- **Estrategia de Recarga**: Cómo prefieres recargar

## Sensores

### Estado del Tanque
| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| Nivel del Tanque | Porcentaje de llenado actual | % |
| Litros en Tanque | Volumen actual | L |
| Kilogramos en Tanque | Peso actual | kg |
| Valor del Tanque | Valor monetario actual | MXN |

### Consumo
| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| Consumo Diario | Uso promedio diario | L/día |
| Consumo Mensual | Uso promedio mensual | L/mes |
| Días Desde Recarga | Días desde última recarga | días |
| Litros Consumidos | Total consumido desde recarga | L |

### Proyecciones
| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| Días Restantes | Días estimados hasta vacío | días |
| Semanas Restantes | Semanas estimadas hasta vacío | semanas |
| Fecha Próxima Recarga | Fecha proyectada de recarga | timestamp |
| Litros Recomendados | Cantidad sugerida de recarga | L |
| Costo Recomendado | Costo estimado de recarga | MXN |

### Solar (si está habilitado)
| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| Eficiencia Solar | Porcentaje de eficiencia real | % |
| Ahorro Solar Mensual | Ahorros mensuales | MXN/mes |
| ROI Solar Acumulado | Ahorros totales acumulados | MXN |
| Consumo Agua Caliente | Uso diario de gas para agua caliente | L/día |

## Servicios

### `dura_gas.record_refill`
Registra una nueva recarga de gas.

```yaml
service: dura_gas.record_refill
data:
  liters: 96
  price_per_liter: 10.88
  refill_date: "2024-01-15 10:30:00"  # Opcional
```

### `dura_gas.update_level`
Actualiza manualmente el nivel del tanque.

```yaml
service: dura_gas.update_level
data:
  level_percent: 75
```

### `dura_gas.update_price`
Actualiza el precio actual del gas.

```yaml
service: dura_gas.update_price
data:
  price_per_liter: 11.50
```

### `dura_gas.set_heating_mode`
Cambia el modo de calentamiento de agua.

```yaml
service: dura_gas.set_heating_mode
data:
  mode: solar_gas_hybrid  # solar_gas_hybrid, solar_only, gas_only, none
```

### `dura_gas.set_strategy`
Cambia la estrategia de recarga.

```yaml
service: dura_gas.set_strategy
data:
  strategy: fill_complete  # fill_complete, fixed_300, fixed_400, etc.
  custom_amount: 450  # Solo para estrategia personalizada
```

## Ejemplo de Dashboard

```yaml
type: entities
title: Monitor de Gas LP
entities:
  - entity: sensor.duragas_tank_level
  - entity: sensor.duragas_tank_liters
  - entity: sensor.duragas_tank_value
  - entity: sensor.duragas_days_remaining
  - entity: sensor.duragas_next_refill_date
  - entity: binary_sensor.duragas_low_level
  - entity: binary_sensor.duragas_refill_recommended
```

## Ejemplos de Automatización

### Notificación de Nivel Bajo
```yaml
automation:
  - alias: "Gas LP - Alerta de Nivel Bajo"
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

### Resumen Semanal
```yaml
automation:
  - alias: "Gas LP - Resumen Semanal"
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

## Preguntas Frecuentes

### ¿Qué tamaños de tanque son compatibles?
Tamaños estándar mexicanos: 120L, 180L, 300L, 500L, 1000L, además de tamaños personalizados de 50L a 5000L.

### ¿Por qué la capacidad utilizable es del 80%?
Por seguridad, los tanques de gas LP no deben llenarse más del 80% para permitir la expansión térmica.

### ¿Qué tan precisas son las proyecciones?
Las proyecciones mejoran con el tiempo a medida que se recopilan más datos de recarga. Las proyecciones iniciales pueden ser menos precisas.

### ¿Funciona sin calentador solar de agua?
¡Sí! El seguimiento solar es opcional. La integración funciona muy bien para hogares que solo usan gas.

## Solución de Problemas

### Los sensores muestran "Desconocido"
Esto es normal antes de registrar la primera recarga. Registra una recarga para comenzar el seguimiento.

### Las proyecciones parecen incorrectas
Asegúrate de haber registrado al menos una recarga y actualizado el nivel actual con precisión.

### Los servicios no aparecen
Reinicia Home Assistant después de la instalación y revisa los logs en busca de errores.

## Contribuir

¡Las contribuciones son bienvenidas! Por favor lee nuestra [Guía de Contribución](.github/CONTRIBUTING.md).

## Licencia

Licencia MIT - ver [LICENSE](LICENSE) para más detalles.

## Soporte

- [Reportar Problemas](https://github.com/Rob-Negrete/ha-dura-gas/issues)
- [Solicitar Funciones](https://github.com/Rob-Negrete/ha-dura-gas/issues)
