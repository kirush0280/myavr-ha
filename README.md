# MyAVR ATS Controller — интеграция для Home Assistant

Интеграция для контроллера АВР (ввода резерва) [MyAVR.ru](https://myavr.ru).
Читает статус городской сети и генератора, положение контактора, ошибки,
моточасы и режим работы; позволяет отдавать команды старт/стоп генератора
и управлять расписанием профилактических запусков.

Транспорт — Modbus TCP (порт 502). SNMP и MQTT контроллер тоже поддерживает,
но здесь используется только Modbus как самый полный по составу данных.

<p align="center">
  <img src="custom_components/myavr/brand/logo.png" alt="MyAVR" width="240">
</p>

## Возможности

- **46 сущностей** после установки: сеть L1/L2/L3, ген L1/L2/L3, частоты,
  батарея инвертора, положение контактора, режим работы, моточасы (текущие,
  до замены масла, общие), 20 отдельных индикаторов ошибок, флаги
  расписания, кнопки старт/стоп/расписание.
- **Русская локализация** для всех сущностей (имена + иконки).
- **Локальный логотип и иконка** интеграции (HA 2026.3+ раздаёт через
  свой API, без внешних CDN).
- **Config Flow** — добавление через UI, никакого YAML.
- **Опрос** каждые 15 секунд (настраивается).

## Требования

- Home Assistant **2026.3.0** и новее (нужен новый брендовый API
  для локальной иконки).
- Контроллер MyAVR с прошивкой, поддерживающей Modbus TCP.
- Сетевой доступ HA → контроллер по TCP:502.

## Установка

### Через HACS (рекомендуется)

1. HACS → **Integrations** → правый верхний угол `⋮` → **Custom repositories**.
2. Repository: `https://github.com/kirush0280/myavr-ha`, Category: **Integration**.
3. **Add** → в списке появится «MyAVR ATS Controller» → **Download**.
4. Перезапусти Home Assistant.
5. **Settings → Devices & Services → Add Integration** → «MyAVR ATS».

### Вручную

1. Скачай архив из [Releases](https://github.com/kirush0280/myavr-ha/releases)
   или сделай `git clone https://github.com/kirush0280/myavr-ha.git`.
2. Скопируй папку `custom_components/myavr/` в `<config>/custom_components/`
   (в итоге должно получиться `<config>/custom_components/myavr/manifest.json`).
3. Перезапусти Home Assistant.
4. **Settings → Devices & Services → Add Integration** → «MyAVR ATS».

## Настройка

При добавлении интеграция спросит:

| Поле | По умолчанию | Что это |
|---|---|---|
| Host | — | IP-адрес контроллера, например `192.168.1.100` |
| Port | `502` | TCP-порт Modbus |
| Device ID (Unit ID) | `0` | Modbus Unit ID — у MyAVR это `0` |
| Scan interval | `15` s | Период опроса |

### Особенность адресации

Контроллер MyAVR ожидает **полный номер регистра** в поле PDU-адреса
Modbus, а не смещение от 30001/40001. Интеграция это учитывает —
пользователю ничего делать не нужно.

## Что видно в HA

**Сенсоры (напряжение / частота):**
`sensor.myavr_mains_l1`, `sensor.myavr_mains_l2`, `sensor.myavr_mains_l3`,
`sensor.myavr_mains_freq`, `sensor.myavr_gen_l1`, `sensor.myavr_gen_l2`,
`sensor.myavr_gen_l3`, `sensor.myavr_gen_freq`,
`sensor.myavr_inverter_battery`.

**Сенсоры (состояние / моточасы):**
`sensor.myavr_contactor_position`, `sensor.myavr_start_mode`,
`sensor.myavr_engine_hours_current`, `sensor.myavr_engine_hours_setpoint`,
`sensor.myavr_engine_hours_total`, `sensor.myavr_starts_total`,
`sensor.myavr_starts_since_oil`.

**Бинарные сенсоры:**
`binary_sensor.myavr_no_errors`, `binary_sensor.myavr_start_command_sent`,
`binary_sensor.myavr_preventive_start_flag`,
`binary_sensor.myavr_schedule_enabled`, `binary_sensor.myavr_schedule_inhibit`,
`binary_sensor.myavr_error_1` … `binary_sensor.myavr_error_20`.

**Кнопки:** `button.myavr_start_generator`, `button.myavr_stop_generator`,
`button.myavr_schedule_on`, `button.myavr_schedule_off`.

**Селектор режима:** `select.myavr_start_mode` (Ручной / Авто / Эко).

## Использование в автоматизациях

```yaml
# Уведомление при пропадании сети
automation:
  - alias: MyAVR - Пропадание сети
    trigger:
      - platform: numeric_state
        entity_id: sensor.myavr_mains_l1
        below: 180
        for: "00:00:30"
    action:
      - service: notify.mobile_app
        data:
          title: Сеть
          message: "Просело L1: {{ states('sensor.myavr_mains_l1') }} В"

# Автозапуск генератора по кнопке в UI
automation:
  - alias: MyAVR - Ручной запуск
    trigger:
      - platform: state
        entity_id: input_button.run_generator
    action:
      - service: button.press
        target:
          entity_id: button.myavr_start_generator
```

## Безопасность

**Команды записи (`40001–40007`) физически стартуют / останавливают
генератор и переключают контактор.** Перед первым тестом убедись, что
контроллер в безопасном состоянии (генератор заглушен, нагрузки
отключены, если это критично).

Интеграция намеренно не пишет ничего в контроллер без явной команды —
все записи идут только по нажатию кнопки или изменению селектора режима.

## Отладка

Логи компонента:

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.myavr: debug
    pymodbus: info
```

Проверить, что HA видит устройство по Modbus, можно из HA-контейнера:

```bash
docker exec homeassistant python -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('192.168.1.100', port=502, timeout=3)
c.connect()
r = c.read_input_registers(address=30001, count=6, slave=0)
print(r.registers if r and not r.isError() else 'ERROR')
c.close()
"
```

Должны прийти 6 чисел — фазные напряжения (десятки вольт × 10).

## Ограничения / TODO

- Описания 20 ошибок сверены по смыслу с мануалом v3.4, но точные
  формулировки могут отличаться в разных прошивках.
- Команды записи протестированы только на read-only чтение регистров;
  боевой тест `start_generator` пока не проводился.
- SNMP и MQTT не поддерживаются, только Modbus TCP.

## Лицензия

[MIT](LICENSE).

## Благодарности

Спасибо [MyAVR.ru](https://myavr.ru) за открытую документацию по протоколу
и Modbus-таблицу.
