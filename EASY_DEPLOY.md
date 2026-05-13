# 🚀 ПРОСТОЙ СПОСОБ РАЗВЕРТЫВАНИЯ TELEGRAM WEB APP

## ✅ Самый простой способ (без API):

### Шаг 1: Загрузите файл на GitHub

1. Откройте: https://github.com/denisklyuchko-design/mango
2. Нажмите кнопку **"Add file"** (справа сверху)
3. Выберите **"Upload files"**
4. Перетащите файл `frontend/telegram_app.html` в область загрузки
5. Нажмите **"Commit changes"**

### Шаг 2: Включите GitHub Pages

1. В репозитории перейдите во вкладку **"Settings"**
2. В левом меню нажмите **"Pages"**
3. В разделе **"Build and deployment"**:
   - **Source**: выберите **"Deploy from a branch"**
   - **Branch**: 
     - Первый dropdown: выберите **"main"** (или "master")
     - Второй dropdown: выберите **"/ (root)"**
4. Нажмите **"Save"**

### Шаг 3: Проверьте

1. Подождите 1-2 минуты
2. Откройте: https://denisklyuchko-design.github.io/mango/telegram_app.html
3. Должно открыться меню с суши

## 🎯 Альтернативные простые способы:

### Способ 1: Vercel (самый быстрый)

1. Зарегистрируйтесь на https://vercel.com
2. Нажмите **"Add New Project"**
3. Импортируйте ваш GitHub репозиторий `mango`
4. Vercel автоматически развернет сайт
5. Получите ссылку: `https://mango-telegram-app.vercel.app/telegram_app.html`

### Способ 2: Netlify Drop (очень просто)

1. Откройте: https://app.netlify.com/drop
2. Перетащите папку с файлом `telegram_app.html`
3. Получите ссылку: `https://mango-sushi-wok.netlify.app/telegram_app.html`

### Способ 3: GitHub Desktop (если установлен)

1. Откройте GitHub Desktop
2. File → Add Local Repository → выберите папку с проектом
3. Создайте новую ветку (Current Branch → New Branch)
4. Commit → Push to origin
5. Включите GitHub Pages как описано выше

## 📱 Что делать после получения ссылки:

### 1. Обновите URL в боте

Откройте `backend/telegram_bot.py` и замените:

```python
# Было:
WEBAPP_URL = 'https://denisklyuchko-design.github.io/mango/telegram_app.html'

# Стало (ваша новая ссылка):
WEBAPP_URL = 'https://mango-telegram-app.vercel.app/telegram_app.html'
# ИЛИ
WEBAPP_URL = 'https://mango-sushi-wok.netlify.app/telegram_app.html'
```

### 2. Перезапустите бота

```bash
# Остановите бота (Ctrl+C)
# Запустите снова:
python backend/telegram_bot.py
```

### 3. Протестируйте

1. Откройте бота в Telegram
2. Нажмите `/start`
3. Нажмите "🍱 Меню"
4. Должно открыться ваше Web App

## 🔗 Ваши ссылки:

- **Бот**: https://t.me/mango_sushi_wok_bot
- **GitHub**: https://github.com/denisklyuchko-design/mango
- **Web App** (после настройки): будет ваша ссылка из шага 3

## 📋 Чек-лист:

- [ ] Файл `telegram_app.html` загружен на GitHub
- [ ] GitHub Pages включен (Settings → Pages)
- [ ] Ссылка на Web App работает
- [ ] URL в боте обновлен
- [ ] Бот перезапущен
- [ ] Web App открывается в Telegram

## 🆘 Если что-то не так:

### Файл не загружается:
- Проверьте размер файла (должен быть < 100MB)
- Попробуйте через Git: `git add telegram_app.html && git commit && git push`

### GitHub Pages не включается:
- Убедитесь, что вы владелец репозитория
- Проверьте, что репозиторий публичный (Public)
- Обновите страницу и попробуйте снова

### Ссылка не работает:
- Подождите 2-3 минуты
- Проверьте правильность URL
- Очистите кэш браузера

## 💡 Совет:

Если GitHub Pages вызывает трудности, используйте **Vercel** или **Netlify** - они проще и быстрее!

**Удачи! Все получится! 🍀**