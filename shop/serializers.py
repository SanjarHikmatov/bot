from rest_framework import serializers
from .models import User, Category, Product, ProductColor, ProductColorImage, Cart, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'telegram_id', 'phone_number', 'language', 'is_active_bot', 'created_at']
        read_only_fields = ['created_at']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'parent', 'image', 'is_active', 'order', 'level', 'children', 'created_at']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class ProductColorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColorImage
        fields = ['id', 'image', 'order']


class ProductColorSerializer(serializers.ModelSerializer):
    images = ProductColorImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductColor
        fields = ['id', 'name_uz', 'name_ru', 'hex_code', 'price', 'is_available', 'images']


class ProductSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name_uz', 'name_ru', 'description_uz', 'description_ru', 
                 'main_image', 'is_active', 'categories', 'colors', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    product_color = ProductColorSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'product_color', 'quantity', 'total_price', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_color = ProductColorSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_color', 'quantity', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_amount', 'phone_number', 
                 'address', 'notes', 'items', 'created_at', 'updated_at']
