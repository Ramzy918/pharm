from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Create specific categories (bébé, masques, tests, gants, consommables)'

    def handle(self, *args, **options):
        # Define specific categories
        categories_data = [
            {
                'name': 'Bébé',
                'slug': 'bebe',
                'description': 'Produits pour bébés et nourrissons',
                'products': [
                    {'name': 'Couches Bébé Taille M', 'price': 15.99, 'sku': 'COUCHE-M'},
                    {'name': 'Lait Infantile 0-6 mois', 'price': 12.99, 'sku': 'LAIT-0-6'},
                    {'name': 'Biberon Anti-colique', 'price': 8.99, 'sku': 'BIB-ANTI'},
                    {'name': 'Gel Lavant Bébé', 'price': 6.99, 'sku': 'GEL-BEBE'},
                    {'name': 'Crème Change Bébé', 'price': 4.99, 'sku': 'CREAM-CHANGE'},
                ]
            },
            {
                'name': 'Masques',
                'slug': 'masques',
                'description': 'Masques de protection et chirurgicaux',
                'products': [
                    {'name': 'Masque Chirurgical Type IIR', 'price': 0.50, 'sku': 'MASK-IIR'},
                    {'name': 'Masque FFP2 Sans Valve', 'price': 0.80, 'sku': 'MASK-FFP2'},
                    {'name': 'Masque Enfant Taille S', 'price': 0.45, 'sku': 'MASK-ENF'},
                    {'name': 'Masque Lavable Réutilisable', 'price': 3.99, 'sku': 'MASK-LAV'},
                    {'name': 'Masque KN95', 'price': 0.75, 'sku': 'MASK-KN95'},
                ]
            },
            {
                'name': 'Tests',
                'slug': 'tests',
                'description': 'Tests de dépistage et diagnostics',
                'products': [
                    {'name': 'Test COVID Antigénique', 'price': 2.99, 'sku': 'TEST-COV'},
                    {'name': 'Test Grossesse Précoce', 'price': 1.99, 'sku': 'TEST-GROS'},
                    {'name': 'Test Glycémie', 'price': 8.99, 'sku': 'TEST-GLY'},
                    {'name': 'Test Urinaire Complet', 'price': 3.99, 'sku': 'TEST-URI'},
                    {'name': 'Test Allergie Alimentaire', 'price': 12.99, 'sku': 'TEST-ALL'},
                ]
            },
            {
                'name': 'Gants',
                'slug': 'gants',
                'description': 'Gants de protection médicaux',
                'products': [
                    {'name': 'Gants Nitrile Taille M', 'price': 0.15, 'sku': 'GANT-NIT-M'},
                    {'name': 'Gants Latex Taille L', 'price': 0.12, 'sku': 'GANT-LTX-L'},
                    {'name': 'Gants Vinyle Taille S', 'price': 0.10, 'sku': 'GANT-VIN-S'},
                    {'name': 'Gants Chirurgicaux Stériles', 'price': 0.25, 'sku': 'GANT-CHIR'},
                    {'name': 'Gants Examen Non Stériles', 'price': 0.08, 'sku': 'GANT-EXAM'},
                ]
            },
            {
                'name': 'Consommables',
                'slug': 'consommables',
                'description': 'Produits consommables médicaux',
                'products': [
                    {'name': 'Seringue 5ml', 'price': 0.20, 'sku': 'SER-5ML'},
                    {'name': 'Compresses Stériles 10x10', 'price': 2.99, 'sku': 'COMP-10X10'},
                    {'name': 'Bandage Élastique 5cm', 'price': 1.99, 'sku': 'BAND-5CM'},
                    {'name': 'Alcool 70% 100ml', 'price': 1.49, 'sku': 'ALC-70-100'},
                    {'name': 'Bétadine 30ml', 'price': 3.99, 'sku': 'BETA-30ML'},
                ]
            }
        ]

        created_categories = 0
        created_products = 0

        for cat_data in categories_data:
            # Check if category already exists
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )

            if created:
                created_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created category: {category.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Category already exists: {category.name}")
                )

            # Create products for this category
            for prod_data in cat_data['products']:
                product, created = Product.objects.get_or_create(
                    sku=prod_data['sku'],
                    defaults={
                        'name': prod_data['name'],
                        'price': prod_data['price'],
                        'category': category,
                        'stock': 100,  # Default stock
                        'summary': f"{prod_data['name']} - {category.name}"
                    }
                )

                if created:
                    created_products += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  Created product: {product.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  Product already exists: {product.name}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary: {created_categories} categories created, "
                f"{created_products} products created"
            )
        )
