from django.db import transaction
from rest_framework import filters, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .messaging import publish_order_created
from .models import Category, Order, Patient, Product
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    CategorySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    PatientSerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ("category", "slug")
    search_fields = ("name", "summary", "sku", "category__name")
    ordering_fields = ("name", "price", "stock", "expiration_date")
    ordering = ("name",)


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = Patient.objects.all().order_by("id")
        user = self.request.user
        if getattr(user, "is_staff", False):
            return qs
        return qs.filter(auth_user_id=user.id)


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("lines__product").order_by("-created_at")
        user = self.request.user
        if getattr(user, "is_staff", False):
            return qs
        return qs.filter(auth_user_id=user.id)

    def get_permissions(self):
        if self.action in ("partial_update", "update"):
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action in ("partial_update", "update"):
            return OrderStatusSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()

        def _pub():
            publish_order_created(order_id=order.pk, user_id=order.auth_user_id, total=order.total)

        transaction.on_commit(_pub)
