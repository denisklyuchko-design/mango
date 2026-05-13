# Инструкция по настройке Telegram Web App для Mango Sushi Wok POS

## 📋 Обзор

Это руководство поможет вам настроить полноценное Telegram-приложение для вашей POS-системы Mango Sushi Wok с ценами в польских злотых (PLN).

## 🎯 Что у нас есть

1. **Telegram Web App** (`frontend/telegram_app.html`) - полноценное POS-приложение, которое открывается прямо в Telegram
2. **Telegram Bot** (`backend/telegram_bot.py`) - бот для взаимодействия с пользователями
3. **POS Система** (`frontend/index_v2.html`) - основная версия для использования в ресторане

## 🚀 Пошаговая инструкция

### Шаг 1: Создание Telegram бота

1. Откройте Telegram и найдите **@BotFather**
2. Отправьте команду `/newbot`
3. Введите имя бота (например, `Mango Sushi Wok Bot`)
4. Введите username бота (например, `mango_sushi_wok_bot`)
5. **Сохраните полученный токен** (выглядит как `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Шаг 2: Настройка Web App

1. В **@BotFather** отправьте команду `/newapp`
2. Выберите вашего бота
3. Введите название Web App (например, `Mango Sushi Wok Menu`)
4. Введите описание
5. Загрузите фото (640x360 пикселей) - логотип ресторана
6. **Введите URL вашего Web App** (см. Шаг 3)
7. Введите короткое название для кнопки (например, `🍱 Меню`)

### Шаг 3: Размещение Web App

#### Вариант A: GitHub Pages (бесплатно)

1. Создайте репозиторий на GitHub
2. Загрузите файл `frontend/telegram_app.html`
3. Включите GitHub Pages в настройках репозитория
4. Ваш URL будет: `https://yourusername.github.io/telegram_app.html`

#### Вариант B: Ваш хостинг

1. Загрузите `frontend/telegram_app.html` на ваш хостинг
2. URL должен быть доступен по HTTPS
3. Пример: `https://mangosushiwok.com/telegram_app.html`

### Шаг 4: Настройка бота

1. Откройте `backend/telegram_bot.py`
2. Замените `YOUR_BOT_TOKEN_HERE` на ваш токен из @BotFather
3. Замените `https://your-domain.com/telegram_app.html` на ваш URL из Шага 3

```python
BOT_TOKEN = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'  # Ваш токен
WEBAPP_URL = 'https://yourusername.github.io/telegram_app.html'  # Ваш URL
```

### Шаг 5: Установка зависимостей

```bash
# Перейдите в директорию backend
cd backend

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 6: Запуск бота

```bash
# Запустите бота
python telegram_bot.py
```

### Шаг 7: Тестирование

1. Найдите вашего бота в Telegram по username
2. Нажмите `/start`
3. Нажмите кнопку "🍱 Меню"
4. Должно открыться Web App с меню
5. Добавьте товары в корзину и оформите заказ
6. Заказ должен прийти в бот

## 🔧 Дополнительные настройки

### Настройка клавиатуры бота

В файле `backend/telegram_bot.py` вы можете изменить кнопки:

```python
def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🍱 Меню", web_app=WebAppInfo(url=WEBAPP_URL)))
    builder.add(KeyboardButton(text="📊 Мои заказы"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.add(KeyboardButton(text="📞 Контакты"))
    return builder.as_keyboard(resize_keyboard=True)
```

### Изменение меню

Меню находится в `frontend/telegram_app.html` в переменной `MENU`. Вы можете:
- Изменять названия блюд
- Менять цены
- Добавлять новые позиции
- Изменять описания

Пример:
```javascript
const MENU=[
  {id:1,nr:"Филадельфия Люкс",np:"Filadelfia Lux",p:28,c:"sushi_rolls",dr:"Лосось, сыр, огурец, авокадо",dp:"Łosoś, ser, ogórek, awokado",e:"🍣"},
  // ... другие блюда
];
```

### Изменение языков

Поддерживаются два языка: русский (ru) и польский (pl). Вы можете добавить другие языки в объекте `T` в `frontend/telegram_app.html`.

## 📊 Мониторинг и администрирование

### Просмотр заказов

Все заказы хранятся в памяти бота. Для просмотра:

```python
# В telegram_bot.py добавьте команду
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    stats = OrderManager.get_order_stats()
    await message.answer(f"""
    📊 Статистика:
    Всего заказов: {stats['total_orders']}
    Выручка: {stats['total_revenue']} zł
    За сегодня: {stats['today_orders']} заказов, {stats['today_revenue']} zł
    """)
```

### Экспорт данных

Для экспорта заказов в JSON добавьте:

```python
@dp.message(Command("export"))
async def cmd_export(message: types.Message):
    import json
    with open('orders_export.json', 'w', encoding='utf-8') as f:
        json.dump(orders_db, f, ensure_ascii=False, indent=2)
    await message.answer_document(types.FSInputFile('orders_export.json'))
```

## 🔒 Безопасность

1. **Никогда не публикуйте токен бота** в открытом доступе
2. Используйте переменные окружения для хранения токена
3. Ограничьте доступ к админ-командам по ID пользователя

```python
# Пример проверки админ-доступа
ADMIN_IDS = [123456789, 987654321]  # Ваши ID

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа")
        return
    # ... остальной код
```

## 🌐 Хостинг бота

### Вариант A: VPS (рекомендуется)

1. Арендуйте VPS (Ubuntu 20.04+)
2. Установите Python 3.8+
3. Настройте автозапуск бота через systemd

```bash
# Создайте сервис
sudo nano /etc/systemd/system/mango-bot.service
```

```ini
[Unit]
Description=Mango Sushi Wok Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pos_project/backend
ExecStart=/usr/bin/python3 /home/ubuntu/pos_project/backend/telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Запустите сервис
sudo systemctl start mango-bot
sudo systemctl enable mango-bot
```

### Вариант B: Heroku (бесплатно с ограничениями)

1. Создайте аккаунт на Heroku
2. Установите Heroku CLI
3. Создайте приложение и подключите репозиторий
4. Добавьте переменные окружения:
   - `TELEGRAM_BOT_TOKEN`
   - `WEBAPP_URL`

### Вариант C: PythonAnywhere (бесплатно)

1. Зарегистрируйтесь на PythonAnywhere
2. Загрузите файлы
3. Настройте виртуальное окружение
4. Запустите бота через консоль

## 📱 Тестирование на разных устройствах

### Десктоп
- Откройте бота в Telegram Desktop
- Нажмите кнопку "🍱 Меню"
- Web App откроется в отдельном окне

### Мобильное устройство
- Откройте бота в Telegram для Android/iOS
- Нажмите кнопку "🍱 Меню"
- Web App откроется на весь экран

## 🐛 Устранение неполадок

### Web App не открывается
1. Проверьте URL в настройках бота
2. Убедитесь, что URL доступен по HTTPS
3. Проверьте консоль браузера на ошибки

### Бот не отвечает
1. Проверьте токен бота
2. Убедитесь, что бот запущен
3. Проверьте логи бота

### Заказ не создается
1. Проверьте консоль браузера в Web App
2. Убедитесь, что данные правильно отправляются
3. Проверьте логи бота

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи бота
2. Проверьте консоль браузера в Web App
3. Убедитесь, что все URL настроены правильно
4. Проверьте переменные окружения

## 🎉 Готово!

Теперь у вас есть полноценное Telegram-приложение для вашего ресторана Mango Sushi Wok с:
- ✅ Интерактивным меню
- ✅ Корзиной покупок
- ✅ Оформлением заказов
- ✅ Отслеживанием статусов
- ✅ Двумя языками (RU/PL)
- ✅ Ценами в польских злотых

**Приятной работы! 🍣🍜**