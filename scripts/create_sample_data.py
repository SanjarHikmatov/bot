"""
Sample data creation script for Telegram Shop Bot
Run this script to populate the database with sample categories and products
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_shop.settings')
django.setup()

from shop.models import Category, Product, ProductColor
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_data():
    print("Creating sample data...")
    
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )
        print(f"Created admin user: {admin.username}")
    
    electronics = Category.objects.create(
        name_uz="Elektronika",
        name_ru="Электроника",
        order=1
    )
    
    phones = Category.objects.create(
        name_uz="Telefonlar",
        name_ru="Телефоны",
        parent=electronics,
        order=1
    )
    
    laptops = Category.objects.create(
        name_uz="Noutbuklar",
        name_ru="Ноутбуки",
        parent=electronics,
        order=2
    )
    
    clothing = Category.objects.create(
        name_uz="Kiyim-kechak",
        name_ru="Одежда",
        order=2
    )
    
    mens_clothing = Category.objects.create(
        name_uz="Erkaklar kiyimi",
        name_ru="Мужская одежда",
        parent=clothing,
        order=1
    )
    
    print("Created categories")
    
    iphone = Product.objects.create(
        name_uz="iPhone 15 Pro",
        name_ru="iPhone 15 Pro",
        description_uz="Eng yangi iPhone modeli. A17 Pro chip bilan.",
        description_ru="Новейшая модель iPhone. С чипом A17 Pro."
    )
    iphone.categories.add(phones)
    
    ProductColor.objects.create(
        product=iphone,
        name_uz="Qora",
        name_ru="Черный",
        hex_code="#000000",
        price=15000000
    )
    
    ProductColor.objects.create(
        product=iphone,
        name_uz="Oq",
        name_ru="Белый",
        hex_code="#FFFFFF",
        price=15000000
    )
    
    ProductColor.objects.create(
        product=iphone,
        name_uz="Ko'k",
        name_ru="Синий",
        hex_code="#0000FF",
        price=15500000
    )
    
    samsung = Product.objects.create(
        name_uz="Samsung Galaxy S24",
        name_ru="Samsung Galaxy S24",
        description_uz="Samsung'ning eng yangi flagman telefoni.",
        description_ru="Новейший флагманский телефон Samsung."
    )
    samsung.categories.add(phones)
    
    ProductColor.objects.create(
        product=samsung,
        name_uz="Qora",
        name_ru="Черный",
        hex_code="#000000",
        price=12000000
    )
    
    ProductColor.objects.create(
        product=samsung,
        name_uz="Yashil",
        name_ru="Зеленый",
        hex_code="#00FF00",
        price=12500000
    )
    
    macbook = Product.objects.create(
        name_uz="MacBook Air M3",
        name_ru="MacBook Air M3",
        description_uz="Apple M3 chip bilan yangi MacBook Air.",
        description_ru="Новый MacBook Air с чипом Apple M3."
    )
    macbook.categories.add(laptops)
    
    ProductColor.objects.create(
        product=macbook,
        name_uz="Kumush",
        name_ru="Серебристый",
        hex_code="#C0C0C0",
        price=25000000
    )
    
    ProductColor.objects.create(
        product=macbook,
        name_uz="Kosmik kulrang",
        name_ru="Космический серый",
        hex_code="#696969",
        price=25000000
    )
    
    tshirt = Product.objects.create(
        name_uz="Erkaklar uchun futbolka",
        name_ru="Мужская футболка",
        description_uz="100% paxta futbolka. Yumshoq va qulay.",
        description_ru="Футболка из 100% хлопка. Мягкая и удобная."
    )
    tshirt.categories.add(mens_clothing)
    
    ProductColor.objects.create(
        product=tshirt,
        name_uz="Qora",
        name_ru="Черный",
        hex_code="#000000",
        price=150000
    )
    
    ProductColor.objects.create(
        product=tshirt,
        name_uz="Oq",
        name_ru="Белый",
        hex_code="#FFFFFF",
        price=150000
    )
    
    ProductColor.objects.create(
        product=tshirt,
        name_uz="Qizil",
        name_ru="Красный",
        hex_code="#FF0000",
        price=180000
    )
    
    print("Created products with colors")
    print("Sample data creation completed!")

if __name__ == "__main__":
    create_sample_data()
