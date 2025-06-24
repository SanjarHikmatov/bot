from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Category, Product, ProductColor, ProductColorImage, Cart, Order, OrderItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'telegram_id', 'phone_number', 'language', 'is_active_bot', 'date_joined')
    list_filter = ('language', 'is_active_bot', 'is_staff', 'is_superuser')
    search_fields = ('username', 'telegram_id', 'phone_number')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Telegram Info'), {'fields': ('telegram_id', 'phone_number', 'language', 'is_active_bot')}),
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'parent', 'is_active', 'order', 'level')
    list_filter = ('is_active', 'parent')
    search_fields = ('name_uz', 'name_ru')
    list_editable = ('order', 'is_active')
    
    def level(self, obj):
        return obj.level
    level.short_description = _('Level')

admin.site.register(Category, CategoryAdmin)


class ProductColorImageInline(admin.TabularInline):
    model = ProductColorImage
    extra = 1


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'is_active', 'created_at')
    list_filter = ('is_active', 'categories', 'created_at')
    search_fields = ('name_uz', 'name_ru')
    filter_horizontal = ('categories',)
    inlines = [ProductColorInline]

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'name_uz', 'name_ru', 'price', 'is_available')
    list_filter = ('is_available', 'product')
    search_fields = ('name_uz', 'name_ru', 'product__name_uz')
    inlines = [ProductColorImageInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_color', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product_color__product__name_uz')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'phone_number')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')
