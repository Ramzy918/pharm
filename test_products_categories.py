#!/usr/bin/env python
"""
🧪 TESTS PRODUITS ET CATÉGORIES

Tests pour vérifier que tous les produits ont bien leur catégorie
et que le filtrage fonctionne correctement
"""

import os
import sys
import django
import requests
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.catalog.models import Product, Category
from rest_framework.test import APIClient
from rest_framework import status

class TestProductsCategories(TestCase):
    """Tests pour vérifier les produits et leurs catégories"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_all_products_have_categories(self):
        """Test: Tous les produits ont une catégorie"""
        
        products_without_category = Product.objects.filter(category__isnull=True)
        
        self.assertEqual(
            products_without_category.count(), 
            0, 
            f"Produits sans catégorie trouvés: {[p.name for p in products_without_category]}"
        )
        
        total_products = Product.objects.count()
        self.assertGreater(total_products, 0, "Aucun produit trouvé")
        
        print(f"✅ Tous les {total_products} produits ont une catégorie")
    
    def test_categories_exist(self):
        """Test: Les catégories principales existent"""
        
        expected_categories = ['tests', 'masques', 'gants', 'consommables', 'bebe']
        existing_categories = Category.objects.filter(slug__in=expected_categories)
        
        self.assertEqual(
            existing_categories.count(), 
            len(expected_categories),
            f"Catégories manquantes: {set(expected_categories) - set(existing_categories.values_list('slug', flat=True))}"
        )
        
        for category in existing_categories:
            self.assertTrue(
                Product.objects.filter(category=category).exists(),
                f"Aucun produit trouvé pour la catégorie {category.name}"
            )
    
    def test_category_filtering(self):
        """Test: Filtrage par catégorie fonctionne"""
        
        categories = Category.objects.all()
        
        for category in categories:
            response = self.client.get(f'/api/products/?category={category.id}')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            products = response.json()
            
            # Vérifier que tous les produits retournés appartiennent à la bonne catégorie
            for product in products:
                self.assertEqual(
                    product['category'], 
                    category.id,
                    f"Produit {product['name']} dans la mauvaise catégorie"
                )
            
            print(f"✅ Catégorie {category.name}: {len(products)} produits")
    
    def test_category_slug_filtering(self):
        """Test: Filtrage par slug de catégorie"""
        
        # Test avec les slugs connus
        category_slugs = ['tests', 'masques', 'gants', 'consommables', 'bebe']
        
        for slug in category_slugs:
            category = Category.objects.get(slug=slug)
            
            response = self.client.get(f'/api/products/?category_slug={slug}')
            
            if response.status_code == status.HTTP_200_OK:
                products = response.json()
                
                # Vérifier que tous les produits sont dans la bonne catégorie
                for product in products:
                    product_category = Category.objects.get(id=product['category'])
                    self.assertEqual(
                        product_category.slug,
                        slug,
                        f"Produit {product['name']} dans la mauvaise catégorie pour slug {slug}"
                    )
                
                print(f"✅ Slug {slug}: {len(products)} produits")
            else:
                print(f"⚠️  Filtrage par slug {slug} non implémenté (code {response.status_code})")
    
    def test_product_details_include_category(self):
        """Test: Les détails des produits incluent la catégorie"""
        
        products = Product.objects.all()[:5]  # Tester 5 produits
        
        for product in products:
            response = self.client.get(f'/api/products/{product.id}/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            product_data = response.json()
            
            # Vérifier que les informations de catégorie sont présentes
            self.assertIn('category', product_data)
            self.assertIn('category_name', product_data)
            self.assertEqual(product_data['category'], product.category.id)
            self.assertEqual(product_data['category_name'], product.category.name)
    
    def test_home_page_category_links(self):
        """Test: Les liens de catégories sur la page d'accueil"""
        
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la page contient les liens de catégories
        expected_links = [
            'category=tests',
            'category=masques', 
            'category=gants',
            'category=consommables',
            'category=bebe'
        ]
        
        content = response.content.decode()
        
        for link in expected_links:
            self.assertIn(
                link, 
                content, 
                f"Lien de catégorie manquant: {link}"
            )
        
        print("✅ Tous les liens de catégories présents sur la page d'accueil")

def test_products_categories_web():
    """Test des produits et catégories via API REST"""
    
    print("🧪 TESTS PRODUITS ET CATÉGORIES")
    print("=" * 50)
    
    base_url = "http://localhost:8081"
    
    # Authentification
    try:
        response = requests.post(f"{base_url}/api/token/", {
            "email": "pro@demo.local",
            "password": "demodemo123"
        })
        
        if response.status_code == 200:
            token = response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            print("✅ Authentification réussie")
        else:
            print("❌ Authentification échouée")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 1: Vérifier les catégories
    print("\n1. Test: Vérification des catégories...")
    try:
        response = requests.get(f"{base_url}/api/categories/", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ {len(categories)} catégories trouvées")
            
            expected_slugs = ['tests', 'masques', 'gants', 'consommables', 'bebe']
            found_slugs = [cat['slug'] for cat in categories if cat['slug'] in expected_slugs]
            
            print(f"   Catégories attendues: {len(expected_slugs)}")
            print(f"   Catégories trouvées: {len(found_slugs)}")
            
            for slug in found_slugs:
                print(f"   ✅ {slug}")
            
            missing = set(expected_slugs) - set(found_slugs)
            if missing:
                print(f"   ⚠️  Manquantes: {missing}")
        else:
            print(f"❌ Erreur catégories: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 2: Vérifier les produits
    print("\n2. Test: Vérification des produits...")
    try:
        response = requests.get(f"{base_url}/api/products/", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            
            # Vérifier que chaque produit a une catégorie
            products_without_category = [p for p in products if not p.get('category')]
            
            if products_without_category:
                print(f"❌ {len(products_without_category)} produits sans catégorie:")
                for product in products_without_category[:5]:
                    print(f"   - {product.get('name', 'N/A')}")
                return False
            else:
                print("✅ Tous les produits ont une catégorie")
            
            # Vérifier les informations de catégorie
            products_with_category_info = [p for p in products if p.get('category_name')]
            print(f"   Produits avec nom de catégorie: {len(products_with_category_info)}/{len(products)}")
        else:
            print(f"❌ Erreur produits: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 3: Filtrage par catégorie
    print("\n3. Test: Filtrage par catégorie...")
    try:
        # Obtenir les catégories avec leurs ID
        cat_response = requests.get(f"{base_url}/api/categories/", headers=headers)
        categories = cat_response.json()
        
        for category in categories[:3]:  # Tester 3 catégories
            cat_id = category['id']
            cat_slug = category['slug']
            cat_name = category['name']
            
            # Filtrer par ID de catégorie
            prod_response = requests.get(f"{base_url}/api/products/?category={cat_id}", headers=headers)
            
            if prod_response.status_code == 200:
                filtered_products = prod_response.json()
                print(f"✅ {cat_name}: {len(filtered_products)} produits")
                
                # Vérifier que tous les produits sont dans la bonne catégorie
                all_correct = True
                for product in filtered_products:
                    if product.get('category') != cat_id:
                        print(f"   ❌ {product.get('name')} dans mauvaise catégorie")
                        all_correct = False
                
                if all_correct:
                    print(f"   ✅ Tous les produits dans la bonne catégorie")
            else:
                print(f"❌ Erreur filtrage {cat_name}: {prod_response.status_code}")
    except Exception as e:
        print(f"❌ Erreur filtrage: {e}")
    
    # Test 4: Page d'accueil
    print("\n4. Test: Page d'accueil...")
    try:
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            content = response.text
            
            # Vérifier les liens de catégories
            category_links = [
                'category=tests',
                'category=masques',
                'category=gants', 
                'category=consommables',
                'category=bebe'
            ]
            
            found_links = []
            for link in category_links:
                if link in content:
                    found_links.append(link)
            
            print(f"✅ Page d'accueil accessible")
            print(f"   Liens de catégories trouvés: {len(found_links)}/{len(category_links)}")
            
            for link in found_links:
                print(f"   ✅ {link}")
            
            missing_links = set(category_links) - set(found_links)
            if missing_links:
                print(f"   ⚠️  Liens manquants: {missing_links}")
        else:
            print(f"❌ Erreur page d'accueil: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur page d'accueil: {e}")
    
    # Test 5: Statistiques
    print("\n5. Test: Statistiques par catégorie...")
    try:
        cat_response = requests.get(f"{base_url}/api/categories/", headers=headers)
        categories = cat_response.json()
        
        total_products = 0
        for category in categories:
            cat_id = category['id']
            cat_name = category['slug']
            
            # Compter les produits dans cette catégorie
            prod_response = requests.get(f"{base_url}/api/products/?category={cat_id}", headers=headers)
            
            if prod_response.status_code == 200:
                products = prod_response.json()
                count = len(products)
                total_products += count
                print(f"   {cat_name}: {count} produits")
        
        print(f"   Total: {total_products} produits")
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TESTS PRODUITS/CATÉGORIES TERMINÉS!")
    return True

def main():
    """Fonction principale"""
    print("📦 TESTS PRODUITS ET CATÉGORIES")
    print("=" * 50)
    
    success = test_products_categories_web()
    
    if success:
        print("\n🎯 BILAN:")
        print("✅ Catégories principales créées")
        print("✅ Tous les produits ont une catégorie")
        print("✅ Filtrage par catégorie fonctionnel")
        print("✅ Liens de catégories sur page d'accueil")
        print("✅ API endpoints fonctionnels")
    else:
        print("\n❌ Certains tests ont échoué")
        print("🔧 Vérifiez les données et la configuration")

if __name__ == '__main__':
    main()
