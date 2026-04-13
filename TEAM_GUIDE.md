# Guide du Travail en Équipe - Plateforme Pharm

Ce guide explique comment lancer la plateforme de manière distribuée sur plusieurs machines.

## 📋 Répartition des rôles

*   **Membre A (Master - Vous)** : Lance l'infrastructure (RabbitMQ, Traefik) + l'Interface Web (Web-UI).
*   **Membre B** : Lance le Service d'Authentification (Auth).
*   **Membre C** : Lance le Service Catalogue (Catalog).
*   **Membre D** : Lance le Service de Notifications (Worker).

---

## 🛠 Préparation : Le Réseau

1.  Connectez toutes les machines au **même réseau Wi-Fi**.
2.  Chaque membre doit trouver son adresse IP locale :
    *   **Mac/Linux** : `ifconfig` ou `ip addr`
    *   **Windows** : `ipconfig`
3.  Notez l'adresse IP du **Membre A (Master)**.

---

## 🚀 Étape 1 : Configuration (Tous les membres)

1.  Clonez le projet GitHub.
2.  Copiez le fichier `.env.team` vers un nouveau fichier nommé `.env` :
    ```bash
    cp .env.team .env
    ```
3.  Ouvrez `.env` et remplacez `192.168.1.XX` par l'IP réelle du **Membre A**.
4.  Remplissez `AUTH_IP` et `CATALOG_IP` avec les adresses IP des membres concernés.

---

## 🚀 Étape 2 : Lancement par Rôle

### Membre A (Master)
Lancez d'abord l'infrastructure puis le web :
```bash
docker compose -f deploy/docker-compose.core.yml up -d
docker compose -f deploy/docker-compose.web.yml up -d --build
```

### Membre B (Auth)
```bash
docker compose -f deploy/docker-compose.auth.yml up -d --build
```

### Membre C (Catalog)
```bash
docker compose -f deploy/docker-compose.catalog.yml up -d --build
```

### Membre D (Worker)
```bash
docker compose -f deploy/docker-compose.worker.yml up -d --build
```

---

## 👨‍🏫 Accès Professeur

Pour que le professeur puisse accéder à la plateforme :
1.  Il doit être sur le même Wi-Fi.
2.  Il tape simplement l'IP du **Membre A** dans son navigateur :
    `http://192.168.1.XX`

---

## ⚠️ Notes Importantes
*   **Pare-feu** : Vérifiez que vos pare-feu (Firewall) acceptent les connexions entrantes sur les ports 80, 8000, 8001 et 5672.
*   **Ordre** : Le Membre A doit lancer le `core.yml` en premier pour que RabbitMQ soit prêt.
