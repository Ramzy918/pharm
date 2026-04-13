# Guide du Travail en Équipe - Plateforme Pharm

Ce guide explique comment lancer la plateforme de manière distribuée sur plusieurs machines le jour de la présentation.

## 📋 Répartition des rôles

*   **Membre A (Vous - Master)** : Lance l'infrastructure (`core`) et le service en arrière plan (`worker`). (2 terminaux)
*   **Membre B (Ami 1)** : Lance l'Interface Web (`web`). C'est LUI qui donne son IP au professeur.
*   **Membre C (Ami 2)** : Lance le Service d'Authentification (`auth`).
*   **Membre D (Ami 3)** : Lance le Service Catalogue (`catalog`).

---

## 🛠 Préparation : Le Réseau

Pour que les machines communiquent sans blocage, le plus sûr est d'utiliser le partage de connexion (Hotspot) :
1.  **Membre A (Vous)** activez le "Partage de connexion" sur votre iPhone.
2.  Vous, vos 3 amis, **ET le professeur** vous connectez tous au Wi-Fi de votre iPhone. (L'iPhone agit comme un grand routeur local).
3.  Chaque membre (Vous + 3 amis) doit trouver l'adresse IP de sa machine (attribuée par l'iPhone) :
    *   **Mac** : Touche *Option (⌥)* enfoncée + clic sur l'icône Wi-Fi (ex: `172.20.10.x`).
    *   **Windows** : Ouvrez CMD et tapez `ipconfig` (chercher Adresse IPv4).
4.  Écrivez ces 4 adresses IP sur un papier ou dans un groupe Messenger/WhatsApp pour les partager entre vous.

---

## 🚀 Étape 1 : Configuration (Tous les membres)

1.  Assurez-vous d'avoir fait `git pull` pour avoir la dernière version.
2.  Copiez le fichier `.env.team` en `.env` :
    ```bash
    cp .env.team .env
    ```
3.  Ouvrez `.env` et remplissez TOUTES les adresses IP avec celles trouvées à la préparation. **Tout le monde doit avoir le même fichier `.env`**.

---

## 🚀 Étape 2 : Lancement par Rôle

### Membre A (Master - Vous)
Lancez d'abord l'infrastructure puis le worker :
```bash
docker compose -f deploy/docker-compose.core.yml up -d
docker compose -f deploy/docker-compose.worker.yml up -d --build
```

### Membre B (Ami 1 - Web)
```bash
docker compose -f deploy/docker-compose.web.yml up -d --build
```

### Membre C (Ami 2 - Auth)
```bash
docker compose -f deploy/docker-compose.auth.yml up -d --build
```

### Membre D (Ami 3 - Catalog)
```bash
docker compose -f deploy/docker-compose.catalog.yml up -d --build
```

---

## 👨‍🏫 Accès Professeur

Pour que le professeur puisse accéder à la plateforme :
1.  Il doit être sur le Wi-Fi de votre iPhone.
2.  Il tape l'adresse **IP du Membre B (Ami 1)** dans son navigateur :
    `http://172.20.10.X` (Remplacez par l'IP de l'Ami 1)

---

## ⚠️ Notes Importantes
*   **Pare-feu** : Vérifiez que vos pare-feu (Firewall) sur Windows n'empêchent pas Docker de communiquer (accepter les réseaux privés).
*   L'ordre compte peu, mais le Membre A doit de préférence lancer l'infrastructure `core` en premier.
