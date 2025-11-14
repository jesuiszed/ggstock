from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from users.models import Profile
from .models import (
    Categorie, Fournisseur, Produit, Client as ClientModel, 
    Commande, LigneCommande, Vente, LigneVente, MouvementStock,
    Devis, LigneDevis, Prospect, NoteObservation, AppareilVendu, 
    InterventionSAV, TransfertStock
)


class CategorieModelTest(TestCase):
    """Tests pour le modèle Categorie"""
    
    def setUp(self):
        self.categorie = Categorie.objects.create(
            nom="Équipements Médicaux",
            description="Matériel médical de base"
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.categorie), "Équipements Médicaux")
    
    def test_unique_nom_constraint(self):
        with self.assertRaises(Exception):
            Categorie.objects.create(nom="Équipements Médicaux")
    
    def test_creation_date_auto_set(self):
        self.assertIsNotNone(self.categorie.date_creation)


class FournisseurModelTest(TestCase):
    """Tests pour le modèle Fournisseur"""
    
    def setUp(self):
        self.fournisseur = Fournisseur.objects.create(
            nom="MedTech Solutions",
            email="contact@medtech.fr",
            telephone="0123456789",
            adresse="123 Rue de la Santé",
            ville="Paris",
            code_postal="75001",
            pays="France"
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.fournisseur), "MedTech Solutions")
    
    def test_default_values(self):
        self.assertEqual(self.fournisseur.pays, "France")
        self.assertTrue(self.fournisseur.actif)
    
    def test_email_unique_constraint(self):
        with self.assertRaises(Exception):
            Fournisseur.objects.create(
                nom="Autre Fournisseur",
                email="contact@medtech.fr",
                telephone="0987654321",
                adresse="456 Autre Rue",
                ville="Lyon",
                code_postal="69001"
            )


class ProduitModelTest(TestCase):
    """Tests pour le modèle Produit"""
    
    def setUp(self):
        self.categorie = Categorie.objects.create(nom="Test Catégorie")
        self.fournisseur = Fournisseur.objects.create(
            nom="Test Fournisseur",
            email="test@fournisseur.fr",
            telephone="0123456789",
            adresse="Test Adresse",
            ville="Test Ville",
            code_postal="12345"
        )
        self.produit = Produit.objects.create(
            nom="Stéthoscope Digital",
            reference="STH-001",
            description="Stéthoscope électronique haute qualité",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("150.00"),
            prix_vente=Decimal("250.00"),
            quantite_stock=10,
            seuil_alerte=5
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.produit), "Stéthoscope Digital")
    
    def test_stock_bas_property(self):
        self.produit.quantite_stock = 3
        self.produit.save()
        self.assertTrue(self.produit.stock_bas())
    
    def test_reference_unique_constraint(self):
        with self.assertRaises(Exception):
            Produit.objects.create(
                nom="Autre Produit",
                reference="STH-001",  # Même référence
                categorie=self.categorie,
                fournisseur=self.fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("200.00")
            )
    
    def test_prix_validation(self):
        with self.assertRaises(ValidationError):
            produit = Produit(
                nom="Produit Test",
                reference="TEST-001",
                categorie=self.categorie,
                fournisseur=self.fournisseur,
                prix_achat=Decimal("-10.00"),  # Prix négatif
                prix_vente=Decimal("100.00")
            )
            produit.full_clean()


class ClientModelTest(TestCase):
    """Tests pour le modèle Client"""
    
    def setUp(self):
        self.client = ClientModel.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@email.fr",
            telephone="0123456789",
            adresse="123 Rue de la Paix",
            ville="Paris",
            code_postal="75001",
            entreprise="Clinique Saint-Jean"
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.client), "Dupont Jean")
    
    def test_nom_complet_property(self):
        self.assertEqual(self.client.nom_complet, "Dupont Jean")
    
    def test_email_unique_constraint(self):
        with self.assertRaises(Exception):
            ClientModel.objects.create(
                nom="Martin",
                prenom="Paul",
                email="jean.dupont@email.fr",  # Même email
                telephone="0987654321",
                adresse="456 Avenue Test",
                ville="Lyon",
                code_postal="69001"
            )


class DevisModelTest(TestCase):
    """Tests pour le modèle Devis"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="commercial",
            password="testpass123"
        )
        Profile.objects.create(
            user=self.user,
            role="COMMERCIAL_TERRAIN"
        )
        
        self.client = ClientModel.objects.create(
            nom="Test",
            prenom="Client",
            email="test@client.fr",
            telephone="0123456789",
            adresse="789 Rue du Test",
            ville="Marseille",
            code_postal="13001"
        )
        
        from datetime import date
        self.devis = Devis.objects.create(
            client=self.client,
            commercial=self.user,
            date_validite=date.today() + timedelta(days=30)
        )
    
    def test_string_representation(self):
        self.assertIn("DEV", str(self.devis))
        self.assertIn("Test Client", str(self.devis))
    
    def test_numero_devis_auto_generation(self):
        self.assertIsNotNone(self.devis.numero_devis)
        self.assertTrue(self.devis.numero_devis.startswith("DEV"))
    
    def test_date_expiration_calculation(self):
        expected_date = self.devis.date_creation.date() + timedelta(days=30)
        self.assertEqual(self.devis.date_expiration, expected_date)


class ProspectModelTest(TestCase):
    """Tests pour le modèle Prospect"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="commercial",
            password="testpass123"
        )
        
        self.prospect = Prospect.objects.create(
            nom_entreprise="Hôpital Général",
            nom_contact="Dr. Martin",
            email="dr.martin@hopital.fr",
            telephone="0123456789",
            commercial_assigne=self.user,
            statut="NOUVEAU",
            source="SALON_PROFESSIONNEL"
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.prospect), "Hôpital Général - Dr. Martin")
    
    def test_statut_choices(self):
        self.assertIn(self.prospect.statut, [choice[0] for choice in Prospect.STATUT_CHOICES])


class AppareilVenduModelTest(TestCase):
    """Tests pour le modèle AppareilVendu"""
    
    def setUp(self):
        # Créer les objets nécessaires
        self.categorie = Categorie.objects.create(nom="Test Catégorie")
        self.fournisseur = Fournisseur.objects.create(
            nom="Test Fournisseur",
            email="test@fournisseur.fr",
            telephone="0123456789",
            adresse="Test Adresse",
            ville="Test Ville",
            code_postal="12345"
        )
        self.produit = Produit.objects.create(
            nom="Échographe",
            reference="ECH-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("5000.00"),
            prix_vente=Decimal("8000.00")
        )
        self.client = ClientModel.objects.create(
            nom="Clinique",
            prenom="Test",
            email="clinique@test.fr",
            telephone="0123456789",
            adresse="123 Rue de la Clinique",
            ville="Paris",
            code_postal="75001"
        )
        self.user = User.objects.create_user(
            username="commercial",
            password="testpass123"
        )
        
        # Créer une vente
        self.vente = Vente.objects.create(
            numero_vente="VTE-2024-001",
            client=self.client,
            utilisateur=self.user,
            mode_paiement='CARTE',
            total=Decimal("8000.00")
        )
        
        self.appareil = AppareilVendu.objects.create(
            produit=self.produit,
            numero_serie="ECH001-2024-001",
            client=self.client,
            vente=self.vente,
            date_installation=date.today(),
            lieu_installation="Salle d'examen 1",
            prochaine_maintenance_preventive=date.today() + timedelta(days=365)
        )
    
    def test_string_representation(self):
        expected = f"Échographe (ECH001-2024-001) - Clinique Test"
        self.assertEqual(str(self.appareil), expected)
    
    def test_maintenance_due(self):
        # Test maintenance non due
        self.assertFalse(self.appareil.est_maintenance_due())
        
        # Test maintenance due
        self.appareil.prochaine_maintenance_preventive = date.today() - timedelta(days=1)
        self.appareil.save()
        self.assertTrue(self.appareil.est_maintenance_due())


class InterventionSAVModelTest(TestCase):
    """Tests pour le modèle InterventionSAV"""
    
    def setUp(self):
        # Créer les objets nécessaires
        self.user_tech = User.objects.create_user(
            username="technicien",
            password="testpass123"
        )
        Profile.objects.create(
            user=self.user_tech,
            role="TECHNICIEN"
        )
        
        self.categorie = Categorie.objects.create(nom="Test Catégorie")
        self.fournisseur = Fournisseur.objects.create(
            nom="Test Fournisseur",
            email="test@fournisseur.fr",
            telephone="0123456789",
            adresse="Test Adresse",
            ville="Test Ville",
            code_postal="12345"
        )
        self.produit = Produit.objects.create(
            nom="Scanner",
            reference="SCN-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("50000.00"),
            prix_vente=Decimal("80000.00")
        )
        self.client = ClientModel.objects.create(
            nom="Hôpital",
            prenom="Test",
            email="hopital@test.fr",
            telephone="0123456789",
            adresse="456 Avenue de l'Hôpital",
            ville="Lyon",
            code_postal="69001"
        )
        self.user_commercial = User.objects.create_user(
            username="commercial",
            password="testpass123"
        )
        self.vente = Vente.objects.create(
            numero_vente="VTE-2024-002",
            client=self.client,
            utilisateur=self.user_commercial,
            mode_paiement='VIREMENT',
            total=Decimal("80000.00")
        )
        
        self.appareil = AppareilVendu.objects.create(
            produit=self.produit,
            numero_serie="SCN001-2024-001",
            client=self.client,
            vente=self.vente,
            date_installation=date.today(),
            lieu_installation="Service Radiologie",
            prochaine_maintenance_preventive=date.today() + timedelta(days=365)
        )
        
        self.intervention = InterventionSAV.objects.create(
            type_intervention="PREVENTIVE",
            appareil=self.appareil,
            technicien=self.user_tech,
            date_prevue=datetime.now() + timedelta(days=7),
            duree_prevue=120,
            description="Maintenance préventive annuelle"
        )
    
    def test_string_representation(self):
        self.assertIn("INT", str(self.intervention))
        self.assertIn("Scanner", str(self.intervention))
    
    def test_numero_intervention_auto_generation(self):
        self.assertIsNotNone(self.intervention.numero_intervention)
        self.assertTrue(self.intervention.numero_intervention.startswith("INT"))
    
    def test_client_auto_assignation(self):
        # Le client devrait être automatiquement assigné depuis l'appareil
        self.assertEqual(self.intervention.client, self.appareil.client)


class TransfertStockModelTest(TestCase):
    """Tests pour le modèle TransfertStock"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="technicien",
            password="testpass123"
        )
        
        self.categorie = Categorie.objects.create(nom="Test Catégorie")
        self.fournisseur = Fournisseur.objects.create(
            nom="Test Fournisseur",
            email="test@fournisseur.fr",
            telephone="0123456789",
            adresse="Test Adresse",
            ville="Test Ville",
            code_postal="12345"
        )
        self.produit = Produit.objects.create(
            nom="Oxymètre",
            reference="OXY-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("50.00"),
            prix_vente=Decimal("80.00"),
            quantite_stock=100
        )
        
        self.transfert = TransfertStock.objects.create(
            produit=self.produit,
            quantite=10,
            lieu_origine="Dépôt Central",
            lieu_destination="Showroom Paris",
            demande_par=self.user,
            motif="Réapprovisionnement showroom"
        )
    
    def test_string_representation(self):
        self.assertIn("TRF", str(self.transfert))
        self.assertIn("Oxymètre", str(self.transfert))
    
    def test_numero_transfert_auto_generation(self):
        self.assertIsNotNone(self.transfert.numero_transfert)
        self.assertTrue(self.transfert.numero_transfert.startswith("TRF"))


# ========== TESTS DES VUES ==========

class DashboardViewTest(TestCase):
    """Tests pour les vues dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            role="MANAGER"
        )
    
    def test_dashboard_redirect_anonymous(self):
        """Test redirection pour utilisateur anonyme"""
        response = self.client.get(reverse('inventory:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_dashboard_access_authenticated(self):
        """Test accès au dashboard pour utilisateur connecté"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('inventory:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
    
    def test_dashboard_role_specific_content(self):
        """Test contenu spécifique au rôle dans le dashboard"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('inventory:dashboard'))
        self.assertContains(response, "dashboard_manager.html")


class ProduitViewTest(TestCase):
    """Tests pour les vues des produits"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            role="MANAGER"
        )
        
        self.categorie = Categorie.objects.create(nom="Test Catégorie")
        self.fournisseur = Fournisseur.objects.create(
            nom="Test Fournisseur",
            email="test@fournisseur.fr",
            telephone="0123456789",
            adresse="Test Adresse",
            ville="Test Ville",
            code_postal="12345"
        )
        self.produit = Produit.objects.create(
            nom="Produit Test",
            reference="TEST-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("100.00"),
            prix_vente=Decimal("150.00")
        )
    
    def test_produits_list_view(self):
        """Test de la vue liste des produits"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('inventory:produits_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Produit Test")
    
    def test_produit_detail_view(self):
        """Test de la vue détail d'un produit"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('inventory:produit_detail', kwargs={'pk': self.produit.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Produit Test")
    
    def test_produit_create_view(self):
        """Test de la vue création de produit"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('inventory:produit_create'))
        self.assertEqual(response.status_code, 200)
        
        # Test création via POST
        data = {
            'nom': 'Nouveau Produit',
            'reference': 'NEW-001',
            'categorie': self.categorie.pk,
            'fournisseur': self.fournisseur.pk,
            'prix_achat': '200.00',
            'prix_vente': '300.00',
            'quantite_stock': '50',
            'seuil_alerte': '10'
        }
        response = self.client.post(reverse('inventory:produit_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirection après création
        self.assertTrue(Produit.objects.filter(nom='Nouveau Produit').exists())


class DevisViewTest(TestCase):
    """Tests pour les vues des devis"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="commercial",
            password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            role="COMMERCIAL_TERRAIN"
        )
        
        self.client_model = ClientModel.objects.create(
            nom="Test",
            prenom="Client",
            email="test@client.fr",
            telephone="0123456789",
            adresse="101 Rue de la Paix",
            ville="Nice",
            code_postal="06000"
        )
    
    def test_devis_list_view(self):
        """Test de la vue liste des devis"""
        self.client.login(username="commercial", password="testpass123")
        response = self.client.get(reverse('inventory:devis_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_devis_create_view(self):
        """Test de la vue création de devis"""
        self.client.login(username="commercial", password="testpass123")
        response = self.client.get(reverse('inventory:devis_create'))
        self.assertEqual(response.status_code, 200)


class PermissionTest(TestCase):
    """Tests pour les permissions et les rôles"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer différents utilisateurs avec différents rôles
        self.manager = User.objects.create_user(
            username="manager",
            password="testpass123"
        )
        Profile.objects.create(user=self.manager, role="MANAGER")
        
        self.commercial_showroom = User.objects.create_user(
            username="commercial_showroom",
            password="testpass123"
        )
        Profile.objects.create(user=self.commercial_showroom, role="COMMERCIAL_SHOWROOM")
        
        self.commercial_terrain = User.objects.create_user(
            username="commercial_terrain",
            password="testpass123"
        )
        Profile.objects.create(user=self.commercial_terrain, role="COMMERCIAL_TERRAIN")
        
        self.technicien = User.objects.create_user(
            username="technicien",
            password="testpass123"
        )
        Profile.objects.create(user=self.technicien, role="TECHNICIEN")
    
    def test_manager_access_all(self):
        """Test que le manager a accès à tout"""
        self.client.login(username="manager", password="testpass123")
        
        # Test accès aux différentes sections
        urls_to_test = [
            'inventory:dashboard',
            'inventory:produits_list',
            'inventory:clients_list',
            'users:user_management'
        ]
        
        for url_name in urls_to_test:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [200, 302], f"Failed for {url_name}")
    
    def test_commercial_terrain_devis_access(self):
        """Test que le commercial terrain a accès aux devis"""
        self.client.login(username="commercial_terrain", password="testpass123")
        response = self.client.get(reverse('inventory:devis_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_commercial_showroom_no_devis_access(self):
        """Test que le commercial showroom n'a pas accès aux devis"""
        self.client.login(username="commercial_showroom", password="testpass123")
        response = self.client.get(reverse('inventory:devis_list'))
        # Devrait être redirigé ou avoir une erreur de permission
        self.assertNotEqual(response.status_code, 200)
    
    def test_technicien_intervention_access(self):
        """Test que le technicien a accès aux interventions"""
        self.client.login(username="technicien", password="testpass123")
        response = self.client.get(reverse('inventory:intervention_list'))
        self.assertEqual(response.status_code, 200)


# ========== TESTS D'INTÉGRATION ==========

class WorkflowIntegrationTest(TestCase):
    """Tests d'intégration pour les workflows complets"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="manager",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer les données de base
        self.categorie = Categorie.objects.create(nom="Équipements Médicaux")
        self.fournisseur = Fournisseur.objects.create(
            nom="MedSupply",
            email="contact@medsupply.fr",
            telephone="0123456789",
            adresse="123 Rue Médicale",
            ville="Paris",
            code_postal="75001"
        )
        self.produit = Produit.objects.create(
            nom="Défibrillateur",
            reference="DEF-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("1500.00"),
            prix_vente=Decimal("2500.00"),
            quantite_stock=5
        )
        self.client_model = ClientModel.objects.create(
            nom="Clinique",
            prenom="Moderne",
            email="contact@clinique.fr",
            telephone="0123456789",
            adresse="202 Boulevard de la Santé",
            ville="Toulouse",
            code_postal="31000",
            entreprise="Clinique Moderne SARL"
        )
    
    def test_complete_sales_workflow(self):
        """Test du workflow complet de vente"""
        self.client.login(username="manager", password="testpass123")
        
        # 1. Créer une vente
        vente_data = {
            'client': self.client_model.pk,
            'commercial': self.user.pk,
            'total': '2500.00'
        }
        response = self.client.post(reverse('inventory:vente_create'), vente_data)
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la vente a été créée
        vente = Vente.objects.filter(client=self.client_model).first()
        self.assertIsNotNone(vente)
        
        # 2. Vérifier que le stock a été mis à jour (si logique implémentée)
        # produit_updated = Produit.objects.get(pk=self.produit.pk)
        # self.assertEqual(produit_updated.quantite_stock, 4)
    
    def test_maintenance_workflow(self):
        """Test du workflow de maintenance"""
        self.client.login(username="manager", password="testpass123")
        
        # 1. Créer une vente pour avoir un appareil vendu
        vente = Vente.objects.create(
            numero_vente="VTE-2024-003",
            client=self.client_model,
            utilisateur=self.user,
            mode_paiement='CARTE',
            total=Decimal("2500.00")
        )
        
        # 2. Créer un appareil vendu
        appareil = AppareilVendu.objects.create(
            produit=self.produit,
            numero_serie="DEF001-2024-001",
            client=self.client_model,
            vente=vente,
            date_installation=date.today(),
            lieu_installation="Salle d'urgence",
            prochaine_maintenance_preventive=date.today() + timedelta(days=365)
        )
        
        # 3. Planifier une intervention
        intervention_data = {
            'type_intervention': 'PREVENTIVE',
            'appareil': appareil.pk,
            'technicien': self.user.pk,
            'date_prevue': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'duree_prevue': '120',
            'description': 'Maintenance préventive annuelle'
        }
        response = self.client.post(reverse('inventory:intervention_create'), intervention_data)
        # Vérifier que l'intervention a été créée
        intervention = InterventionSAV.objects.filter(appareil=appareil).first()
        self.assertIsNotNone(intervention)


# ========== TESTS DE PERFORMANCE ==========

class PerformanceTest(TestCase):
    """Tests de performance basiques"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer des données de test en volume
        self.categorie = Categorie.objects.create(nom="Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="Test Fournisseur",
            email="test@fournisseur.fr",
            telephone="0123456789",
            adresse="Test",
            ville="Test",
            code_postal="12345"
        )
        
        # Créer 100 produits pour tester la pagination
        for i in range(100):
            Produit.objects.create(
                nom=f"Produit {i}",
                reference=f"PROD-{i:03d}",
                categorie=self.categorie,
                fournisseur=self.fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("150.00")
            )
    
    def test_produits_list_performance(self):
        """Test de performance de la liste des produits"""
        self.client.login(username="testuser", password="testpass123")
        
        import time
        start_time = time.time()
        response = self.client.get(reverse('inventory:produits_list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # La page doit se charger en moins de 2 secondes
        self.assertLess(end_time - start_time, 2.0)


# ========== TESTS DE SÉCURITÉ ==========

class SecurityTest(TestCase):
    """Tests de sécurité basiques"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="COMMERCIAL_SHOWROOM")
    
    def test_unauthorized_access_protection(self):
        """Test protection contre l'accès non autorisé"""
        # Test accès sans authentification
        response = self.client.get(reverse('inventory:produits_list'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Test accès avec role insuffisant
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('users:user_management'))
        # Devrait être bloqué car pas MANAGER
        self.assertNotEqual(response.status_code, 200)
    
    def test_csrf_protection(self):
        """Test protection CSRF"""
        self.client.login(username="testuser", password="testpass123")
        
        # Tenter de poster sans token CSRF
        response = self.client.post(
            reverse('inventory:produit_create'),
            {'nom': 'Test', 'reference': 'TEST'},
            HTTP_X_CSRFTOKEN=""
        )
        # Django devrait rejeter la requête
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    import unittest
    unittest.main()
