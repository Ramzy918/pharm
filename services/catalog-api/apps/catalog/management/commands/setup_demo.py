import random
from django.core.management.base import BaseCommand
from apps.catalog.models import Product

class Command(BaseCommand):
    help = "Prepare the database for a demo (stock, images, ownership)"

    def add_arguments(self, parser):
        parser.add_argument('--pharmacy-id', type=int, help='ID of the pharmacy user')

    def handle(self, *args, **options):
        pharmacy_id = options['pharmacy_id']
        if not pharmacy_id:
            self.stdout.write(self.style.ERROR("Please provide --pharmacy-id"))
            return

        products = list(Product.objects.all().order_by('id'))
        if not products:
            self.stdout.write("No products found.")
            return

        images = [
            "https://images.unsplash.com/photo-1584308666744-24d5e4a8b7dd?auto=format&fit=crop&w=400&q=80",
            "https://images.unsplash.com/photo-1631549911993-97914e9f3df9?auto=format&fit=crop&w=400&q=80",
            "https://images.unsplash.com/photo-1576602976047-174e57a47881?auto=format&fit=crop&w=400&q=80",
            "https://plus.unsplash.com/premium_photo-1675808575027-6f731a575a64?auto=format&fit=crop&w=400&q=80",
            "https://plus.unsplash.com/premium_photo-1673896582522-6b94e773dc4a?auto=format&fit=crop&w=400&q=80",
        ]

        assigned_count = 0
        
        for i, p in enumerate(products):
            p.stock = random.randint(10, 150)
            p.image_url = random.choice(images)
            
            if i < 300:
                p.auth_user_id = pharmacy_id
                assigned_count += 1
                
        Product.objects.bulk_update(products, ['stock', 'image_url', 'auth_user_id'], batch_size=500)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(products)} products. Assigned {assigned_count} to pharmacy ID {pharmacy_id}."))
