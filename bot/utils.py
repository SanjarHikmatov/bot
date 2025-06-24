from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

TEXTS = {
    'uz': {
        'welcome_new_user': "Salom {name}! Internet do'konimizga xush kelibsiz!\n\nIltimos, telefon raqamingizni ulashing:",
        'welcome_back': "Salom {name}! Qaytganingizdan xursandmiz!",
        'share_contact': "📱 Telefon raqamni ulashish",
        'contact_saved': "Telefon raqamingiz saqlandi! Endi do'kondan foydalanishingiz mumkin.",
        'error_user_not_found': "Foydalanuvchi topilmadi. Iltimos, /start buyrug'ini bosing.",
        'error_wrong_contact': "Iltimos, o'zingizning telefon raqamingizni ulashing.",
        'categories': "🛍 Kategoriyalar",
        'cart': "🛒 Savatcha",
        'language': "🌐 Til",
        'select_category': "Kategoriyani tanlang:",
        'select_subcategory': "{category} bo'limidan kategoriyani tanlang:",
        'no_categories': "Hozircha kategoriyalar mavjud emas.",
        'products_in_category': "{category} kategoriyasidagi mahsulotlar:",
        'no_products_in_category': "Bu kategoriyada mahsulotlar mavjud emas.",
        'error_category_not_found': "Kategoriya topilmadi.",
        'error_product_not_found': "Mahsulot topilmadi.",
        'error_color_not_found': "Rang topilmadi.",
        'select_color': "Rangni tanlang:",
        'no_colors_available': "Bu mahsulot uchun ranglar mavjud emas.",
        'added_to_cart': "Savatchaga qo'shildi!",
        'item_added_to_cart': "{product} ({color}) - {price} so'm\nSavatchaga qo'shildi!",
        'view_cart': "Savatchani ko'rish",
        'continue_shopping': "Xaridni davom ettirish",
        'your_cart': "🛒 Sizning savatchangiz:",
        'total': "Jami",
        'place_order': "Buyurtma berish",
        'clear_cart': "Savatchani tozalash",
        'cart_empty': "Savatchangiz bo'sh.",
        'order_created': "✅ Buyurtma #{order_id} yaratildi!\nJami: {total} so'm\n\nTez orada siz bilan bog'lanamiz.",
        'cart_cleared': "Savatcha tozalandi.",
        'language_changed': "Til o'zgartirildi!",
        'back': "⬅️ Orqaga",
        'orders': 'Mening buyurtmalarim',
        'your_orders': 'Sizning buyurtmalaringiz',
        'no_orders': 'Hozircha buyurtmalar yo‘q',
        'order_status_pending': 'Kutilmoqda',
        'order_status_cancelled': 'Bekor qilingan',
        'cancel_order': 'Buyurtma #{order_id} bekor qilish',
        'order_cancelled': 'Buyurtma #{order_id} bekor qilindi',
        'error_order_not_found': 'Buyurtma topilmadi'
    },
    'ru': {
        'welcome_new_user': "Привет {name}! Добро пожаловать в наш интернет-магазин!\n\nПожалуйста, поделитесь своим номером телефона:",
        'welcome_back': "Привет {name}! Рады видеть вас снова!",
        'share_contact': "📱 Поделиться номером телефона",
        'contact_saved': "Номер телефона сохранен! Теперь вы можете пользоваться магазином.",
        'error_user_not_found': "Пользователь не найден. Пожалуйста, нажмите /start.",
        'error_wrong_contact': "Пожалуйста, поделитесь своим номером телефона.",
        'categories': "🛍 Категории",
        'cart': "🛒 Корзина",
        'language': "🌐 Язык",
        'select_category': "Выберите категорию:",
        'select_subcategory': "Выберите категорию из раздела {category}:",
        'no_categories': "Пока нет доступных категорий.",
        'products_in_category': "Товары в категории {category}:",
        'no_products_in_category': "В этой категории нет товаров.",
        'error_category_not_found': "Категория не найдена.",
        'error_product_not_found': "Товар не найден.",
        'error_color_not_found': "Цвет не найден.",
        'select_color': "Выберите цвет:",
        'no_colors_available': "Для этого товара нет доступных цветов.",
        'added_to_cart': "Добавлено в корзину!",
        'item_added_to_cart': "{product} ({color}) - {price} сум\nДобавлено в корзину!",
        'view_cart': "Посмотреть корзину",
        'continue_shopping': "Продолжить покупки",
        'your_cart': "🛒 Ваша корзина:",
        'total': "Итого",
        'place_order': "Оформить заказ",
        'clear_cart': "Очистить корзину",
        'cart_empty': "Ваша корзина пуста.",
        'order_created': "✅ Заказ #{order_id} создан!\nИтого: {total} сум\n\nМы скоро свяжемся с вами.",
        'cart_cleared': "Корзина очищена.",
        'language_changed': "Язык изменен!",
        'back': "⬅️ Назад",
        'orders': 'Мои заказы',
        'your_orders': 'Ваши заказы',
        'no_orders': 'Пока нет заказов',
        'order_status_pending': 'В ожидании',
        'order_status_cancelled': 'Отменён',
        'cancel_order': 'Отменить заказ #{order_id}',
        'order_cancelled': 'Заказ #{order_id} отменён',
        'error_order_not_found': 'Заказ не найден'
    }
}


def get_text(key, language='uz'):
    """Get translated text"""
    logger.info(f"Fetching text for key: {key}, language: {language}")
    return TEXTS.get(language, TEXTS['uz']).get(key, key)


def create_main_keyboard(language='uz'):
    """Create main menu keyboard"""
    keyboard = [
        [get_text('categories', language), get_text('cart', language)],
        [get_text('orders', language), get_text('language', language)]
    ]
    logger.info(f"Main keyboard for {language}: {keyboard}")
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_categories_keyboard(categories, language='uz', parent_id=None):
    """Create categories inline keyboard"""
    keyboard = []

    for category in categories:
        keyboard.append([InlineKeyboardButton(
            category.get_name(language),
            callback_data=f"cat_{category.id}"
        )])

    if parent_id:
        keyboard.append([InlineKeyboardButton(
            get_text('back', language),
            callback_data="back_to_categories"
        )])

    return InlineKeyboardMarkup(keyboard)


def create_products_keyboard(products, language='uz'):
    """Create products inline keyboard"""
    keyboard = []

    for product in products:
        keyboard.append([InlineKeyboardButton(
            product.get_name(language),
            callback_data=f"prod_{product.id}"
        )])

    keyboard.append([InlineKeyboardButton(
        get_text('back', language),
        callback_data="back_to_categories"
    )])

    return InlineKeyboardMarkup(keyboard)