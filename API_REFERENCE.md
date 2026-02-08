# Структура данных Nightscout API

Этот документ описывает структуру JSON ответов от Nightscout API, используемых интеграцией.

## `/api/v1/entries.json` - Записи глюкозы

```json
[
  {
    "_id": "63f1234567890abcdef12345",
    "device": "xDrip-DexcomG6",
    "date": 1676789012345,
    "dateString": "2023-02-19T10:30:12.345Z",
    "sgv": 142,
    "delta": -5.2,
    "direction": "FortyFiveDown",
    "type": "sgv",
    "filtered": 142000,
    "unfiltered": 141500,
    "rssi": 100,
    "noise": 1,
    "sysTime": "2023-02-19T10:30:12.345Z"
  }
]
```

### Поля direction (направление тренда):
- `DoubleUp` - очень быстрый рост (⇈)
- `SingleUp` - быстрый рост (↑)
- `FortyFiveUp` - умеренный рост (⤴)
- `Flat` - стабильно (→)
- `FortyFiveDown` - умеренное падение (⤵)
- `SingleDown` - быстрое падение (↓)
- `DoubleDown` - очень быстрое падение (⇊)

## `/api/v1/devicestatus.json` - Статус устройств

### Пример от AndroidAPS:

```json
[
  {
    "_id": "63f1234567890abcdef12346",
    "device": "openaps://samsung-s10",
    "created_at": "2023-02-19T10:30:15.123Z",
    "pump": {
      "battery": {
        "percent": 75,
        "voltage": 1.35
      },
      "reservoir": 156.5,
      "status": {
        "status": "normal",
        "timestamp": "2023-02-19T10:30:14Z",
        "bolusing": false,
        "suspended": false
      },
      "extended": {
        "BaseBasalRate": 0.8,
        "ActiveProfile": "Default"
      },
      "clock": "2023-02-19T10:30:14Z"
    },
    "openaps": {
      "suggested": {
        "temp": "absolute",
        "bg": 142,
        "tick": "-5",
        "eventualBG": 95,
        "targetBG": 100,
        "insulinReq": 0,
        "deliverAt": "2023-02-19T10:30:15Z",
        "sensitivityRatio": 1.2,
        "COB": 35,
        "IOB": 2.456,
        "reason": "COB: 35, Dev: -12, BGI: -1.2, ISF: 42",
        "duration": 30,
        "rate": 1.2
      },
      "iob": {
        "iob": 2.456,
        "basaliob": 0.456,
        "bolusiob": 2.0,
        "time": "2023-02-19T10:30:15Z"
      },
      "enacted": {
        "bg": 142,
        "temp": "absolute",
        "snoozeBG": 95,
        "recieved": true,
        "reason": "COB: 35, Dev: -12",
        "rate": 1.2,
        "duration": 30,
        "COB": 35,
        "IOB": 2.456,
        "deliverAt": "2023-02-19T10:30:15Z",
        "timestamp": "2023-02-19T10:30:15Z"
      }
    },
    "uploader": {
      "battery": 85,
      "batteryVoltage": 4125
    },
    "uploaderBattery": 85
  }
]
```

### Пример от Loop (iOS):

```json
[
  {
    "_id": "63f1234567890abcdef12347",
    "device": "loop://iPhone",
    "created_at": "2023-02-19T10:30:15.123Z",
    "pump": {
      "reservoir": 142.3,
      "clock": "2023-02-19T10:30:14+00:00",
      "pumpID": "ABC123",
      "iob": {
        "timestamp": "2023-02-19T10:30:14+00:00",
        "bolus": 1.95,
        "basal": 0.35
      },
      "battery": {
        "status": "normal",
        "voltage": 1.42,
        "percent": 80
      }
    },
    "loop": {
      "name": "Loop",
      "version": "3.2.3",
      "timestamp": "2023-02-19T10:30:15+00:00",
      "iob": {
        "timestamp": "2023-02-19T10:30:15+00:00",
        "iob": 2.3
      },
      "cob": {
        "timestamp": "2023-02-19T10:30:15+00:00",
        "cob": 28
      },
      "predicted": {
        "values": [142, 138, 135, 132, 128, 125]
      }
    },
    "uploader": {
      "battery": 72
    }
  }
]
```

## `/api/v1/treatments.json` - Манипуляции

```json
[
  {
    "_id": "63f1234567890abcdef12348",
    "eventType": "Correction Bolus",
    "created_at": "2023-02-19T10:25:00.000Z",
    "insulin": 2.5,
    "carbs": null,
    "notes": "Коррекция высокой глюкозы",
    "enteredBy": "AndroidAPS"
  },
  {
    "_id": "63f1234567890abcdef12349",
    "eventType": "Meal Bolus",
    "created_at": "2023-02-19T08:30:00.000Z",
    "insulin": 5.2,
    "carbs": 45,
    "notes": "Завтрак - каша",
    "enteredBy": "AndroidAPS"
  }
]
```

## `/api/v1/profile.json` - Профиль настроек

```json
[
  {
    "defaultProfile": "Default",
    "store": {
      "Default": {
        "dia": 5,
        "carbratio": [
          {
            "time": "00:00",
            "value": 10,
            "timeAsSeconds": 0
          }
        ],
        "carbs_hr": 20,
        "delay": 20,
        "sens": [
          {
            "time": "00:00",
            "value": 42,
            "timeAsSeconds": 0
          }
        ],
        "timezone": "Europe/Moscow",
        "basal": [
          {
            "time": "00:00",
            "value": 0.8,
            "timeAsSeconds": 0
          }
        ],
        "target_low": [
          {
            "time": "00:00",
            "value": 90,
            "timeAsSeconds": 0
          }
        ],
        "target_high": [
          {
            "time": "00:00",
            "value": 110,
            "timeAsSeconds": 0
          }
        ],
        "startDate": "1970-01-01T00:00:00.000Z",
        "units": "mg/dl"
      }
    },
    "startDate": "2023-01-01T00:00:00.000Z",
    "mills": "1672531200000",
    "units": "mg/dl",
    "created_at": "2023-01-01T00:00:00.000Z"
  }
]
```

## Параметры запросов

### Фильтрация по времени

```
# Последние N записей
/api/v1/entries.json?count=10

# За последние 24 часа
/api/v1/entries.json?find[dateString][$gte]=2023-02-18T10:30:00.000Z

# Диапазон дат
/api/v1/entries.json?find[dateString][$gte]=2023-02-18T00:00:00.000Z&find[dateString][$lte]=2023-02-19T00:00:00.000Z
```

### Сортировка

```
# По убыванию даты (новые первые)
/api/v1/entries.json?count=10

# По возрастанию даты (старые первые)  
/api/v1/entries.json?count=10&sort%5Bdate%5D=1
```

## Аутентификация

### С API секретом (SHA1 хеш):

```python
import hashlib

api_secret = "your_api_secret"
hashed = hashlib.sha1(api_secret.encode()).hexdigest()

headers = {
    "API-SECRET": hashed
}
```

### С токеном:

```
GET /api/v1/entries.json?token=your-token-here
```

## Troubleshooting API

### Проверка доступности

```bash
# Проверка статуса сервера
curl https://your-nightscout.com/api/v1/status.json

# Проверка последних данных глюкозы
curl https://your-nightscout.com/api/v1/entries.json?count=1

# Проверка devicestatus
curl https://your-nightscout.com/api/v1/devicestatus.json?count=1

# С аутентификацией
curl -H "API-SECRET: your_hashed_secret" \
  https://your-nightscout.com/api/v1/entries.json?count=1
```

### Типичные ошибки

**401 Unauthorized:**
- Неправильный API ключ
- Проверьте настройку `AUTH_DEFAULT_ROLES`

**404 Not Found:**
- Неправильный URL
- Endpoint не существует

**Empty response `[]`:**
- Нет данных за запрашиваемый период
- Проверьте AndroidAPS / xDrip отправку данных

## Использование в интеграции

Интеграция использует следующую логику извлечения данных:

### IOB (Insulin on Board)
```python
# Приоритет источников:
1. devicestatus["openaps"]["suggested"]["IOB"]
2. devicestatus["openaps"]["iob"]["iob"]
3. devicestatus["openaps"]["enacted"]["IOB"]
4. devicestatus["loop"]["iob"]["iob"]
```

### COB (Carbs on Board)
```python
# Приоритет источников:
1. devicestatus["openaps"]["suggested"]["COB"]
2. devicestatus["openaps"]["enacted"]["COB"]
3. devicestatus["loop"]["cob"]["cob"]
```

### Sensitivity Ratio
```python
# Приоритет источников:
1. devicestatus["openaps"]["suggested"]["sensitivityRatio"]
2. devicestatus["openaps"]["enacted"]["sensitivityRatio"]
```

### Reservoir
```python
# Источник:
devicestatus["pump"]["reservoir"]
```

### Pump Battery
```python
# Приоритет:
1. devicestatus["pump"]["battery"]["percent"]
2. devicestatus["pump"]["percent"]
```

### Phone Battery
```python
# Источник:
devicestatus["uploader"]["battery"]
```
