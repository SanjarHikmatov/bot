# Telegram Shop Bot

Django-based Telegram bot for online shopping with admin API.

## Features

- 🤖 Telegram bot interface
- 🛍️ Multi-level categories
- 🎨 Products with multiple colors and prices
- 🛒 Shopping cart functionality
- 📱 Multi-language support (Uzbek/Russian)
- 🔧 Admin API for management
- 🐳 Docker support

## Quick Start

1. **Clone and setup:**
\`\`\`bash
git clone <repository>
cd telegram-shop-bot
cp .env.example .env
\`\`\`

2. **Configure environment:**
Edit `.env` file and add your Telegram bot token:
\`\`\`
TELEGRAM_BOT_TOKEN=your_bot_token_here
\`\`\`

3. **Run with Docker:**
\`\`\`bash
docker-compose up -d
\`\`\`

4. **Create sample data:**
\`\`\`bash
docker-compose exec web python scripts/create_sample_data.py
\`\`\`

5. **Access admin panel:**
- URL: http://localhost:8000/admin/
- Username: admin
- Password: admin123

## Manual Setup (without Docker)

1. **Install dependencies:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. **Setup database:**
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

3. **Create superuser:**
\`\`\`bash
python manage.py createsuperuser
\`\`\`

4. **Run development server:**
\`\`\`bash
python manage.py runserver
\`\`\`

5. **Run bot (in separate terminal):**
\`\`\`bash
python manage.py run_bot
\`\`\`

## API Endpoints

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

### Users
- `GET /api/users/` - List users (admin only)
- `POST /api/users/{id}/toggle_active/` - Toggle user active status

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/{id}/update_status/` - Update order status

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add_item/` - Add item to cart
- `DELETE /api/cart/clear/` - Clear cart

## Bot Commands

- `/start` - Start bot and register
- `🛍 Kategoriyalar` - Browse categories
- `🛒 Savatcha` - View cart
- `🌐 Til` - Change language

## Project Structure

\`\`\`
telegram_shop/
├── telegram_shop/          # Django project settings
├── shop/                   # Main app (models, API)
├── bot/                    # Telegram bot handlers
├── scripts/                # Utility scripts
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker configuration
└── README.md              # This file
\`\`\`

## Models

- **User** - Extended user model with Telegram info
- **Category** - Hierarchical categories
- **Product** - Products with multi-language support
- **ProductColor** - Product variants with colors and prices
- **ProductColorImage** - Images for each color variant
- **Cart** - Shopping cart items
- **Order** - Customer orders
- **OrderItem** - Individual order items

## Development

### Adding new bot handlers:
1. Create handler function in `bot/handlers.py`
2. Add handler to `bot/management/commands/run_bot.py`
3. Update translations in `bot/utils.py`

### Adding new API endpoints:
1. Create serializer in `shop/serializers.py`
2. Create view in `shop/views.py`
3. Add URL pattern in `shop/urls.py`

## Deployment

1. Set production environment variables
2. Use PostgreSQL database
3. Configure Redis for caching
4. Set up reverse proxy (nginx)
5. Use process manager (systemd, supervisor)

## Support

For questions and support, contact: @SectorSoftDev

## License

This project is licensed under the MIT License.
