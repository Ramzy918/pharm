from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Charge un jeu de données type MarketPharm (catégories + produits étendus)."

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des produits existent déjà.")
        parser.add_argument("--reset", action="store_true", help="Supprimer tous les produits existants avant de recréer.")

    def handle(self, *args, **options):
        if options["reset"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Tous les produits et catégories ont été supprimés.")

        if options["if-empty"] and Product.objects.exists():
            self.stdout.write("Catalogue déjà peuplé, seed ignoré.")
            return

        # Créer les catégories principales
        data = [
            ("Tests", "tests", "Tests rapides, antigéniques, autotests, diagnostics."),
            ("Masques", "masques", "Protection respiratoire, chirurgicaux, FFP2, FFP3."),
            ("Gants", "gants", "Gants usage professionnel, nitrile, latex, vinyle."),
            ("Consommables", "consommables", "Consommables pharmacie, matériel médical."),
            ("Bébé", "bebe", "Puériculture et soins bébé, alimentation, hygiène."),
        ]
        cats = {}
        for name, slug, desc in data:
            c, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "description": desc})
            cats[slug] = c
            self.stdout.write(f"Catégorie créée/mise à jour: {name}")

        # Produits étendus pour chaque catégorie
        samples = [
            # Tests
            ("tests", "Test antigénique COVID-19 — boîte 25", "test-antigenique-25", "SKU-TST-25", Decimal("35.00"), 500),
            ("tests", "Test antigénique COVID-19 — boîte 50", "test-antigenique-50", "SKU-TST-50", Decimal("65.00"), 300),
            ("tests", "Autotest unitaire COVID-19", "autotest-unitaire", "SKU-AUTO-1", Decimal("0.40"), 800),
            ("tests", "Test grossesse précoce", "test-grossesse", "SKU-TST-GROS", Decimal("2.99"), 150),
            ("tests", "Test glycémie sanguine", "test-glycemie", "SKU-TST-GLY", Decimal("8.50"), 200),
            ("tests", "Test urinaire complet", "test-urinaire", "SKU-TST-URI", Decimal("3.99"), 180),
            ("tests", "Test allergène alimentaire", "test-allergie", "SKU-TST-ALL", Decimal("12.99"), 100),
            ("tests", "Test cholestérol", "test-cholesterol", "SKU-TST-CHOL", Decimal("6.99"), 120),
            ("tests", "Test VIH rapide", "test-vih", "SKU-TST-VIH", Decimal("15.99"), 80),
            ("tests", "Test hépatite C", "test-hepatite", "SKU-TST-HEP", Decimal("18.99"), 60),

            # Masques
            ("masques", "Masques chirurgicaux Type IIR — boîte 50", "masques-chir-50", "SKU-MSK-50", Decimal("12.50"), 300),
            ("masques", "Masques chirurgicaux Type II — boîte 50", "masques-chir-2-50", "SKU-MSK-2-50", Decimal("10.50"), 250),
            ("masques", "Masques FFP2 sans valve — boîte 20", "masques-ffp2-20", "SKU-MSK-FFP2-20", Decimal("25.00"), 200),
            ("masques", "Masques FFP2 avec valve — boîte 20", "masques-ffp2-valve-20", "SKU-MSK-FFP2V-20", Decimal("28.00"), 150),
            ("masques", "Masques FFP3 — boîte 10", "masques-ffp3-10", "SKU-MSK-FFP3-10", Decimal("35.00"), 100),
            ("masques", "Masques enfant — boîte 30", "masques-enfant-30", "SKU-MSK-ENF-30", Decimal("8.99"), 180),
            ("masques", "Masques lavable réutilisable", "masques-lavable", "SKU-MSK-LAV", Decimal("4.99"), 400),
            ("masques", "Masques à charbon actif", "masques-charbon", "SKU-MSK-CHAR", Decimal("6.99"), 220),
            ("masques", "Masques KN95 — boîte 25", "masques-kn95-25", "SKU-MSK-KN95-25", Decimal("22.00"), 160),
            ("masques", "Masques protection anti-poussière", "masques-poussiere", "SKU-MSK-POU", Decimal("3.99"), 280),

            # Gants
            ("gants", "Gants nitrile Taille S — boîte 100", "gants-nitrile-s", "SKU-GNT-S", Decimal("16.90"), 200),
            ("gants", "Gants nitrile Taille M — boîte 100", "gants-nitrile-m", "SKU-GNT-M", Decimal("18.90"), 200),
            ("gants", "Gants nitrile Taille L — boîte 100", "gants-nitrile-l", "SKU-GNT-L", Decimal("19.90"), 200),
            ("gants", "Gants nitrile Taille XL — boîte 100", "gants-nitrile-xl", "SKU-GNT-XL", Decimal("21.90"), 150),
            ("gants", "Gants latex Taille M — boîte 100", "gants-latex-m", "SKU-GTX-M", Decimal("14.90"), 180),
            ("gants", "Gants latex Taille L — boîte 100", "gants-latex-l", "SKU-GTX-L", Decimal("15.90"), 180),
            ("gants", "Gants vinyle Taille M — boîte 100", "gants-vinyle-m", "SKU-GVN-M", Decimal("12.90"), 220),
            ("gants", "Gants vinyle Taille L — boîte 100", "gants-vinyle-l", "SKU-GVN-L", Decimal("13.90"), 220),
            ("gants", "Gants chirurgicaux stériles — boîte 50", "gants-chir-sterile-50", "SKU-GCS-50", Decimal("35.00"), 100),
            ("gants", "Gants examen non stériles — boîte 100", "gants-examen-100", "SKU-GEX-100", Decimal("8.90"), 300),

            # Consommables
            ("consommables", "Seringue 5ml — boîte 100", "seringue-5ml-100", "SKU-SRG-5-100", Decimal("4.99"), 300),
            ("consommables", "Seringue 10ml — boîte 100", "seringue-10ml-100", "SKU-SRG-10-100", Decimal("5.99"), 280),
            ("consommables", "Seringue nasale pédiatrique", "seringue-nasale", "SKU-SRG-NAS", Decimal("1.45"), 500),
            ("consommables", "Aiguille 21G — boîte 100", "aiguille-21g-100", "SKU-AIG-21-100", Decimal("3.99"), 400),
            ("consommables", "Aiguille 23G — boîte 100", "aiguille-23g-100", "SKU-AIG-23-100", Decimal("3.49"), 400),
            ("consommables", "Compresses stériles 10x10 — boîte 100", "compresses-10x10-100", "SKU-COM-10-100", Decimal("8.99"), 250),
            ("consommables", "Compresses stériles 5x5 — boîte 100", "compresses-5x5-100", "SKU-COM-5-100", Decimal("6.99"), 300),
            ("consommables", "Bandage élastique 5cm", "bandage-elastic-5cm", "SKU-BAN-5", Decimal("2.99"), 400),
            ("consommables", "Bandage élastique 10cm", "bandage-elastic-10cm", "SKU-BAN-10", Decimal("4.99"), 350),
            ("consommables", "Alcool 70% 100ml", "alcool-70-100ml", "SKU-ALC-70-100", Decimal("1.99"), 600),
            ("consommables", "Alcool 70% 250ml", "alcool-70-250ml", "SKU-ALC-70-250", Decimal("3.99"), 400),
            ("consommables", "Bétadine 30ml", "betadine-30ml", "SKU-BET-30", Decimal("4.99"), 350),
            ("consommables", "Bétadine 100ml", "betadine-100ml", "SKU-BET-100", Decimal("12.99"), 200),
            ("consommables", "Gaze stérile 10x10 — paquet 10", "gaze-sterile-10x10", "SKU-GAZ-10", Decimal("3.99"), 300),
            ("consommables", "Pansement adhésif assorted", "pansement-adhesif", "SKU-PAN-ASS", Decimal("5.99"), 250),
            ("consommables", "Gants en latex Taille M (unité)", "gants-latex-m-single", "SKU-GTX-M-S", Decimal("0.15"), 1000),
            ("consommables", "Gants en nitrile Taille M (unité)", "gants-nitrile-m-single", "SKU-GNT-M-S", Decimal("0.18"), 1000),

            # Bébé
            ("bebe", "Lait premier âge 0-6 mois — 900g", "lait-premier-age-0-6", "SKU-LAIT-0-6", Decimal("18.99"), 200),
            ("bebe", "Lait deuxième âge 6-12 mois — 900g", "lait-deuxieme-age-6-12", "SKU-LAIT-6-12", Decimal("19.99"), 180),
            ("bebe", "Lait croissance 12-24 mois — 900g", "lait-croissance-12-24", "SKU-LAIT-12-24", Decimal("20.99"), 160),
            ("bebe", "Couches Taille 1 (2-5kg) — paquet 30", "couches-taille-1", "SKU-COU-1", Decimal("12.99"), 150),
            ("bebe", "Couches Taille 2 (4-8kg) — paquet 28", "couches-taille-2", "SKU-COU-2", Decimal("13.99"), 150),
            ("bebe", "Couches Taille 3 (6-10kg) — paquet 26", "couches-taille-3", "SKU-COU-3", Decimal("14.99"), 140),
            ("bebe", "Couches Taille 4 (9-14kg) — paquet 24", "couches-taille-4", "SKU-COU-4", Decimal("15.99"), 130),
            ("bebe", "Couches Taille 5 (12-16kg) — paquet 22", "couches-taille-5", "SKU-COU-5", Decimal("16.99"), 120),
            ("bebe", "Biberon anti-colique 250ml", "biberon-anti-colique-250", "SKU-BIB-250", Decimal("8.99"), 200),
            ("bebe", "Biberon 150ml — lot de 3", "biberon-150ml-3", "SKU-BIB-150-3", Decimal("15.99"), 100),
            ("bebe", "Gel lavant bébé 500ml", "gel-lavant-bebe-500", "SKU-GLV-500", Decimal("6.99"), 250),
            ("bebe", "Gel lavant bébé 1L", "gel-lavant-bebe-1l", "SKU-GLV-1L", Decimal("11.99"), 150),
            ("bebe", "Crème change bébé 100ml", "creme-change-bebe-100", "SKU-CRM-100", Decimal("4.99"), 300),
            ("bebe", "Crème change bébé 200ml", "creme-change-bebe-200", "SKU-CRM-200", Decimal("7.99"), 200),
            ("bebe", "Lingettes bébé — paquet 80", "lingettes-bebe-80", "SKU-LIN-80", Decimal("3.99"), 400),
            ("bebe", "Lingettes bébé — paquet 240", "lingettes-bebe-240", "SKU-LIN-240", Decimal("9.99"), 200),
            ("bebe", "Thermomètre bébé", "thermometre-bebe", "SKU-THM-BB", Decimal("12.99"), 150),
            ("bebe", "Aspirateur nasal bébé", "aspirateur-nasal-bebe", "SKU-ASP-NAS", Decimal("8.99"), 180),
            ("bebe", "Pack hygiène bébé complet", "pack-hygiene-bebe", "SKU-PACK-HYG", Decimal("24.00"), 100),
            ("bebe", "Couverture bébé coton", "couverture-bebe-coton", "SKU-COUV-COT", Decimal("18.99"), 80),
            ("bebe", "Sucette orthodontique 0-6mois", "sucette-ortho-0-6", "SKU-SUC-0-6", Decimal("3.99"), 250),
            ("bebe", "Sucette orthodontique 6-18mois", "sucette-ortho-6-18", "SKU-SUC-6-18", Decimal("3.99"), 250),
        ]

        created_count = 0
        updated_count = 0

        for cat_slug, title, pslug, sku, price, stock in samples:
            product, created = Product.objects.update_or_create(
                slug=pslug,
                defaults={
                    "name": title,
                    "category": cats[cat_slug],
                    "summary": f"Produit professionnel — catégorie {cats[cat_slug].name}.",
                    "price": price,
                    "stock": stock,
                    "sku": sku,
                },
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✅ Produit créé: {title} ({cats[cat_slug].name})")
            else:
                updated_count += 1
                self.stdout.write(f"🔄 Produit mis à jour: {title} ({cats[cat_slug].name})")

        # Vérification que chaque produit a bien une catégorie
        products_without_category = Product.objects.filter(category__isnull=True)
        if products_without_category.exists():
            self.stdout.write(
                self.style.WARNING(f"⚠️  {products_without_category.count()} produits sans catégorie trouvés!")
            )
            for product in products_without_category:
                self.stdout.write(f"   - {product.name} (SKU: {product.sku})")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Tous les {Product.objects.count()} produits ont une catégorie!")
            )

        # Statistiques par catégorie
        self.stdout.write("\n📊 Statistiques par catégorie:")
        for slug, category in cats.items():
            product_count = Product.objects.filter(category=category).count()
            self.stdout.write(f"   {category.name}: {product_count} produits")

        total_products = Product.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Seed terminé: {created_count} créés, {updated_count} mis à jour, "
                f"{total_products} produits au total!"
            )
        )
