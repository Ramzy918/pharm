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

        if options["if_empty"] and Product.objects.exists():
            self.stdout.write("Catalogue déjà peuplé, seed ignoré.")
            return

        # Créer les catégories principales
        data = [
            ("Bébés", "bebe", "Puériculture et soins bébé, alimentation, hygiène."),
            ("Tests médicaux", "tests", "Tests rapides, antigéniques, autotests, diagnostics."),
            ("Masques", "masques", "Masques de protection et chirurgicaux."),
            ("Gants", "gants", "Gants de protection médicaux."),
            ("Consommables", "consommables", "Produits consommables médicaux."),
            ("Gants & protection", "protection", "Protection respiratoire, gants nitrile et latex."),
            ("Médicaments", "medicaments", "Médicaments sans ordonnance, paracétamol, ibuprofène."),
            ("Rhume & Grippe", "rhume", "Soins pour le rhume, la toux et les états grippaux."),
            ("Digestion", "digestion", "Troubles gastriques, digestion et transit."),
            ("Allergies", "allergie", "Antihistaminiques et soins antiallergiques."),
            ("Premiers secours", "premiers-secours", "Désinfectants, pansements et matériel d'urgence."),
            ("Vitamines", "vitamines", "Compléments alimentaires et multivitamines."),
            ("Para-pharmacie", "para-pharmacie", "Hygiène, cosmétique et soins quotidiens."),
        ]
        cats = {}
        for name, slug, desc in data:
            c, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "description": desc})
            cats[slug] = c
            self.stdout.write(f"Catégorie créée/mise à jour: {name}")

        # Produits étendus pour chaque catégorie
        samples = [
            # Bébés
            ("bebe", "Lait infantile 1er âge", "lait-1er-age", "SKU-BEBE-L1", Decimal("2600.00"), 100),
            ("bebe", "Lait 2ème âge", "lait-2eme-age", "SKU-BEBE-L2", Decimal("2800.00"), 100),
            ("bebe", "Lait anti-colique", "lait-anti-colique", "SKU-BEBE-LAC", Decimal("3200.00"), 80),
            ("bebe", "Couches bébé (Pampers)", "couches-pampers", "SKU-BEBE-COU", Decimal("2200.00"), 150),
            ("bebe", "Lingettes bébé", "lingettes-bebe", "SKU-BEBE-LIN", Decimal("260.00"), 200),
            ("bebe", "Crème érythème fessier", "creme-erytheme", "SKU-BEBE-CRM", Decimal("420.00"), 120),
            ("bebe", "Sérum physiologique", "serum-physio", "SKU-BEBE-SER", Decimal("210.00"), 300),
            ("bebe", "Thermomètre digital", "thermometre-digital", "SKU-BEBE-THD", Decimal("1200.00"), 50),
            ("bebe", "Gel lavant bébé", "gel-lavant-bebe", "SKU-BEBE-GEL", Decimal("900.00"), 100),
            ("bebe", "Huile bébé", "huile-bebe", "SKU-BEBE-HUI", Decimal("700.00"), 90),

            # Tests médicaux
            ("tests", "Test grossesse", "test-grossesse", "SKU-TST-GRO", Decimal("320.00"), 200),
            ("tests", "Test ovulation", "test-ovulation", "SKU-TST-OVU", Decimal("450.00"), 150),
            ("tests", "Test glycémie (Appareil)", "test-glycemie-app", "SKU-TST-GLY", Decimal("1200.00"), 60),
            ("tests", "Bandelettes glycémie", "bandelettes-glycemie", "SKU-TST-BAN", Decimal("2500.00"), 100),
            ("tests", "Test COVID antigénique", "test-covid", "SKU-TST-COV", Decimal("620.00"), 300),
            ("tests", "Test urinaire", "test-urinaire", "SKU-TST-URI", Decimal("330.00"), 150),
            ("tests", "Test cholestérol", "test-cholesterol", "SKU-TST-CHO", Decimal("1900.00"), 80),
            ("tests", "Test VIH rapide", "test-vih", "SKU-TST-VIH", Decimal("1750.00"), 50),

            # Masques
            ("masques", "Masque chirurgical Type IIR", "masque-iir", "SKU-MSK-IIR", Decimal("0.50"), 1000),
            ("masques", "Masque FFP2 sans valve", "masque-ffp2", "SKU-MSK-FFP2", Decimal("0.80"), 500),
            ("masques", "Masque enfant taille S", "masque-enfant", "SKU-MSK-ENF", Decimal("0.45"), 300),
            ("masques", "Masque lavable réutilisable", "masque-lavable", "SKU-MSK-LAV", Decimal("3.99"), 100),
            ("masques", "Masque KN95", "masque-kn95", "SKU-MSK-KN95", Decimal("0.75"), 400),

            # Gants
            ("gants", "Gants nitrile taille M", "gants-nitrile-m", "SKU-GNT-NIT-M", Decimal("0.15"), 1000),
            ("gants", "Gants latex taille L", "gants-latex-l", "SKU-GNT-LTX-L", Decimal("0.12"), 800),
            ("gants", "Gants vinyle taille S", "gants-vinyle-s", "SKU-GNT-VIN-S", Decimal("0.10"), 600),
            ("gants", "Gants chirurgicaux stériles", "gants-chirurgicaux", "SKU-GNT-CHIR", Decimal("0.25"), 200),
            ("gants", "Gants examen non stériles", "gants-examen", "SKU-GNT-EXAM", Decimal("0.08"), 1200),

            # Consommables
            ("consommables", "Seringue 5ml", "seringue-5ml", "SKU-CON-SER5", Decimal("0.20"), 500),
            ("consommables", "Compresses stériles 10x10", "compresses-10x10", "SKU-CON-COMP", Decimal("2.99"), 200),
            ("consommables", "Bande élastique 5cm", "bande-5cm", "SKU-CON-BAND", Decimal("1.99"), 150),
            ("consommables", "Alcool 70% 100ml", "alcool-70-100ml", "SKU-CON-ALC", Decimal("1.49"), 300),
            ("consommables", "Bétadine 30ml", "betadine-30ml", "SKU-CON-BET", Decimal("3.99"), 100),

            # Protection
            ("protection", "Gants latex (boîte 100)", "gants-latex", "SKU-PRO-GLX", Decimal("2250.00"), 120),
            ("protection", "Gants nitrile (boîte 100)", "gants-nitrile", "SKU-PRO-GNT", Decimal("2650.00"), 100),
            ("protection", "Masques chirurgicaux (boîte 50)", "masques-chir", "SKU-PRO-MSK", Decimal("550.00"), 200),
            ("protection", "Gel hydroalcoolique 500ml", "gel-hydro", "SKU-PRO-GEL", Decimal("500.00"), 150),
            ("protection", "Thermomètre infrarouge", "thermometre-infra", "SKU-PRO-THI", Decimal("6500.00"), 40),

            # Médicaments
            ("medicaments", "Paracétamol 500mg", "paracetamol-500", "SKU-MED-PAR", Decimal("225.00"), 500),
            ("medicaments", "Ibuprofène 400mg", "ibuprofene-400", "SKU-MED-IBU", Decimal("350.00"), 400),
            ("medicaments", "Aspirine 100mg", "aspirine-100", "SKU-MED-ASP", Decimal("175.00"), 300),
            ("medicaments", "Diclofénac gel 1%", "diclofenac-gel", "SKU-MED-DIC", Decimal("500.00"), 200),
            ("medicaments", "Spasfon", "spasfon", "SKU-MED-SPA", Decimal("450.00"), 250),

            # Rhume
            ("rhume", "Fervex Adulte", "fervex", "SKU-RHU-FER", Decimal("475.00"), 300),
            ("rhume", "Humex Rhume", "humex", "SKU-RHU-HUM", Decimal("550.00"), 250),
            ("rhume", "Vitamine C 1000mg", "vitamine-c", "SKU-RHU-VIT", Decimal("300.00"), 400),
            ("rhume", "Spray nasal", "spray-nasal", "SKU-RHU-SPR", Decimal("375.00"), 350),
            ("rhume", "Sirop toux sèche/grasse", "sirop-toux", "SKU-RHU-SIR", Decimal("500.00"), 280),

            # Digestion
            ("digestion", "Gaviscon Suspension", "gaviscon", "SKU-DIG-GAV", Decimal("650.00"), 200),
            ("digestion", "Maalox Anti-acide", "maalox", "SKU-DIG-MAA", Decimal("550.00"), 220),
            ("digestion", "Smecta 3g", "smecta", "SKU-DIG-SME", Decimal("450.00"), 300),
            ("digestion", "Charbon actif", "charbon-actif", "SKU-DIG-CHA", Decimal("350.00"), 250),
            ("digestion", "Sirop digestif", "sirop-digestif", "SKU-DIG-SIR", Decimal("500.00"), 180),

            # Allergies
            ("allergie", "Cétirizine 10mg", "cetirizine", "SKU-ALL-CET", Decimal("300.00"), 200),
            ("allergie", "Loratadine 10mg", "loratadine", "SKU-ALL-LOR", Decimal("350.00"), 180),
            ("allergie", "Crème antihistaminique", "creme-anti-hist", "SKU-ALL-CRM", Decimal("450.00"), 150),

            # Premiers secours
            ("premiers-secours", "Bétadine solution dermique", "betadine", "SKU-SEC-BET", Decimal("450.00"), 200),
            ("premiers-secours", "Pansements adhésifs (boîte)", "pansements", "SKU-SEC-PAN", Decimal("225.00"), 300),
            ("premiers-secours", "Alcool médical 70%", "alcool-medical", "SKU-SEC-ALC", Decimal("300.00"), 250),
            ("premiers-secours", "Compresses stériles", "compresses", "SKU-SEC-COM", Decimal("350.00"), 300),
            ("premiers-secours", "Eau oxygénée", "eau-oxygenee", "SKU-SEC-EAU", Decimal("300.00"), 220),

            # Vitamines
            ("vitamines", "Multivitamines A-Z", "multivitamines", "SKU-VIT-MUL", Decimal("600.00"), 150),
            ("vitamines", "Magnésium B6", "magnesium", "SKU-VIT-MAG", Decimal("500.00"), 200),
            ("vitamines", "Fer + Acide Folique", "fer", "SKU-VIT-FER", Decimal("450.00"), 180),
            ("vitamines", "Oméga 3", "omega-3", "SKU-VIT-OME", Decimal("900.00"), 120),

            # Para-pharmacie
            ("para-pharmacie", "Crème hydratante corps/visage", "creme-hydratante", "SKU-PAR-HYD", Decimal("1000.00"), 100),
            ("para-pharmacie", "Crème solaire SPF 50+", "creme-solaire", "SKU-PAR-SOL", Decimal("1650.00"), 80),
            ("para-pharmacie", "Baume à lèvres", "baume-levres", "SKU-PAR-BAU", Decimal("350.00"), 200),
            ("para-pharmacie", "Shampooing antipelliculaire", "shampooing", "SKU-PAR-SHA", Decimal("1100.00"), 120),
            ("para-pharmacie", "Dentifrice blancheur", "dentifrice", "SKU-PAR-DEN", Decimal("350.00"), 300),
            ("para-pharmacie", "Brosse à dents", "brosse-a-dents", "SKU-PAR-BAD", Decimal("275.00"), 250),
            ("para-pharmacie", "Bain de bouche", "bain-bouche", "SKU-PAR-BAI", Decimal("650.00"), 180),
            ("para-pharmacie", "Gel anti-acné", "gel-acne", "SKU-PAR-ACN", Decimal("1050.00"), 100),
            ("para-pharmacie", "Solution lentilles", "solution-lentilles", "SKU-PAR-SLN", Decimal("1400.00"), 70),
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
