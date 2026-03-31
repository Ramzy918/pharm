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
    # Champs élargis pour imports CSV (ex. Kaggle) : noms longs, descriptions, codes CIP/ID variés
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=200)
    summary = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=128, unique=True)
    expiration_date = models.DateField(null=True, blank=True)
    auth_user_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )
    
    # Compteurs et flags
    rating = models.IntegerField(default=0)
    user_likes = models.PositiveIntegerField(default=0)
    is_ai_recommended = models.BooleanField(default=False)
    user_recommendations = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        """Calculer la moyenne des notes"""
        ratings = self.ratings.all()
        if ratings.exists():
            total = sum(r.rating for r in ratings)
            return round(total / ratings.count(), 1)
        return 0.0


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
        DELIVERED = "DELIVERED", "Livrée"
        CANCELLED = "CANCELLED", "Annulée"

    auth_user_id = models.PositiveIntegerField(db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_percent = models.PositiveSmallIntegerField(default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    # User information
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(max_length=254, blank=True, default='')
    
    # Address information
    city = models.CharField(max_length=120, blank=True, default='')
    commune = models.CharField(max_length=120, blank=True, default='')
    detailed_address = models.TextField(blank=True, default='')
    postal_code = models.CharField(max_length=16, blank=True, default='')
    
    # Delivery method
    delivery_method = models.CharField(max_length=20, blank=True, default='domicile')
    
    # Auto-shipping
    auto_shipped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class ProductRating(models.Model):
    """Simple rating system - user can rate product once and delete rating"""
    auth_user_id = models.PositiveIntegerField(db_index=True)
    product = models.ForeignKey(Product, related_name="ratings", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i}⭐") for i in range(0, 6)])
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_rating')
        ]
    
    def __str__(self):
        return f"User {self.auth_user_id} - {self.product.name} - {self.rating}/5"


class ProductRecommendation(models.Model):
    """Product recommendation system - user can recommend once"""
    auth_user_id = models.PositiveIntegerField(db_index=True)
    product = models.ForeignKey(Product, related_name="recommendations", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_recommendation')
        ]
    
    def __str__(self):
        return f"User {self.auth_user_id} recommends {self.product.name}"


class ProductLike(models.Model):
    """Product like system - user can like once"""
    auth_user_id = models.PositiveIntegerField(db_index=True)
    product = models.ForeignKey(Product, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_like')
        ]
    
    def __str__(self):
        return f"User {self.auth_user_id} likes {self.product.name}"
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
    # Champs élargis pour imports CSV (ex. Kaggle) : noms longs, descriptions, codes CIP/ID variés
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, db_index=True)
    summary = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=128)
    expiration_date = models.DateField(null=True, blank=True)
    auth_user_id = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    pharmacy_name = models.CharField(max_length=255, blank=True, null=True)
    pharmacy_wilaya = models.CharField(max_length=100, blank=True, null=True)
    
    # Compteurs et flags
    rating = models.IntegerField(default=0)
    user_likes = models.PositiveIntegerField(default=0)
    is_ai_recommended = models.BooleanField(default=False)
    user_recommendations = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        """Calculer la moyenne des notes"""
        ratings = self.ratings.all()
        if ratings.exists():
            total = sum(r.rating for r in ratings)
            return round(total / ratings.count(), 1)
        return 0.0


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
        DELIVERED = "DELIVERED", "Livrée"
        CANCELLED = "CANCELLED", "Annulée"

    auth_user_id = models.PositiveIntegerField(db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_percent = models.PositiveSmallIntegerField(default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    # User information
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(max_length=254, blank=True, default='')
    
    # Address information
    city = models.CharField(max_length=120, blank=True, default='')
    commune = models.CharField(max_length=120, blank=True, default='')
    detailed_address = models.TextField(blank=True, default='')
    postal_code = models.CharField(max_length=16, blank=True, default='')
    
    # Delivery method
    delivery_method = models.CharField(max_length=20, blank=True, default='domicile')
    
    # Auto-shipping
    auto_shipped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class ProductRating(models.Model):
    """Simple rating system - user can rate product once and delete rating"""
    auth_user_id = models.PositiveIntegerField(db_index=True)
    product = models.ForeignKey(Product, related_name="ratings", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i}⭐") for i in range(0, 6)])
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_rating')
        ]
    
    def __str__(self):
        return f"User {self.auth_user_id} - {self.product.name} - {self.rating}/5"


class ProductRecommendation(models.Model):
    """Product recommendation system - user can recommend once"""
    auth_user_id = models.PositiveIntegerField(db_index=True)
    product = models.ForeignKey(Product, related_name="recommendations", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_recommendation')
        ]
    
    def __str__(self):
        return f"User {self.auth_user_id} recommends {self.product.name}"


class ProductLike(models.Model):
    """Product like system - user can like once"""
    auth_user_id = models.PositiveIntegerField(db_index=True)
    product = models.ForeignKey(Product, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_like')
        ]
    
    def __str__(self):
        return f"User {self.auth_user_id} likes {self.product.name}"
