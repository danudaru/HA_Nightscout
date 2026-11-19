# Nightscout Extended Integration для Home Assistant

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/danudaru/HA_Nightscout)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Nightscout](https://img.shields.io/badge/Nightscout-14.x+-purple.svg)](https://nightscout.github.io/)

Расширенная интеграция Nightscout для Home Assistant, предоставляющая полный мониторинг данных о диабете из системы Nightscout / AndroidAPS с расширенной статистикой, диагностикой и автоматизацией.

## 🌟 Основные возможности

### 📊 Мониторинг глюкозы
- **Blood Glucose (BG)** - текущий уровень с динамическими иконками тренда
- Поддержка единиц измерения: **mg/dL** и **mmol/L**
- Настраиваемый целевой диапазон (по умолчанию 70-180 mg/dL / 3.9-10.0 mmol/L)

### 📈 Расширенная статистика (для периодов: 24ч, 7д, 30д, 90д)
- **eA1c** - расчётный гликированный гемоглобин
- **Mean BG** - средний уровень глюкозы
- **Median BG** - медианный уровень глюкозы
- **StdDev** - стандартное отклонение
- **CV** - коэффициент вариации
- **GVI** - индекс гликемической вариабельности
- **PGS** - гликемический статус пациента
- **TIR/TBR/TAR** - Time in/Below/Above Range
 - Оптимизированная загрузка: статистика рассчитывается с задержкой после запуска и обновляется раз в 6 часов

### 💉 Мониторинг инсулина и углеводов
- **IOB** (Insulin on Board) - активный инсулин
- **COB** (Carbs on Board) - активные углеводы
- **Sensitivity Ratio** - коэффициент чувствительности
- История болюсов и приёма углеводов

### 🔧 Диагностика и мониторинг системы
- Статус сервера Nightscout (доступность, DNS)
- Свежесть данных ф цветовой индикацией (🟢🟡🔴)
- Мониторинг размера базы данных
- Заряд батарей (помпа, телефон)
- Остаток инсулина в резервуаре

### 🌐 Управление DDNS
- Поддержка **FreeDNS** и **DuckDNS**
- Автоматическое обновление DNS записей
- Мониторинг срока действия доменного имени

### 📊 Система отчётов
- Временные отчёты (ежедневные, еженедельные, месячные)
- Анализ контроля глюкозы
- Отчёты по инсулину и углеводам
- Диагностические отчёты

### 🎨 Готовая панель управления
- 4 вкладки: Обзор, Графики, Статистика, Диагностика
- Цветовая индикация статуса показателей
- Полукруглые индикаторы CV/GVI/PGS (apexcharts-card)
- Референсные значения для всех метрик

## 💻 Требования

- Home Assistant 2023.1 или новее
- Nightscout сервер (версия 14.x или новее)
- AndroidAPS или другая система замкнутого цикла (опционально для IOB/COB)

## 🚀 Быстрый старт

### Установка

### Установка

#### Способ 1: Через HACS (рекомендуется)

1. Откройте HACS → Интеграции
2. Нажмите ⋮ → Пользовательские репозитории
3. Добавьте URL: `https://github.com/danudaru/HA_Nightscout`
4. Установите интеграцию
5. Перезапустите Home Assistant

#### Способ 2: Ручная установка

1. Скопируйте папку `custom_components/nightscout` в `/config/custom_components/`
2. Перезапустите Home Assistant

### Настройка

1. Настройки → Устройства и службы → Добавить интеграцию
2. Найдите **Nightscout Extended**
3. Введите URL вашего Nightscout сервера и API Key (если требуется)
4. Готово! Все сенсоры будут созданы автоматически

Подробная инструкция: [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📖 Документация

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Полное руководство по настройке и использованию
- **[НОВЫЕ_ФУНКЦИИ.md](НОВЫЕ_ФУНКЦИИ.md)** - Описание новых возможностей версии 2.0
- **[CHANGELOG.md](CHANGELOG.md)** - История изменений
- **[API_REFERENCE.md](API_REFERENCE.md)** - Справка по Nightscout API

## 🗂️ Структура проекта

```
custom_components/nightscout/
├── __init__.py              # Инициализация интеграции
├── api.py                   # API клиент для Nightscout
├── config_flow.py           # UI конфигурация и настройки
├── const.py                 # Константы
├── defaults.py              # Референсные значения показателей
├── diagnostics.py           # Диагностика и управление DDNS
├── manifest.json            # Метаданные интеграции
├── reports.py               # Генерация отчётов
├── sensor.py                # Основные сенсоры
├── sensor_diagnostics.py    # Диагностические сенсоры
├── sensor_statistics.py     # Статистические сенсоры
├── statistics.py            # Расчёт статистики
├── strings.json             # Локализация (EN)
├── utils.py                 # Вспомогательные функции
└── translations/
    ├── en.json              # Английская локализация
    └── ru.json              # Русская локализация
```

## 📊 Доступные сенсоры

### Основные сенсоры
- `sensor.blood_glucose` - Текущая глюкоза
- `sensor.nightscout_insulin_on_board` - IOB
- `sensor.nightscout_carbs_on_board` - COB  
- `sensor.nightscout_sensitivity_ratio` - Чувствительность

### Сенсоры eA1c
- `sensor.nightscout_ea1c_24h` / `_7d` / `_30d` / `_90d`

### Статистические сенсоры (за каждый период)
- `sensor.mean_bg_[период]` - Средняя глюкоза
- `sensor.median_bg_[период]` - Медианная глюкоза
- `sensor.stddev_[период]` - Стандартное отклонение
- `sensor.cv_[период]` - Коэффициент вариации
- `sensor.gvi_[период]` - Индекс вариабельности
- `sensor.pgs_[период]` - Гликемический статус
- `sensor.time_in_range_[период]` - Time in Range
- `sensor.time_below_range_[период]` - Time Below Range
- `sensor.time_above_range_[период]` - Time Above Range

Периоды: `24h`, `7d`, `30d`, `90d`

### Диагностические сенсоры
- `sensor.nightscout_server_status` - Статус сервера
- `sensor.nightscout_data_freshness` - Свежесть данных
- `sensor.nightscout_database_size` - Размер БД
- `sensor.nightscout_pump_reservoir` - Остаток инсулина
- `sensor.nightscout_pump_battery` - Заряд помпы
- `sensor.nightscout_phone_battery` - Заряд телефона

Полный список: **99+ сенсоров**

## ⚙️ Настройка параметров

После установки интеграции настройте параметры:

1. **Настройки** → **Устройства и службы** → **Nightscout Extended** → **Настроить**

Доступные параметры:
- **Единицы измерения глюкозы**: mg/dL или mmol/L
- **Целевой диапазон**: мин/макс значения
- **DDNS**: включение и настройка FreeDNS/DuckDNS
- **Срок действия домена**: дата для мониторинга

## 🎨 Панель управления

Установите готовую панель из `nightscout_dashboard_extended.yaml`:

### Вкладка 1: Обзор
- Карточки текущей глюкозы
- Основные показатели (eA1c, IOB, COB)
- Статус устройств
- Time in Range карточки и полукруглые индикаторы CV/GVI/PGS

### Вкладка 2: Графики
- График глюкозы (настраиваемый период)
- IOB, COB, Sensitivity
- Базальная скорость
- История лечения

### Вкладка 3: Статистика
- Разделы по временным периодам
- Все статистические показатели
- Цветовая индикация

### Вкладка 4: Диагностика
- Статус сервера и данных
- Графики батарей
- Остаток инсулина
- Информация о системе

### Компактная карточка глюкозы (HACS)

Если нужна отдельная карточка текущих показаний без полной панели, интеграция из коробки совместима с [SugarTV Card](https://github.com/wiltodelta/homeassistant-sugartv-card) (доступна в HACS Default). Карточка сама читает тренд из атрибута `direction` и может показывать активный инсулин:

```yaml
type: custom:sugartv-card
glucose_value: sensor.blood_glucose
insulin_value: sensor.nightscout_insulin_on_board # необязательно
```

![SugarTV Card в широком и вертикальном слоте](https://raw.githubusercontent.com/wiltodelta/homeassistant-sugartv-card/v0.22.0/sugartv-card-layouts.png)

## 📈 Референсные значения

Все показатели имеют встроенные референсные диапазоны с цветовой индикацией:

| Показатель | 🟢 Норма | 🟡 Внимание | 🔴 Критично |
|-----------|---------|-----------|-----------|
| eA1c | < 7.0% | 7.0-8.0% | > 8.0% |
| TIR | > 70% | 50-70% | < 30% |
| TBR | < 4% | 4-10% | > 10% |
| TAR | < 25% | 25-50% | > 50% |
| CV | < 36% | 36-50% | > 50% |

Подробнее: [defaults.py](custom_components/nightscout/defaults.py)

## 🔧 Примеры автоматизаций

### Уведомление о низкой глюкозе

```yaml
automation:
  - alias: "Nightscout: Низкая глюкоза"
    trigger:
      - platform: numeric_state
        entity_id: sensor.blood_glucose
        below: 70
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Низкая глюкоза!"
          message: "Глюкоза: {{ states('sensor.blood_glucose') }} mg/dL"
          data:
            priority: high
```

### Напоминание о замене инсулина

```yaml
automation:
  - alias: "Nightscout: Мало инсулина"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_pump_reservoir
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "💉 Мало инсулина"
          message: "Осталось {{ states('sensor.nightscout_pump_reservoir') }} U"
```

## 🆕 Что нового в v2.0

### Добавлено
- ✨ 36 новых статистических сенсоров (Mean, Median, StdDev, CV, GVI, PGS, TIR/TBR/TAR)
- 🔧 3 диагностических сенсора (Server Status, Data Freshness, Database Size)
- 🌐 Управление DDNS (FreeDNS, DuckDNS)
- 📊 Система генерации отчётов
- 🎯 Настраиваемый целевой диапазон
- 🌍 Поддержка mmol/L
- 🎨 Расширенная панель управления (4 вкладки)
- 📖 Референсные значения для всех показателей

### Изменено
- ⚠️ **BREAKING**: `sensor.blood_sugar` → `sensor.blood_glucose`
- ⚡ Статистика обновляется каждые 6 часов (вместо каждую минуту)
- 🔐 Улучшена безопасность хранения данных

Полный список: [CHANGELOG.md](CHANGELOG.md)

## 🐛 Устранение неполадок

### Интеграция не подключается
- Проверьте URL сервера (https://)
- Проверьте API Key (если сервер защищён)
- Убедитесь, что сервер доступен

### Нет данных IOB/COB
- Убедитесь, что AndroidAPS/Loop передают данные
- Проверьте devicestatus: `https://your-url/api/v1/devicestatus`

### Статистика не обновляется
- Статистика обновляется каждые 6 часов
- Для принудительного обновления перезапустите HA

Подробнее: [SETUP_GUIDE.md - Устранение неполадок](SETUP_GUIDE.md#устранение-неполадок)

## 🤝 Вклад в проект

Мы приветствуем вклад в проект! 

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 🙏 Благодарности

- [Nightscout Project](https://nightscout.github.io/)
- [Home Assistant Community](https://www.home-assistant.io/)
- [AndroidAPS](https://androidaps.readthedocs.io/)

## 📞 Поддержка

- 🐛 [Issues на GitHub](https://github.com/danudaru/HA_Nightscout/issues)
- 💬 [Обсуждения](https://github.com/danudaru/HA_Nightscout/discussions)
- 📧 Email: [your-email@example.com]

---

**⭐ Если проект полезен, поставьте звёздочку на GitHub!**

## 🔗 Полезные ссылки

- [Nightscout](https://nightscout.github.io/)
- [AndroidAPS](https://androidaps.readthedocs.io/)
- [Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)

После установки будут созданы следующие сенсоры:

| Entity ID | Описание | Единицы |
|-----------|----------|---------|
| `sensor.blood_glucose` | Уровень глюкозы | мг/дл или ммоль/л |
| `sensor.nightscout_insulin_on_board` | Активный инсулин (IOB) | U |
| `sensor.nightscout_carbs_on_board` | Активные углеводы (COB) | г |
| `sensor.nightscout_sensitivity_ratio` | Коэффициент чувствительности | - |
| `sensor.nightscout_ea1c_24h` | eA1c за 24 часа | % |
| `sensor.nightscout_ea1c_7d` | eA1c за 7 дней | % |
| `sensor.nightscout_ea1c_30d` | eA1c за 30 дней | % |
| `sensor.nightscout_ea1c_90d` | eA1c за 90 дней | % |
| `sensor.nightscout_pump_reservoir` | Инсулин в резервуаре | U |
| `sensor.nightscout_pump_battery` | Батарея помпы | % |
| `sensor.nightscout_phone_battery` | Батарея телефона | % |
| `sensor.nightscout_basal_rate` | Базальная скорость | U/ч |
| `sensor.nightscout_temp_basal` | Временный базал | U/ч |
| `sensor.nightscout_last_treatment` | Последнее действие | - |
| `sensor.nightscout_last_bolus` | Последний болюс | U |
| `sensor.nightscout_last_carbs` | Последние углеводы | г |
| `sensor.nightscout_loop_status` | Статус петли | - |
| `sensor.nightscout_device_status` | Статус устройства | - |

Статистические сенсоры (за каждый период: `24h`, `7d`, `30d`, `90d`):
- `sensor.mean_bg_[период]`
- `sensor.median_bg_[период]`
- `sensor.stddev_[период]`
- `sensor.cv_[период]`
- `sensor.gvi_[период]`
- `sensor.pgs_[период]`
- `sensor.time_in_range_[период]`
- `sensor.time_below_range_[период]`
- `sensor.time_above_range_[период]`

## Автоматизации

### Пример 1: Уведомление о низкой глюкозе

```yaml
automation:
  - alias: "Низкая глюкоза"
    trigger:
      - platform: numeric_state
        entity_id: sensor.blood_glucose
        below: 70
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Низкая глюкоза!"
          message: "Уровень глюкозы: {{ states('sensor.blood_glucose') }} мг/дл"
          data:
            priority: high
            ttl: 0
```

### Пример 2: Уведомление о низком уровне инсулина в помпе

```yaml
automation:
  - alias: "Низкий уровень инсулина"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_pump_reservoir
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "💉 Низкий уровень инсулина"
          message: "Осталось {{ states('sensor.nightscout_pump_reservoir') }} U"
```

### Пример 3: Уведомление о высоком eA1c

```yaml
automation:
  - alias: "Высокий eA1c за неделю"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_ea1c_7d
        above: 7.0
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Высокий eA1c"
          message: "eA1c за 7 дней: {{ states('sensor.nightscout_ea1c_7d') }}%"
```

## Устранение неполадок

### Сенсоры недоступны (Unavailable)

**IOB, COB, Sensitivity недоступны:**
- Убедитесь, что AndroidAPS или ваша система замкнутого цикла отправляет данные в Nightscout
- Проверьте, что в Nightscout включен плагин `openaps` или `loop`
- Проверьте в Nightscout API: `https://your-nightscout-url/api/v1/devicestatus.json`

**eA1c сенсоры недоступны:**
- Необходимо минимум несколько записей глюкозы за запрашиваемый период
- Проверьте, что записи глюкозы поступают регулярно

**Диагностические сенсоры недоступны:**
- Убедитесь, что ваша помпа и телефон передают данные в Nightscout
- Проверьте структуру данных в `/api/v1/devicestatus.json`

### Ошибки подключения

- Проверьте правильность URL (должен начинаться с `https://` или `http://`)
- Проверьте API ключ, если сервер защищен
- Убедитесь, что сервер Nightscout доступен из вашей сети Home Assistant

### Проверка логов

Включите подробное логирование для отладки:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.nightscout: debug
    py_nightscout: debug
```

## Структура проекта

```
nightscout/
├── __init__.py          # Инициализация интеграции
├── api.py               # Расширенный API клиент
├── config_flow.py       # Настройка через UI
├── const.py             # Константы
├── manifest.json        # Метаданные интеграции
├── sensor.py            # Сенсоры
├── strings.json         # Локализация
└── utils.py             # Вспомогательные функции
```

## Технические детали

### API Endpoints

Интеграция использует следующие Nightscout API endpoints:

- `/api/v1/entries.json` - получение записей глюкозы
- `/api/v1/devicestatus.json` - получение статуса устройств (IOB, COB, помпа, батареи)
- `/api/v1/status.json` - информация о сервере

### Частота обновления

- Глюкоза, IOB, COB, диагностика: каждую **1 минуту**
- eA1c сенсоры: каждую **1 минуту** (с кэшированием на стороне Nightscout)

### Формула расчета eA1c

```
eA1c (%) = 3.31 + 0.02392 × [средняя глюкоза в мг/дл]
```

Эта формула основана на исследовании GMI (Glucose Management Indicator) и соответствует соотношениям, используемым профессиональными системами мониторинга.

## Поддержка

### Сообщить о проблеме

Если вы обнаружили ошибку или у вас есть предложение:
1. Проверьте существующие [Issues](https://github.com/danudaru/HA_Nightscout/issues)
2. Создайте новый Issue с подробным описанием
3. Приложите логи, если возможно

### Вклад в проект

Pull requests приветствуются! Пожалуйста:
1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## Лицензия

Этот проект распространяется под лицензией AGPL-3.0, как и оригинальная интеграция Home Assistant Nightscout.

## Благодарности

- Оригинальная интеграция Nightscout от [@marciogranzotto](https://github.com/marciogranzotto)
- [Nightscout Project](https://nightscout.github.io/)
- [AndroidAPS](https://androidaps.readthedocs.io/)
- Сообщество Home Assistant

## Связанные проекты

- [Nightscout](https://nightscout.github.io/) - Система мониторинга глюкозы в облаке
- [AndroidAPS](https://androidaps.readthedocs.io/) - Система искусственной поджелудочной железы для Android
- [py-nightscout](https://github.com/ps-jay/py-nightscout) - Python библиотека для Nightscout API

---

**Дисклеймер**: Эта интеграция предназначена для мониторинга и информационных целей. Не используйте данные из Home Assistant для принятия медицинских решений без консультации с врачом. Всегда сверяйтесь с показаниями вашего основного устройства мониторинга глюкозы.
