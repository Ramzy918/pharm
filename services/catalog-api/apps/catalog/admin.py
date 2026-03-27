from django.contrib import admin

from .models import Category, Order, OrderLine, Patient, Product, ProductLike, ProductRating, ProductRecommendation


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "stock")
    list_filter = ("category",)
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("company_name", "auth_user_id", "city")
    search_fields = ("company_name", "auth_user_id")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "auth_user_id", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderLineInline]


@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at", "product")
    search_fields = ("user__email", "product__name")
    readonly_fields = ("created_at",)


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")
    list_filter = ("rating", "created_at", "product")
    search_fields = ("user__email", "product__name")
    readonly_fields = ("created_at",)


@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at", "product")
    search_fields = ("user__email", "product__name")
    readonly_fields = ("created_at",)
