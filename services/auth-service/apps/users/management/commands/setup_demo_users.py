from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = "Create/Reset real demo accounts for Pharmacies, Clients and Admin"

    def handle(self, *args, **options):
        # 1. Admin account
        admin, created = User.objects.get_or_create(
            email="admin@demo.local",
            defaults={
                "first_name": "Admin",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True
            }
        )
        admin.set_password("adminadmin123")
        admin.save()
        self.stdout.write(self.style.SUCCESS(f"Admin prêt : {admin.email} (adminadmin123)"))

        # 2. Pharmacy accounts
        pharmacies_data = [
            {"email": "elchifaa@demo.local", "pwd": "pharmacie123", "name": "Pharmacie El Chifaa", "wilaya": "Alger"},
            {"email": "ibnsina@demo.local", "pwd": "pharmacie123", "name": "Pharmacie Ibn Sina", "wilaya": "Oran"},
            {"email": "elyakout@demo.local", "pwd": "pharmacie123", "name": "Pharmacie El Yakout", "wilaya": "Constantine"},
            {"email": "centrale@demo.local", "pwd": "pharmacie123", "name": "Pharmacie Centrale", "wilaya": "Blida"}
        ]

        for data in pharmacies_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "first_name": data["name"].split()[-1],
                    "pharmacy_name": data["name"],
                    "wilaya": data["wilaya"],
                    "role": User.Role.PHARMACY,
                    "is_active": True
                }
            )
            user.set_password(data["pwd"])
            user.pharmacy_name = data["name"]
            user.wilaya = data["wilaya"]
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Pharmacie prête : {data['email']} ({data['pwd']})"))

        # 3. Client PRO (Acheteur)
        pro, created = User.objects.get_or_create(
            email="pro@demo.local",
            defaults={
                "first_name": "Aitali",
                "last_name": "Idir",
                "role": User.Role.PRO,
                "wilaya": "Alger",
                "is_active": True
            }
        )
        pro.set_password("propro123")
        pro.wilaya = "Alger"
        pro.is_active = True
        pro.save()
        self.stdout.write(self.style.SUCCESS(f"Client PRO prêt : {pro.email} (propro123)"))

        self.stdout.write(self.style.SUCCESS("Tous les comptes de démo ont été réinitialisés avec succès !"))
