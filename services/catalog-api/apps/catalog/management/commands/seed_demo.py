from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Charge un jeu de données type MarketPharm (catégories + produits)."

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des produits existent déjà.")

    def handle(self, *args, **options):
        if options["if_empty"] and Product.objects.exists():
            self.stdout.write("Catalogue déjà peuplé, seed ignoré.")
            return

        data = [
            ("Tests", "tests", "Tests rapides, antigéniques, autotests."),
            ("Masques", "masques", "Protection respiratoire."),
            ("Gants", "gants", "Gants usage professionnel."),
            ("Consommables", "consommables", "Consommables pharmacie."),
            ("Bébé", "bebe", "Puériculture et soins bébé."),
        ]
        cats = {}
        for name, slug, desc in data:
            c, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "description": desc})
            cats[slug] = c

        samples = [
            ("tests", "Test antigénique — boîte 25", "test-antigenique-25", "SKU-TST-25", Decimal("35.00"), 500),
            ("tests", "Autotest unitaire", "autotest-unitaire", "SKU-AUTO-1", Decimal("0.40"), 800),
            ("masques", "Masques chirurgicaux — boîte 50", "masques-chir-50", "SKU-MSK-50", Decimal("12.50"), 300),
            ("gants", "Gants nitrile M — boîte 100", "gants-nitrile-m", "SKU-GNT-M", Decimal("18.90"), 200),
            ("consommables", "Seringue nasale pédiatrique", "seringue-nasale", "SKU-SRG-01", Decimal("1.45"), 120),
            ("bebe", "Pack hygiène bébé", "pack-bebe", "SKU-BB-01", Decimal("24.00"), 60),
        ]
        for cat_slug, title, pslug, sku, price, stock in samples:
            Product.objects.update_or_create(
                slug=pslug,
                defaults={
                    "name": title,
                    "category": cats[cat_slug],
                    "summary": "Produit professionnel — démo.",
                    "price": price,
                    "stock": stock,
                    "sku": sku,
                },
            )
        self.stdout.write(self.style.SUCCESS("Seed catalogue terminé."))
