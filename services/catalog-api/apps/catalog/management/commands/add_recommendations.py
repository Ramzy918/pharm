from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.catalog.models import Product, ProductRecommendation


class Command(BaseCommand):
    help = "Ajoute des recommandations utilisateur aux produits existants"

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des recommandations existent déjà.")

    def handle(self, *args, **options):
        if options["if-empty"] and ProductRecommendation.objects.exists():
            self.stdout.write("Des recommandations existent déjà, opération ignorée.")
            return

        # Get the first few products
        products = Product.objects.all()[:4]
        
        if not products:
            self.stdout.write(self.style.WARNING("Aucun produit trouvé. Seed vide ?"))
            return

        # Get or create demo users
        users = []
        for i in range(1, 7):
            user, created = User.objects.get_or_create(
                id=i,
                defaults={
                    'username': f'user{i}',
                    'email': f'user{i}@example.com',
                    'password': 'demo123'
                }
            )
            users.append(user)

        # Add recommendations from different users (12 recommendations total)
        recommendation_data = [
            # Product 1 recommendations
            (users[0], products[0]),
            (users[1], products[0]),
            (users[2], products[0]),
            # Product 2 recommendations
            (users[1], products[1]),
            (users[2], products[1]),
            (users[3], products[1]),
            # Product 3 recommendations
            (users[0], products[2]),
            (users[3], products[2]),
            (users[4], products[2]),
            # Product 4 recommendations
            (users[2], products[3]),
            (users[4], products[3]),
            (users[5], products[3]),
        ]
        
        added = 0
        for user, product in recommendation_data:
            recommendation, created = ProductRecommendation.objects.get_or_create(
                user=user,
                product=product
            )
            if created:
                added += 1
                self.stdout.write(f"✅ {user.username} recommande {product.name}")
        
        # Update recommendation counters
        for product in products:
            product.user_recommendations = ProductRecommendation.objects.filter(product=product).count()
            product.save()

        self.stdout.write(self.style.SUCCESS(f"✅ {added} recommandations utilisateur ajoutées avec succès."))
