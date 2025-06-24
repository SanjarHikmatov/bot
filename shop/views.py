from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from .models import User, Category, Product, ProductColor, Cart, Order
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer, 
    ProductColorSerializer, CartSerializer, OrderSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()
        telegram_id = self.request.query_params.get('telegram_id')
        if telegram_id:
            queryset = queryset.filter(telegram_id=telegram_id)
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active_bot = not user.is_active_bot
        user.save()
        return Response({'status': 'success', 'is_active': user.is_active_bot})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif parent_id == '':
            queryset = queryset.filter(parent__isnull=True)
        return queryset.order_by('order', 'name_uz')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_id = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        
        if search:
            queryset = queryset.filter(
                Q(name_uz__icontains=search) | 
                Q(name_ru__icontains=search) |
                Q(description_uz__icontains=search) |
                Q(description_ru__icontains=search)
            )
        
        return queryset.distinct().order_by('-created_at')

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product_color_id = request.data.get('product_color_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product_color = ProductColor.objects.get(id=product_color_id, is_available=True)
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product_color=product_color,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ProductColor.DoesNotExist:
            return Response({'error': 'Product color not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'status': 'success'})

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'success', 'new_status': new_status})
        
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
