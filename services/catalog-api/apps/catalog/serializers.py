from decimal import Decimal

from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from .discounts import apply_discount
from .models import Category, Order, OrderLine, Patient, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

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
        )


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
        )
        read_only_fields = ("id", "auth_user_id", "status", "subtotal", "discount_percent", "total", "created_at", "lines")


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status",)


class OrderCreateSerializer(serializers.Serializer):
    lines = OrderLineWriteSerializer(many=True)

    def validate_lines(self, value):
        if not value:
            raise serializers.ValidationError("Au moins une ligne est requise.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        raw_lines = validated_data["lines"]
        order = Order.objects.create(
            auth_user_id=user.id,
            status=Order.Status.PENDING,
            subtotal=Decimal("0.00"),
            discount_percent=0,
            total=Decimal("0.00"),
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
