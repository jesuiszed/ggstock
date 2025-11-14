#!/usr/bin/env python3
"""
Script de configuration des données de laboratoire pour GGStock
Créé par l'IA Assistant pour configurer une plateforme de laboratoire africaine
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_inventory.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from inventory.models import Categorie, Fournisseur, Produit, Client
from users.models import User, Profile

def setup_categories():
    """Créer les catégories de laboratoire"""
    print("🧪 Création des catégories de laboratoire...")
    
    categories = [
        {
            'nom': 'Hématologie',
            'description': 'Équipements et consommables pour les analyses hématologiques - Numération globulaire, hémogramme, tests de coagulation'
        },
        {
            'nom': 'Biochimie', 
            'description': 'Équipements et réactifs pour les analyses biochimiques - Glycémie, urée, créatinine, enzymes hépatiques'
        },
        {
            'nom': 'Consommables',
            'description': 'Consommables généraux de laboratoire - Tubes, pipettes, gants, réactifs de base, solutions de nettoyage'
        }
    ]
    
    for cat_data in categories:
        categorie, created = Categorie.objects.get_or_create(
            nom=cat_data['nom'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"   ✅ Catégorie créée: {categorie.nom}")
        else:
            print(f"   ⚡ Catégorie existante: {categorie.nom}")

def setup_fournisseur():
    """Créer le fournisseur Zybio"""
    print("🏢 Création du fournisseur Zybio...")
    
    fournisseur, created = Fournisseur.objects.get_or_create(
        nom='Zybio',
        defaults={
            'contact_nom': 'Service Commercial Zybio',
            'email': 'commercial@zybio.com',
            'telephone': '+221 76 369 21 67',
            'adresse': 'Zone Industrielle de Diamniadio',
            'ville': 'Dakar',
            'code_postal': '12500',
            'pays': 'Sénégal',
            'notes': 'Fournisseur spécialisé dans les équipements de laboratoire médical en Afrique de l\'Ouest. Distributeur officiel d\'analyseurs d\'hématologie et de biochimie.'
        }
    )
    
    if created:
        print(f"   ✅ Fournisseur créé: {fournisseur.nom}")
    else:
        print(f"   ⚡ Fournisseur existant: {fournisseur.nom}")
        # Mettre à jour les informations
        fournisseur.telephone = '+221 76 369 21 67'
        fournisseur.ville = 'Dakar'
        fournisseur.pays = 'Sénégal'
        fournisseur.save()
        print("   📱 Informations de contact mises à jour")
    
    return fournisseur

def setup_produits(fournisseur):
    """Créer les 5 produits consommables pour analyseurs"""
    print("🔬 Création des produits consommables de laboratoire...")
    
    # Récupération des catégories
    hematologie = Categorie.objects.get(nom='Hématologie')
    biochimie = Categorie.objects.get(nom='Biochimie')
    consommables = Categorie.objects.get(nom='Consommables')
    
    produits = [
        {
            'nom': 'Kit Réactifs Hématologie CBC-5 DIFF',
            'reference': 'ZYB-HEM-001',
            'description': 'Kit de réactifs pour analyse hématologique complète avec formule leucocytaire 5 populations. Compatible avec analyseurs d\'hématologie Zybio série EOS. Contient : diluant, lysant, solution de nettoyage et contrôles qualité.',
            'categorie': hematologie,
            'quantite_stock': 5,
            'seuil_alerte': 2,
            'unite_mesure': 'Kit',
            'actif': True,
            'notes': 'Stockage recommandé entre 2-8°C. Durée de vie : 12 mois. Kit pour 1000 tests.'
        },
        {
            'nom': 'Cartouches Biochimie Multi-Paramètres',
            'reference': 'ZYB-BIO-002', 
            'description': 'Cartouches de réactifs secs pour analyses biochimiques multi-paramètres. Panel complet : glucose, urée, créatinine, ALAT, ASAT, bilirubine totale, cholestérol, triglycérides, protéines totales.',
            'categorie': biochimie,
            'quantite_stock': 5,
            'seuil_alerte': 2,
            'unite_mesure': 'Boîte de 25',
            'actif': True,
            'notes': 'Compatible analyseur Zybio série ELite. Stockage température ambiante. 200 tests par cartouche.'
        },
        {
            'nom': 'Tubes EDTA Vacutainer 3ml',
            'reference': 'ZYB-CON-003',
            'description': 'Tubes de prélèvement sous vide avec anticoagulant EDTA K3 pour analyses hématologiques. Bouchon violet, stériles, usage unique. Conformes normes ISO 13485.',
            'categorie': consommables,
            'quantite_stock': 5,
            'seuil_alerte': 2,
            'unite_mesure': 'Boîte de 100',
            'actif': True,
            'notes': 'Conservation à température ambiante. Agitation douce nécessaire après prélèvement.'
        },
        {
            'nom': 'Solution de Contrôle Qualité Tri-Level',
            'reference': 'ZYB-QC-004',
            'description': 'Solution de contrôle qualité 3 niveaux (bas, normal, élevé) pour validation des performances analytiques en hématologie et biochimie. Matrice similaire au sang humain.',
            'categorie': consommables,
            'quantite_stock': 5,
            'seuil_alerte': 2,
            'unite_mesure': 'Kit de 3 flacons',
            'actif': True,
            'notes': 'Stockage 2-8°C. Homogénéiser avant usage. Traçabilité NIST disponible.'
        },
        {
            'nom': 'Cuvettes Spectrophotométrie Jetables',
            'reference': 'ZYB-CUV-005',
            'description': 'Cuvettes semi-micro en polystyrène pour spectrophotométrie UV-Visible. Volume 1.5ml, trajet optique 10mm. Compatibles avec tous analyseurs biochimiques standards.',
            'categorie': consommables,
            'quantite_stock': 5,
            'seuil_alerte': 2,
            'unite_mesure': 'Boîte de 500',
            'actif': True,
            'notes': 'Usage unique. Transparence optimale de 340 à 700nm. Emballage individuel stérile.'
        }
    ]
    
    for prod_data in produits:
        produit, created = Produit.objects.get_or_create(
            reference=prod_data['reference'],
            defaults={
                'nom': prod_data['nom'],
                'description': prod_data['description'],
                'categorie': prod_data['categorie'],
                'fournisseur': fournisseur,
                'quantite_stock': prod_data['quantite_stock'],
                'seuil_alerte': prod_data['seuil_alerte'],
                'unite_mesure': prod_data['unite_mesure'],
                'actif': prod_data['actif'],
                'notes': prod_data['notes'],
                # Prix laissés à 0 comme demandé
                'prix_achat': Decimal('0.00'),
                'prix_vente': Decimal('0.00')
            }
        )
        
        if created:
            print(f"   ✅ Produit créé: {produit.nom} ({produit.reference})")
        else:
            # Mettre à jour la quantité stock à 5
            produit.quantite_stock = 5
            produit.save()
            print(f"   ⚡ Produit existant mis à jour: {produit.nom}")

def setup_client_laboratoire():
    """Créer un client laboratoire type"""
    print("🏥 Création d'un client laboratoire...")
    
    client, created = Client.objects.get_or_create(
        email='laboratoire.central@hopital-dakar.sn',
        defaults={
            'prenom': 'Dr. Aminata',
            'nom': 'DIOP',
            'entreprise': 'Laboratoire Central - Hôpital Principal de Dakar',
            'telephone': '+221 33 824 56 78',
            'adresse': 'Avenue Cheikh Anta Diop, Fann',
            'ville': 'Dakar',
            'code_postal': '12000',
            'pays': 'Sénégal',
            'actif': True,
            'notes': 'Laboratoire de référence pour les analyses médicales. Spécialisé en hématologie, biochimie et microbiologie. Équipe de 15 techniciens qualifiés.'
        }
    )
    
    if created:
        print(f"   ✅ Client créé: {client.get_full_name()} - {client.entreprise}")
    else:
        print(f"   ⚡ Client existant: {client.get_full_name()}")

def setup_admin_user():
    """Créer un utilisateur administrateur"""
    print("👤 Configuration de l'utilisateur administrateur...")
    
    try:
        admin_user, created = User.objects.get_or_create(
            username='admin_lab',
            defaults={
                'email': 'admin@ggstock-lab.sn',
                'first_name': 'Administrateur',
                'last_name': 'Laboratoire',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('AdminLab2025!')
            admin_user.save()
            
            # Créer le profil
            profile, profile_created = Profile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'role': 'admin',
                    'telephone': '+221 76 369 21 67',
                    'adresse': 'Dakar, Sénégal'
                }
            )
            
            print(f"   ✅ Administrateur créé: {admin_user.username}")
            print(f"   🔑 Mot de passe: AdminLab2025!")
        else:
            print(f"   ⚡ Administrateur existant: {admin_user.username}")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la création de l'admin: {e}")

def main():
    """Fonction principale d'initialisation"""
    print("🚀 INITIALISATION DE LA PLATEFORME DE LABORATOIRE GGSTOCK")
    print("=" * 60)
    print("🌍 Configuration pour l'Afrique - Dakar, Sénégal")
    print("🔬 Spécialisé en équipements de laboratoire médical")
    print("=" * 60)
    
    try:
        # Exécution des étapes de configuration
        setup_categories()
        print()
        
        fournisseur = setup_fournisseur()
        print()
        
        setup_produits(fournisseur)
        print()
        
        setup_client_laboratoire()
        print()
        
        setup_admin_user()
        print()
        
        print("=" * 60)
        print("✅ CONFIGURATION TERMINÉE AVEC SUCCÈS!")
        print("🌟 La plateforme est maintenant configurée pour un laboratoire africain")
        print()
        print("📋 RÉSUMÉ DE LA CONFIGURATION:")
        print(f"   • {Categorie.objects.count()} catégories de laboratoire")
        print(f"   • {Fournisseur.objects.count()} fournisseur(s) - Zybio Sénégal")
        print(f"   • {Produit.objects.count()} produits consommables")
        print(f"   • {Client.objects.count()} client(s) laboratoire")
        print(f"   • Configuration: Dakar, Sénégal (+221 76 369 21 67)")
        print()
        print("🎯 Prochaines étapes recommandées:")
        print("   1. Ajouter des images aux produits")
        print("   2. Personnaliser l'interface avec thème africain")
        print("   3. Configurer les prix si nécessaire")
        print("   4. Démarrer le serveur: python manage.py runserver")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ ERREUR LORS DE LA CONFIGURATION: {e}")
        print("🔍 Vérifiez que Django est correctement installé et configuré")

if __name__ == '__main__':
    main()
