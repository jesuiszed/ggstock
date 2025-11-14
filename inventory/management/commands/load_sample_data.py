from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import (
    Categorie, Fournisseur, Produit, Client, 
    Vente, LigneVente, MouvementStock
)
from decimal import Decimal
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Charge des données d\'exemple (appareils médicaux) dans la base de données'

    def handle(self, *args, **options):
        self.stdout.write('Début du chargement des données médicales...')

        # Créer un superutilisateur si nécessaire
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='System'
            )
            self.stdout.write(self.style.SUCCESS('Superutilisateur créé: admin/admin123'))

        # Catégories médicales
        categories_data = [
            {'nom': 'Imagerie médicale', 'description': 'Appareils d\'imagerie (IRM, scanner, etc.)'},
            {'nom': 'Surveillance', 'description': 'Moniteurs, tensiomètres, oxymètres'},
            {'nom': 'Chirurgie', 'description': 'Équipements pour blocs opératoires'},
            {'nom': 'Laboratoire', 'description': 'Analyseurs, centrifugeuses, microscopes'},
            {'nom': 'Soins', 'description': 'Pompes à perfusion, aspirateurs médicaux'},
        ]
        for cat_data in categories_data:
            cat, created = Categorie.objects.get_or_create(
                nom=cat_data['nom'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Catégorie créée: {cat.nom}')

        # Fournisseurs médicaux
        fournisseurs_data = [
            {
                'nom': 'MedTech France',
                'email': 'contact@medtech.fr',
                'telephone': '01 11 22 33 44',
                'adresse': '10 Rue de la Santé',
                'ville': 'Paris',
                'code_postal': '75012'
            },
            {
                'nom': 'BioMedical Solutions',
                'email': 'info@biomedical.fr',
                'telephone': '02 22 33 44 55',
                'adresse': '20 Avenue Pasteur',
                'ville': 'Lyon',
                'code_postal': '69003'
            },
            {
                'nom': 'SurgiPlus',
                'email': 'ventes@surgiplus.fr',
                'telephone': '03 33 44 55 66',
                'adresse': '30 Boulevard de l\'Hôpital',
                'ville': 'Marseille',
                'code_postal': '13005'
            },
        ]
        for fournisseur_data in fournisseurs_data:
            fournisseur, created = Fournisseur.objects.get_or_create(
                email=fournisseur_data['email'],
                defaults=fournisseur_data
            )
            if created:
                self.stdout.write(f'Fournisseur créé: {fournisseur.nom}')

        # Produits médicaux
        produits_data = [
            {
                'nom': 'Moniteur multiparamétrique',
                'reference': 'MED-001',
                'code_barre': '1000000000001',
                'description': 'Surveillance des signes vitaux en réanimation',
                'categorie': 'Surveillance',
                'fournisseur': 'MedTech France',
                'prix_achat': Decimal('1200.00'),
                'prix_vente': Decimal('1800.00'),
                'quantite_stock': 10,
                'seuil_alerte': 2
            },
            {
                'nom': 'Pompe à perfusion',
                'reference': 'MED-002',
                'code_barre': '1000000000002',
                'description': 'Administration contrôlée de médicaments',
                'categorie': 'Soins',
                'fournisseur': 'BioMedical Solutions',
                'prix_achat': Decimal('800.00'),
                'prix_vente': Decimal('1200.00'),
                'quantite_stock': 15,
                'seuil_alerte': 3
            },
            {
                'nom': 'Scanner médical',
                'reference': 'MED-003',
                'code_barre': '1000000000003',
                'description': 'Appareil d\'imagerie médicale haute résolution',
                'categorie': 'Imagerie médicale',
                'fournisseur': 'MedTech France',
                'prix_achat': Decimal('25000.00'),
                'prix_vente': Decimal('32000.00'),
                'quantite_stock': 2,
                'seuil_alerte': 1
            },
            {
                'nom': 'Microscope de laboratoire',
                'reference': 'MED-004',
                'code_barre': '1000000000004',
                'description': 'Microscope optique pour analyses biologiques',
                'categorie': 'Laboratoire',
                'fournisseur': 'BioMedical Solutions',
                'prix_achat': Decimal('500.00'),
                'prix_vente': Decimal('900.00'),
                'quantite_stock': 20,
                'seuil_alerte': 5
            },
            {
                'nom': 'Table d\'opération électrique',
                'reference': 'MED-005',
                'code_barre': '1000000000005',
                'description': 'Table réglable pour interventions chirurgicales',
                'categorie': 'Chirurgie',
                'fournisseur': 'SurgiPlus',
                'prix_achat': Decimal('7000.00'),
                'prix_vente': Decimal('9500.00'),
                'quantite_stock': 3,
                'seuil_alerte': 1
            }
        ]
        user = User.objects.first()
        for produit_data in produits_data:
            categorie = Categorie.objects.get(nom=produit_data['categorie'])
            fournisseur = Fournisseur.objects.get(nom=produit_data['fournisseur'])
            produit, created = Produit.objects.get_or_create(
                reference=produit_data['reference'],
                defaults={
                    'nom': produit_data['nom'],
                    'code_barre': produit_data.get('code_barre'),
                    'description': produit_data['description'],
                    'categorie': categorie,
                    'fournisseur': fournisseur,
                    'prix_achat': produit_data['prix_achat'],
                    'prix_vente': produit_data['prix_vente'],
                    'quantite_stock': produit_data['quantite_stock'],
                    'seuil_alerte': produit_data['seuil_alerte']
                }
            )
            if created:
                self.stdout.write(f'Produit créé: {produit.nom}')
                MouvementStock.objects.create(
                    produit=produit,
                    type_mouvement='ENTREE',
                    quantite=produit.quantite_stock,
                    quantite_avant=0,
                    quantite_apres=produit.quantite_stock,
                    motif='Stock initial',
                    utilisateur=user
                )

        # Clients (établissements de santé)
        clients_data = [
            {
                'nom': 'Hôpital Saint-Louis',
                'prenom': 'Service Achats',
                'email': 'achats@stlouis.fr',
                'telephone': '01 44 44 44 44',
                'adresse': '1 Avenue Claude Vellefaux',
                'ville': 'Paris',
                'code_postal': '75010'
            },
            {
                'nom': 'Clinique du Parc',
                'prenom': 'Direction',
                'email': 'direction@cliniqueparc.fr',
                'telephone': '04 72 00 00 00',
                'adresse': '15 Rue du Parc',
                'ville': 'Lyon',
                'code_postal': '69006'
            },
            {
                'nom': 'Centre Médical Provence',
                'prenom': 'Administration',
                'email': 'admin@cmprovence.fr',
                'telephone': '04 91 00 00 00',
                'adresse': '20 Boulevard National',
                'ville': 'Marseille',
                'code_postal': '13001'
            }
        ]
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            if created:
                self.stdout.write(f'Client créé: {client.nom_complet}')

        # Ventes d'exemple
        clients = Client.objects.all()
        produits = Produit.objects.all()
        for i in range(5):
            numero_vente = f'VTE-MED-{i+1:03d}'
            if not Vente.objects.filter(numero_vente=numero_vente).exists():
                vente = Vente.objects.create(
                    numero_vente=numero_vente,
                    client=random.choice(clients),
                    mode_paiement=random.choice(['ESPECES', 'CARTE', 'CHEQUE']),
                    utilisateur=user,
                    date_vente=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                for _ in range(random.randint(1, 2)):
                    produit = random.choice(produits)
                    quantite = random.randint(1, 2)
                    LigneVente.objects.create(
                        vente=vente,
                        produit=produit,
                        quantite=quantite,
                        prix_unitaire=produit.prix_vente
                    )
                    ancien_stock = produit.quantite_stock
                    produit.quantite_stock = max(0, produit.quantite_stock - quantite)
                    produit.save()
                    MouvementStock.objects.create(
                        produit=produit,
                        type_mouvement='SORTIE',
                        quantite=quantite,
                        quantite_avant=ancien_stock,
                        quantite_apres=produit.quantite_stock,
                        motif=f'Vente {vente.numero_vente}',
                        utilisateur=user
                    )
                vente.calculer_total()
                self.stdout.write(f'Vente créée: {vente.numero_vente}')

        self.stdout.write(self.style.SUCCESS('Données médicales chargées avec succès !'))
        self.stdout.write('Vous pouvez maintenant vous connecter avec:')
        self.stdout.write('  Utilisateur: admin')
        self.stdout.write('  Mot de passe: admin123')
