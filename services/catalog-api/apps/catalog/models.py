from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    summary = models.CharField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=64, unique=True)
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Patient(models.Model):
    """Profil « professionnel / pharmacie » lié à l’identifiant Auth (sans FK cross-DB)."""

    auth_user_id = models.PositiveIntegerField(unique=True, db_index=True)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        CONFIRMED = "CONFIRMED", "Confirmée"
        SHIPPED = "SHIPPED", "Expédiée"
        CANCELLED = "CANCELLED", "Annulée"

    auth_user_id = models.PositiveIntegerField(db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_percent = models.PositiveSmallIntegerField(default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
