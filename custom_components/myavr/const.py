"""Constants for the MyAVR ATS Controller integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "myavr"

DEFAULT_NAME: Final = "MyAVR ATS"
DEFAULT_PORT: Final = 502
DEFAULT_DEVICE_ID: Final = 0
DEFAULT_SCAN_INTERVAL: Final = 15

CONF_DEVICE_ID: Final = "device_id"

# Manufacturer / model reported by the controller over SNMP sysDescr.
MANUFACTURER: Final = "MyAVR.ru"
MODEL: Final = "ATS controller"

# The controller expects the FULL register number as the Modbus PDU address
# (e.g. read register 30001 with address=30001), not a zero-based offset.
# Verified against the physical device 192.168.100.46.

# Input registers (FC04) — read only.
REG_MAINS_L1: Final = 30001
REG_MAINS_L2: Final = 30002
REG_MAINS_L3: Final = 30003
REG_MAINS_L1_MIN: Final = 30004
REG_MAINS_L2_MIN: Final = 30005
REG_MAINS_L3_MIN: Final = 30006
REG_MAINS_L1_MAX: Final = 30007
REG_MAINS_L2_MAX: Final = 30008
REG_MAINS_L3_MAX: Final = 30009
REG_GEN_L1: Final = 30010
REG_GEN_L2: Final = 30011
REG_GEN_L3: Final = 30012
REG_GEN_L1_MIN: Final = 30013
REG_GEN_L2_MIN: Final = 30014
REG_GEN_L3_MIN: Final = 30015
REG_GEN_L1_MAX: Final = 30016
REG_GEN_L2_MAX: Final = 30017
REG_GEN_L3_MAX: Final = 30018
REG_INV_BATTERY: Final = 30019
REG_INV_BATTERY_MIN: Final = 30020
REG_INV_BATTERY_MAX: Final = 30021
REG_START_COMMAND_SENT: Final = 30022
REG_ERROR_FIRST: Final = 30023
REG_ERROR_LAST: Final = 30042
REG_NO_ERRORS: Final = 30099
REG_MAINS_FREQ: Final = 30100
REG_MAINS_FREQ_TOLERANCE: Final = 30101
REG_GEN_FREQ: Final = 30102
REG_GEN_FREQ_TOLERANCE: Final = 30103
REG_ENGINE_HOURS_CURRENT: Final = 30104
REG_ENGINE_HOURS_SETPOINT: Final = 30105
REG_ENGINE_HOURS_TOTAL: Final = 30106
REG_PREVENTIVE_START_FLAG: Final = 30107
REG_START_MODE: Final = 30108
REG_STARTS_SINCE_OIL: Final = 30109
REG_STARTS_TOTAL: Final = 30110
REG_SCHEDULE_ENABLED: Final = 30111
REG_SCHEDULE_INHIBIT: Final = 30112
REG_CONTACTOR_POSITION: Final = 30113

# Contiguous read blocks (start_register, count).
# Reading in blocks keeps polling fast and avoids per-register round trips.
READ_BLOCKS: Final = [
    (30001, 42),   # 30001..30042
    (30099, 15),   # 30099..30113
]

# Holding registers (FC03/FC06) — command registers, write pulse of 1.
REG_CMD_START: Final = 40001
REG_CMD_STOP: Final = 40002
REG_CMD_MODE_AUTO: Final = 40003
REG_CMD_MODE_MANUAL: Final = 40004
REG_CMD_MODE_ECO: Final = 40005
REG_CMD_SCHEDULE_ON: Final = 40006
REG_CMD_SCHEDULE_OFF: Final = 40007

# Value scaling: these registers report tenths.
SCALE_TENTH: Final = frozenset(
    {
        REG_INV_BATTERY,
        REG_INV_BATTERY_MIN,
        REG_INV_BATTERY_MAX,
        REG_MAINS_FREQ,
        REG_GEN_FREQ,
    }
)

# Start mode enum (register 30108).
START_MODE_MANUAL: Final = 0
START_MODE_AUTO: Final = 1
START_MODE_ECO: Final = 2
START_MODE_MAP: Final = {
    START_MODE_MANUAL: "manual",
    START_MODE_AUTO: "auto",
    START_MODE_ECO: "eco",
}

# Contactor position enum (register 30113).
CONTACTOR_MAP: Final = {
    0: "undefined",
    1: "off",
    2: "mains",
    3: "generator",
}

# Human-readable error descriptions (registers 30023..30042 -> errors 1..20).
ERROR_DESCRIPTIONS: Final = {
    1: "Аварийная остановка генератора",
    2: "Напряжение сети выше порога",
    3: "Напряжение сети ниже порога",
    4: "Авария контактора (нет напряжения на выходе)",
    5: "Падение напряжения на контакторе",
    6: "OilService: замените масло в генераторе",
    7: "Внутренняя ошибка (блок питания)",
    8: "Системное время не установлено",
    9: "Авария контактора (залипание)",
    10: "Ошибка запуска генератора",
    11: "Ошибка чередования фаз сети",
    12: "Ошибка чередования фаз генератора",
    13: "Ошибка контроля трёх фаз сети",
    14: "Ошибка контроля трёх фаз генератора",
    15: "Ошибка профилактического запуска",
    16: "Частота городской сети вне диапазона",
    17: "Частота генератора вне диапазона",
    18: "Напряжение генератора выше порога",
    19: "Напряжение генератора ниже порога",
    20: "Нажата внешняя кнопка «Аварийная остановка»",
}
