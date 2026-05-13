#!/usr/bin/env python3
"""
Telegram Bot for Mango Sushi Wok POS System
Интеграция с Telegram Web App
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = '8791266418:AAELCANoPfk88UHrbXRKzjEuWGIalv5npSs'  # Ваш токен
WEBAPP_URL = 'https://denisklyuchko-design.github.io/mango/frontend/index_final.html'  # Ваш GitHub Pages URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище данных (в реальном проекте используйте базу данных)
orders_db = []
users_db = {}

class OrderManager:
    """Управление заказами"""
    
    @staticmethod
    def create_order(user_id: int, order_data: dict) -> dict:
        """Создание нового заказа"""
        order = {
            'id': len(orders_db) + 1,
            'user_id': user_id,
            'items': order_data.get('items', []),
            'total': order_data.get('total', 0),
            'status': 'new',
            'created_at': datetime.now().isoformat(),
            'type': order_data.get('type', 'table'),
            'table_id': order_data.get('table_id'),
            'delivery_info': order_data.get('delivery_info')
        }
        orders_db.append(order)
        return order
    
    @staticmethod
    def get_user_orders(user_id: int) -> list:
        """Получение заказов пользователя"""
        return [o for o in orders_db if o['user_id'] == user_id]
    
    @staticmethod
    def get_order_stats() -> dict:
        """Статистика по заказам"""
        total_orders = len(orders_db)
        total_revenue = sum(o['total'] for o in orders_db)
        today_orders = [o for o in orders_db if o['created_at'][:10] == datetime.now().strftime('%Y-%m-%d')]
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'today_orders': len(today_orders),
            'today_revenue': sum(o['total'] for o in today_orders)
        }

# Клавиатуры
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🍱 Меню", web_app=WebAppInfo(url=WEBAPP_URL)))
    builder.add(KeyboardButton(text="📊 Мои заказы"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.add(KeyboardButton(text="📞 Контакты"))
    return builder.as_keyboard(resize_keyboard=True)

def get_order_keyboard(order_id: int) -> ReplyKeyboardMarkup:
    """Клавиатура для заказа"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=f"📋 Заказ #{order_id}"))
    builder.add(KeyboardButton(text="🔄 Обновить статус"))
    return builder.as_keyboard(resize_keyboard=True)

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Сохраняем пользователя
    users_db[user.id] = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language': user.language_code
    }
    
    welcome_text = f"""
🥭 **Добро пожаловать в Mango Sushi Wok!**

Привет, {user.first_name}! 👋

Я ваш персональный помощник для заказа вкуснейших суши и вок.

🎯 **Что я умею:**
• 🍱 Показывать меню с ценами в злотых
• 📱 Принимать заказы через удобное Web App
• 📊 Отслеживать статус заказов
• 🚚 Организовывать доставку

👇 **Нажмите кнопку ниже, чтобы начать заказ!**
    """
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Обработчик команды /menu"""
    menu_text = """
🍱 **Наше меню:**

**🍣 Суши и роллы:**
• Филадельфия Люкс - 28 zł
• Калифорния - 22 zł
• Дракон - 26 zł

**🍜 Вок и супы:**
• Рамен - 26 zł
• Том Ям - 28 zł
• Удон с морепродуктами - 28 zł

**🎁 Сеты:**
• Сет Премиум - 120 zł
• Сет для двоих - 80 zł

👉 Нажмите кнопку "🍱 Меню" ниже, чтобы увидеть полное меню и сделать заказ!
    """
    
    await message.answer(
        menu_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
ℹ️ **Помощь:**

**Как сделать заказ:**
1. Нажмите кнопку "🍱 Меню"
2. Выберите блюда и добавьте в корзину
3. Оформите заказ через Web App
4. Оплатите при получении или онлайн

**Доставка:**
🚚 Доставка по городу - 10 zł
⏱️ Время доставки - 45-60 минут
💰 Минимальный заказ - 50 zł

**Контакты:**
📞 Телефон: +48 123 456 789
📧 Email: info@mangosushiwok.com
🌐 Сайт: mangosushiwok.com

**Команды:**
/start - Начать работу
/menu - Показать меню
/orders - Мои заказы
/help - Эта справка
    """
    
    await message.answer(
        help_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(Command("orders"))
async def cmd_orders(message: types.Message):
    """Обработчик команды /orders"""
    user_id = message.from_user.id
    orders = OrderManager.get_user_orders(user_id)
    
    if not orders:
        await message.answer(
            "📋 У вас пока нет заказов.\n\nНажмите кнопку '🍱 Меню', чтобы сделать первый заказ!",
            reply_markup=get_main_keyboard()
        )
        return
    
    orders_text = "📋 **Ваши заказы:**\n\n"
    for order in orders[-5:]:  # Показываем последние 5 заказов
        status_emoji = {
            'new': '🆕',
            'cooking': '👨‍🍳',
            'ready': '✅',
            'delivered': '🚚',
            'cancelled': '❌'
        }.get(order['status'], '📋')
        
        orders_text += f"""
{status_emoji} **Заказ #{order['id']}**
📅 {order['created_at'][:16].replace('T', ' ')}
💰 {order['total']} zł
📦 {len(order['items'])} позиций
Статус: {order['status']}
        """
    
    await message.answer(
        orders_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Админ панель"""
    stats = OrderManager.get_order_stats()
    await message.answer(
        f"""
📊 **Статистика:**
Всего заказов: {stats['total_orders']}
Выручка: {stats['total_revenue']} zł
За сегодня: {stats['today_orders']} заказов, {stats['today_revenue']} zł
        """,
        parse_mode="Markdown"
    )

@dp.message()
async def handle_message(message: types.Message):
    """Обработчик текстовых сообщений"""
    text = message.text
    
    if text == "🍱 Меню":
        # Отправляем Web App
        await message.answer(
            "🍱 Открываю меню...\n\nВыбирайте блюда и оформляйте заказ!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🍱 Открыть меню", web_app=WebAppInfo(url=WEBAPP_URL))]
                ],
                resize_keyboard=True
            )
        )
    
    elif text == "📊 Мои заказы":
        await cmd_orders(message)
    
    elif text == "ℹ️ Помощь":
        await cmd_help(message)
    
    elif text == "📞 Контакты":
        contacts_text = """
📞 **Наши контакты:**

🏢 **Адрес:**
ул. Примерная 123
Варшава, Польша

🕐 **Режим работы:**
Пн-Чт: 12:00 - 22:00
Пт-Сб: 12:00 - 23:00
Вс: 12:00 - 21:00

📞 **Телефон:** +48 123 456 789
📧 **Email:** info@mangosushiwok.com
🌐 **Сайт:** mangosushiwok.com

📱 **Социальные сети:**
• Instagram: @mangosushiwok
• Facebook: Mango Sushi Wok
        """
        await message.answer(contacts_text, parse_mode="Markdown")

# Обработчик данных от Web App
@dp.message(lambda message: message.web_app_data)
async def handle_webapp_data(message: types.Message):
    """Обработчик данных от Web App"""
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get('type') == 'order':
            # Создаем заказ
            order = OrderManager.create_order(
                user_id=message.from_user.id,
                order_data=data.get('order', {})
            )
            
            # Отправляем подтверждение
            items_text = "\n".join([
                f"• {item['name']} x{item['q']} - {item['p'] * item['q']} zł"
                for item in order['items']
            ])
            
            confirmation_text = f"""
✅ **Заказ успешно создан!**

📋 **Заказ #{order['id']}**

**Состав заказа:**
{items_text}

💰 **Итого:** {order['total']} zł

📍 **Тип:** {'Доставка' if order['type'] == 'delivery' else 'Стол'}

⏱️ **Время приготовления:** 20-30 минут

Мы уже начали готовить ваш заказ! 🍳
            """
            
            await message.answer(
                confirmation_text,
                reply_markup=get_order_keyboard(order['id']),
                parse_mode="Markdown"
            )
            
            # Отправляем уведомление администратору (если нужно)
            logger.info(f"Новый заказ #{order['id']} от пользователя {message.from_user.id}")
    
    except Exception as e:
        logger.error(f"Ошибка обработки данных Web App: {e}")
        await message.answer("❌ Произошла ошибка при обработке заказа. Попробуйте еще раз.")

async def main():
    """Основная функция"""
    logger.info("Запуск бота...")
    logger.info(f"Web App URL: {WEBAPP_URL}")
    
    # Удаляем вебхук (если использовался)
    await bot.delete_webhook()
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")