"""
Tests d'API et d'intégration avancée pour l'Enterprise Inventory Management System
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date, datetime, timedelta
import json
from io import BytesIO
from PIL import Image

from users.models import Profile
from inventory.models import (
    Categorie, Fournisseur, Produit, Client as ClientModel,
    Commande, LigneCommande, Vente, LigneVente, MouvementStock,
    Devis, LigneDevis, Prospect, AppareilVendu, InterventionSAV, TransfertStock
)


class APIEndpointsTest(TestCase):
    """Tests pour les endpoints API"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="apiuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer des données de test
        self.categorie = Categorie.objects.create(nom="API Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="API Fournisseur",
            email="api@fournisseur.fr",
            telephone="0123456789",
            adresse="API Adresse",
            ville="API Ville",
            code_postal="12345"
        )
        
        for i in range(5):
            Produit.objects.create(
                nom=f"API Produit {i}",
                reference=f"API-{i:03d}",
                categorie=self.categorie,
                fournisseur=self.fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("150.00")
            )
        
        for i in range(3):
            ClientModel.objects.create(
                nom=f"Client{i}",
                prenom="API",
                email=f"client{i}@test.fr",
                telephone=f"012345678{i}"
            )
    
    def test_api_produit_search(self):
        """Test de l'API de recherche de produits"""
        self.client.login(username="apiuser", password="testpass123")
        
        # Test recherche basique
        response = self.client.get(reverse('inventory:api_produit_search'), {'q': 'API'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
        
        # Vérifier la structure des résultats
        first_result = data['results'][0]
        self.assertIn('id', first_result)
        self.assertIn('text', first_result)
        self.assertIn('reference', first_result)
        self.assertIn('prix_vente', first_result)
    
    def test_api_client_search(self):
        """Test de l'API de recherche de clients"""
        self.client.login(username="apiuser", password="testpass123")
        
        response = self.client.get(reverse('inventory:api_client_search'), {'q': 'Client'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
    
    def test_api_authentication_required(self):
        """Test que l'authentification est requise pour les APIs"""
        # Test sans authentification
        response = self.client.get(reverse('inventory:api_produit_search'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login


class FileUploadTest(TestCase):
    """Tests pour l'upload de fichiers"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="uploaduser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        self.categorie = Categorie.objects.create(nom="Upload Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="Upload Fournisseur",
            email="upload@fournisseur.fr",
            telephone="0123456789",
            adresse="Upload Adresse",
            ville="Upload Ville",
            code_postal="12345"
        )
    
    def create_test_image(self):
        """Créer une image de test"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
    
    def test_product_image_upload(self):
        """Test d'upload d'image pour un produit"""
        self.client.login(username="uploaduser", password="testpass123")
        
        test_image = self.create_test_image()
        
        product_data = {
            'nom': 'Produit avec Image',
            'reference': 'IMG-001',
            'categorie': self.categorie.pk,
            'fournisseur': self.fournisseur.pk,
            'prix_achat': '100.00',
            'prix_vente': '150.00',
            'quantite_stock': '10',
            'seuil_alerte': '5',
            'image': test_image
        }
        
        response = self.client.post(reverse('inventory:produit_create'), product_data)
        self.assertEqual(response.status_code, 302)  # Redirection après création
        
        # Vérifier que le produit a été créé avec l'image
        produit = Produit.objects.get(reference='IMG-001')
        self.assertTrue(produit.image)
    
    def test_invalid_file_upload(self):
        """Test d'upload de fichier invalide"""
        self.client.login(username="uploaduser", password="testpass123")
        
        # Créer un fichier texte au lieu d'une image
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is not an image',
            content_type='text/plain'
        )
        
        product_data = {
            'nom': 'Produit Test',
            'reference': 'INV-001',
            'categorie': self.categorie.pk,
            'fournisseur': self.fournisseur.pk,
            'prix_achat': '100.00',
            'prix_vente': '150.00',
            'image': invalid_file
        }
        
        response = self.client.post(reverse('inventory:produit_create'), product_data)
        # Devrait échouer à cause du type de fichier invalide
        self.assertEqual(response.status_code, 200)  # Reste sur la page de création


class PDFGenerationTest(TestCase):
    """Tests pour la génération de PDF"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="pdfuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="COMMERCIAL_TERRAIN")
        
        self.client_model = ClientModel.objects.create(
            nom="Client PDF",
            prenom="Test",
            email="clientpdf@test.fr",
            telephone="0123456789",
            entreprise="Entreprise Test PDF"
        )
        
        self.categorie = Categorie.objects.create(nom="PDF Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="PDF Fournisseur",
            email="pdf@fournisseur.fr",
            telephone="0123456789",
            adresse="PDF Adresse",
            ville="PDF Ville",
            code_postal="12345"
        )
        
        self.produit = Produit.objects.create(
            nom="Produit PDF",
            reference="PDF-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("100.00"),
            prix_vente=Decimal("150.00")
        )
        
        self.devis = Devis.objects.create(
            client=self.client_model,
            commercial=self.user,
            objet="Test Devis PDF",
            conditions_paiement="30 jours"
        )
        
        LigneDevis.objects.create(
            devis=self.devis,
            produit=self.produit,
            quantite=2,
            prix_unitaire=Decimal("150.00")
        )
    
    def test_devis_pdf_generation(self):
        """Test de génération de PDF pour un devis"""
        self.client.login(username="pdfuser", password="testpass123")
        
        response = self.client.get(reverse('inventory:devis_pdf', kwargs={'pk': self.devis.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_pdf_content_not_empty(self):
        """Test que le PDF généré n'est pas vide"""
        self.client.login(username="pdfuser", password="testpass123")
        
        response = self.client.get(reverse('inventory:devis_pdf', kwargs={'pk': self.devis.pk}))
        self.assertGreater(len(response.content), 1000)  # PDF doit faire plus de 1KB


class FormValidationTest(TestCase):
    """Tests avancés de validation des formulaires"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="formuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        self.categorie = Categorie.objects.create(nom="Form Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="Form Fournisseur",
            email="form@fournisseur.fr",
            telephone="0123456789",
            adresse="Form Adresse",
            ville="Form Ville",
            code_postal="12345"
        )
    
    def test_produit_form_validation_errors(self):
        """Test des erreurs de validation du formulaire produit"""
        self.client.login(username="formuser", password="testpass123")
        
        # Test avec des données invalides
        invalid_data = {
            'nom': '',  # Nom requis
            'reference': '',  # Référence requise
            'prix_achat': '-10.00',  # Prix négatif
            'prix_vente': 'invalid',  # Prix invalide
            'quantite_stock': '-5'  # Quantité négative
        }
        
        response = self.client.post(reverse('inventory:produit_create'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Reste sur la page avec erreurs
        
        # Vérifier que les erreurs sont affichées
        self.assertContains(response, 'Ce champ est obligatoire')
    
    def test_email_uniqueness_validation(self):
        """Test de validation d'unicité des emails"""
        self.client.login(username="formuser", password="testpass123")
        
        # Créer un premier client
        ClientModel.objects.create(
            nom="Premier",
            prenom="Client",
            email="unique@test.fr",
            telephone="0123456789"
        )
        
        # Tenter de créer un second client avec le même email
        duplicate_data = {
            'nom': 'Deuxième',
            'prenom': 'Client',
            'email': 'unique@test.fr',  # Email déjà utilisé
            'telephone': '0987654321'
        }
        
        response = self.client.post(reverse('inventory:client_create'), duplicate_data)
        # Devrait échouer à cause de l'email dupliqué
        self.assertEqual(response.status_code, 200)
    
    def test_price_validation(self):
        """Test de validation des prix"""
        self.client.login(username="formuser", password="testpass123")
        
        # Test avec prix de vente inférieur au prix d'achat
        price_data = {
            'nom': 'Produit Test Prix',
            'reference': 'PRICE-001',
            'categorie': self.categorie.pk,
            'fournisseur': self.fournisseur.pk,
            'prix_achat': '200.00',
            'prix_vente': '100.00',  # Inférieur au prix d'achat
            'quantite_stock': '10'
        }
        
        response = self.client.post(reverse('inventory:produit_create'), price_data)
        # Le formulaire devrait accepter cela (pas de validation métier automatique)
        # Mais on pourrait ajouter une validation personnalisée


class PaginationTest(TestCase):
    """Tests pour la pagination"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="paginationuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer beaucoup d'objets pour tester la pagination
        self.categorie = Categorie.objects.create(nom="Pagination Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="Pagination Fournisseur",
            email="pagination@fournisseur.fr",
            telephone="0123456789",
            adresse="Pagination Adresse",
            ville="Pagination Ville",
            code_postal="12345"
        )
        
        # Créer 50 produits
        for i in range(50):
            Produit.objects.create(
                nom=f"Produit Pagination {i}",
                reference=f"PAG-{i:03d}",
                categorie=self.categorie,
                fournisseur=self.fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("150.00")
            )
    
    def test_products_pagination(self):
        """Test de la pagination des produits"""
        self.client.login(username="paginationuser", password="testpass123")
        
        # Première page
        response = self.client.get(reverse('inventory:produits_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Produit Pagination')
        
        # Vérifier la présence de liens de pagination
        if 'paginator' in response.context:
            paginator = response.context['paginator']
            self.assertGreater(paginator.num_pages, 1)
        
        # Test deuxième page
        response = self.client.get(reverse('inventory:produits_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_page_number(self):
        """Test avec un numéro de page invalide"""
        self.client.login(username="paginationuser", password="testpass123")
        
        # Page trop élevée
        response = self.client.get(reverse('inventory:produits_list') + '?page=999')
        # Django devrait rediriger vers la dernière page ou afficher une erreur 404
        self.assertIn(response.status_code, [200, 404])


class SearchFilterTest(TestCase):
    """Tests pour les fonctionnalités de recherche et filtrage"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="searchuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer des données variées pour les tests de recherche
        self.categorie1 = Categorie.objects.create(nom="Électronique")
        self.categorie2 = Categorie.objects.create(nom="Mécanique")
        
        self.fournisseur = Fournisseur.objects.create(
            nom="Search Fournisseur",
            email="search@fournisseur.fr",
            telephone="0123456789",
            adresse="Search Adresse",
            ville="Search Ville",
            code_postal="12345"
        )
        
        # Produits avec différentes caractéristiques
        Produit.objects.create(
            nom="Stéthoscope Électronique",
            reference="STET-001",
            categorie=self.categorie1,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("150.00"),
            prix_vente=Decimal("250.00"),
            quantite_stock=5
        )
        
        Produit.objects.create(
            nom="Table d'Examen Mécanique",
            reference="TABLE-001",
            categorie=self.categorie2,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("500.00"),
            prix_vente=Decimal("800.00"),
            quantite_stock=15
        )
    
    def test_product_search_by_name(self):
        """Test de recherche de produits par nom"""
        self.client.login(username="searchuser", password="testpass123")
        
        response = self.client.get(
            reverse('inventory:produits_list') + '?search=Stéthoscope'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stéthoscope Électronique")
        self.assertNotContains(response, "Table d'Examen")
    
    def test_product_search_by_reference(self):
        """Test de recherche de produits par référence"""
        self.client.login(username="searchuser", password="testpass123")
        
        response = self.client.get(
            reverse('inventory:produits_list') + '?search=TABLE-001'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Table d'Examen Mécanique")
    
    def test_product_filter_by_category(self):
        """Test de filtrage par catégorie"""
        self.client.login(username="searchuser", password="testpass123")
        
        response = self.client.get(
            reverse('inventory:produits_list') + f'?categorie={self.categorie1.pk}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stéthoscope Électronique")
        self.assertNotContains(response, "Table d'Examen")
    
    def test_combined_search_and_filter(self):
        """Test de recherche et filtrage combinés"""
        self.client.login(username="searchuser", password="testpass123")
        
        response = self.client.get(
            reverse('inventory:produits_list') + 
            f'?search=Électronique&categorie={self.categorie1.pk}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stéthoscope Électronique")


class ConcurrencyTest(TestCase):
    """Tests de concurrence basiques"""
    
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        
        self.user1 = User.objects.create_user("user1", "user1@test.com", "pass")
        self.user2 = User.objects.create_user("user2", "user2@test.com", "pass")
        
        Profile.objects.create(user=self.user1, role="MANAGER")
        Profile.objects.create(user=self.user2, role="MANAGER")
        
        self.categorie = Categorie.objects.create(nom="Concurrency Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="Concurrency Fournisseur",
            email="concurrency@fournisseur.fr",
            telephone="0123456789",
            adresse="Concurrency Adresse",
            ville="Concurrency Ville",
            code_postal="12345"
        )
        
        self.produit = Produit.objects.create(
            nom="Produit Concurrent",
            reference="CONC-001",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal("100.00"),
            prix_vente=Decimal("150.00"),
            quantite_stock=10
        )
    
    def test_concurrent_stock_updates(self):
        """Test de mises à jour concurrentes du stock"""
        self.client1.login(username="user1", password="pass")
        self.client2.login(username="user2", password="pass")
        
        # Les deux utilisateurs tentent de modifier le même produit
        update_data = {
            'nom': self.produit.nom,
            'reference': self.produit.reference,
            'categorie': self.categorie.pk,
            'fournisseur': self.fournisseur.pk,
            'prix_achat': '100.00',
            'prix_vente': '150.00',
            'quantite_stock': '5'  # Réduction du stock
        }
        
        # Premier utilisateur met à jour
        response1 = self.client1.post(
            reverse('inventory:produit_update', kwargs={'pk': self.produit.pk}),
            update_data
        )
        
        # Deuxième utilisateur met à jour avec une quantité différente
        update_data['quantite_stock'] = '3'
        response2 = self.client2.post(
            reverse('inventory:produit_update', kwargs={'pk': self.produit.pk}),
            update_data
        )
        
        # Vérifier que les deux mises à jour ont été traitées
        self.assertIn(response1.status_code, [200, 302])
        self.assertIn(response2.status_code, [200, 302])
        
        # Vérifier l'état final
        produit_updated = Produit.objects.get(pk=self.produit.pk)
        # La dernière mise à jour devrait prévaloir
        self.assertEqual(produit_updated.quantite_stock, 3)


if __name__ == '__main__':
    import unittest
    unittest.main()
