#!/usr/bin/env python3
"""
Script simple de configuration des données de laboratoire
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_inventory.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from inventory.models import Categorie, Fournisseur, Produit

print("🚀 Début de la configuration...")

# 1. Créer les catégories
print("Création des catégories...")
categories_data = [
    ('Hématologie', 'Analyses sanguines et hématologiques'),
    ('Biochimie', 'Analyses biochimiques et enzymatiques'), 
    ('Consommables', 'Consommables de laboratoire')
]

for nom, desc in categories_data:
    cat, created = Categorie.objects.get_or_create(nom=nom, defaults={'description': desc})
    print(f"  - {nom}: {'Créé' if created else 'Existant'}")

# 2. Créer le fournisseur Zybio
print("Création du fournisseur Zybio...")
fournisseur, created = Fournisseur.objects.get_or_create(
    nom='Zybio',
    defaults={
        'telephone': '+221 76 369 21 67',
        'ville': 'Dakar',
        'pays': 'Sénégal',
        'adresse': 'Dakar, Sénégal'
    }
)
print(f"  - Zybio: {'Créé' if created else 'Existant'}")

# 3. Mettre à jour les quantités existantes à 5 et supprimer les prix
print("Mise à jour des produits existants...")
produits_existants = Produit.objects.all()
for produit in produits_existants:
    produit.quantite_stock = 5
    produit.prix_achat = Decimal('0.00')
    produit.prix_vente = Decimal('0.00')
    produit.save()
    print(f"  - {produit.nom}: Quantité mise à jour (5), prix supprimés")

print("✅ Configuration terminée!")
print(f"Total catégories: {Categorie.objects.count()}")
print(f"Total fournisseurs: {Fournisseur.objects.count()}")
print(f"Total produits: {Produit.objects.count()}")
