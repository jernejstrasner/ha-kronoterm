"""Constants for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "kronoterm"

DEFAULT_PORT: Final = 8099
DEFAULT_SCAN_INTERVAL: Final = 15  # seconds

# Raw register values that mean "no sensor / not set" (after signed conversion).
SENTINEL_NO_SENSOR: Final = -600  # -60.0 °C
SENTINEL_UNSET: Final = 0x3FFF  # 16383

# ---------------------------------------------------------------- registers
# System
REG_SYSTEM_ON: Final = 2012
REG_OPERATION_PROGRAM_SELECT: Final = 2013  # 0 normal / 1 eco / 2 comfort
REG_SYSTEM_TEMP_CORRECTION: Final = 2014
REG_VACATION_MODE: Final = 2022
REG_WORKING_FUNCTION: Final = 2001
REG_ERROR_WARNING: Final = 2006
REG_OPERATION_REGIME: Final = 2007  # 0 cooling / 1 heating / 2 off
REG_OPERATION_PROGRAM: Final = 2008
REG_DEFROST_STATUS: Final = 2011
REG_ERROR_FLAGS: Final = 2114

# DHW
REG_DHW_SETPOINT: Final = 2023
REG_DHW_CURRENT_SETPOINT: Final = 2024
REG_DHW_OPERATION_MODE: Final = 2026  # 0 off / 1 normal / 2 schedule
REG_DHW_TEMP: Final = 2102
REG_DHW_CIRCULATION_STATUS: Final = 2028
REG_DHW_CIRCULATION_PUMP: Final = 2328
REG_THERMAL_DISINFECTION: Final = 2301

# Temperatures
REG_HP_INLET_TEMP: Final = 2101
REG_OUTSIDE_TEMP: Final = 2103
REG_HP_OUTLET_TEMP: Final = 2104
REG_COMPRESSOR_INLET_TEMP: Final = 2105
REG_COMPRESSOR_OUTLET_TEMP: Final = 2106

# Performance
REG_POWER: Final = 2129  # W, electrical input
REG_CAPACITY: Final = 2329  # W, thermal output
REG_COP: Final = 2371  # x0.01
REG_SCOP: Final = 2372  # x0.01
# NOTE: documented counters 2361/2363 read 0 on firmware 3.16-1; the live
# counters are the (formerly undocumented) 2362/2364.
REG_ELECTRICAL_ENERGY: Final = 2362  # x1 kWh, lifetime
REG_HEATING_ENERGY: Final = 2364  # x0.1 kWh, lifetime
REG_PRESSURE: Final = 2326  # x0.1 bar
REG_HP_LOAD: Final = 2327  # %

# Runtime
REG_COMPRESSOR_STATUS: Final = 2318
REG_MAIN_PUMP_STATUS: Final = 2038
REG_HOURS_COOLING: Final = 2089
REG_HOURS_COMPRESSOR_HEATING: Final = 2090
REG_HOURS_COMPRESSOR_DHW: Final = 2091
REG_COMPRESSOR_MINUTES_DAILY: Final = 2092

# Heating/cooling loops (N = 1..4): temp, setpoint, mode, pump
LOOPS: Final = {
    1: {"temp": 2130, "setpoint": 2187, "mode": 2042, "pump": 2045},
    2: {"temp": 2110, "setpoint": 2049, "mode": 2052, "pump": 2055},
    3: {"temp": 2111, "setpoint": 2059, "mode": 2062, "pump": 2065},
    4: {"temp": 2112, "setpoint": 2069, "mode": 2072, "pump": 2075},
}
LOOP_MODE_OFF: Final = 0
LOOP_MODE_NORMAL: Final = 1
LOOP_MODE_SCHEDULE: Final = 2

# Per-loop heating curve + program offsets (N = 1..4)
LOOP_CURVE_COLD: Final = {1: 2309, 2: 2310, 3: 2311, 4: 2312}  # water °C at cold point
LOOP_CURVE_WARM: Final = {1: 2314, 2: 2315, 3: 2316, 4: 2317}  # water °C at warm point
LOOP_ADAPTIVE_CURVE: Final = {1: 2320, 2: 2321, 3: 2322, 4: 2323}
LOOP_ECO_OFFSET: Final = {1: 2047, 2: 2057, 3: 2067, 4: 2077}  # x0.1 °C, signed
LOOP_COMFORT_OFFSET: Final = {1: 2048, 2: 2058, 3: 2068, 4: 2078}  # x0.1 °C, signed

# Experimental / undocumented registers (exposed disabled-by-default)
REG_EXPERIMENTAL: Final = {
    2131: ("reg_2131", 1.0, None),
    2145: ("reg_2145_theoretical_cop", 0.01, None),
    2147: ("reg_2147_load", 1.0, "%"),
    2172: ("reg_2172_theoretical_power", 1.0, "W"),
    2184: ("reg_2184_fan_speed", 1.0, "%"),
    2361: ("reg_2361_electrical_energy_alt", 1.0, "kWh"),
    2363: ("reg_2363_thermal_energy_alt", 0.1, "kWh"),
}

# Enum mappings (register value -> state string)
WORKING_FUNCTION: Final = {
    0: "heating",
    1: "dhw",
    2: "cooling",
    3: "pool_heating",
    4: "dhw_overheating",
    5: "standby",
    7: "remote_off",
}
OPERATION_REGIME: Final = {0: "cooling", 1: "heating", 2: "off"}
OPERATION_PROGRAM: Final = {0: "normal", 1: "eco", 2: "comfort", 4: "screed_drying"}
ERROR_WARNING: Final = {0: "none", 1: "warning", 2: "alarm", 3: "notice"}
OPERATION_PROGRAM_SELECT: Final = {0: "normal", 1: "eco", 2: "comfort"}
DHW_MODE: Final = {0: "off", 1: "normal", 2: "schedule"}
