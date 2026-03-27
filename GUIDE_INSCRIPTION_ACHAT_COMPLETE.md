# 🎯 Guide Complet: De l'Inscription à l'Achat - IMPLEMENTATION

## 📖 Table des Matières
1. [Vue Générale](#vue-générale)
2. [Fonctionnalités Implémentées](#fonctionnalités-implémentées)
3. [Phase 1: Enregistrement](#phase-1-enregistrement)
4. [Phase 2: Connexion](#phase-2-connexion)
5. [Phase 3: Shopping](#phase-3-shopping)
6. [Phase 4: Achat avec Vérification Stock](#phase-4-achat-avec-vérification-stock)
7. [Exemples Concrets](#exemples-concrets)

---

## 🚀 Fonctionnalités Implémentées

### ⭐ Système de Likes (J'aime)
- **Modèle**: `ProductLike` avec contrainte unique (produit, utilisateur)
- **API Endpoints**:
  - `POST /api/products/{id}/like/` - Ajouter/retirer un like (toggle)
- **Compteur**: Champ `user_likes` sur le modèle Product
- **Interface Admin**: `ProductLikeAdmin` pour gestion
- **Comportement**: Un utilisateur ne peut liker qu'une fois par produit

### 💬 Système de Recommandations
- **Modèle**: `ProductRecommendation` avec contrainte unique (produit, utilisateur)
- **API Endpoints**:
  - `POST /api/products/{id}/recommend/` - Basculer recommandation (toggle)
  - `POST /api/products/{id}/ai_recommend/` - Recommandation IA
  - `GET /api/products/{id}/recommendations/` - Lister recommandations
- **Compteur**: Champ `user_recommendations` sur le modèle Product
- **Interface Admin**: `ProductRecommendationAdmin` 
- **Comportement**: Toggle (ajouter/retirer en un clic)

### ⭐⭐⭐⭐⭐ Système de Notation (Rating)
- **Modèle**: `ProductRating` avec choix 1-5 étoiles, contrainte unique
- **API Endpoints**:
  - `POST /api/products/{id}/rate/` - Noter un produit (1-5 étoiles)
  - `POST /api/products/{id}/unrate/` - Retirer la note
  - `GET /api/products/{id}/ratings/` - Voir toutes les notes
- **Calcul**: Moyenne automatique avec `get_average_rating()` 
- **Interface Admin**: `ProductRatingAdmin` 
- **Affichage**: Étoiles dans le catalogue

### 🚚 Auto-Livraison Automatique
- **Logique**: Commandes CONFIRMED → SHIPPED après 30 minutes
- **Champ**: `auto_shipped_at` sur le modèle Order
- **Déclencheur**: Commande management `auto_update_order_status`
- **Simulation**: Pour démonstration du workflow

### 🏷️ Filtrage par Catégorie
- **Backend**: Paramètre GET `category=id` dans l'API
- **Frontend Catalogue**: Boutons rapides avec icônes (Tests, Masques, Gants, Bébé, Consommables)
- **Page Accueil**: Grille Bento avec liens vers catégories
- **Images**: Mapping correct des images statiques

### 📋 Formulaire Checkout Complet
- **🧍‍♂️ Informations utilisateur**: Téléphone ⭐, Email (optionnel)
- **📍 Adresse**: Ville ⭐, Commune (optionnel), Adresse détaillée ⭐, Code postal (optionnel)
- **🚚 Livraison**: Domicile (défaut), Point relais (optionnel)

### 🛠️ Commandes de Peuplement Base de Données
- **`seed_demo.py`**: 60+ produits avec catégories étendues
- **`add_ratings`**: 15 notations utilisateur (1-5 étoiles)
- **`add_recommendations`**: 12 recommandations utilisateur
- **`create_specific_categories`**: Catégories spécifiques et produits
- **`auto_update_order_status`**: Auto-livraison automatique

### 🔧 Interfaces d'Administration
- **ProductLikeAdmin**: Gestion des likes utilisateur
- **ProductRecommendationAdmin**: Gestion des recommandations
- **ProductRatingAdmin**: Gestion des notations
- **OrderAdmin**: Gestion complète des commandes

### 🔄 Migrations Base de Données
- **0007**: Ajout champs Order + ProductRating
- **0008**: Ajout ProductRecommendation + compteurs Product

---

## 📊 Vue Générale

```
                          ┌─────────────────────────────┐
                          │    USER (Utilisateur)      │
                          └─────────────────────────────┘
                          │
                          ├──────────────────────────────┐
                          │                              │
                    🆕 NOUVEAU USER            ✓ USER EXISTANT
                          │                              │
                          ↓                              ↓
                    [INSCRIPTION]             [CONNEXION]
                          │                              │
                    1. Email?                  1. Email?
                    2. Password?               2. Password?
                    3. Nom?                    ↓
                          │            ✅ Token JWT généré
                          ↓                      │
            ✅ User créé en auth-service         │
                          │                      │
                          └──────────────┬───────┘
                                         │
                                   ✅ AUTHENTIFIÉ
                                         │
                                         ↓
                             ┌────────────────────┐
                             │ ACCÈS AU CATALOGUE │
                             └────────────────────┘
                                         │
                                    SHOPPING
                                         │
                     ┌───────────────────┴────────────────┐
                     │                                    │
                ✅ AJOUTER AU PANIER          ✅ CONSULTER PANIER
                     │                                    │
                     └───────────────────┬────────────────┘
                                         │
                                         ↓
                              ┌────────────────────┐
                              │ VALIDER COMMANDE   │
                              └────────────────────┘
                                         │
                                         ↓
                          🔍 VÉRIFIER STOCK SUFFISANT?
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                  ✅ OUI              ❌ NON              (Erreur)
                    │                    │                    │
                    ↓                    ↓                    ↓
            📉 DÉCRÉMENTER       ❌ REJETER          ⚠️ AFFICHER
              STOCK              COMMANDE           ERREUR
                    │
                    ↓
          💾 ENREGISTRER COMMANDE
                    │
                    ↓
          📨 NOTIFIER (RabbitMQ)
                    │
                    ↓
         	   ✅ SUCCÈS
```

---

## Phase 1: Enregistrement

### 📝 Flux Détaillé

```
┌────────────────────────────────────┐
│  🌐 web.localhost/inscription/     │  ← Step 1: Utilisateur accède
└────────────────────────────────────┘
                    │
                    ↓
      ┌─────────────────────────────────┐
      │  Formulaire HTML affiché         │
      │                                 │
      │  [Email:]          john@ex.com   │
      │  [Password:]       ••••••••      │
      │  [Confirm Pwd:]    ••••••••      │
      │  [Nom Complet:]    John Doe     │
      │                                 │
      │  [Bouton] S'inscrire            │
      └─────────────────────────────────┘
                    │
                    ↓ POST /inscription/
            ┌──────────────────┐
            │  Web-UI Vérifie   │
            └──────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    VALIDE?              INVALIDE?
         │                     │
         ✅                    ❌
         │                     │
         ↓                     ↓
    Continue          Affiche Erreur
                      • Password < 8?
                      • Passwords ≠?
                      • Email vide?
                    │
                    ↑
         └─────── Retour form ────────┘

                    ↓
        ┌───────────────────────────────┐
        │  POST /api/users/register/    │
        │  Vers Auth-Service            │
        └───────────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │  Auth-Service Vérifie         │
        │  UserRegisterSerializer       │
        └───────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    VALIDE?              INVALIDE?
         │                     │
         ✅                    ❌
         │                     │
         ↓                     ↓
    Crée User          Email Déjà Existant?
    Hash Password      Password < 8?
         │                     │
         ↓                     ↓
    INSERT INTO        Retourne Erreur 400
    users_user         {"detail": "..."}
         │                     │
         └──────────┬──────────┘
                    │
                    ↓
    ✅ User Créé en Base de Données
            auth_db
            
            Table: users_user
            ┌────────────────────────────┐
            │ id  │ email  │ password_hash│
            ├────────────────────────────┤
            │ 1   │john@ex │ pbkdf2$...  │
            └────────────────────────────┘
                    │
                    ↓
    Redirection: /connexion/
```

### 💾 Données Créées en Base

```sql
-- Table: auth.users_user
INSERT INTO users_user (email, password, first_name, USERNAME_FIELD, role, is_active)
VALUES (
  'john@example.com',                    -- email
  'pbkdf2_sha256$390000$...$...',       -- password HASÉ (jamais en clair)
  'John Doe',                           -- first_name
  'john@example.com',                   -- username = email
  'PRO',                                -- role
  TRUE                                  -- is_active
);
```

---

## Phase 2: Connexion

### 🔐 Flux Détaillé

```
┌────────────────────────────────────┐
│  🌐 web.localhost/connexion/       │  ← Step 1: Utilisateur accède
└────────────────────────────────────┘
                    │
                    ↓
      ┌─────────────────────────────────┐
      │  Formulaire HTML affiché         │
      │                                 │
      │  [Email:]          john@ex.com   │
      │  [Password:]       ••••••••      │
      │                                 │
      │  [Bouton] Se Connecter          │
      └─────────────────────────────────┘
                    │
                    ↓ POST /connexion/
            ┌──────────────────┐
            │  Web-UI Récupère  │
            │  Email + Password │
            └──────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │  POST /api/token/             │
        │  → Auth-Service               │
        └───────────────────────────────┘
        
        Payload:
        {
          "email": "john@example.com",
          "password": "MyPassword123"
        }
                    │
                    ↓
        ┌───────────────────────────────┐
        │  Auth-Service Vérifie         │
        │  RoleTokenObtainPairView      │
        └───────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    VALIDE?              INVALIDE?
         │                     │
    Email existe?        Email N'existe pas?
    Password correct?    Password incorrect?
         │                     │
         ✅                    ❌
         │                     ↓
         ↓              HTTP 401 Unauthorized
    Générer JWT         {
         │              "detail": "No active account..."
         ↓              }
    Signer Token              │
    + role + email            ↓
         │              Web-UI Affiche:
         ↓              "E-mail ou mot de passe incorrect"
    Retourner
             │
             ↓
    ┌─────────────────────────────────┐
    │  Response JSON                  │
    ├─────────────────────────────────┤
    │ {                               │
    │   "access": "eyJ0eXAi...",      │← JWT Token
    │   "refresh": "eyJ0eXAi...",     │← Refresh Token
    │   "role": "PRO",                │← Role (ADMIN/PRO/PHARMACY)
    │   "email": "john@example.com"   │← Email
    │ }                               │
    └─────────────────────────────────┘
             │
             ↓
    Web-UI Stocke en Session
    request.session["access"] = "eyJ0eXAi..."
             │
             ↓
    Message: "Connexion réussie."
             │
             ↓
    Redirection: /catalogue/
             │
             ↓
    ✅ USER CONNECTÉ
```

### 🔐 Contenu du JWT Token (Décodé)

```json
{
  "token_type": "access",
  "exp": 1234567890,           // Expiration (5 min par défaut)
  "iat": 1234567890,           // Émis à
  "jti": "abc123...",          // ID unique
  "user_id": 1,                // ID utilisateur
  "email": "john@example.com", // Email
  "role": "PRO"                // Role (PRO, ADMIN, PHARMACY)
}
```

---

## Phase 3: Shopping

### 🛍️ Flux Détaillé

```
┌────────────────────────────────────┐
│  ✅ USER CONNECTÉ & AUTHENTIFIÉ   │
│  JWT Token en session              │
└────────────────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │  GET /catalogue/              │
        │  Avec Header Authorization:   │
        │  Bearer eyJ0eXAi...          │
        └───────────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │  GET /api/products/           │
        │  (Catalog-API)                │
        └───────────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │  Catalog-API Valide Token     │
        │  & Récupère Produits          │
        └───────────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │  Retourne Liste Produits      │
        ├───────────────────────────────┤
        │ [                             │
        │   {                           │
        │     "id": 1,                  │
        │     "name": "Paracétamol",    │
        │     "price": 5.99,            │
        │     "stock": 10,  ← IMPORTANT │
        │     "sku": "PARA-500-001",    │
        │     "user_likes": 5,           │← LIKES
        │     "average_rating": 4.5,     │← RATING
        │     "user_recommendations": 3, │← RECOMMENDATIONS
        │     "is_liked_by_user": false,│← USER STATUS
        │     "is_recommended_by_user": true│
        │   },                          │
        │   { ... }                     │
        │ ]                             │
        └───────────────────────────────┘
                    │
                    ↓
     ┌──────────────────────────────────┐
     │  Web-UI Affiche Catalogue         │
     │                                  │
     │  ┌────────────────────────────┐  │
     │  │ Paracétamol 500mg          │  │
     │  │ Prix: 5.99€                │  │
     │  │ Stock: ✅ 10 disponibles   │  │
     │  │ ⭐ 4.5 (15 notes)          │  │← RATING
     │  │ ❤️ 5 likes                 │  │← LIKES
     │  │ 🎯 3 recommandations      │  │← RECOMMENDATIONS
     │  │                            │  │
     │  │ [Ajouter au Panier] ← Click│  │
     │  └────────────────────────────┘  │
     │                                  │
     │  ┌────────────────────────────┐  │
     │  │ Ibuprofène 400mg           │  │
     │  │ Prix: 3.99€                │  │
     │  │ Stock: ✅ 25 disponibles   │  │
     │  │                            │  │
     │  │ [Ajouter au Panier] ← Click│  │
     │  └────────────────────────────┘  │
     └──────────────────────────────────┘
                    │
              User Clique
              "Ajouter au Panier"
                    │
                    ↓
        ┌───────────────────────────────┐
        │  POST /panier/ajouter/1/      │
        │  (Web-UI - Client-Side)       │
        └───────────────────────────────┘
                    │
                    ↓
        Panier en Session:
        {
          "1": 1,  ← Produit ID 1, Qté 1
          "2": 1   ← Produit ID 2, Qté 1
        }
                    │
                    ↓
        Message: "Produit ajouté au panier."
                    │
                    ↓
        Redirection: /panier/
                    │
                    ↓
     ┌──────────────────────────────────┐
     │  Affichage Panier                │
     │                                  │
     │  ┌────────────────────────────┐  │
     │  │ Paracétamol 500mg          │  │
     │  │ Quantité: [1] ✓            │ ← modifier ici
     │  │ Total: 5.99€               │  │
     │  │ [Retirer]                  │  │
     │  └────────────────────────────┘  │
     │                                  │
     │  ┌────────────────────────────┐  │
     │  │ Ibuprofène 400mg           │  │
     │  │ Quantité: [1] ✓            │  │
     │  │ Total: 3.99€               │  │
     │  │ [Retirer]                  │  │
     │  └────────────────────────────┘  │
     │                                  │
     │  Total Estimé: 9.98€             │
     │                                  │
     │  [Valider la Commande] ← Click   │
     └──────────────────────────────────┘
```

---

## Phase 4: Achat avec Vérification Stock

### 💳 Flux Critique

```
User Clique "Valider la Commande"
                    │
                    ↓
        ┌───────────────────────────────┐
        │  POST /commander/             │
        │  (Web-UI)                     │
        └───────────────────────────────┘
                    │
                    ├─ Panier = {1: 1, 2: 1}
                    │
                    ↓
        Prépare Payload:
        {
          "lines": [
            {
              "product_id": 1,
              "quantity": 1
            },
            {
              "product_id": 2,
              "quantity": 1
            }
          ],
          "phone": "0123456789",
          "email": "test@example.com",
          "city": "Alger",
          "commune": "El Harrach",
          "detailed_address": "123 Rue de la Liberté",
          "postal_code": "16000",
          "delivery_method": "domicile"
        }
                    │
                    ↓
        ┌───────────────────────────────┐
        │  POST /api/orders/            │
        │  (Catalog-API)                │
        │  + JWT Token                  │
        └───────────────────────────────┘
                    │
                    ↓
    🔄 Démarrer Transaction Atomique
    BEGIN TRANSACTION;
                    │
                    ↓
    ┌───────────────────────────────────┐
    │ 🔍 BOUCLE: Pour chaque produit   │
    └───────────────────────────────────┘
                    │
     ┌──────────────┴──────────────┐
     │                              │
   Produit 1            Produit 2
   ID = 1               ID = 2
   Qté = 1              Qté = 1
     │                    │
     ↓                    ↓
    ┌──────────────────┐ ┌──────────────────┐
    │ SELECT stock     │ │ SELECT stock     │
    │ FROM product     │ │ FROM product     │
    │ WHERE id = 1     │ │ WHERE id = 2     │
    │ FOR UPDATE ← Lock│ │ FOR UPDATE ← Lock│
    └──────────────────┘ └──────────────────┘
        stock = 10          stock = 25
     │                    │
     ↓                    ↓
    ┌──────────────────┐ ┌──────────────────┐
    │ Vérifier: stock  │ │ Vérifier: stock  │
    │ >= qty ?         │ │ >= qty ?         │
    │ 10 >= 1 ?        │ │ 25 >= 1 ?        │
    └──────────────────┘ └──────────────────┘
         ✅ OUI               ✅ OUI
     │                    │
     ↓                    ↓
    ┌──────────────────┐ ┌──────────────────┐
    │ INSERT orderline │ │ INSERT orderline │
    │ (order_id, prod, │ │ (order_id, prod, │
    │  qty, price)     │ │  qty, price)     │
    └──────────────────┘ └──────────────────┘
     │                    │
     ↓                    ↓
    ┌──────────────────┐ ┌──────────────────┐
    │ UPDATE product   │ │ UPDATE product   │
    │ stock = stock - 1│ │ stock = stock - 1│
    │ 10 - 1 = 9 ✅   │ │ 25 - 1 = 24 ✅  │
    └──────────────────┘ └──────────────────┘
     │                    │
     └──────────────┬─────┘
                    │
                    ↓
    ✅ Toutes les vérifications OK
                    │
                    ↓
    ┌──────────────────────────────────┐
    │ Calculer Remise (Volume)         │
    │ Subtotal: 9.98€                  │
    │ Remise: -5% = -0.50€             │
    │ Total: 9.48€                     │
    └──────────────────────────────────┘
                    │
                    ↓
    ┌──────────────────────────────────┐
    │ INSERT INTO order (              │
    │   auth_user_id = 1,              │
    │   status = "PENDING",            │
    │   subtotal = 9.98,               │
    │   discount_percent = 5,          │
    │   total = 9.48,                  │
    │   phone = "0123456789",         │← NEW
    │   email = "test@example.com",    │← NEW
    │   city = "Alger",                 │← NEW
    │   commune = "El Harrach",         │← NEW
    │   detailed_address = "123 Rue...",│← NEW
    │   postal_code = "16000",         │← NEW
    │   delivery_method = "domicile",  │← NEW
    │   created_at = NOW()             │
    │ ) RETURNING id;                  │
    │                                  │
    │ Order ID: 42 ✅                  │
    └──────────────────────────────────┘
                    │
                    ↓
    COMMIT TRANSACTION;  ← Tout confirmé!
                    │
                    ↓
    ✅ SUCCÈS COMPLET
    - Order créé
    - Stock décrémenté
    - Remises appliquées
    - Informations complètes enregistrées
                    │
                    ↓
    Publier Message RabbitMQ:
    {
      "order_id": 42,
      "user_id": 1,
      "total": 9.48,
      "timestamp": "2026-03-24T10:30:00Z"
    }
                    │
                    ↓
    Worker Notification reçoit
    → Envoie email au client ✅
                    │
                    ↓
    ┌──────────────────────────────────┐
    │  Response Web-UI                 │
    ├──────────────────────────────────┤
    │ {                                │
    │   "id": 42,                      │
    │   "status": "PENDING",           │
    │   "total": 9.48,                 │
    │   "phone": "0123456789",         │
    │   "city": "Alger",               │
    │   "lines": [                     │
    │     {"product_id": 1, "qty": 1}, │
    │     {"product_id": 2, "qty": 1}  │
    │   ]                              │
    │ }                                │
    └──────────────────────────────────┘
                    │
                    ↓
    Message: "Commande enregistrée...
             Une notification a été envoyée..."
                    │
                    ↓
    Redirection: /commandes/
                    │
                    ↓
    ✅ Commande visible dans l'historique
```

### 🚨 Scénario d'Erreur: Stock Insuffisant

```
User Essaie de Commander 15 Paracétamol
(Mais stock = 10 seulement)
                    │
                    ↓
    BEGIN TRANSACTION;
                    │
                    ↓
    SELECT stock FROM product WHERE id = 1
    FOR UPDATE;
    
    stock = 10
                    │
                    ↓
    ✅ Vérifier: 10 >= 15 ?
           ❌ NON!
                    │
                    ↓
    raise ValidationError(
      "Stock insuffisant pour Paracétamol"
    )
                    │
                    ↓
    ROLLBACK TRANSACTION;  ← Tout annulé!
                    │
                    ↓
    ❌ ERREUR
    - Order NOT créé
    - Stock INCHANGÉ (toujours 10)
                    │
                    ↓
    HTTP 400 Bad Request
    {
      "lines": "Stock insuffisant pour Paracétamol"
    }
                    │
                    ↓
    Web-UI reçoit erreur
                    │
                    ↓
    Affiche: "Stock insuffisant pour Paracétamol"
                    │
                    ↓
    Redirection: /panier/
                    │
                    ↓
    ⚠️ User peut corriger la quantité et réessayer
```

---

## 📋 Exemples Concrets

### Exemple 1: Achat Réussi

```
AVANT:
  Paracétamol (ID=1): stock = 10
  Ibuprofène (ID=2): stock = 25

USER:
  1. S'inscrit: john@example.com / MyPass123
  2. Se connecte
  3. Ajoute au panier: 3x Paracétamol, 2x Ibuprofène
  4. Remplit formulaire checkout complet
  5. Valide commande

VÉRIFICATIONS:
  ✅ Paracétamol: 10 >= 3 ? OUI
  ✅ Ibuprofène: 25 >= 2 ? OUI

RÉSULTATS:
  ✅ Commande créée: ID=42
  ✅ Paracétamol: stock = 10 - 3 = 7
  ✅ Ibuprofène: stock = 25 - 2 = 23
  ✅ Total: (5.99 * 3) + (3.99 * 2) = 17.97€
  ✅ Remise 5%: 17.97 * 0.95 = 17.07€
  ✅ Email de confirmation envoyé
  ✅ Informations livraison enregistrées

BASE DE DONNÉES APRÈS:
  Table: catalog_product
  ┌────────────────────┐
  │ ID │ name │ stock  │
  ├────────────────────┤
  │ 1  │Para  │ 7 ←✅  │
  │ 2  │Ibu   │ 23 ←✅ │
  └────────────────────┘

  Table: catalog_order
  ┌──────────────────────────────────────────────────────────┐
  │ ID │ user_id │ total │ status │ phone      │ city     │
  ├──────────────────────────────────────────────────────────┤
  │ 42 │ 1       │ 17.07 │PENDING │0123456789 │ Alger    │
  └──────────────────────────────────────────────────────────┘
```

### Exemple 2: Achat Échoué (Stock Insuffisant)

```
AVANT:
  Antibiotique (ID=5): stock = 2

USER:
  1. Se connecte
  2. Ajoute au panier: 5x Antibiotique
  3. Valide commande

VÉRIFICATION:
  ✅ Antibiotique: 2 >= 5 ? ❌ NON!

RÉSULTATS:
  ❌ Commande REJETÉE
  ❌ Stock INCHANGÉ: 2
  ❌ Message d'erreur affiché
  ❌ User reste sur le panier

BASE DE DONNÉES APRÈS:
  Table: catalog_product
  ┌────────────────────┐
  │ ID │ name │ stock  │
  ├────────────────────┤
  │ 5  │Anti  │ 2 ← INCHANGÉ │
  └────────────────────┘

  Aucune order créée ❌
```

### Exemple 3: Race Condition (Simulée)

```
SCENARIO:
  Product stock = 5
  2 users achètent simultanément

TIMELINE:
  T1: User A SELECT stock = 5, FOR UPDATE (LOCK)
  T2: User B Essaie SELECT (ATTEND - bloqué)
  T3: User A Vérifie: 5 >= 3 ? ✅ OUI
  T4: User A UPDATE stock = 5 - 3 = 2
  T5: User A COMMIT
  T6: User B SELECT stock = 2 (LOCK LIBÉRÉ)
  T7: User B Vérifie: 2 >= 4 ? ❌ NON
  T8: User B ROLLBACK

RÉSULTAT:
  ✅ User A: Commande réussie, stock = 2
  ❌ User B: Commande rejetée, stock inchangé
  ✅ Pas de double-vente!
```

---

## ✅ Résumé des Garanties

| Aspect | Garantie | Preuve |
|--------|----------|--------|
| **Stock** | Jamais vendu plus que disponible | `if stock < qty: error` |
| **Authentification** | Password jamais en clair | PBKDF2 hash |
| **Atomicité** | Tout-ou-rien | `@transaction.atomic` |
| **Concurrence** | Pas de race condition | `select_for_update()` |
| **Notification** | Event-driven | RabbitMQ message |
| **Audit** | Traçabilité complète | Order history + Stock logs |
| **Sécurité** | JWT Token validation | Bearer token required |
| **Données** | Informations complètes | Formulaire checkout étendu |

---

## 🎓 À Retenir

```
┌─────────────────────────────────────────────────────┐
│                   LE FLUX COMPLET                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. INSCRIPTION + LOGIN                           │
│     └─ Email + Password hasé                      │
│     └─ JWT Token généré (avec role)               │
│                                                     │
│  2. SHOPPING                                       │
│     └─ Voir produits + stock (décrémenté)         │
│     └─ Ajouter/modifier panier (session)         │
│     └─ Likes, Ratings, Recommandations           │
│                                                     │
│  3. ACHAT                                          │
│     └─ Vérifier stock AVANT de décrémenter       │
│     └─ Décrémenter stock atomiquement             │
│     └─ Créer order & orderlines                   │
│     └─ Tout-ou-rien: transaction.atomic           │
│     └─ Formulaire checkout complet                 │
│                                                     │
│  4. NOTIFICATION                                   │
│     └─ RabbitMQ message envoyé                    │
│     └─ Worker notification traite                 │
│     └─ Email envoyé au client                     │
│                                                     │
│  5. AUTO-LIVRAISON                                 │
│     └─ PENDING → CONFIRMED → SHIPPED → DELIVERED  │
│     └─ Auto-update toutes les 5 minutes           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 DÉPLOIEMENT

### Commandes Essentielles

```bash
# 1. Migration
docker compose exec catalog-api python manage.py migrate

# 2. Peuplement base de données
docker compose exec catalog-api python manage.py seed_demo --reset
docker compose exec catalog-api python manage.py add_ratings
docker compose exec catalog-api python manage.py add_recommendations

# 3. Auto-livraison (toutes les 5 minutes)
docker compose exec catalog-api python manage.py auto_update_order_status

# 4. Tests complets
python test_complete_guide.py
```

### Vérification

```bash
# Vérifier tous les modèles
docker compose exec catalog-api python manage.py shell
>>> from apps.catalog.models import *
>>> Product.objects.count()
>>> Order.objects.count()
>>> ProductRating.objects.count()
>>> ProductLike.objects.count()
>>> ProductRecommendation.objects.count()
```

**🎉 SYSTÈME PRODUCTION-READY!**

---

## 📚 Documentation Technique

### API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/products/` | GET | Lister produits avec likes/ratings |
| `/api/products/{id}/like/` | POST | Like/Unlike (toggle) |
| `/api/products/{id}/rate/` | POST | Noter (1-5 étoiles) |
| `/api/products/{id}/unrate/` | POST | Supprimer note |
| `/api/products/{id}/recommend/` | POST | Recommander/Retirer |
| `/api/products/{id}/ai_recommend/` | POST | Recommandations IA |
| `/api/orders/` | POST | Créer commande |
| `/api/categories/` | GET | Lister catégories |

### Modèles de Données

```python
# Product
{
    "id": 1,
    "name": "Paracétamol 500mg",
    "price": "5.99",
    "stock": 10,
    "user_likes": 5,
    "average_rating": 4.5,
    "user_recommendations": 3,
    "is_liked_by_user": false,
    "is_recommended_by_user": true
}

# Order
{
    "id": 42,
    "status": "PENDING",
    "total": "17.07",
    "phone": "0123456789",
    "city": "Alger",
    "detailed_address": "123 Rue de la Liberté",
    "delivery_method": "domicile"
}
```

---

**✅ GUIDE COMPLET IMPLEMENTÉ ET FONCTIONNEL!**
