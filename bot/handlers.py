from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from django.contrib.auth import get_user_model
from shop.models import Category, Product, ProductColor, Cart, Order, OrderItem
from .utils import get_text, create_main_keyboard, create_categories_keyboard, create_products_keyboard
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def start(update, context):
    """Start command handler"""
    telegram_user = update.effective_user
    logger.info(f"User Telegram ID: {telegram_user.id}, Username: {telegram_user.username}")

    user, created = User.objects.get_or_create(
        telegram_id=telegram_user.id,
        defaults={
            'username': telegram_user.username or f'user_{telegram_user.id}',
            'first_name': telegram_user.first_name or '',
            'last_name': telegram_user.last_name or '',
        }
    )
    logger.info(f"User created or found: {user.username}, Telegram ID: {telegram_user.id}")

    context.user_data['language'] = user.language
    context.user_data['user_id'] = user.id

    if created or not user.phone_number:
        keyboard = [[KeyboardButton(get_text('share_contact', user.language), request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        update.message.reply_text(
            get_text('welcome_new_user', user.language).format(name=telegram_user.first_name),
            reply_markup=reply_markup
        )
    else:
        reply_markup = create_main_keyboard(user.language)
        update.message.reply_text(
            get_text('welcome_back', user.language).format(name=user.first_name),
            reply_markup=reply_markup
        )

def contact_handler(update, context):
    """Handle contact sharing"""
    contact = update.message.contact

    if contact.user_id == update.effective_user.id:
        try:
            user = User.objects.get(telegram_id=update.effective_user.id)
            user.phone_number = contact.phone_number
            user.save()

            reply_markup = create_main_keyboard(user.language)
            update.message.reply_text(
                get_text('contact_saved', user.language),
                reply_markup=reply_markup
            )
        except User.DoesNotExist:
            update.message.reply_text(get_text('error_user_not_found', 'uz'))
    else:
        update.message.reply_text(get_text('error_wrong_contact', 'uz'))

def categories_handler(update, context):
    """Show categories"""
    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        # Get root categories
        categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order')

        if categories.exists():
            reply_markup = create_categories_keyboard(categories, language)
            update.message.reply_text(
                get_text('select_category', language),
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(get_text('no_categories', language))

    except User.DoesNotExist:
        update.message.reply_text(get_text('error_user_not_found', 'uz'))

def category_callback(update, context):
    """Handle category selection"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        category_id = int(query.data.split('_')[1])
        category = Category.objects.get(id=category_id, is_active=True)

        subcategories = category.children.filter(is_active=True).order_by('order')

        if subcategories.exists():
            reply_markup = create_categories_keyboard(subcategories, language, parent_id=category.id)
            query.edit_message_text(
                get_text('select_subcategory', language).format(category=category.get_name(language)),
                reply_markup=reply_markup
            )
        else:
            products = category.products.filter(is_active=True)[:10]

            if products.exists():
                reply_markup = create_products_keyboard(products, language)
                query.edit_message_text(
                    get_text('products_in_category', language).format(category=category.get_name(language)),
                    reply_markup=reply_markup
                )
            else:
                query.edit_message_text(get_text('no_products_in_category', language))

    except (Category.DoesNotExist, ValueError, IndexError):
        query.edit_message_text(get_text('error_category_not_found', 'uz'))
    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def product_callback(update, context):
    """Handle product selection"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        product_id = int(query.data.split('_')[1])
        product = Product.objects.get(id=product_id, is_active=True)

        colors = product.colors.filter(is_available=True)

        if colors.exists():
            keyboard = []
            for color in colors:
                keyboard.append([InlineKeyboardButton(
                    f"{color.get_name(language)} - {color.price} so'm",
                    callback_data=f"color_{color.id}"
                )])

            keyboard.append([InlineKeyboardButton(get_text('back', language), callback_data="back_to_categories")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = f"*{product.get_name(language)}*\n\n"
            text += f"{product.get_description(language)}\n\n"
            text += get_text('select_color', language)

            if product.main_image:
                query.message.reply_photo(
                    photo=product.main_image,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            query.edit_message_text(get_text('no_colors_available', language))

    except (Product.DoesNotExist, ValueError, IndexError):
        query.edit_message_text(get_text('error_product_not_found', 'uz'))
    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def color_callback(update, context):
    """Handle color selection and add to cart"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        color_id = int(query.data.split('_')[1])
        color = ProductColor.objects.get(id=color_id, is_available=True)

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product_color=color,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
        cart_item.save()

        query.answer(get_text('added_to_cart', language), show_alert=True)

        keyboard = [
            [InlineKeyboardButton(get_text('view_cart', language), callback_data="view_cart")],
            [InlineKeyboardButton(get_text('continue_shopping', language), callback_data="back_to_categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = get_text('item_added_to_cart', language).format(
            product=color.product.get_name(language),
            color=color.get_name(language),
            price=color.price
        )

        query.edit_message_text(text, reply_markup=reply_markup)

    except (ProductColor.DoesNotExist, ValueError, IndexError):
        query.edit_message_text(get_text('error_color_not_found', 'uz'))
    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def cart_handler(update, context):
    """Show cart contents"""
    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        cart_items = Cart.objects.filter(user=user)

        if cart_items.exists():
            text = get_text('your_cart', language) + "\n\n"
            total = 0

            for item in cart_items:
                item_total = item.total_price
                total += item_total
                text += f"• {item.product_color.product.get_name(language)}\n"
                text += f"  {item.product_color.get_name(language)}\n"
                text += f"  {item.quantity} x {item.product_color.price} = {item_total} so'm\n\n"

            text += f"*{get_text('total', language)}: {total} so'm*"

            keyboard = [
                [InlineKeyboardButton(get_text('place_order', language), callback_data="place_order")],
                [InlineKeyboardButton(get_text('clear_cart', language), callback_data="clear_cart")],
                [InlineKeyboardButton(get_text('continue_shopping', language), callback_data="back_to_categories")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            update.message.reply_text(get_text('cart_empty', language))

    except User.DoesNotExist:
        update.message.reply_text(get_text('error_user_not_found', 'uz'))

def view_cart_callback(update, context):
    """Handle view cart callback"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        cart_items = Cart.objects.filter(user=user)

        if cart_items.exists():
            text = get_text('your_cart', language) + "\n\n"
            total = 0

            for item in cart_items:
                item_total = item.total_price
                total += item_total
                text += f"• {item.product_color.product.get_name(language)}\n"
                text += f"  {item.product_color.get_name(language)}\n"
                text += f"  {item.quantity} x {item.product_color.price} = {item_total} so'm\n\n"

            text += f"*{get_text('total', language)}: {total} so'm*"

            keyboard = [
                [InlineKeyboardButton(get_text('place_order', language), callback_data="place_order")],
                [InlineKeyboardButton(get_text('clear_cart', language), callback_data="clear_cart")],
                [InlineKeyboardButton(get_text('continue_shopping', language), callback_data="back_to_categories")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            query.edit_message_text(get_text('cart_empty', language))

    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def place_order_callback(update, context):
    """Handle place order callback"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        cart_items = Cart.objects.filter(user=user)

        if cart_items.exists():
            total = sum(item.total_price for item in cart_items)

            order = Order.objects.create(
                user=user,
                total_amount=total,
                phone_number=user.phone_number or '',
                status='pending'
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_color=cart_item.product_color,
                    quantity=cart_item.quantity,
                    price=cart_item.product_color.price
                )

            cart_items.delete()

            text = get_text('order_created', language).format(
                order_id=order.id,
                total=total
            )

            query.edit_message_text(text)
        else:
            query.edit_message_text(get_text('cart_empty', language))

    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def clear_cart_callback(update, context):
    """Handle clear cart callback"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        Cart.objects.filter(user=user).delete()

        query.edit_message_text(get_text('cart_cleared', language))

    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def language_handler(update, context):
    """Handle language selection"""
    try:
        user = User.objects.get(telegram_id=update.effective_user.id)

        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            "Tilni tanlang / Выберите язык:",
            reply_markup=reply_markup
        )

    except User.DoesNotExist:
        update.message.reply_text("Iltimos, avval /start buyrug'ini bosing")

def language_callback(update, context):
    """Handle language selection callback"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)

        language = query.data.split('_')[1]
        user.language = language
        user.save()

        context.user_data['language'] = language

        reply_markup = create_main_keyboard(language)
        query.message.reply_text(
            get_text('language_changed', language),
            reply_markup=reply_markup
        )

    except User.DoesNotExist:
        query.edit_message_text("Iltimos, avval /start buyrug'ini bosing")

def back_to_categories_callback(update, context):
    """Handle back to categories callback"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order')

        if categories.exists():
            reply_markup = create_categories_keyboard(categories, language)
            query.edit_message_text(
                get_text('select_category', language),
                reply_markup=reply_markup
            )
        else:
            query.edit_message_text(get_text('no_categories', language))

    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))

def orders_handler(update, context):
    """Show user orders and their statuses"""
    try:
        telegram_id = update.effective_user.id
        logger.info(f"Fetching orders for Telegram ID: {telegram_id}")

        user = User.objects.get(telegram_id=telegram_id)
        logger.info(f"User found: {user.username}, Language: {user.language}")

        language = user.language
        orders = Order.objects.filter(user=user).order_by('-created_at')
        logger.info(f"Orders found: {list(orders)}")

        if orders.exists():
            logger.info("Orders exist, building response")
            text = get_text('your_orders', language) + "\n\n"
            for order in orders:
                status_text = get_text(f'order_status_{order.status}', language)
                text += f"📦 Buyurtma #{order.id}\n"
                text += f"💰 Summa: {order.total_amount} so'm\n"
                text += f"📅 Sana: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                text += f"📋 Status: {status_text}\n\n"

            keyboard = []
            for order in orders:
                if order.status == 'pending':
                    keyboard.append([
                        InlineKeyboardButton(
                            get_text('cancel_order', language).format(order_id=order.id),
                            callback_data=f"cancel_order_{order.id}"
                        )
                    ])
            keyboard.append([InlineKeyboardButton(get_text('back', language), callback_data="back_to_categories")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            logger.info("No orders found for user")
            update.message.reply_text(get_text('no_orders', language))

    except User.DoesNotExist:
        logger.error(f"User with Telegram ID {telegram_id} not found")
        update.message.reply_text(get_text('error_user_not_found', 'uz'))
    except Exception as e:
        logger.error(f"Error in orders_handler: {str(e)}", exc_info=True)
        update.message.reply_text("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.", parse_mode='Markdown')

def cancel_order_callback(update, context):
    """Handle order cancellation"""
    query = update.callback_query
    query.answer()

    try:
        user = User.objects.get(telegram_id=update.effective_user.id)
        language = user.language

        order_id = int(query.data.split('_')[2])
        order = Order.objects.get(id=order_id, user=user, status='pending')

        order.status = 'cancelled'
        order.save()

        query.edit_message_text(
            get_text('order_cancelled', language).format(order_id=order.id)
        )

    except (Order.DoesNotExist, ValueError, IndexError):
        query.edit_message_text(get_text('error_order_not_found', 'uz'))
    except User.DoesNotExist:
        query.edit_message_text(get_text('error_user_not_found', 'uz'))


def setup_handlers(dispatcher):
    """Setup all bot handlers"""
    logger.info("Setting up bot handlers")

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("orders", orders_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(🛍\s*Kategoriyalar|Категории)$'), categories_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(🛒\s*Savatcha|Корзина)$'), cart_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(🌐\s*Til|Язык)$'), language_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(Mening buyurtmalarim|Мои заказы)$'), orders_handler))

    dispatcher.add_handler(CallbackQueryHandler(category_callback, pattern='^cat_'))
    dispatcher.add_handler(CallbackQueryHandler(product_callback, pattern='^prod_'))
    dispatcher.add_handler(CallbackQueryHandler(color_callback, pattern='^color_'))
    dispatcher.add_handler(CallbackQueryHandler(view_cart_callback, pattern='^view_cart$'))
    dispatcher.add_handler(CallbackQueryHandler(place_order_callback, pattern='^place_order$'))
    dispatcher.add_handler(CallbackQueryHandler(clear_cart_callback, pattern='^clear_cart$'))
    dispatcher.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    dispatcher.add_handler(CallbackQueryHandler(back_to_categories_callback, pattern='^back_to_categories$'))
    dispatcher.add_handler(CallbackQueryHandler(cancel_order_callback, pattern='^cancel_order_'))

    def log_message(update, context):
        logger.info(f"Received message: {update.message.text} from user {update.effective_user.id}")

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, log_message))

    logger.info("All handlers set up successfully")