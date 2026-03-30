import random
from django.core.management.base import BaseCommand
from apps.catalog.models import Product

class Command(BaseCommand):
    help = "Setup multiple pharmacies with products and wilayas for demo (using real user IDs)"

    def handle(self, *args, **options):
        # Using the real IDs from auth-service as reported by the user creation
        pharmacies = [
            {"id": 10, "email": "elchifaa@demo.local", "name": "Pharmacie El Chifaa", "wilaya": "Alger"},
            {"id": 11, "email": "ibnsina@demo.local", "name": "Pharmacie Ibn Sina", "wilaya": "Oran"},
            {"id": 12, "email": "elyakout@demo.local", "name": "Pharmacie El Yakout", "wilaya": "Constantine"},
            {"id": 13, "email": "centrale@demo.local", "name": "Pharmacie Centrale", "wilaya": "Blida"},
        ]

        # Reset all products
        self.stdout.write("Distribution des produits entre les pharmacies Réelles...")
        
        all_products = list(Product.objects.all())
        random.shuffle(all_products)
        
        chunk_size = len(all_products) // len(pharmacies)
        
        for i, pharm in enumerate(pharmacies):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i != len(pharmacies) - 1 else len(all_products)
            
            subset = all_products[start:end]
            count = Product.objects.filter(id__in=[p.id for p in subset]).update(
                auth_user_id=pharm["id"],
                pharmacy_name=pharm["name"],
                pharmacy_wilaya=pharm["wilaya"]
            )
            self.stdout.write(f"Pharmacie {pharm['name']} ({pharm['wilaya']}) : {count} produits assignés à l'ID {pharm['id']}.")
            
        self.stdout.write(self.style.SUCCESS("Demo multi-pharmacie configurée avec succès !"))
