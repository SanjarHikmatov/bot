import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from bot.handlers import (
    start, contact_handler, categories_handler, category_callback,
    product_callback, color_callback, cart_handler, view_cart_callback,
    place_order_callback, clear_cart_callback, language_handler,
    language_callback, back_to_categories_callback
)
from bot.utils import get_text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Telegram Bot'

    def handle(self, *args, **options):
        """Run the bot"""
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN is not set in settings')
            )
            return

        updater = Updater(settings.TELEGRAM_BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))

        dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
        dispatcher.add_handler(MessageHandler(
            Filters.regex(f"^({get_text('categories', 'uz')}|{get_text('categories', 'ru')})$"),
            categories_handler
        ))
        dispatcher.add_handler(MessageHandler(
            Filters.regex(f"^({get_text('cart', 'uz')}|{get_text('cart', 'ru')})$"),
            cart_handler
        ))
        dispatcher.add_handler(MessageHandler(
            Filters.regex(f"^({get_text('language', 'uz')}|{get_text('language', 'ru')})$"),
            language_handler
        ))

        dispatcher.add_handler(CallbackQueryHandler(category_callback, pattern=r"^cat_\d+$"))
        dispatcher.add_handler(CallbackQueryHandler(product_callback, pattern=r"^prod_\d+$"))
        dispatcher.add_handler(CallbackQueryHandler(color_callback, pattern=r"^color_\d+$"))
        dispatcher.add_handler(CallbackQueryHandler(view_cart_callback, pattern="^view_cart$"))
        dispatcher.add_handler(CallbackQueryHandler(place_order_callback, pattern="^place_order$"))
        dispatcher.add_handler(CallbackQueryHandler(clear_cart_callback, pattern="^clear_cart$"))
        dispatcher.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_(uz|ru)$"))
        dispatcher.add_handler(CallbackQueryHandler(back_to_categories_callback, pattern="^back_to_categories$"))

        self.stdout.write(
            self.style.SUCCESS('Bot started successfully!')
        )

        updater.start_polling()
        updater.idle()