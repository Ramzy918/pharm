from django import template

from apps.catalog.models import Category, Product, Order, ProductRating, ProductRecommendation, ProductLike

register = template.Library()

@register.simple_tag
def admin_products_count():
    return Product.objects.count()

@register.simple_tag
def admin_categories_count():
    return Category.objects.count()

@register.simple_tag
def admin_orders_count():
    return Order.objects.count()

@register.simple_tag
def admin_ratings_count():
    return ProductRating.objects.count()

@register.simple_tag
def admin_recommendations_count():
    return ProductRecommendation.objects.count()

@register.simple_tag
def admin_likes_count():
    return ProductLike.objects.count()
