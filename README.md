# Marketplace pharmacie (style MarketPharm) — architecture microservices

Projet de démonstration : UI proche d’une marketplace B2B type [MarketPharm](https://marketpharm.fr/) (catalogue pro, panier, remises volume), avec les contraintes **API REST**, **JWT + rôles**, **UI qui consomme l’API**, **RabbitMQ**, **Consul**, **Traefik** et **un conteneur par service** (équivalent « un serveur » en démo).

> **Version Django** : le code utilise **Django 4.2 LTS** (recommandé). Django 2.x est en fin de vie et non compatible avec des versions récentes de Python ; pour un rendu académique, indiquez que la stack est alignée sur les exigences fonctionnelles (REST, JWT, etc.) avec une version maintenue.

## Services

| Service | Rôle |
|--------|------|
| **traefik** | Reverse proxy / load balancer (routage par `Host`) |
| **consul** | Registre / découverte (`:8500`, UI) |
| **rabbitmq** | File de messages (exchange `marketpharm`, clé `order.created`) |
| **postgres-auth** | Base du service auth |
| **postgres-catalog** | Base du catalogue / commandes |
| **auth-service** | JWT (`/api/token/`, refresh), utilisateurs, rôles `ADMIN` / `PHARMACY` / `PRO` |
| **catalog-api** | CRUD + métier : `/api/products/`, `/api/categories/`, `/api/patients/`, `/api/orders/` |
| **notification-worker** | Consommateur asynchrone (simulation notification commande) |
| **web-ui** | Application web classique (templates Django) consommant l’API avec le jeton en session |

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Linux containers)
- Ajouter dans `C:\Windows\System32\drivers\etc\hosts` :

```text
127.0.0.1 web.localhost api.localhost auth.localhost
```

## Démarrage

```bash
cd c:\Users\hiche\pharm
copy .env.example .env
docker compose up --build
```

Les ports peuvent être mappés autrement dans `docker-compose.yml` (ex. **8081** au lieu de 80). Adaptez les URLs :

- **Interface web** : `http://localhost:8081` (ou `:80` si vous mappez `80:80`)  
- **Traefik dashboard** : `http://localhost:8082` (si `8082:8080` est défini)  
- **Consul** : `http://localhost:8501` (si `8501:8500`)  
- **RabbitMQ management** : `http://localhost:15673` (si `15673:15672`) (`guest` / `guest` par défaut)

### Si ça ne démarre pas (Windows)

1. **`exec /app/entrypoint.sh: no such file or directory`** : fins de ligne Windows (CRLF) dans `entrypoint.sh`. Les Dockerfiles exécutent `sed` pour corriger ; refaites `docker compose build --no-cache`.
2. **`admin.E403` TEMPLATES** : corrigé dans `config/settings.py` (auth + catalogue) ; en cas d’image ancienne : `docker compose build --no-cache auth-service catalog-api`.
3. **Traefik 404 / routeurs en conflit** : les labels utilisent des noms uniques `pharm-web`, `pharm-api`, `pharm-auth`. Si un autre projet Docker expose les mêmes noms de routeur, arrêtez-le ou changez encore le préfixe.
4. **502 juste après `up`** : attendre quelques secondes que Gunicorn soit prêt, puis rafraîchir.

## Comptes de démonstration

Créés au démarrage du service `auth-service` :

| E-mail | Mot de passe | Rôle |
|--------|----------------|------|
| `pro@demo.local` | `demodemo123` | Professionnel |
| `admin@demo.local` | `adminadmin123` | Admin catalogue (JWT) |

## API (aperçu)

- Obtenir un jeton : `POST http://auth.localhost:8081/api/token/` (ajuster le port si besoin)  
  Corps JSON : `{"email":"pro@demo.local","password":"demodemo123"}`
- Catalogue : `GET http://api.localhost:8081/api/products/` (header `Authorization: Bearer <access>`)
- Commande : `POST http://api.localhost:8081/api/orders/` avec `{"lines":[{"product_id":1,"quantity":2}]}`

**Important** : `JWT_SIGNING_KEY` doit être **identique** entre `auth-service` et `catalog-api` (déjà le cas via `docker-compose.yml` / `.env`).

## Déploiement multi-serveurs

En production, chaque image peut être déployée sur une machine distincte : mêmes variables d’environnement, même réseau (VPN / VPC), instances enregistrées dans Consul, Traefik en frontal pointant vers les nœuds ou utilisant la découverte Consul selon votre maquette.

## Découverte Consul

Exemple après démarrage :

```bash
curl http://localhost:8500/v1/catalog/services
```

Les services enregistrent un health check HTTP sur `/health/`.
