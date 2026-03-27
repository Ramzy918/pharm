from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.views import (
    CategoryViewSet, 
    OrderViewSet, 
    PatientViewSet, 
    ProductViewSet,
    product_like_view,
    product_rate_view,
    product_unrate_view,
    product_ratings_view,
    product_recommend_view,
    product_ai_recommend_view,
    product_recommendations_view,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include("apps.core.urls")),
    path("api/", include(router.urls)),
    # Rating and Like endpoints
    path("api/products/<int:pk>/like/", product_like_view, name="product-like"),
    path("api/products/<int:pk>/rate/", product_rate_view, name="product-rate"),
    path("api/products/<int:pk>/unrate/", product_unrate_view, name="product-unrate"),
    path("api/products/<int:pk>/ratings/", product_ratings_view, name="product-ratings"),
    # Recommendation endpoints
    path("api/products/<int:pk>/recommend/", product_recommend_view, name="product-recommend"),
    path("api/products/<int:pk>/ai_recommend/", product_ai_recommend_view, name="product-ai-recommend"),
    path("api/products/<int:pk>/recommendations/", product_recommendations_view, name="product-recommendations"),
]
