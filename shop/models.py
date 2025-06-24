from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=2, choices=[('uz', 'Uzbek'), ('ru', 'Russian')], default='uz')
    is_active_bot = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.telegram_id})"


class Category(models.Model):
    name_uz = models.CharField(max_length=200, verbose_name=_("Name (Uzbek)"))
    name_ru = models.CharField(max_length=200, verbose_name=_("Name (Russian)"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name_uz']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name_uz

    def get_name(self, language='uz'):
        return getattr(self, f'name_{language}', self.name_uz)

    @property
    def level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level


class Product(models.Model):
    name_uz = models.CharField(max_length=200, verbose_name=_("Name (Uzbek)"))
    name_ru = models.CharField(max_length=200, verbose_name=_("Name (Russian)"))
    description_uz = models.TextField(blank=True, verbose_name=_("Description (Uzbek)"))
    description_ru = models.TextField(blank=True, verbose_name=_("Description (Russian)"))
    categories = models.ManyToManyField(Category, related_name='products')
    main_image = models.ImageField(upload_to='products/', verbose_name=_("Main Image"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name_uz

    def get_name(self, language='uz'):
        return getattr(self, f'name_{language}', self.name_uz)

    def get_description(self, language='uz'):
        return getattr(self, f'description_{language}', self.description_uz)


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name_uz = models.CharField(max_length=100, verbose_name=_("Color Name (Uzbek)"))
    name_ru = models.CharField(max_length=100, verbose_name=_("Color Name (Russian)"))
    hex_code = models.CharField(max_length=7, blank=True, help_text="Color hex code (e.g., #FF0000)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Product Color")
        verbose_name_plural = _("Product Colors")

    def __str__(self):
        return f"{self.product.name_uz} - {self.name_uz}"

    def get_name(self, language='uz'):
        return getattr(self, f'name_{language}', self.name_uz)


class ProductColorImage(models.Model):
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_colors/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("Product Color Image")
        verbose_name_plural = _("Product Color Images")


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product_color']
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    def __str__(self):
        return f"{self.user.username} - {self.product_color}"

    @property
    def total_price(self):
        return self.product_color.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.order} - {self.product_color}"

    @property
    def total_price(self):
        if self.price is not None and self.quantity is not None:
            total = self.price * self.quantity
            return total
        return 'None Type'