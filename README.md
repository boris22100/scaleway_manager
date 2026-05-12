# 🚀 Scaleway Cloud Manager

Une interface d'administration multi-utilisateurs et souveraine pour piloter vos infrastructures Scaleway. Conçu pour la rapidité, la sécurité et la portabilité des données.

## 🛠 Spécifications Techniques

* **Core :** Python 3.9+ avec Streamlit (Interface réactive)
* **Base de données :** SQLite (Isolation totale par utilisateur)
* **Déploiement :** Docker & Docker Compose
* **Infrastructure cible :** Scaleway (Instances, DNS, Snapshots)
* **Provisioning :** Cloud-init (Installation auto de Docker & Docker Compose v2)

## ✨ Fonctionnalités Clés

### 📊 Monitoring & Backups
- Vue d'ensemble de vos instances par zone géographique (`fr-par-1`, `fr-par-2`).
- Gestion de la protection des instances (sécurité contre la suppression accidentelle).
- Création de snapshots (backups flash) en un clic.

### 🌐 Gestionnaire DNS Avancé
- Interface intuitive pour la gestion des records (A, CNAME, TXT, MX).
- **Import Bulk :** Synchronisation de zone entière par copier-coller de texte.
- **Export BIND :** Exportation universelle au format Zone File pour une portabilité totale.

### 🚀 Déploiement "One-Click"
- Bibliothèque de templates Docker Compose réutilisables.
- Provisioning automatique via Cloud-init sur des instances Debian Bookworm.

### 🔐 Sécurité & Multi-utilisateurs
- Système d'authentification avec hachage des mots de passe.
- **Gouvernance :** Le premier compte créé devient Admin et doit approuver manuellement les nouveaux utilisateurs.
- **Persistance :** Session persistante même après un rafraîchissement de page (F5).

---

## 🏗 Installation et Tutoriel

### 1. Pré-requis
* Docker et Docker Compose installés sur votre machine ou serveur.
* Un compte Scaleway avec Access Key et Secret Key.

### 2. Lancement rapide
Clonez le dépôt et lancez l'orchestration :

```bash
git clone [https://github.com/boris22100/scaleway_manager.git](https://github.com/ton-user/scaleway_manager.git)
cd scaleway_manager
docker-compose up --build -d
