# Enterprise Inventory Management System

Un système complet de gestion d'inventaire d'entreprise développé avec Django et Tailwind CSS.

## 🌟 Fonctionnalités

### Gestion des Produits
- ✅ Création, modification, suppression de produits
- ✅ Gestion des catégories et fournisseurs
- ✅ Suivi des stocks avec alertes de stock bas
- ✅ Upload d'images de produits
- ✅ Codes-barres et références uniques

### Gestion des Fournisseurs
- ✅ Base de données complète des fournisseurs
- ✅ Informations de contact et adresses
- ✅ Suivi des produits par fournisseur
- ✅ Statut actif/inactif

### Gestion du Stock
- ✅ Suivi en temps réel des quantités
- ✅ Mouvements de stock (entrées, sorties, ajustements)
- ✅ Seuils d'alerte personnalisables
- ✅ Historique complet des mouvements

### Gestion des Clients
- ✅ Base de données clients complète
- ✅ Informations personnelles et adresses
- ✅ Historique des commandes et ventes

### Gestion des Commandes
- ✅ Création et suivi des commandes
- ✅ Statuts multiples (en attente, confirmée, expédiée, livrée)
- ✅ Lignes de commande détaillées
- ✅ Calcul automatique des totaux

### Gestion des Ventes
- ✅ Point de vente avec différents modes de paiement
- ✅ Ventes comptoir et ventes clients
- ✅ Remises et calculs de totaux
- ✅ Factures imprimables

### Dashboard et Reporting
- ✅ Vue d'ensemble avec statistiques clés
- ✅ Alertes de stock bas
- ✅ Produits les plus vendus
- ✅ Chiffres de ventes

### Interface Publique
- ✅ Catalogue client avec recherche
- ✅ Filtrage par catégories
- ✅ Page d'accueil attrayante

## 🛠 Technologies Utilisées

- **Framework**: Django 5.2.4
- **Base de données**: SQLite (par défaut)
- **Frontend**: Tailwind CSS via CDN
- **Interface d'administration**: Django Admin personnalisée
- **Langues**: Python, HTML, CSS, JavaScript

## � Installation et Configuration

### Prérequis
- Python 3.8+
- pip (gestionnaire de packages Python)

### Installation

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd ggstock
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Sur macOS/Linux
   # ou
.venv\Scripts\activate     # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install django pillow
```

4. **Effectuer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Charger les données d'exemple**
```bash
python manage.py load_sample_data
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

## 🔑 Accès au système

### Compte administrateur
- **URL**: http://localhost:8000/admin/
- **Utilisateur**: `admin`
- **Mot de passe**: `admin123`

### Interface principale
- **Dashboard**: http://localhost:8000/
- **Catalogue client**: http://localhost:8000/client/

## 📋 Fonctionnalités détaillées

### Dashboard principal
- Statistiques en temps réel (produits, clients, fournisseurs)
- Alertes de stock bas
- Chiffre d'affaires du mois
- Commandes en attente
- Produits les plus vendus
- Derniers mouvements de stock
- Actions rapides

### Gestion des produits
- CRUD complet des produits
- Gestion des images
- Calcul automatique des marges
- Alertes de stock bas
- Filtres et recherche avancée
- Historique des mouvements

### Gestion du stock
- Vue d'ensemble du stock
- Valeur totale du stock
- Identification des produits en rupture
- Suivi des mouvements (entrées/sorties/ajustements)
- Seuils d'alerte personnalisables

### Interface client
- Catalogue public des produits
- Recherche et filtres
- Affichage par catégories
- Pagination
- Design responsive

## 🗂 Structure du projet

```
enterprise-inventory/
├── enterprise_inventory/        # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/                   # Application principale
│   ├── models.py               # Modèles de données
│   ├── views.py                # Vues
│   ├── admin.py                # Configuration admin
│   ├── forms.py                # Formulaires
│   ├── urls.py                 # URLs de l'app
│   └── management/commands/    # Commandes personnalisées
├── templates/                   # Templates HTML
│   ├── base.html
│   └── inventory/
└── media/                      # Fichiers uploadés
```

## 🔧 Configuration avancée

### Base de données
Pour utiliser PostgreSQL ou MySQL, modifiez `DATABASES` dans `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Variables d'environnement
Créez un fichier `.env` pour les configurations sensibles:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 📊 Modèles de données

### Produit
- Nom, référence, code-barres
- Catégorie et fournisseur
- Prix d'achat et de vente
- Quantité en stock et seuil d'alerte
- Image et description

### Client
- Informations personnelles complètes
- Adresse de livraison
- Historique des commandes et ventes

### Commande
- Numéro de commande unique
- Statut (en attente, confirmée, expédiée, livrée)
- Lignes de commande avec produits et quantités
- Calcul automatique du total

### Vente
- Numéro de vente unique
- Mode de paiement
- Lignes de vente avec produits et quantités
- Gestion des remises
- Mise à jour automatique du stock

## 🚀 Déploiement

### Production
1. Configurer les variables d'environnement
2. Utiliser une base de données production (PostgreSQL/MySQL)
3. Configurer les fichiers statiques avec `collectstatic`
4. Utiliser un serveur web (Nginx + Gunicorn)

### Docker (optionnel)
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos modifications
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème:
1. Vérifiez les logs Django
2. Consultez la documentation Django
3. Ouvrez une issue sur le repository

## 🔄 Mises à jour futures

- [ ] API REST avec Django REST Framework
- [ ] Système de notifications
- [ ] Rapports et analyses avancées
- [ ] Intégration e-commerce
- [ ] Application mobile
- [ ] Multi-entrepôts
- [ ] Codes-barres et QR codes
