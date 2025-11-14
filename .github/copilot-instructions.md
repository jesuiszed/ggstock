<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Enterprise Inventory Management System

Ce projet est un système de gestion d'inventaire d'entreprise développé avec Django et Tailwind CSS.

## Architecture du projet

- **Framework**: Django 5.2.4
- **Base de données**: SQLite (par défaut)
- **Frontend**: Tailwind CSS via CDN
- **Interface d'administration**: Django Admin customisée

## Structure des modèles

- **Categorie**: Classification des produits
- **Fournisseur**: Gestion des fournisseurs
- **Produit**: Produits avec gestion de stock
- **Client**: Base de données clients
- **Commande/LigneCommande**: Système de commandes
- **Vente/LigneVente**: Système de ventes
- **MouvementStock**: Traçabilité des mouvements de stock

## Fonctionnalités principales

1. **Gestion des produits**: CRUD complet avec images, catégories, prix
2. **Gestion du stock**: Suivi en temps réel, alertes de stock bas
3. **Gestion des fournisseurs**: Informations complètes des fournisseurs
4. **Gestion des clients**: Base de données clients avec historique
5. **Système de commandes**: Commandes avec statuts et lignes de commande
6. **Système de ventes**: Ventes avec différents modes de paiement
7. **Dashboard**: Vue d'ensemble avec statistiques
8. **Catalogue client**: Interface publique pour parcourir les produits

## Conventions de code

- Utiliser le français pour les labels et messages utilisateur
- Suivre les conventions Django pour la structure des vues et modèles
- Utiliser Tailwind CSS pour le styling avec des classes utilitaires
- Les templates héritent de `base.html`
- Les URLs sont organisées avec des namespaces (`inventory:`)

## Commandes utiles

- `python manage.py makemigrations` - Créer les migrations
- `python manage.py migrate` - Appliquer les migrations
- `python manage.py load_sample_data` - Charger des données d'exemple
- `python manage.py runserver` - Lancer le serveur de développement

## Configuration

- Variables de configuration dans `settings.py`
- URLs principales dans `enterprise_inventory/urls.py`
- URLs de l'app dans `inventory/urls.py`
- Templates dans le dossier `templates/`
