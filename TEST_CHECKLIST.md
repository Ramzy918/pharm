# ✅ Checklist de Test - Stock & Authentification

## 🚀 Démarrer l'Application

```bash
cd c:\Users\hiche\pharm

# Démarrer les services avec Docker Compose
docker-compose up -d
```

Attendre quelques secondes pour que les services démarrent.

---

## 📝 Test 1: Inscription (Signup)

### Étape 1: Accéder à la page d'inscription
```
URL: http://web.localhost/inscription/
```

**Résultat attendu:**
- ✅ Formulaire affiche avec champs:
  - Nom complet
  - Email
  - Mot de passe
  - Confirmer mot de passe

### Étape 2: Tester avec données invalides

**Test A: Mot de passe trop court**
```
Email: test@example.com
Password: "abc123"  (moins de 8 caractères)
```

**Résultat attendu:** 
- ❌ Erreur s'affiche
- ❌ Compte NON créé

**Test B: Mots de passe ne correspondent pas**
```
Email: test@example.com
Password: "SecurePass123"
Confirm: "DifferentPass123"
```

**Résultat attendu:**
- ❌ Erreur "Les mots de passe ne correspondent pas"

### Étape 3: S'inscrire avec données valides

```
Email: john.doe@test.com
Nom complet: John Doe
Password: MyPassword123
Confirm: MyPassword123
```

**Résultat attendu:**
- ✅ Message: "Inscription réussie! Vous pouvez vous connecter."
- ✅ Redirection vers page `/connexion/`
- ✅ Compte créé en base de données

---

## 🔐 Test 2: Connexion (Login)

### Étape 1: Accéder à la page de connexion
```
URL: http://web.localhost/connexion/
```

**Résultat attendu:**
- ✅ Formulaire avec:
  - Email
  - Mot de passe

### Étape 2: Tester avec mauvaises données

**Test A: Email inexistant**
```
Email: nonexistent@test.com
Password: MyPassword123
```

**Résultat attendu:**
- ❌ Erreur: "E-mail ou mot de passe incorrect."

**Test B: Mot de passe incorrect**
```
Email: john.doe@test.com  (doit exister du Test 1)
Password: WrongPassword
```

**Résultat attendu:**
- ❌ Erreur: "E-mail ou mot de passe incorrect."

### Étape 3: Se connecter avec données correctes

```
Email: john.doe@test.com
Password: MyPassword123
```

**Résultat attendu:**
- ✅ Message: "Connexion réussie."
- ✅ Redirection vers `/catalogue/`
- ✅ Utilisateur peut voir les produits
- ✅ Token JWT stocké en session

---

## 📦 Test 3: Gestion du Stock

### Prérequis
- ✅ Être connecté (Test 2 réussi)
- ✅ Au moins 1 produit en catalogue avec stock > 0

### Étape 1: Vérifier le stock initial

**Action:**
```
1. Aller à /catalogue/
2. Trouver un produit (ex: "Paracétamol 500mg")
3. Noter le stock actuel
```

**Résultat attendu:**
- ✅ Stock affiché (ex: "Stock: 10")

### Étape 2: Ajouter au panier moins que le stock

**Scénario: Produit a 10 unités, on en commande 3**

**Action:**
```
1. Cliquer sur "Ajouter au panier"
2. Aller au panier
3. Modifier la quantité à 3
4. Cliquer "Valider la commande"
```

**Résultat attendu:**
- ✅ Commande créée
- ✅ Message: "Commande enregistrée."
- ✅ Redirection vers `/commandes/`
- ✅ Nouvelle commande visible

**Vérification en base de données:**
```bash
# Connecter à la base PostgreSQL
psql -U catalog -d catalog_db -p 5432 -h localhost

# Vérifier le stock
SELECT id, name, stock FROM catalog_product WHERE name = 'Paracétamol 500mg';

# Avant: stock = 10
# Après: stock = 7 ✅
```

### Étape 3: Essayer de commander plus que disponible

**Scénario: Produit a 7 unités, on en demande 10**

**Action:**
```
1. Ajouter le même produit 10 fois au panier
2. Cliquer "Valider la commande"
```

**Résultat attendu:**
- ❌ Erreur: "Stock insuffisant pour Paracétamol 500mg"
- ❌ Commande rejetée
- ✅ Stock inchangé (7)
- ✅ Redirection vers panier

---

## 🔄 Test 4: Flux Complet (Bout en Bout)

### Étape 1: S'inscrire
```
1. POST /inscription/ avec données valides
2. ✅ Compte créé
3. ✅ Redirection login
```

### Étape 2: Se connecter
```
1. POST /connexion/
2. ✅ JWT Token généré
3. ✅ Redirection catalogue
```

### Étape 3: Acheter
```
1. GET /catalogue/ (voir produits)
2. POST /panier/ajouter/1/ (ajouter produit)
3. GET /panier/ (voir panier)
4. POST /commander/ (passer commande)
5. ✅ Stock décrémenté
```

### Étape 4: Vérifier AdminPanel
```
1. Se déconnecter
2. Créer compte admin:
   - Email: admin@test.com
   - Role: ADMIN (via shell Django)
3. Se connecter en tant qu'admin
4. Aller à /admin/
5. ✅ Dashboard visible
6. Cliquer sur "Gestion des Produits"
7. ✅ Voir le produit avec stock mis à jour
```

---

## 🛠️ Debugging

### Si l'enregistrement échoue

```bash
# Vérifier les logs auth-service
docker logs auth-service

# Vérifier la base de données
psql -U auth -d auth_db
SELECT * FROM users_user;
```

### Si la connexion ne fonctionne pas

```bash
# Vérifier les logs
docker logs auth-service

# Tester l'endpoint manuellement
curl -X POST http://auth.localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@test.com","password":"MyPassword123"}'

# Vous devriez recevoir:
{
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi...",
  "role": "PRO",
  "email": "john.doe@test.com"
}
```

### Si le stock ne décrémente pas

```bash
# Vérifier les logs catalog-api
docker logs catalog-api

# Vérifier la commande en base
psql -U catalog -d catalog_db

SELECT o.id, ol.quantity, p.name, p.stock 
FROM catalog_order o
JOIN catalog_orderline ol ON o.id = ol.order_id
JOIN catalog_product p ON ol.product_id = p.id
ORDER BY o.id DESC;
```

### Redémarrer les services

```bash
# Arrêter tout
docker-compose down

# Redémarrer
docker-compose up -d

# Vérifier l'état
docker-compose ps
```

---

## ✨ Résumé des Critères

| Test | Critère | Statut |
|------|---------|--------|
| T1.1 | Formulaire inscription s'affiche | ☐ |
| T1.2 | Validation mot de passe court | ☐ |
| T1.3 | Validation mots de passe différents | ☐ |
| T1.4 | Inscription réussie crée le compte | ☐ |
| T2.1 | Formulaire connexion s'affiche | ☐ |
| T2.2 | Email inexistant → erreur | ☐ |
| T2.3 | Mot de passe incorrect → erreur | ☐ |
| T2.4 | Login réussi → JWT généré | ☐ |
| T3.1 | Stock affiché en catalogue | ☐ |
| T3.2 | Achat < stock → Accepté | ☐ |
| T3.3 | Stock décrémenté après achat | ☐ |
| T3.4 | Achat > stock → Rejeté | ☐ |
| T4.1 | Inscription → Login → Achat | ☐ |
| T4.2 | Admin voit le stock mis à jour | ☐ |

**Cochez les cases au fur et à mesure des tests** ✅

---

## 📞 Besoin d'Aide?

Si un test échoue:
1. Vérifiez les logs: `docker logs <service>`
2. Vérifiez la base de données
3. Vérifiez la console du navigateur (F12)
4. Consultez [DOCUMENTATION_STOCK_AUTH.md](DOCUMENTATION_STOCK_AUTH.md)
