from decimal import Decimal

from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from .discounts import apply_discount
from .models import Category, Order, OrderLine, Patient, Product, ProductRating, ProductLike, ProductRecommendation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    user_likes = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    is_recommended_by_user = serializers.SerializerMethodField()
    user_recommendations = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "category_name",
            "name",
            "slug",
            "summary",
            "price",
            "stock",
            "sku",
            "expiration_date",
            "is_liked_by_user",
            "user_likes",
            "average_rating",
            "rating_count",
            "user_rating",
            "is_recommended_by_user",
            "user_recommendations",
        )
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return ProductLike.objects.filter(user=request.user, product=obj).exists()
        return False
    
    def get_user_likes(self, obj):
        return ProductLike.objects.filter(product=obj).count()
    
    def get_average_rating(self, obj):
        ratings = ProductRating.objects.filter(product=obj)
        if ratings.exists():
            return sum(r.rating for r in ratings) / len(ratings)
        return 0
    
    def get_rating_count(self, obj):
        return ProductRating.objects.filter(product=obj).count()
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            rating = ProductRating.objects.filter(user=request.user, product=obj).first()
            return rating.rating if rating else None
        return None
    
    def get_is_recommended_by_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return ProductRecommendation.objects.filter(user=request.user, product=obj).exists()
        return False
    
    def get_user_recommendations(self, obj):
        return ProductRecommendation.objects.filter(product=obj).count()


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id",
            "auth_user_id",
            "company_name",
            "phone",
            "address_line",
            "city",
            "postal_code",
        )
        read_only_fields = ("id", "auth_user_id")

    def create(self, validated_data):
        user = self.context["request"].user
        return Patient.objects.create(auth_user_id=user.id, **validated_data)


class OrderLineReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderLine
        fields = ("id", "product", "product_name", "quantity", "unit_price")


class OrderLineWriteSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "auth_user_id",
            "status",
            "subtotal",
            "discount_percent",
            "total",
            "created_at",
            "lines",
            "phone",
            "email",
            "city",
            "commune",
            "detailed_address",
            "postal_code",
            "delivery_method",
            "auto_shipped_at",
        )
        read_only_fields = ("id", "auth_user_id", "status", "subtotal", "discount_percent", "total", "created_at", "lines", "auto_shipped_at")


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status",)


class OrderCreateSerializer(serializers.Serializer):
    lines = OrderLineWriteSerializer(many=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=120, required=False, allow_blank=True)
    commune = serializers.CharField(max_length=120, required=False, allow_blank=True)
    detailed_address = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=16, required=False, allow_blank=True)
    delivery_method = serializers.CharField(max_length=20, required=False, default='domicile')

    def validate_lines(self, value):
        if not value:
            raise serializers.ValidationError("Au moins une ligne est requise.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        raw_lines = validated_data["lines"]
        
        # Extract order fields
        order_fields = {
            'phone': validated_data.get('phone', ''),
            'email': validated_data.get('email', ''),
            'city': validated_data.get('city', ''),
            'commune': validated_data.get('commune', ''),
            'detailed_address': validated_data.get('detailed_address', ''),
            'postal_code': validated_data.get('postal_code', ''),
            'delivery_method': validated_data.get('delivery_method', 'domicile'),
        }
        
        order = Order.objects.create(
            auth_user_id=user.id,
            status=Order.Status.PENDING,
            subtotal=Decimal("0.00"),
            discount_percent=0,
            total=Decimal("0.00"),
            **order_fields
        )
        
        subtotal = Decimal("0.00")
        for item in raw_lines:
            product = item["product"]
            qty = item["quantity"]
            p = Product.objects.select_for_update().get(pk=product.pk)
            if p.stock < qty:
                raise serializers.ValidationError({"lines": f"Stock insuffisant pour {p.name}."})
            OrderLine.objects.create(order=order, product=p, quantity=qty, unit_price=p.price)
            subtotal += p.price * qty
            Product.objects.filter(pk=p.pk).update(stock=F("stock") - qty)
        total, pct = apply_discount(subtotal)
        order.subtotal = subtotal
        order.discount_percent = pct
        order.total = total
        order.save()
        return order


class ProductRatingSerializer(serializers.ModelSerializer):
    """Serializer for product ratings"""
    class Meta:
        model = ProductRating
        fields = ('id', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating product ratings"""
    class Meta:
        model = ProductRating
        fields = ('rating', 'comment')
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value


class ProductRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for product recommendations"""
    class Meta:
        model = ProductRecommendation
        fields = ('id', 'user', 'product', 'created_at')
        read_only_fields = ('id', 'user', 'product', 'created_at')
