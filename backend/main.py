from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from enum import Enum
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import os

app = FastAPI(title="Sushi Restaurant POS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATA MODELS ====================

class Lang(str, Enum):
    ru = "ru"
    pl = "pl"


class OrderStatus(str, Enum):
    open = "open"
    cooking = "cooking"
    ready = "ready"
    delivered = "delivered"
    closed = "closed"
    cancelled = "cancelled"

class TableStatus(str, Enum):
    free = "free"
    occupied = "occupied"
    reserved = "reserved"

class DeliveryStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    on_way = "on_way"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    online = "online"

class UnitType(str, Enum):
    piece = "piece"
    kg = "kg"
    gram = "gram"
    liter = "liter"
    pack = "pack"

# ==================== PYDANTIC MODELS ====================

class MenuItem(BaseModel):
    name: str
    name_ru: Optional[str] = None
    name_pl: Optional[str] = None
    name_en: Optional[str] = None
    price: float
    category: str
    description: Optional[str] = ""
    ingredients: Optional[List[str]] = []
    prep_time: int = 15  # minutes
    is_active: bool = True

class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int
    notes: Optional[str] = ""
    price: Optional[float] = None

class OrderCreate(BaseModel):
    table_id: Optional[int] = None
    is_delivery: bool = False
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    items: List[OrderItem] = []

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    items: Optional[List[OrderItem]] = None

class TableCreate(BaseModel):
    name: str
    capacity: Optional[int] = 4

class InventoryItem(BaseModel):
    name: str
    name_ru: Optional[str] = None
    name_pl: Optional[str] = None
    unit: UnitType = UnitType.piece
    current_stock: float = 0
    min_stock: float = 0
    cost_per_unit: float = 0
    category: str = "general"

class InventoryUpdate(BaseModel):
    current_stock: Optional[float] = None
    min_stock: Optional[float] = None
    cost_per_unit: Optional[float] = None

class WriteOff(BaseModel):
    item_id: int
    quantity: float
    reason: str
    notes: Optional[str] = ""

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    method: PaymentMethod
    tip: Optional[float] = 0

class RecipeItem(BaseModel):
    menu_item_id: int
    ingredient_id: int
    quantity: float

class Employee(BaseModel):
    name: str
    role: str
    pin: str
    is_active: bool = True

# ==================== DATABASES (In-Memory) ====================

# Tables
tables_db: List[Dict[str, Any]] = [
    {"id": i, "name": f"Стол {i}", "capacity": 4, "status": "free", "order_id": None}
    for i in range(1, 13)
]

# Menu items (Sushi restaurant specific)
menu_db: List[Dict[str, Any]] = [
    # Sushi Rolls
    {"id": 1, "name": "Филадельфия", "name_ru": "Филадельфия", "name_en": "Philadelphia", "name_pl": "Filadelfia",
     "price": 399, "category": "sushi_rolls", "description": "Лосось, сливочный сыр, огурец, рис",
     "ingredients": ["лосось", "сливочный сыр", "огурец", "рис"], "prep_time": 10, "is_active": True},
    {"id": 2, "name": "Калифорния", "name_ru": "Калифорния", "name_en": "California", "name_pl": "Kalifornia",
     "price": 349, "category": "sushi_rolls", "description": "Краб, авокадо, огурец, икра масаго",
     "ingredients": ["краб", "авокадо", "огурец", "икра масаго"], "prep_time": 10, "is_active": True},
    {"id": 3, "name": "Дракон", "name_ru": "Дракон", "name_en": "Dragon", "name_pl": "Smok",
     "price": 449, "category": "sushi_rolls", "description": "Угорь, авокадо, унаги соус, кунжут",
     "ingredients": ["угорь", "авокадо", "унаги соус", "кунжут"], "prep_time": 12, "is_active": True},
    {"id": 4, "name": "Маки с лососем", "name_ru": "Маки с лососем", "name_en": "Salmon Maki", "name_pl": "Maki z łososiem",
     "price": 199, "category": "maki", "description": "Лосось, рис, нори",
     "ingredients": ["лосось", "рис", "нори"], "prep_time": 5, "is_active": True},
    {"id": 5, "name": "Маки с огурцом", "name_ru": "Маки с огурцом", "name_en": "Cucumber Maki", "name_pl": "Maki z ogórkiem",
     "price": 129, "category": "maki", "description": "Огурец, рис, нори",
     "ingredients": ["огурец", "рис", "нори"], "prep_time": 5, "is_active": True},
    
    # Nigiri & Sashimi
    {"id": 6, "name": "Нигири с лососем", "name_ru": "Нигири с лососем", "name_en": "Salmon Nigiri", "name_pl": "Nigiri z łososiem",
     "price": 149, "category": "nigiri", "description": "Лосось, рис",
     "ingredients": ["лосось", "рис"], "prep_time": 5, "is_active": True},
    {"id": 7, "name": "Нигири с тунцом", "name_ru": "Нигири с тунцом", "name_en": "Tuna Nigiri", "name_pl": "Nigiri z tuńczykiem",
     "price": 169, "category": "nigiri", "description": "Тунец, рис",
     "ingredients": ["тунец", "рис"], "prep_time": 5, "is_active": True},
    {"id": 8, "name": "Сашими микс", "name_ru": "Сашими микс", "name_en": "Sashimi Mix", "name_pl": "Miks sashimi",
     "price": 599, "category": "sashimi", "description": "Ассорти из лосося, тунца и желтохвоста",
     "ingredients": ["лосось", "тунец", "желтохвост"], "prep_time": 8, "is_active": True},
    
    # Hot Dishes
    {"id": 9, "name": "Темпура креветки", "name_ru": "Темпура креветки", "name_en": "Shrimp Tempura", "name_pl": "Krewetka tempura",
     "price": 349, "category": "hot_dishes", "description": "Креветки в кляре темпура",
     "ingredients": ["креветки", "кляр темпура"], "prep_time": 15, "is_active": True},
    {"id": 10, "name": "Рамен с курицей", "name_ru": "Рамен с курицей", "name_en": "Chicken Ramen", "name_pl": "Ramen z kurczakiem",
     "price": 399, "category": "hot_dishes", "description": "Бульон, лапша, курица, яйцо, нори",
     "ingredients": ["бульон", "лапша", "курица", "яйцо", "нори"], "prep_time": 12, "is_active": True},
    {"id": 11, "name": "Якитори", "name_ru": "Якитори", "name_en": "Yakitori", "name_pl": "Yakitori",
     "price": 299, "category": "hot_dishes", "description": "Куриные шашлычки на гриле",
     "ingredients": ["курица", "соус терияки"], "prep_time": 15, "is_active": True},
    
    # Soups
    {"id": 12, "name": "Мисо суп", "name_ru": "Мисо суп", "name_en": "Miso Soup", "name_pl": "Zupa miso",
     "price": 149, "category": "soups", "description": "Традиционный японский суп",
     "ingredients": ["паста мисо", "тофу", "водоросли вакаме"], "prep_time": 5, "is_active": True},
    
    # Drinks
    {"id": 13, "name": "Зеленый чай", "name_ru": "Зеленый чай", "name_en": "Green Tea", "name_pl": "Zielona herbata",
     "price": 89, "category": "drinks", "description": "Традиционный японский чай",
     "ingredients": ["зеленый чай"], "prep_time": 3, "is_active": True},
    {"id": 14, "name": "Саке", "name_ru": "Саке", "name_en": "Sake", "name_pl": "Sake",
     "price": 499, "category": "drinks", "description": "Японское рисовое вино, 300мл",
     "ingredients": ["саке"], "prep_time": 1, "is_active": True},
    {"id": 15, "name": "Асахи пиво", "name_ru": "Асахи пиво", "name_en": "Asahi Beer", "name_pl": "Piwo Asahi",
     "price": 299, "category": "drinks", "description": "Японское пиво, 330мл",
     "ingredients": ["пиво Asahi"], "prep_time": 1, "is_active": True},
    
    # Desserts
    {"id": 16, "name": "Моти микс", "name_ru": "Моти микс", "name_en": "Mochi Mix", "name_pl": "Miks mochi",
     "price": 249, "category": "desserts", "description": "Японские рисовые пирожные",
     "ingredients": ["рисовая мука", "сахар", "начинка"], "prep_time": 2, "is_active": True},
    {"id": 17, "name": "Мороженое", "name_ru": "Мороженое", "name_en": "Ice Cream", "name_pl": "Lody",
     "price": 149, "category": "desserts", "description": "Зеленый чай или кунжут",
     "ingredients": ["мороженое"], "prep_time": 2, "is_active": True},
    
    # Sets
    {"id": 18, "name": "Сет 'Премиум'", "name_ru": "Сет 'Премиум'", "name_en": "Premium Set", "name_pl": "Zestaw Premium",
     "price": 1999, "category": "sets", "description": "Филадельфия, Дракон, Сашими микс, Мисо суп",
     "ingredients": ["лосось", "угорь", "тунец", "сливочный сыр"], "prep_time": 20, "is_active": True},
    {"id": 19, "name": "Сет 'Вечеринка'", "name_ru": "Сет 'Вечеринка'", "name_en": "Party Set", "name_pl": "Zestaw imprezowy",
     "price": 2999, "category": "sets", "description": "Большой набор роллов на компанию",
     "ingredients": ["лосось", "тунец", "угорь", "краб", "авокадо"], "prep_time": 25, "is_active": True},
]

# Orders
orders_db: List[Dict[str, Any]] = []

# Inventory
inventory_db: List[Dict[str, Any]] = [
    {"id": 1, "name": "Лосось свежий", "name_ru": "Лосось свежий", "name_en": "Fresh Salmon", "name_pl": "Świeży łosoś",
     "unit": UnitType.kg, "current_stock": 5.0, "min_stock": 1.0, "cost_per_unit": 800, "category": "fish"},
    {"id": 2, "name": "Тунец свежий", "name_ru": "Тунец свежий", "name_en": "Fresh Tuna", "name_pl": "Świeży tuńczyk",
     "unit": UnitType.kg, "current_stock": 3.0, "min_stock": 0.5, "cost_per_unit": 1200, "category": "fish"},
    {"id": 3, "name": "Угорь копченый", "name_ru": "Угорь копченый", "name_en": "Smoked Eel", "name_pl": "Wędzony węgorz",
     "unit": UnitType.kg, "current_stock": 1.5, "min_stock": 0.3, "cost_per_unit": 1500, "category": "fish"},
    {"id": 4, "name": "Рис для суши", "name_ru": "Рис для суши", "name_en": "Sushi Rice", "name_pl": "Ryż do sushi",
     "unit": UnitType.kg, "current_stock": 10.0, "min_stock": 2.0, "cost_per_unit": 120, "category": "grains"},
    {"id": 5, "name": "Нори листы", "name_ru": "Нори листы", "name_en": "Nori Sheets", "name_pl": "Płatki nori",
     "unit": UnitType.pack, "current_stock": 20, "min_stock": 5, "cost_per_unit": 80, "category": "supplies"},
    {"id": 6, "name": "Сливочный сыр", "name_ru": "Сливочный сыр", "name_en": "Cream Cheese", "name_pl": "Ser kremowy",
     "unit": UnitType.kg, "current_stock": 2.0, "min_stock": 0.5, "cost_per_unit": 450, "category": "dairy"},
    {"id": 7, "name": "Авокадо", "name_ru": "Авокадо", "name_en": "Avocado", "name_pl": "Awokado",
     "unit": UnitType.piece, "current_stock": 15, "min_stock": 5, "cost_per_unit": 60, "category": "vegetables"},
    {"id": 8, "name": "Огурец", "name_ru": "Огурец", "name_en": "Cucumber", "name_pl": "Ogórek",
     "unit": UnitType.kg, "current_stock": 3.0, "min_stock": 0.5, "cost_per_unit": 80, "category": "vegetables"},
    {"id": 9, "name": "Соус унаги", "name_ru": "Соус унаги", "name_en": "Unagi Sauce", "name_pl": "Sos unagi",
     "unit": UnitType.liter, "current_stock": 2.0, "min_stock": 0.5, "cost_per_unit": 300, "category": "sauces"},
    {"id": 10, "name": "Икра масаго", "name_ru": "Икра масаго", "name_en": "Masago Roe", "name_pl": "Ikra masago",
     "unit": UnitType.kg, "current_stock": 0.5, "min_stock": 0.1, "cost_per_unit": 2000, "category": "seafood"},
    {"id": 11, "name": "Креветки", "name_ru": "Креветки", "name_en": "Shrimp", "name_pl": "Krewetki",
     "unit": UnitType.kg, "current_stock": 2.0, "min_stock": 0.5, "cost_per_unit": 600, "category": "seafood"},
    {"id": 12, "name": "Куриное филе", "name_ru": "Куриное филе", "name_en": "Chicken Fillet", "name_pl": "Filet z kurczaka",
     "unit": UnitType.kg, "current_stock": 3.0, "min_stock": 1.0, "cost_per_unit": 250, "category": "meat"},
    {"id": 13, "name": "Паста мисо", "name_ru": "Паста мисо", "name_en": "Miso Paste", "name_pl": "Pasta miso",
     "unit": UnitType.kg, "current_stock": 1.0, "min_stock": 0.2, "cost_per_unit": 400, "category": "supplies"},
    {"id": 14, "name": "Тофу", "name_ru": "Тофу", "name_en": "Tofu", "name_pl": "Tofu",
     "unit": UnitType.kg, "current_stock": 1.0, "min_stock": 0.3, "cost_per_unit": 200, "category": "supplies"},
    {"id": 15, "name": "Водоросли вакаме", "name_ru": "Водоросли вакаме", "name_en": "Wakame Seaweed", "name_pl": "Wodorosty wakame",
     "unit": UnitType.kg, "current_stock": 0.5, "min_stock": 0.1, "cost_per_unit": 600, "category": "supplies"},
]

# Recipes (menu item -> ingredients mapping)
recipes_db: List[Dict[str, Any]] = [
    # Philadelphia roll
    {"menu_item_id": 1, "ingredient_id": 1, "quantity": 0.08},  # salmon 80g
    {"menu_item_id": 1, "ingredient_id": 6, "quantity": 0.03},  # cream cheese 30g
    {"menu_item_id": 1, "ingredient_id": 8, "quantity": 0.05},  # cucumber 50g
    {"menu_item_id": 1, "ingredient_id": 4, "quantity": 0.025},  # rice 25g
    # California roll
    {"menu_item_id": 2, "ingredient_id": 7, "quantity": 0.05},  # avocado 50g
    {"menu_item_id": 2, "ingredient_id": 8, "quantity": 0.05},  # cucumber 50g
    {"menu_item_id": 2, "ingredient_id": 10, "quantity": 0.01},  # masago 10g
    {"menu_item_id": 2, "ingredient_id": 4, "quantity": 0.025},  # rice 25g
    # Dragon roll
    {"menu_item_id": 3, "ingredient_id": 3, "quantity": 0.08},  # eel 80g
    {"menu_item_id": 3, "ingredient_id": 7, "quantity": 0.05},  # avocado 50g
    {"menu_item_id": 3, "ingredient_id": 9, "quantity": 0.02},  # unagi sauce 20ml
    {"menu_item_id": 3, "ingredient_id": 4, "quantity": 0.025},  # rice 25g
    # Salmon maki
    {"menu_item_id": 4, "ingredient_id": 1, "quantity": 0.04},  # salmon 40g
    {"menu_item_id": 4, "ingredient_id": 5, "quantity": 0.5},  # nori 0.5 sheet
    {"menu_item_id": 4, "ingredient_id": 4, "quantity": 0.02},  # rice 20g
    # Cucumber maki
    {"menu_item_id": 5, "ingredient_id": 8, "quantity": 0.05},  # cucumber 50g
    {"menu_item_id": 5, "ingredient_id": 5, "quantity": 0.5},  # nori 0.5 sheet
    {"menu_item_id": 5, "ingredient_id": 4, "quantity": 0.02},  # rice 20g
    # Salmon nigiri
    {"menu_item_id": 6, "ingredient_id": 1, "quantity": 0.03},  # salmon 30g
    {"menu_item_id": 6, "ingredient_id": 4, "quantity": 0.02},  # rice 20g
    # Tuna nigiri
    {"menu_item_id": 7, "ingredient_id": 2, "quantity": 0.03},  # tuna 30g
    {"menu_item_id": 7, "ingredient_id": 4, "quantity": 0.02},  # rice 20g
]

# Write-offs log
write_offs_db: List[Dict[str, Any]] = []

# Payments
payments_db: List[Dict[str, Any]] = []

# Delivery orders
deliveries_db: List[Dict[str, Any]] = []

# Kitchen print queue
kitchen_queue: List[Dict[str, Any]] = []

# Statistics / Financial data
financial_stats = {
    "daily_sales": [],
    "monthly_sales": [],
    "total_revenue": 0,
    "total_costs": 0,
    "total_waste": 0,
}

# ==================== TRANSLATIONS ====================

translations = {
    "status_ok": {"ru": "Сервер работает", "pl": "Serwer działa", "en": "Server is running"},
    "order_created": {"ru": "Заказ создан", "pl": "Zamówienie utworzone", "en": "Order created"},
    "table_not_found": {"ru": "Стол не найден", "pl": "Stolik nie znaleziony", "en": "Table not found"},
    "table_occupied": {"ru": "Стол уже занят", "pl": "Stolik jest już zajęty", "en": "Table is already occupied"},
    "order_not_found": {"ru": "Заказ не найден", "pl": "Zamówienie nie znalezione", "en": "Order not found"},
    "order_closed": {"ru": "Заказ закрыт", "pl": "Zamówienie zamknięte", "en": "Order closed"},
    "insufficient_stock": {"ru": "Недостаточно товара на складе", "pl": "Niewystarczająca ilość towaru w magazynie", "en": "Insufficient stock"},
    "item_not_found": {"ru": "Товар не найден", "pl": "Produkt nie znaleziony", "en": "Item not found"},
    "write_off_recorded": {"ru": "Списание записано", "pl": "Wycofanie zapisane", "en": "Write-off recorded"},
    "payment_recorded": {"ru": "Оплата записана", "pl": "Płatność zapisana", "en": "Payment recorded"},
    "delivery_created": {"ru": "Доставка создана", "pl": "Dostawa utworzona", "en": "Delivery created"},
    "low_stock_alert": {"ru": "Заканчивается товар", "pl": "Kończący się towar", "en": "Low stock alert"},
}

# ==================== HELPER FUNCTIONS ====================

def get_translation(key: str, lang: str = "ru") -> str:
    return translations.get(key, {}).get(lang, key)

def calculate_order_total(items: List[Dict]) -> float:
    total = 0
    for item in items:
        menu_item = next((m for m in menu_db if m["id"] == item["menu_item_id"]), None)
        if menu_item:
            price = item.get("price") or menu_item["price"]
            total += price * item["quantity"]
    return total

def check_inventory_for_order(items: List[Dict]) -> Dict[int, float]:
    """Check if there's enough inventory for an order. Returns required quantities."""
    required = {}
    for order_item in items:
        recipes = [r for r in recipes_db if r["menu_item_id"] == order_item["menu_item_id"]]
        for recipe in recipes:
            ingredient_id = recipe["ingredient_id"]
            qty_needed = recipe["quantity"] * order_item["quantity"]
            required[ingredient_id] = required.get(ingredient_id, 0) + qty_needed
    
    # Check stock
    for item_id, qty in required.items():
        inventory_item = next((i for i in inventory_db if i["id"] == item_id), None)
        if inventory_item and inventory_item["current_stock"] < qty:
            return None  # Insufficient stock
    
    return required

def deduct_inventory(required: Dict[int, float]):
    """Deduct ingredients from inventory."""
    for item_id, qty in required.items():
        inventory_item = next((i for i in inventory_db if i["id"] == item_id), None)
        if inventory_item:
            inventory_item["current_stock"] -= qty

def get_low_stock_items() -> List[Dict]:
    """Get items that are below minimum stock level."""
    return [item for item in inventory_db if item["current_stock"] <= item["min_stock"]]

def add_to_kitchen_queue(order: Dict):
    """Add order to kitchen print queue."""
    kitchen_queue.append({
        "id": len(kitchen_queue) + 1,
        "order_id": order["id"],
        "items": order["items"],
        "table_name": next((t["name"] for t in tables_db if t["id"] == order.get("table_id")), None) if order.get("table_id") else None,
        "is_delivery": order.get("is_delivery", False),
        "customer_name": order.get("customer_name"),
        "customer_phone": order.get("customer_phone"),
        "delivery_address": order.get("delivery_address"),
        "created_at": order["created_at"],
        "status": "pending",
        "printed": False,
    })

def calculate_financial_stats():
    """Calculate financial statistics."""
    closed_orders = [o for o in orders_db if o["status"] == "closed"]
    total_revenue = sum(o.get("total", 0) for o in closed_orders)
    total_payments = sum(p["amount"] for p in payments_db)
    total_waste = sum(w["total_cost"] for w in write_offs_db)
    
    # Calculate inventory value
    inventory_value = sum(item["current_stock"] * item["cost_per_unit"] for item in inventory_db)
    
    return {
        "total_revenue": total_revenue,
        "total_payments": total_payments,
        "total_waste": total_waste,
        "inventory_value": inventory_value,
        "profit": total_revenue - total_waste,  # Simplified
        "orders_count": len(closed_orders),
        "avg_order_value": total_revenue / len(closed_orders) if closed_orders else 0,
    }

# ==================== API ENDPOINTS ====================

@app.get("/status")
def status(lang: Lang = Lang.ru):
    return {"message": get_translation("status_ok", lang.value), "timestamp": datetime.now().isoformat()}

# ==================== TABLES ====================

@app.get("/tables")
def get_tables():
    return {"tables": tables_db}

@app.post("/tables")
def create_table(table: TableCreate):
    new_id = max((t["id"] for t in tables_db), default=0) + 1
    new_table = {
        "id": new_id,
        "name": table.name,
        "capacity": table.capacity or 4,
        "status": "free",
        "order_id": None,
    }
    tables_db.append(new_table)
    return {"message": "Table created", "table": new_table}

@app.put("/tables/{table_id}")
def update_table(table_id: int, table: TableCreate):
    existing = next((t for t in tables_db if t["id"] == table_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Table not found")
    existing["name"] = table.name
    existing["capacity"] = table.capacity or 4
    return {"message": "Table updated", "table": existing}

@app.delete("/tables/{table_id}")
def delete_table(table_id: int):
    global tables_db
    table = next((t for t in tables_db if t["id"] == table_id), None)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    if table["status"] == "occupied":
        raise HTTPException(status_code=400, detail="Cannot delete occupied table")
    tables_db = [t for t in tables_db if t["id"] != table_id]
    return {"message": "Table deleted"}

# ==================== MENU ====================

@app.get("/menu")
def get_menu(category: Optional[str] = None, lang: Optional[str] = None):
    items = [m for m in menu_db if m["is_active"]]
    if category:
        items = [m for m in items if m["category"] == category]
    if lang:
        for item in items:
            item["display_name"] = item.get(f"name_{lang}") or item["name"]
    return {"menu": items, "categories": list(set(m["category"] for m in menu_db if m["is_active"]))}

@app.get("/menu/{item_id}")
def get_menu_item(item_id: int):
    item = next((m for m in menu_db if m["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@app.post("/menu")
def create_menu_item(item: MenuItem):
    new_id = max((m["id"] for m in menu_db), default=0) + 1
    new_item = {
        "id": new_id,
        "name": item.name,
        "name_ru": item.name_ru or item.name,
        "name_pl": item.name_pl or item.name,
        "name_en": item.name_en or item.name,
        "price": item.price,
        "category": item.category,
        "description": item.description or "",
        "ingredients": item.ingredients or [],
        "prep_time": item.prep_time,
        "is_active": item.is_active,
    }
    menu_db.append(new_item)
    return {"message": "Menu item created", "item": new_item}

@app.put("/menu/{item_id}")
def update_menu_item(item_id: int, item: MenuItem):
    existing = next((m for m in menu_db if m["id"] == item_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Menu item not found")
    existing["name"] = item.name
    existing["price"] = item.price
    existing["category"] = item.category
    existing["description"] = item.description or ""
    existing["prep_time"] = item.prep_time
    existing["is_active"] = item.is_active
    return {"message": "Menu item updated", "item": existing}

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int):
    global menu_db
    item = next((m for m in menu_db if m["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    item["is_active"] = False
    return {"message": "Menu item deactivated"}

# ==================== ORDERS ====================

@app.post("/orders")
def create_order(order: OrderCreate, lang: Lang = Lang.ru):
    # Validate table if provided
    table = None
    if order.table_id:
        table = next((t for t in tables_db if t["id"] == order.table_id), None)
        if table is None:
            raise HTTPException(status_code=404, detail=get_translation("table_not_found", lang.value))
        if table["status"] == "occupied":
            raise HTTPException(status_code=400, detail=get_translation("table_occupied", lang.value))
    
    # Check inventory
    if order.items:
        required = check_inventory_for_order(order.items)
        if required is None:
            raise HTTPException(status_code=400, detail=get_translation("insufficient_stock", lang.value))
    else:
        required = {}
    
    # Create order
    new_order = {
        "id": len(orders_db) + 1,
        "table_id": order.table_id,
        "is_delivery": order.is_delivery,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "items": [],
        "total": 0,
        "status": "open",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    
    # Add items
    for order_item in order.items:
        menu_item = next((m for m in menu_db if m["id"] == order_item.menu_item_id), None)
        if menu_item:
            new_order["items"].append({
                "menu_item_id": order_item.menu_item_id,
                "menu_item_name": menu_item["name"],
                "quantity": order_item.quantity,
                "price": menu_item["price"],
                "notes": order_item.notes or "",
                "status": "pending",
            })
    
    new_order["total"] = calculate_order_total(new_order["items"])
    
    orders_db.append(new_order)
    
    # Update table status
    if table:
        table["status"] = "occupied"
        table["order_id"] = new_order["id"]
    
    # Deduct inventory
    if required:
        deduct_inventory(required)
    
    # Add to kitchen queue
    add_to_kitchen_queue(new_order)
    
    return {
        "message": get_translation("order_created", lang.value),
        "order": new_order,
        "table": table,
    }

@app.get("/orders")
def get_orders(status: Optional[OrderStatus] = None, table_id: Optional[int] = None):
    orders = orders_db.copy()
    if status:
        orders = [o for o in orders if o["status"] == status]
    if table_id:
        orders = [o for o in orders if o["table_id"] == table_id]
    return {"orders": orders}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=get_translation("order_not_found", "ru"))
    return order

@app.put("/orders/{order_id}")
def update_order(order_id: int, update: OrderUpdate):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if update.status:
        order["status"] = update.status.value
        order["updated_at"] = datetime.now().isoformat(timespec="seconds")
        
        if update.status == OrderStatus.ready:
            order["ready_at"] = datetime.now().isoformat(timespec="seconds")
        elif update.status == OrderStatus.delivered:
            order["delivered_at"] = datetime.now().isoformat(timespec="seconds")
    
    if update.items:
        for new_item in update.items:
            menu_item = next((m for m in menu_db if m["id"] == new_item.menu_item_id), None)
            if menu_item:
                order["items"].append({
                    "menu_item_id": new_item.menu_item_id,
                    "menu_item_name": menu_item["name"],
                    "quantity": new_item.quantity,
                    "price": menu_item["price"],
                    "notes": new_item.notes or "",
                    "status": "pending",
                })
        order["total"] = calculate_order_total(order["items"])
        order["updated_at"] = datetime.now().isoformat(timespec="seconds")
    
    return {"message": "Order updated", "order": order}

@app.post("/orders/{order_id}/close")
def close_order(order_id: int):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["status"] == "closed":
        raise HTTPException(status_code=400, detail="Order already closed")
    
    order["status"] = "closed"
    order["closed_at"] = datetime.now().isoformat(timespec="seconds")
    
    # Free up table
    table = next((t for t in tables_db if t["order_id"] == order_id), None)
    if table:
        table["status"] = "free"
        table["order_id"] = None
    
    return {"message": "Order closed", "order": order}

@app.post("/orders/{order_id}/print")
def print_order(order_id: int):
    """Generate kitchen ticket for printing."""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Generate printable ticket
    ticket = {
        "order_id": order["id"],
        "table": next((t["name"] for t in tables_db if t["id"] == order.get("table_id")), "Delivery") if order.get("table_id") else "Delivery",
        "items": order["items"],
        "total": order["total"],
        "created_at": order["created_at"],
        "ticket_text": generate_ticket_text(order),
    }
    
    return {"ticket": ticket}

def generate_ticket_text(order: Dict) -> str:
    lines = []
    lines.append("=" * 40)
    lines.append("    SUSHI RESTAURANT")
    lines.append("    КУХОННЫЙ ЧЕК")
    lines.append("=" * 40)
    
    if order.get("table_id"):
        table = next((t for t in tables_db if t["id"] == order["table_id"]), None)
        if table:
            lines.append(f"Стол: {table['name']}")
    
    if order.get("is_delivery"):
        lines.append("ДОСТАВКА")
        if order.get("customer_name"):
            lines.append(f"Клиент: {order['customer_name']}")
        if order.get("customer_phone"):
            lines.append(f"Телефон: {order['customer_phone']}")
        if order.get("delivery_address"):
            lines.append(f"Адрес: {order['delivery_address']}")
    
    lines.append(f"Заказ #{order['id']}")
    lines.append(f"Время: {order['created_at']}")
    lines.append("-" * 40)
    
    for item in order["items"]:
        qty_str = f"{item['quantity']}x"
        name = item["menu_item_name"]
        notes = f" ({item['notes']})" if item.get("notes") else ""
        lines.append(f"{qty_str} {name}{notes}")
    
    lines.append("-" * 40)
    lines.append(f"ИТОГО: {order['total']} руб.")
    lines.append("=" * 40)
    
    return "\n".join(lines)

# ==================== KITCHEN ====================

@app.get("/kitchen/queue")
def get_kitchen_queue():
    return {"queue": kitchen_queue}

@app.put("/kitchen/queue/{queue_id}")
def update_kitchen_queue(queue_id: int, status: str = "printed"):
    item = next((q for q in kitchen_queue if q["id"] == queue_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    item["status"] = status
    item["printed"] = (status == "printed")
    return {"message": "Queue updated", "item": item}

@app.get("/kitchen/orders")
def get_kitchen_orders():
    """Get orders that need to be prepared."""
    cooking_orders = [o for o in orders_db if o["status"] in ["open", "cooking"]]
    return {"orders": cooking_orders}

# ==================== INVENTORY ====================

@app.get("/inventory")
def get_inventory(category: Optional[str] = None):
    items = inventory_db.copy()
    if category:
        items = [i for i in items if i["category"] == category]
    return {"inventory": items}

@app.get("/inventory/low-stock")
def get_low_stock():
    return {"items": get_low_stock_items()}

@app.get("/inventory/{item_id}")
def get_inventory_item(item_id: int):
    item = next((i for i in inventory_db if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=get_translation("item_not_found", "ru"))
    return item

@app.post("/inventory")
def create_inventory_item(item: InventoryItem):
    new_id = max((i["id"] for i in inventory_db), default=0) + 1
    new_item = {
        "id": new_id,
        "name": item.name,
        "name_ru": item.name_ru or item.name,
        "name_pl": item.name_pl or item.name,
        "name_en": item.name_en or item.name,
        "unit": item.unit.value,
        "current_stock": item.current_stock,
        "min_stock": item.min_stock,
        "cost_per_unit": item.cost_per_unit,
        "category": item.category,
    }
    inventory_db.append(new_item)
    return {"message": "Inventory item created", "item": new_item}

@app.put("/inventory/{item_id}")
def update_inventory_item(item_id: int, update: InventoryUpdate):
    item = next((i for i in inventory_db if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if update.current_stock is not None:
        item["current_stock"] = update.current_stock
    if update.min_stock is not None:
        item["min_stock"] = update.min_stock
    if update.cost_per_unit is not None:
        item["cost_per_unit"] = update.cost_per_unit
    return {"message": "Inventory updated", "item": item}

# ==================== WRITE-OFFS ====================

@app.post("/inventory/write-off")
def create_write_off(write_off: WriteOff):
    item = next((i for i in inventory_db if i["id"] == write_off.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item["current_stock"] < write_off.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for write-off")
    
    item["current_stock"] -= write_off.quantity
    total_cost = write_off.quantity * item["cost_per_unit"]
    
    write_off_record = {
        "id": len(write_offs_db) + 1,
        "item_id": write_off.item_id,
        "item_name": item["name"],
        "quantity": write_off.quantity,
        "unit": item["unit"],
        "reason": write_off.reason,
        "notes": write_off.notes or "",
        "total_cost": total_cost,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    
    write_offs_db.append(write_off_record)
    
    return {"message": get_translation("write_off_recorded", "ru"), "write_off": write_off_record}

@app.get("/inventory/write-offs")
def get_write_offs(days: Optional[int] = 30):
    cutoff = datetime.now() - timedelta(days=days)
    recent = [w for w in write_offs_db if datetime.fromisoformat(w["created_at"]) > cutoff]
    return {"write_offs": recent}

# ==================== PAYMENTS ====================

@app.post("/payments")
def create_payment(payment: PaymentCreate):
    order = next((o for o in orders_db if o["id"] == payment.order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment_record = {
        "id": len(payments_db) + 1,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "method": payment.method.value,
        "tip": payment.tip or 0,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    
    payments_db.append(payment_record)
    
    return {"message": get_translation("payment_recorded", "ru"), "payment": payment_record}

@app.get("/payments")
def get_payments(days: Optional[int] = 30):
    cutoff = datetime.now() - timedelta(days=days)
    recent = [p for p in payments_db if datetime.fromisoformat(p["created_at"]) > cutoff]
    return {"payments": recent}

# ==================== DELIVERIES ====================

@app.post("/deliveries")
def create_delivery(order: OrderCreate):
    """Create a delivery order."""
    order.is_delivery = True
    result = create_order(order)
    
    delivery_record = {
        "id": len(deliveries_db) + 1,
        "order_id": result["order"]["id"],
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "estimated_time": (datetime.now() + timedelta(minutes=45)).isoformat(timespec="seconds"),
    }
    
    deliveries_db.append(delivery_record)
    
    return {"message": get_translation("delivery_created", "ru"), "delivery": delivery_record, "order": result["order"]}

@app.get("/deliveries")
def get_deliveries(status: Optional[str] = None):
    deliveries = deliveries_db.copy()
    if status:
        deliveries = [d for d in deliveries if d["status"] == status]
    return {"deliveries": deliveries}

@app.put("/deliveries/{delivery_id}")
def update_delivery(delivery_id: int, status: str):
    delivery = next((d for d in deliveries_db if d["id"] == delivery_id), None)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    delivery["status"] = status
    if status == "on_way":
        delivery["dispatched_at"] = datetime.now().isoformat(timespec="seconds")
    elif status == "delivered":
        delivery["delivered_at"] = datetime.now().isoformat(timespec="seconds")
    return {"message": "Delivery updated", "delivery": delivery}

# ==================== STATISTICS / REPORTS ====================

@app.get("/statistics/financial")
def get_financial_statistics():
    return calculate_financial_stats()

@app.get("/statistics/daily")
def get_daily_statistics(date: Optional[str] = None):
    """Get daily statistics for a specific date."""
    target_date = date if date else datetime.now().strftime("%Y-%m-%d")
    
    # Filter orders for the date
    daily_orders = [o for o in orders_db 
                   if o.get("created_at", "")[:10] == target_date]
    
    daily_revenue = sum(o.get("total", 0) for o in daily_orders if o["status"] == "closed")
    daily_payments = [p for p in payments_db if p["created_at"][:10] == target_date]
    
    # Payment method breakdown
    payment_methods = {}
    for p in daily_payments:
        method = p["method"]
        payment_methods[method] = payment_methods.get(method, 0) + p["amount"]
    
    return {
        "date": target_date,
        "total_orders": len(daily_orders),
        "closed_orders": len([o for o in daily_orders if o["status"] == "closed"]),
        "revenue": daily_revenue,
        "payment_methods": payment_methods,
        "avg_order_value": daily_revenue / len(daily_orders) if daily_orders else 0,
    }

@app.get("/statistics/popular-items")
def get_popular_items(limit: int = 10):
    """Get most popular menu items."""
    item_sales = {}
    for order in orders_db:
        for item in order.get("items", []):
            item_id = item["menu_item_id"]
            if item_id not in item_sales:
                item_sales[item_id] = {"name": item["menu_item_name"], "quantity": 0, "revenue": 0}
            item_sales[item_id]["quantity"] += item["quantity"]
            item_sales[item_id]["revenue"] += item["price"] * item["quantity"]
    
    sorted_items = sorted(item_sales.values(), key=lambda x: x["revenue"], reverse=True)
    return {"items": sorted_items[:limit]}

@app.get("/alerts")
def get_alerts():
    """Get all system alerts (low stock, etc.)."""
    alerts = []
    
    # Low stock alerts
    low_stock = get_low_stock_items()
    for item in low_stock:
        alerts.append({
            "type": "low_stock",
            "severity": "warning",
            "message": f"Заканчивается {item['name']}: {item['current_stock']} {item['unit']}",
            "item_id": item["id"],
        })
    
    # Active orders alerts
    active_orders = [o for o in orders_db if o["status"] in ["open", "cooking"]]
    if len(active_orders) > 10:
        alerts.append({
            "type": "high_volume",
            "severity": "info",
            "message": f"Много активных заказов: {len(active_orders)}",
        })
    
    return {"alerts": alerts}

# ==================== RECIPES ====================

@app.get("/recipes")
def get_recipes(menu_item_id: Optional[int] = None):
    recipes = recipes_db.copy()
    if menu_item_id:
        recipes = [r for r in recipes if r["menu_item_id"] == menu_item_id]
    
    # Enrich with item names
    enriched = []
    for recipe in recipes:
        menu_item = next((m for m in menu_db if m["id"] == recipe["menu_item_id"]), None)
        ingredient = next((i for i in inventory_db if i["id"] == recipe["ingredient_id"]), None)
        enriched.append({
            **recipe,
            "menu_item_name": menu_item["name"] if menu_item else None,
            "ingredient_name": ingredient["name"] if ingredient else None,
        })
    
    return {"recipes": enriched}

# ==================== PRINT ENDPOINTS ====================

@app.get("/print/ticket/{order_id}")
def print_ticket(order_id: int):
    """Get formatted ticket for kitchen printer."""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    ticket_text = generate_ticket_text(order)
    
    return {
        "order_id": order_id,
        "ticket": ticket_text,
        "print_ready": True,
    }

@app.get("/print/report/daily")
def print_daily_report(date: Optional[str] = None):
    """Generate daily report for printing."""
    stats = get_daily_statistics(date)
    
    lines = []
    lines.append("=" * 40)
    lines.append("    ДНЕВНОЙ ОТЧЕТ")
    lines.append(f"    Дата: {stats['date']}")
    lines.append("=" * 40)
    lines.append(f"Всего заказов: {stats['total_orders']}")
    lines.append(f"Закрыто заказов: {stats['closed_orders']}")
    lines.append(f"Выручка: {stats['revenue']} руб.")
    lines.append(f"Средний чек: {stats['avg_order_value']:.2f} руб.")
    lines.append("-" * 40)
    lines.append("Оплата по методам:")
    for method, amount in stats["payment_methods"].items():
        lines.append(f"  {method}: {amount} руб.")
    lines.append("=" * 40)
    
    return {"report_text": "\n".join(lines)}

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
