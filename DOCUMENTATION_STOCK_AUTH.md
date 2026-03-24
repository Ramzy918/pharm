# 📚 Documentation: Stock & Authentification

## 1️⃣ Gestion Automatique du Stock

### Fonctionnement

Quand un client **effectue un achat**, le processus est:

```
1. ✅ Client ajoute produits au panier (côté Web-UI)
   ↓
2. 📤 Client clique "Valider la commande"
   ↓
3. 🔍 Backend VÉRIFIE: Y a-t-il assez en stock?
   ├─ OUI  → Continuer
   └─ NON  → ❌ Erreur "Stock insuffisant"
   ↓
4. 📉 Backend DÉCRÉMENTE: stock = stock - quantité_achetée
   ↓
5. 💾 Backend ENREGISTRE la commande en base de données
   ↓
6. 📧 Backend envoie NOTIFICATION (RabbitMQ)
   ↓
7. ✅ Client reçoit confirmation
```

### Code Responsable

**Fichier:** [services/catalog-api/apps/catalog/serializers.py](../services/catalog-api/apps/catalog/serializers.py#L94-L105)

```python
@transaction.atomic  # ← Tout-ou-rien (important!)
def create(self, validated_data):
    for item in raw_lines:
        product = item["product"]
        qty = item["quantity"]
        
        # 1️⃣ VÉRIFICATION du stock
        p = Product.objects.select_for_update().get(pk=product.pk)
        if p.stock < qty:
            raise ValidationError(f"Stock insuffisant pour {p.name}")
        
        # 2️⃣ CRÉATION de la ligne de commande
        OrderLine.objects.create(
            order=order, 
            product=p, 
            quantity=qty, 
            unit_price=p.price
        )
        
        # 3️⃣ DÉCRÉMENTATION atomique du stock
        Product.objects.filter(pk=p.pk).update(
            stock=F("stock") - qty  # ← F() = opération DB directe
        )
```

### Points Clés

| Concept | Explication |
|---------|-----------|
| `@transaction.atomic` | Si une erreur survient, TOUT est annulé. Pas de commande sans décrémentation. |
| `select_for_update()` | Verrouille le produit pendant la vérification (évite les race conditions) |
| `F("stock") - qty` | L'opération se fait directement en BD = très rapide et sûr |
| `ValidationError` | Si stock insuffisant, la commande est rejetée |

### Exemple Concret

**Avant la commande:**
```
Produit: Paracétamol 500mg
Stock: 10 unités
```

**Client commande 7 unités:**
```
1. Vérification: 10 >= 7 ?  ✅ OUI
2. Stock après achat: 10 - 7 = 3 ✅
3. Commande enregistrée ✅
```

**Si client commande 15 unités:**
```
1. Vérification: 10 >= 15 ?  ❌ NON
2. ❌ Erreur: "Stock insuffisant pour Paracétamol 500mg"
3. Commande rejetée, stock inchangé (10)
```

---

## 2️⃣ Authentification (Inscription + Login)

### Inscription (Signup)

**Flux:**
1. Utilisateur visite `/inscription/`
2. Remplit formulaire: Email, Mot de passe (2x), Nom complet
3. Validation:
   - Email obligatoire et unique ✅
   - Mot de passe >= 8 caractères ✅
   - Les 2 mots de passe correspondent ✅
4. Si OK → Utilisateur créé en base de données (avec hash sécurisé)
5. Redirige vers `/connexion/`

**Fichier:** [services/web-ui/apps/shop/views.py](../services/web-ui/apps/shop/views.py#L47-L86) (`signup_view`)

**API:** `POST /api/users/register/`
```json
{
  "email": "john@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "role": "PRO"
}
```

### Connexion (Login)

**Flux:**
1. Utilisateur visite `/connexion/`
2. Remplit: Email, Mot de passe
3. Backend vérifie:
   - Email existe-t-il? ✅
   - Mot de passe correct? ✅
4. Si OK → Génère JWT Token (contient email + role)
5. Token stocké en session
6. Redirige vers `/catalogue/`

**Fichier:** [services/web-ui/apps/shop/views.py](../services/web-ui/apps/shop/views.py#L18-L35) (`login_view`)

**API:** `POST /api/token/`
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "PRO",
  "email": "john@example.com"
}
```

### Sécurité

**Points importants:**

1. **Hash de password:** Utilise Django's `set_password()`
   ```python
   user.set_password(password)  # Hash automatique avec PBKDF2
   ```

2. **JWT Token:** 
   - Contient: `user_id`, `email`, `role`
   - Signé avec SECRET_KEY
   - Expire automatiquement (défaut: 5 minutes pour access token)

3. **Validation stricte:**
   - Mot de passe >= 8 caractères
   - Email format vérifié
   - Email unique en base

### Tester l'Authentification

**1. Créer un compte:**
```bash
curl -X POST http://web.localhost/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "first_name": "Test User"
  }'
```

**2. Se connecter:**
```bash
curl -X POST http://auth.localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

**3. Utiliser le token pour accéder aux ressources protégées:**
```bash
curl -X GET http://api.localhost/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 3️⃣ Résumé des Fichiers Modifiés

| Fichier | Change | Raison |
|---------|--------|--------|
| `services/auth-service/apps/users/serializers.py` | ✅ Ajout `UserRegisterSerializer` | Password obligatoire à l'enregistrement |
| `services/auth-service/apps/users/views.py` | ✅ Utilise `UserRegisterSerializer` | Pour RegisterView |
| `services/web-ui/apps/shop/views.py` | ✅ Fonction `signup_view()` | Frontend pour l'enregistrement |
| `services/web-ui/apps/shop/urls.py` | ✅ Route `/inscription/` | Lien vers signup |
| `services/catalog-api/apps/catalog/serializers.py` | ✓ Inchangé | Stock déjà implémenté |

---

## 4️⃣ Workflow Complet: Utilisateur à Achat

```
1. INSCRIPTION
   └─ POST /inscription/
      └─ POST /api/users/register/
         └─ User créé en auth-service

2. LOGIN
   └─ POST /connexion/
      └─ POST /api/token/
         └─ JWT Token généré

3. SHOPPING
   └─ GET /catalogue/
      └─ GET /api/products/ (avec token)
         └─ Affiche produits

4. PANIER
   └─ POST /panier/ajouter/1/
      └─ Stocké en session

5. CHECKPOINT: Vérification Stock
   └─ GET /panier/
      └─ Affiche les articles

6. ACHAT
   └─ POST /commander/
      └─ POST /api/orders/
         ├─ ✅ Vérifier stock
         ├─ ✅ Créer OrderLine
         ├─ ✅ Décrémenter stock
         ├─ ✅ Calculer remise
         ├─ ✅ Enregistrer Order
         └─ ✅ Envoyer notification

7. CONFIRMATION
   └─ Redirection /commandes/
      └─ Affiste la nouvelle commande
```

---

## 5️⃣ Tests à Effectuer

### Test 1: Stock insuffisant ❌
```
1. Produit a 5 unités en stock
2. Client essaie d'en commander 10
3. Résultat: ❌ Erreur "Stock insuffisant"
4. Stock reste à 5 ✅
```

### Test 2: Achat normal ✅
```
1. Produit a 10 unités
2. Client commande 3
3. Résultat: ✅ Commande acceptée
4. Stock passe à 7 ✅
```

### Test 3: Inscription + Login
```
1. POST /inscription/ avec email+password
2. User créé ✅
3. POST /connexion/ avec même email+password
4. JWT Token généré ✅
```

### Test 4: Login échoué
```
1. POST /connexion/ avec mauvais password
2. Résultat: ❌ "Email ou mot de passe incorrect"
```

---

## 📞 Support

Si vous avez des questions, vérifiez:
- Logs auth-service: `docker logs auth-service`
- Logs catalog-api: `docker logs catalog-api`  
- Logs web-ui: `docker logs web-ui`
- Vérifier database: `psql -U auth -d auth_db` (pour auth) ou `psql -U catalog -d catalog_db` (pour catalog)
