from django.db import transaction
from rest_framework import filters, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .messaging import publish_order_created
from .models import Category, Order, Patient, Product, ProductRating, ProductLike, ProductRecommendation
from .permissions import IsAdminOrReadOnly, IsAdminOrPharmacyOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    CategorySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    PatientSerializer,
    ProductSerializer,
    ProductRatingSerializer,
    ProductRatingCreateSerializer,
    ProductRecommendationSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrPharmacyOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ("category", "category__slug", "slug", "pharmacy_wilaya")
    search_fields = ("name", "summary", "sku", "category__name")
    ordering_fields = ("name", "price", "stock", "expiration_date")
    ordering = ("name",)

    def get_queryset(self):
        qs = Product.objects.select_related("category").all()
        if self.request.query_params.get("my_store") == "true" and self.request.user.is_authenticated:
            qs = qs.filter(auth_user_id=self.request.user.id)
        return qs.order_by("name")

    def perform_create(self, serializer):
        user_id = self.request.user.id
        # Extract extra info from token if available
        token = self.request.auth
        pharm_name = token.get("pharmacy_name") if token else None
        pharm_wilaya = token.get("wilaya") if token else None
        
        serializer.save(
            auth_user_id=user_id,
            pharmacy_name=pharm_name,
            pharmacy_wilaya=pharm_wilaya
        )


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
            publish_order_created(order_id=order.pk, user_id=order.auth_user_id, email=order.email, total=order.total)

        transaction.on_commit(_pub)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def product_like_view(request, pk):
    """Like or unlike a product"""
    try:
        product = Product.objects.get(pk=pk)
        like, created = ProductLike.objects.get_or_create(
            auth_user_id=request.user.id,
            product=product
        )
        
        if not created:
            # Unlike
            like.delete()
            return Response({
                "message": "Recommandation retirée",
                "liked": False,
                "likes_count": ProductLike.objects.filter(product=product).count()
            })
        else:
            # Like
            return Response({
                "message": "Merci pour votre recommandation !",
                "liked": True,
                "likes_count": ProductLike.objects.filter(product=product).count()
            })
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def product_rate_view(request, pk):
    """Rate or update a product rating"""
    try:
        product = Product.objects.get(pk=pk)
        
        # Get or create rating
        rating, created = ProductRating.objects.get_or_create(
            auth_user_id=request.user.id,
            product=product,
            defaults={
                'rating': request.data.get('rating', 5),
                'comment': request.data.get('comment', '')
            }
        )
        
        if not created:
            # Update existing rating
            serializer = ProductRatingCreateSerializer(rating, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                message = "Note mise à jour"
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = "Note ajoutée avec succès"
        
        # Calculate new average
        ratings = ProductRating.objects.filter(product=product)
        avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
        
        return Response({
            "message": message,
            "rating": rating.rating,
            "comment": rating.comment,
            "average_rating": avg_rating,
            "rating_count": ratings.count()
        })
        
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def product_unrate_view(request, pk):
    """Remove a product rating"""
    try:
        product = Product.objects.get(pk=pk)
        rating = ProductRating.objects.filter(auth_user_id=request.user.id, product=product).first()
        
        if rating:
            rating.delete()
            # Calculate new average
            ratings = ProductRating.objects.filter(product=product)
            avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
            
            return Response({
                "message": "Note supprimée",
                "average_rating": avg_rating,
                "rating_count": ratings.count()
            })
        else:
            return Response({"error": "Aucune note à supprimer"}, status=status.HTTP_400_BAD_REQUEST)
            
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_ratings_view(request, pk):
    """Get all ratings for a product"""
    try:
        product = Product.objects.get(pk=pk)
        ratings = ProductRating.objects.filter(product=product).order_by('-created_at')
        serializer = ProductRatingSerializer(ratings, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def product_recommend_view(request, pk):
    """Recommend or unrecommend a product (toggle)"""
    try:
        product = Product.objects.get(pk=pk)
        
        # Toggle recommendation
        recommendation, created = ProductRecommendation.objects.get_or_create(
            auth_user_id=request.user.id,
            product=product
        )
        
        if not created:
            # Remove recommendation
            recommendation.delete()
            return Response({
                "message": "Recommandation retirée",
                "recommended": False,
                "recommendations_count": ProductRecommendation.objects.filter(product=product).count()
            })
        else:
            # Add recommendation
            return Response({
                "message": "Produit recommandé !",
                "recommended": True,
                "recommendations_count": ProductRecommendation.objects.filter(product=product).count()
            })
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def product_ai_recommend_view(request, pk):
    """AI-based product recommendation"""
    try:
        product = Product.objects.get(pk=pk)
        
        # Simple AI logic: recommend based on similar products in category
        similar_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:3]
        
        recommendations = []
        for similar_product in similar_products:
            recommendations.append({
                "id": similar_product.id,
                "name": similar_product.name,
                "price": similar_product.price,
                "reason": f"Similaire à {product.name} dans la catégorie {product.category.name}"
            })
        
        return Response({
            "message": "Recommandations IA générées",
            "recommendations": recommendations
        })
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_recommendations_view(request, pk):
    """Get all recommendations for a product"""
    try:
        product = Product.objects.get(pk=pk)
        recommendations = ProductRecommendation.objects.filter(product=product).order_by('-created_at')
        serializer = ProductRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)
