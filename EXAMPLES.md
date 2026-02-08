# Примеры использования и автоматизаций

Коллекция полезных автоматизаций и примеров использования интеграции Nightscout Extended.

## 📱 Уведомления о глюкозе

### Критически низкая глюкоза (гипогликемия)

```yaml
automation:
  - alias: "🚨 Критически низкая глюкоза"
    description: "Немедленное уведомление при глюкозе <55 мг/дл"
    trigger:
      - platform: numeric_state
        entity_id: sensor.blood_sugar
        below: 55
    action:
      # Звуковое уведомление на телефоне
      - service: notify.mobile_app_iphone
        data:
          title: "🚨 ГИПОГЛИКЕМИЯ!"
          message: "Глюкоза: {{ states('sensor.blood_sugar') }} мг/дл"
          data:
            priority: high
            ttl: 0
            channel: alarm_stream
            sound: alarm.mp3
      
      # Включить свет в спальне (если ночь)
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness: 255
          color_name: red
      
      # Голосовое оповещение
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room_speaker
          message: "Внимание! Критически низкая глюкоза!"
```

### Низкая глюкоза с трендом падения

```yaml
automation:
  - alias: "⚠️ Низкая глюкоза с быстрым падением"
    description: "Предупреждение при глюкозе <80 и быстром падении"
    trigger:
      - platform: numeric_state
        entity_id: sensor.blood_sugar
        below: 80
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.blood_sugar', 'direction') in 
             ['SingleDown', 'DoubleDown', 'FortyFiveDown'] }}
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "⚠️ Внимание: низкая глюкоза"
          message: >
            Глюкоза {{ states('sensor.blood_sugar') }} мг/дл
            и быстро падает {{ state_attr('sensor.blood_sugar', 'direction') }}
          data:
            priority: high
```

### Высокая глюкоза (гипергликемия)

```yaml
automation:
  - alias: "📈 Высокая глюкоза"
    description: "Уведомление при устойчиво высокой глюкозе"
    trigger:
      - platform: numeric_state
        entity_id: sensor.blood_sugar
        above: 250
        for:
          minutes: 30
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "📈 Высокая глюкоза"
          message: >
            Глюкоза {{ states('sensor.blood_sugar') }} мг/дл
            в течение 30+ минут
            IOB: {{ states('sensor.nightscout_insulin_on_board') }} U
          data:
            actions:
              - action: "OPEN_AAPS"
                title: "Открыть AAPS"
```

### Уведомление о входе в целевой диапазон

```yaml
automation:
  - alias: "✅ Глюкоза в норме"
    description: "Уведомление о возврате в целевой диапазон"
    trigger:
      - platform: numeric_state
        entity_id: sensor.blood_sugar
        above: 70
        below: 180
    condition:
      # Только если была вне диапазона последние 15 минут
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - 
              as_timestamp(states.sensor.blood_sugar.last_changed)) > 900 }}
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "✅ Глюкоза в норме"
          message: "Глюкоза вернулась в целевой диапазон: {{ states('sensor.blood_sugar') }} мг/дл"
```

## 💉 IOB и COB автоматизации

### Предупреждение о высоком IOB перед сном

```yaml
automation:
  - alias: "💉 Высокий IOB перед сном"
    description: "Предупреждение о риске ночной гипо"
    trigger:
      - platform: time
        at: "22:30:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.nightscout_insulin_on_board
        above: 2
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "💉 Внимание: высокий IOB"
          message: >
            Активный инсулин: {{ states('sensor.nightscout_insulin_on_board') }} U
            Рассмотрите прием углеводов перед сном
            Текущая глюкоза: {{ states('sensor.blood_sugar') }} мг/дл
```

### Уведомление об активных углеводах

```yaml
automation:
  - alias: "🍎 Высокие активные углеводы"
    description: "Напоминание проверить глюкозу при высоком COB"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_carbs_on_board
        above: 60
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🍎 Высокие активные углеводы"
          message: >
            COB: {{ states('sensor.nightscout_carbs_on_board') }} г
            Проверьте уровень глюкозы через 30 минут
```

## 📊 eA1c мониторинг

### Уведомление о повышении eA1c

```yaml
automation:
  - alias: "📊 Повышенный eA1c (7 дней)"
    description: "Уведомление о высоком eA1c за неделю"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_ea1c_7d
        above: 7.0
    condition:
      # Отправлять не чаще раза в день
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - 
              as_timestamp(state_attr('automation.ea1c_alert', 'last_triggered') | default(0))) 
             > 86400 }}
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "📊 Внимание: повышенный eA1c"
          message: >
            eA1c за 7 дней: {{ states('sensor.nightscout_ea1c_7d') }}%
            Целевой показатель: <7.0%
            
            eA1c за 30 дней: {{ states('sensor.nightscout_ea1c_30d') }}%
```

### Еженедельный отчет eA1c

```yaml
automation:
  - alias: "📈 Еженедельный отчет eA1c"
    description: "Отчет каждое воскресенье вечером"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "📈 Еженедельный отчет"
          message: >
            Анализ контроля глюкозы:
            
            eA1c (7 дней): {{ states('sensor.nightscout_ea1c_7d') }}%
            eA1c (30 дней): {{ states('sensor.nightscout_ea1c_30d') }}%
            eA1c (90 дней): {{ states('sensor.nightscout_ea1c_3month') }}%
            
            Средняя глюкоза: {{ states('sensor.blood_sugar') }} мг/дл
```

## 🔋 Диагностические автоматизации

### Низкий уровень инсулина в резервуаре

```yaml
automation:
  - alias: "💧 Низкий уровень инсулина в резервуаре"
    description: "Предупреждение о необходимости замены резервуара"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_pump_reservoir
        below: 20
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "💧 Низкий уровень инсулина"
          message: >
            В резервуаре осталось {{ states('sensor.nightscout_pump_reservoir') }} U
            Подготовьте новый резервуар
          data:
            actions:
              - action: "RESERVOIR_CHANGED"
                title: "Резервуар заменен"
      
      # Добавить в список покупок
      - service: shopping_list.add_item
        data:
          name: "Резервуары для инсулиновой помпы"
```

### Критически низкий инсулин

```yaml
automation:
  - alias: "🚨 Критически низкий инсулин"
    description: "Срочное уведомление при <10 U"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_pump_reservoir
        below: 10
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🚨 Критически низкий инсулин!"
          message: "Осталось {{ states('sensor.nightscout_pump_reservoir') }} U - замените немедленно!"
          data:
            priority: high
            ttl: 0
```

### Низкий заряд батареи помпы

```yaml
automation:
  - alias: "🔋 Низкий заряд батареи помпы"
    description: "Уведомление при заряде <20%"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_pump_battery
        below: 20
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🔋 Низкий заряд помпы"
          message: >
            Заряд батареи помпы: {{ states('sensor.nightscout_pump_battery') }}%
            Подготовьте запасную батарею
```

### Низкий заряд телефона (Android/AAPS)

```yaml
automation:
  - alias: "📱 Низкий заряд телефона AAPS"
    description: "Предупреждение о разряде телефона с AAPS"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nightscout_phone_battery
        below: 30
    condition:
      # Только если не заряжается
      - condition: template
        value_template: "{{ states('sensor.phone_charging_state') != 'charging' }}"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "📱 Зарядите телефон с AAPS"
          message: >
            Заряд телефона: {{ states('sensor.nightscout_phone_battery') }}%
            AAPS может прекратить работу!
          data:
            priority: high
```

## 🌙 Ночные автоматизации

### Ночной профиль мониторинга

```yaml
automation:
  - alias: "🌙 Усиленный ночной мониторинг"
    description: "Более частые проверки глюкозы ночью"
    trigger:
      - platform: time_pattern
        minutes: "/15"  # Каждые 15 минут
    condition:
      - condition: time
        after: "23:00:00"
        before: "07:00:00"
      - condition: or
        conditions:
          - condition: numeric_state
            entity_id: sensor.blood_sugar
            below: 90
          - condition: numeric_state
            entity_id: sensor.blood_sugar
            above: 200
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom_led_strip
        data:
          brightness: 50
          color_name: >
            {% if states('sensor.blood_sugar')|float < 90 %}
              red
            {% else %}
              orange
            {% endif %}
      - delay:
          seconds: 5
      - service: light.turn_off
        target:
          entity_id: light.bedroom_led_strip
```

## 🏃 Активность и спорт

### Предупреждение перед тренировкой

```yaml
automation:
  - alias: "🏃 Проверка перед тренировкой"
    description: "Проверить IOB/COB перед тренировкой"
    trigger:
      - platform: calendar
        event: start
        entity_id: calendar.fitness
        offset: "-00:15:00"  # За 15 минут
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🏃 Подготовка к тренировке"
          message: >
            Через 15 минут тренировка!
            
            Глюкоза: {{ states('sensor.blood_sugar') }} мг/дл
            IOB: {{ states('sensor.nightscout_insulin_on_board') }} U
            COB: {{ states('sensor.nightscout_carbs_on_board') }} г
            
            {% if states('sensor.blood_sugar')|float < 120 %}
            ⚠️ Рекомендуется принять углеводы
            {% endif %}
```

## 📈 Дашборд условия

### Цветовая индикация статуса

```yaml
# В card-mod или подобном
style: |
  :host {
    --card-background-color: 
      {% set bg = states('sensor.blood_sugar')|float %}
      {% if bg < 70 %}
        rgba(255, 0, 0, 0.3)
      {% elif bg > 180 %}
        rgba(255, 165, 0, 0.3)
      {% else %}
        rgba(0, 255, 0, 0.2)
      {% endif %}
      ;
  }
```

### Шаблонный сенсор статуса

```yaml
template:
  - sensor:
      - name: "Статус глюкозы"
        unique_id: glucose_status
        state: >
          {% set bg = states('sensor.blood_sugar')|float(0) %}
          {% set dir = state_attr('sensor.blood_sugar', 'direction') %}
          {% if bg < 70 %}
            Низкая
          {% elif bg > 180 %}
            Высокая
          {% else %}
            Норма
          {% endif %}
        icon: >
          {% set dir = state_attr('sensor.blood_sugar', 'direction') %}
          {% if dir == 'DoubleUp' %}
            mdi:chevron-triple-up
          {% elif dir == 'SingleUp' %}
            mdi:arrow-up
          {% elif dir == 'Flat' %}
            mdi:arrow-right
          {% elif dir == 'SingleDown' %}
            mdi:arrow-down
          {% elif dir == 'DoubleDown' %}
            mdi:chevron-triple-down
          {% else %}
            mdi:help-circle
          {% endif %}
```

## 🔔 Умные уведомления

### Адаптивный приоритет уведомлений

```yaml
automation:
  - alias: "🔔 Умные уведомления глюкозы"
    description: "Адаптивная система уведомлений"
    trigger:
      - platform: state
        entity_id: sensor.blood_sugar
    variables:
      bg: "{{ trigger.to_state.state|float }}"
      direction: "{{ state_attr('sensor.blood_sugar', 'direction') }}"
      iob: "{{ states('sensor.nightscout_insulin_on_board')|float }}"
    action:
      - choose:
          # Критическая гипо
          - conditions:
              - condition: template
                value_template: "{{ bg < 55 }}"
            sequence:
              - service: notify.mobile_app_iphone
                data:
                  title: "🚨 КРИТИЧЕСКАЯ ГИПО"
                  message: "{{ bg }} мг/дл"
                  data:
                    priority: high
                    ttl: 0
                    sound: alarm.mp3
          
          # Гипо с высоким IOB
          - conditions:
              - condition: template
                value_template: "{{ bg < 80 and iob > 1.5 }}"
            sequence:
              - service: notify.mobile_app_iphone
                data:
                  title: "⚠️ Гипо + высокий IOB"
                  message: "BG: {{ bg }}, IOB: {{ iob }}"
                  data:
                    priority: high
```

## 📊 Статистика и отчеты

### Ежемесячный отчет

```yaml
automation:
  - alias: "📊 Месячный отчет диабета"
    description: "Отчет в последний день месяца"
    trigger:
      - platform: time
        at: "21:00:00"
    condition:
      - condition: template
        value_template: >
          {{ now().day == (now().replace(day=1) + 
             timedelta(days=32)).replace(day=1).day - 1 }}
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "📊 Месячный отчет"
          message: >
            Результаты за {{ now().strftime('%B %Y') }}:
            
            eA1c (30д): {{ states('sensor.nightscout_ea1c_30d') }}%
            eA1c (90д): {{ states('sensor.nightscout_ea1c_3month') }}%
            
            Поздравляем с завершением месяца!
```

---

## 💡 Советы по использованию

1. **Тестируйте автоматизации** в безопасном режиме перед активацией
2. **Не полагайтесь только на HA** для критических уведомлений
3. **Держите резервные уведомления** в AAPS/xDrip
4. **Настройте режим "Не беспокоить"** для некритичных оповещений ночью
5. **Регулярно проверяйте** работоспособность автоматизаций

---

## ⚠️ Важные предупреждения

- Используйте эти автоматизации как **дополнение**, а не замену стандартным алертам
- Всегда проверяйте показания на основном устройстве
- Не принимайте медицинские решения только на основе данных HA
- Проконсультируйтесь с врачом перед использованием автоматизаций

---

**Есть идеи для новых автоматизаций?**  
Поделитесь ими в [GitHub Discussions](https://github.com/yourusername/HA_Nightscout/discussions)!
