# 🚀 Scaleway Cloud Manager

Une interface d'administration multi-utilisateurs et souveraine pour piloter vos infrastructures **Scaleway**. Conçu pour la rapidité, la sécurité et la portabilité des données.

## 🛠 Spécifications Techniques

-   **Core :** Python 3.9+ avec **Streamlit** (Interface réactive)
-   **Base de données :** SQLite (Isolation totale par utilisateur et persistance)
-   **Déploiement :** Docker & Docker Compose
-   **Infrastructure cible :** Scaleway (Instances, DNS, Snapshots)
-   **Provisioning :** Cloud-init (Installation auto de Docker & Docker Compose v2 sur les instances déployées)

## ✨ Fonctionnalités Clés

### 📊 Monitoring & Backups

-   **Vue d'ensemble :** Visualisez vos instances par zone géographique (`fr-par-1`, `fr-par-2`).
-   **Protection :** Détection automatique du flag "protected" sur Scaleway (l'option de suppression disparaît pour éviter les erreurs).
-   **Snapshots :** Création de sauvegardes instantanées en un clic.

### 🌐 Gestionnaire DNS Avancé

-   **Interface intuitive :** Gestion simplifiée des enregistrements (`A`, `CNAME`, `TXT`, `MX`).
-   **Import Bulk :** Synchronisation de zones entières par copier-coller de texte brut.
-   **Export BIND :** Génération instantanée du fichier de zone au format BIND pour une portabilité totale.

### 🚀 Déploiement "One-Click"

-   Bibliothèque de templates **Docker Compose** réutilisables.
-   Choix du type d'instance (`PLAY2`, `DEV1`, etc.).
-   Provisioning automatique via **Cloud-init** sur Debian Bookworm.

## 🏗 Tutoriel d'Installation Complet

### 1\. Pré-requis

-   Git installé sur votre machine.
-   Docker & Docker Compose opérationnels.
-   Un compte Scaleway avec **Access Key**, **Secret Key** et **Project ID**.

### 2\. Récupération du projet

Ouvrez un terminal (PowerShell sur Windows ou Bash sur Linux) :

Bash

  

git clone https://github.com/boris22100/scaleway\_manager.git
cd scaleway\_manager

### 3\. Fichiers de configuration du projet

Assurez-vous que votre répertoire contient les fichiers suivants :

**Dockerfile**

Dockerfile

  

FROM python:3.9-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit requests pandas
COPY app.py .
RUN mkdir data
EXPOSE 8501
CMD \["streamlit", "run", "app.py", "--server.address=0.0.0.0"\]

**docker-compose.yml**

YAML

  

services:
  scw-manager:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    restart: unless-stopped

**.gitignore** _(Crucial pour la sécurité)_

Plaintext

  

data/
\*.db
\_\_pycache\_\_/
.venv/
.env

### 4\. Lancement de l'application

Lancez la construction et le démarrage du conteneur :

Bash

  

docker-compose up --build -d

L'interface est maintenant accessible sur : **http://localhost:8501**

## ⚙️ Configuration Initiale (Pas à pas)

### Étape 1 : Création du compte Admin

Lors du premier accès à l'interface :

1.  Allez sur l'onglet **"Créer un compte"**.
2.  Le tout premier utilisateur enregistré devient automatiquement **Administrateur** du système.
3.  Les utilisateurs suivants devront être approuvés manuellement par l'admin dans l'onglet **Gouvernance**.

### Étape 2 : Connexion & Persistance

-   **Validation :** Le formulaire est validé automatiquement en appuyant sur la touche **Entrée**.
-   **Navigation :** Grâce à la gestion des jetons de session, vous restez connecté même après un rafraîchissement de la page (**F5**).

### Étape 3 : Ajout de vos clés API

1.  Allez dans l'onglet **⚙️ Comptes**.
2.  Ajoutez un profil (ex: _"BoWiz Prod"_).
3.  Renseignez votre _Access Key_, _Secret Key_ et _Project ID_.
4.  Sélectionnez ce profil dans la barre latérale gauche pour activer la communication avec Scaleway.

### Étape 4 : Gestion DNS

1.  Allez dans l'onglet **🌐 DNS**.
2.  Cliquez sur l'un de vos domaines pour charger les records existants.
3.  Utilisez l'outil **"Importation Bulk"** pour ajouter plusieurs lignes d'un coup.
4.  Utilisez le bouton **"Générer Export BIND"** pour obtenir une sauvegarde texte complète prête à être migrée ailleurs.

## 🔐 Sécurité & Maintenance

-   **Souveraineté :** Toutes vos données (identifiants, templates, logs) sont stockées localement dans `data/manager.db`.
-   **Sauvegarde :** Pensez à sauvegarder régulièrement le fichier `manager.db`.
-   **Mise à jour :** Pour mettre à jour l'application, effectuez un `git pull` puis relancez `docker-compose up --build -d`.

_Développé par_ **_Boris Mallach_** _pour une gestion cloud simplifiée et souveraine._
