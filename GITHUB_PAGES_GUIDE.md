# 📖 ПОДРОБНАЯ ИНСТРУКЦИЯ ПО НАСТРОЙКЕ GITHUB PAGES

## 🔹 ШАГ 1: Перейдите в ваш репозиторий

1. Откройте браузер
2. Перейдите по ссылке: https://github.com/denisklyuchko-design/mango
3. Вы должны увидеть ваш репозиторий

## 🔹 ШАГ 2: Загрузите файл telegram_app.html

### Вариант A: Через веб-интерфейс GitHub

1. В вашем репозитории нажмите кнопку **"Add file"** → **"Upload files"**
2. Перетащите файл `frontend/telegram_app.html` в область загрузки
   - Или нажмите "choose your files" и выберите файл
3. В поле "Commit changes" введите: "Add Telegram Web App"
4. Нажмите **"Commit changes"**

### Вариант B: Через Git (если установлен)

```bash
# Клонируйте репозиторий (если еще не клонировали)
git clone https://github.com/denisklyuchko-design/mango.git
cd mango

# Скопируйте файл
copy c:\pos_project\frontend\telegram_app.html .

# Или для Mac/Linux:
# cp /path/to/pos_project/frontend/telegram_app.html .

# Добавьте файл в git
git add telegram_app.html

# Сделайте коммит
git commit -m "Add Telegram Web App"

# Отправьте на GitHub
git push origin main
```

## 🔹 ШАГ 3: Включите GitHub Pages

1. **В вашем репозитории** перейдите во вкладку **"Settings"** (вверху)
2. **В левом меню** найдите раздел **"Pages"** и нажмите на него
3. **Настройте параметры**:
   - **Source**: Выберите "Deploy from a branch"
   - **Branch**: 
     - В первом выпадающем списке выберите **"main"** (или "master")
     - Во втором выпадающем списке выберите **"/ (root)"**
4. **Нажмите кнопку "Save"**

## 🔹 ШАГ 4: Проверьте, что GitHub Pages включился

1. После сохранения, подождите **1-2 минуты**
2. На той же странице (Settings → Pages) вы должны увидеть:
   - "Your site is live at https://denisklyuchko-design.github.io/mango/"
3. **Проверьте ссылку**:
   - Откройте: https://denisklyuchko-design.github.io/mango/telegram_app.html
   - Должно открыться ваше меню с суши

## 🔹 ШАГ 5: Проверьте работу Web App

1. Откройте ссылку: https://denisklyuchko-design.github.io/mango/telegram_app.html
2. Вы должны увидеть:
   - Логотип Mango Sushi Wok
   - Меню с блюдами
   - Кнопки категорий
   - Корзину внизу

## 🐛 ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ:

### ❌ Не вижу вкладку "Pages" в Settings

**Решение:**
- Убедитесь, что вы владелец репозитория
- Попробуйте обновить страницу (F5)
- Выйдите и войдите в аккаунт снова

### ❌ После сохранения ссылка не работает

**Решение:**
1. Подождите 2-3 минуты (GitHub Pages может задерживаться)
2. Проверьте, что файл действительно загружен:
   - Перейдите в репозиторий
   - Убедитесь, что видите файл `telegram_app.html`
3. Попробуйте очистить кэш браузера (Ctrl+Shift+Delete)

### ❌ Вижу ошибку 404

**Решение:**
1. Проверьте правильность ссылки:
   - Должно быть: `https://denisklyuchko-design.github.io/mango/telegram_app.html`
   - НЕ: `https://denisklyuchko-design.github.io/telegram_app.html`
2. Убедитесь, что файл называется именно `telegram_app.html` (не `Telegram_app.html`)

### ❌ Файл не загружается

**Решение:**
1. Проверьте размер файла (должен быть меньше 100MB)
2. Попробуйте загрузить через Git (вариант B выше)
3. Проверьте интернет-соединение

## 📱 АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ (если GitHub Pages не работает):

### Вариант 1: Vercel (бесплатно и быстро)

1. Зарегистрируйтесь на https://vercel.com
2. Импортируйте ваш GitHub репозиторий
3. Vercel автоматически развернет сайт
4. Получите ссылку вида: `https://mango-telegram-app.vercel.app/telegram_app.html`

### Вариант 2: Netlify (бесплатно)

1. Зарегистрируйтесь на https://netlify.com
2. Перетащите папку с файлом `telegram_app.html`
3. Получите ссылку вида: `https://mango-sushi-wok.netlify.app/telegram_app.html`

### Вариант 3: Ваш хостинг

Если у вас есть хостинг:
1. Загрузите файл `telegram_app.html` на хостинг
2. Получите ссылку: `https://mangosushiwok.com/telegram_app.html`

## 🔄 ЧТО ДЕЛАТЬ ПОСЛЕ НАСТРОЙКИ GITHUB PAGES:

1. **Обновите URL в боте** (если использовали альтернативный хостинг):
   - Откройте `backend/telegram_bot.py`
   - Найдите строку: `WEBAPP_URL = 'https://...'`
   - Замените на вашу новую ссылку
   - Сохраните файл

2. **Перезапустите бота**:
   - Остановите бота (Ctrl+C в терминале)
   - Запустите снова: `python backend/telegram_bot.py`

3. **Протестируйте**:
   - Откройте бота в Telegram
   - Нажмите "🍱 Меню"
   - Должно открыться Web App

## 📞 ЕСЛИ ВСЕ ЕЩЕ ЕСТЬ ПРОБЛЕМЫ:

1. **Проверьте логи GitHub**:
   - В репозитории перейдите во вкладку "Actions"
   - Посмотрите, есть ли ошибки при сборке

2. **Проверьте права доступа**:
   - Убедитесь, что репозиторий публичный (Public)
   - Или что у вас есть доступ к настройкам

3. **Обратитесь в поддержку GitHub**:
   - https://support.github.com/contact

**Удачи! Все получится! 🚀**