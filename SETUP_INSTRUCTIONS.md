# 🚀 ПОШАГОВАЯ ИНСТРУКЦИЯ ПО ЗАПУСКУ TELEGRAM-ПРИЛОЖЕНИЯ

## ✅ Что уже сделано:

1. **Бот создан** - токен: `8791266418:AAELCANoPfk88UHrbXRKzjEuWGIalv5npSs`
2. **Код обновлен** - все файлы готовы к работе
3. **GitHub репозиторий** - `https://github.com/denisklyuchko-design/mango`

## 📋 Что нужно сделать:

### 🔹 ШАГ 1: Настроить GitHub Pages

1. **Перейдите в ваш репозиторий**: https://github.com/denisklyuchko-design/mango
2. **Загрузите файлы**:
   - `frontend/telegram_app.html` → в корень репозитория
   - `frontend/index_v2.html` → в корень репозитория (опционально)
3. **Включите GitHub Pages**:
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: main (или master)
   - Folder: / (root)
   - Нажмите Save
4. **Подождите 1-2 минуты** и проверьте ссылку:
   - https://denisklyuchko-design.github.io/mango/telegram_app.html

### 🔹 ШАГ 2: Установить зависимости для бота

Откройте терминал (командную строку) и выполните:

```bash
# Перейдите в папку с проектом
cd c:\pos_project\backend

# Установите необходимые библиотеки
pip install aiogram>=3.0.0
```

Или если у вас уже есть requirements.txt:
```bash
pip install -r requirements.txt
```

### 🔹 ШАГ 3: Запустить бота

```bash
# В папке backend
python telegram_bot.py
```

Вы должны увидеть:
```
INFO - Запуск бота...
INFO - Web App URL: https://denisklyuchko-design.github.io/mango/telegram_app.html
```

### 🔹 ШАГ 4: Протестировать бота

1. **Откройте Telegram**
2. **Найдите вашего бота** по ссылке: https://t.me/mango_sushi_wok_bot
   (или по username, который вы задали при создании)
3. **Нажмите /start** или кнопку "Start"
4. **Нажмите кнопку "🍱 Меню"**
5. **Должно открыться Web App** с меню

### 🔹 ШАГ 5: Проверить работу

1. **Добавьте товары в корзину** в Web App
2. **Оформите заказ**
3. **Заказ должен прийти в бота** и отобразиться сообщением

## 🐛 Если что-то не работает:

### ❌ Web App не открывается
1. Проверьте, что GitHub Pages включен
2. Проверьте ссылку: https://denisklyuchko-design.github.io/mango/telegram_app.html
3. Убедитесь, что файл загружен в репозиторий

### ❌ Бот не отвечает
1. Проверьте, что бот запущен (в терминале должно быть INFO сообщение)
2. Проверьте токен в файле `backend/telegram_bot.py`
3. Убедитесь, что зависимости установлены

### ❌ Заказ не создается
1. Проверьте консоль браузера в Web App (F12 → Console)
2. Проверьте логи бота в терминале
3. Убедитесь, что Web App URL правильный

## 📱 Ссылки:

- **Бот**: https://t.me/mango_sushi_wok_bot (или ваш username)
- **Web App**: https://denisklyuchko-design.github.io/mango/telegram_app.html
- **GitHub**: https://github.com/denisklyuchko-design/mango

## 🎯 Что делать дальше:

1. **Протестируйте все функции**:
   - Создание заказа
   - Просмотр заказов (/orders)
   - Помощь (/help)
   - Админ панель (/admin)

2. **Настройте под себя**:
   - Измените меню в `frontend/telegram_app.html`
   - Поменяйте контакты в `backend/telegram_bot.py`
   - Настройте цены

3. **Разверните на сервере** (опционально):
   - Арендуйте VPS
   - Настройте автозапуск бота
   - Используйте базу данных вместо памяти

## 📞 Если нужна помощь:

1. Проверьте логи бота в терминале
2. Проверьте консоль браузера (F12)
3. Убедитесь, что все URL правильные
4. Перечитайте эту инструкцию

**Удачи! 🍀**