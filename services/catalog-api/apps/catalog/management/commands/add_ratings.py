from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.catalog.models import Product, ProductRating


class Command(BaseCommand):
    help = "Ajoute des évaluations utilisateurs aux produits"

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des évaluations existent déjà.")

    def handle(self, *args, **options):
        if options["if-empty"] and ProductRating.objects.exists():
            self.stdout.write("Des évaluations existent déjà, opération ignorée.")
            return

        # Get products
        products = Product.objects.all()[:5]
        
        if not products:
            self.stdout.write(self.style.WARNING("Aucun produit trouvé."))
            return

        # Get or create demo users
        users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                id=i,
                defaults={
                    'username': f'user{i}',
                    'email': f'user{i}@example.com',
                    'password': 'demo123'
                }
            )
            users.append(user)

        # Create ratings data (15 ratings total)
        rating_data = [
            # User 1 ratings
            (users[0], products[0], 5, "Excellent produit!"),
            (users[0], products[1], 4, "Très bon rapport qualité/prix"),
            (users[0], products[2], 5, "Parfait pour nos besoins"),
            # User 2 ratings
            (users[1], products[0], 4, "Bon produit"),
            (users[1], products[1], 4, "Satisfait"),
            (users[1], products[3], 5, "Excellent service"),
            # User 3 ratings
            (users[2], products[1], 5, "Top qualité"),
            (users[2], products[2], 5, "Recommandé"),
            (users[2], products[4], 5, "Impeccable"),
            # User 4 ratings
            (users[3], products[0], 3, "Correct mais peut mieux faire"),
            (users[3], products[2], 4, "Bon produit"),
            (users[3], products[3], 4, "Satisfaisant"),
            # User 5 ratings
            (users[4], products[1], 4, "Bien"),
            (users[4], products[3], 5, "Excellent"),
            (users[4], products[4], 3, "Moyen"),
        ]
        
        added = 0
        for user, product, rating, comment in rating_data:
            rating_obj, created = ProductRating.objects.get_or_create(
                user=user,
                product=product,
                defaults={"rating": rating, "comment": comment}
            )
            if created:
                added += 1
                avg = float(product.get_average_rating())
                self.stdout.write(f"✅ {user.username} note {product.name}: {rating}⭐ (moyenne: {avg:.2f})")
        
        self.stdout.write(self.style.SUCCESS(f"\n✨ {added} évaluations ajoutées au catalogue!"))
