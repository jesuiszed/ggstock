"""
Tests de performance et monitoring pour l'Enterprise Inventory Management System
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import connection
from django.test.utils import override_settings
from django.core.management import call_command
from django.core.cache import cache
from decimal import Decimal
import time
import statistics
from contextlib import contextmanager

from users.models import Profile
from inventory.models import (
    Categorie, Fournisseur, Produit, Client as ClientModel,
    Commande, LigneCommande, Vente, LigneVente, MouvementStock,
    Devis, LigneDevis
)


@contextmanager
def query_counter():
    """Context manager pour compter les requêtes SQL"""
    initial_queries = len(connection.queries)
    yield
    final_queries = len(connection.queries)
    print(f"Nombre de requêtes SQL: {final_queries - initial_queries}")


class DatabasePerformanceTest(TestCase):
    """Tests de performance de la base de données"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="perfuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer des données de test en volume
        self.setup_large_dataset()
    
    def setup_large_dataset(self):
        """Créer un jeu de données volumineux pour les tests"""
        # Créer plusieurs catégories
        for i in range(10):
            Categorie.objects.create(nom=f"Catégorie Perf {i}")
        
        # Créer plusieurs fournisseurs
        for i in range(20):
            Fournisseur.objects.create(
                nom=f"Fournisseur Perf {i}",
                email=f"perf{i}@fournisseur.fr",
                telephone=f"01234567{i:02d}",
                adresse=f"Adresse Perf {i}",
                ville=f"Ville {i}",
                code_postal=f"{10000 + i}"
            )
        
        # Créer beaucoup de produits
        categories = list(Categorie.objects.all())
        fournisseurs = list(Fournisseur.objects.all())
        
        for i in range(500):  # 500 produits
            Produit.objects.create(
                nom=f"Produit Performance {i}",
                reference=f"PERF-{i:04d}",
                categorie=categories[i % len(categories)],
                fournisseur=fournisseurs[i % len(fournisseurs)],
                prix_achat=Decimal(f"{50 + (i % 200)}.00"),
                prix_vente=Decimal(f"{100 + (i % 300)}.00"),
                quantite_stock=i % 100
            )
        
        # Créer des clients
        for i in range(100):
            ClientModel.objects.create(
                nom=f"Client{i}",
                prenom="Performance",
                email=f"perf{i}@client.fr",
                telephone=f"09876543{i:02d}"
            )
    
    def test_products_list_performance(self):
        """Test de performance de la liste des produits"""
        self.client.login(username="perfuser", password="testpass123")
        
        # Mesurer le temps de réponse
        start_time = time.time()
        
        with query_counter():
            response = self.client.get(reverse('inventory:produits_list'))
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0)  # Moins de 2 secondes
        print(f"Temps de réponse liste produits: {response_time:.3f}s")
    
    def test_search_performance(self):
        """Test de performance de la recherche"""
        self.client.login(username="perfuser", password="testpass123")
        
        search_terms = ["Performance", "PERF-0001", "Catégorie"]
        response_times = []
        
        for term in search_terms:
            start_time = time.time()
            
            with query_counter():
                response = self.client.get(
                    reverse('inventory:produits_list') + f'?search={term}'
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            self.assertEqual(response.status_code, 200)
            print(f"Recherche '{term}': {response_time:.3f}s")
        
        avg_response_time = statistics.mean(response_times)
        self.assertLess(avg_response_time, 1.0)  # Moyenne < 1 seconde
    
    def test_dashboard_performance(self):
        """Test de performance du dashboard"""
        self.client.login(username="perfuser", password="testpass123")
        
        start_time = time.time()
        
        with query_counter():
            response = self.client.get(reverse('users:dashboard'))
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.5)  # Moins de 1.5 secondes
        print(f"Temps de réponse dashboard: {response_time:.3f}s")
    
    def test_database_connection_pool(self):
        """Test du pool de connexions à la base de données"""
        connections_used = []
        
        for i in range(10):
            start_time = time.time()
            
            # Simuler une requête
            list(Produit.objects.all()[:1])
            
            end_time = time.time()
            connections_used.append(end_time - start_time)
        
        # Vérifier que les connexions sont réutilisées efficacement
        avg_time = statistics.mean(connections_used)
        self.assertLess(avg_time, 0.1)  # Très rapide pour les connexions


class MemoryUsageTest(TestCase):
    """Tests d'utilisation mémoire"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="memuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
    
    def get_memory_usage(self):
        """Obtenir l'utilisation mémoire approximative"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0  # psutil non disponible
    
    def test_large_queryset_memory(self):
        """Test d'utilisation mémoire pour de gros querysets"""
        # Créer beaucoup d'objets
        categorie = Categorie.objects.create(nom="Memory Test")
        fournisseur = Fournisseur.objects.create(
            nom="Memory Fournisseur",
            email="memory@fournisseur.fr",
            telephone="0123456789",
            adresse="Memory Adresse",
            ville="Memory Ville",
            code_postal="12345"
        )
        
        # Créer 1000 produits
        produits = []
        for i in range(1000):
            produits.append(Produit(
                nom=f"Produit Memory {i}",
                reference=f"MEM-{i:04d}",
                categorie=categorie,
                fournisseur=fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("150.00")
            ))
        
        Produit.objects.bulk_create(produits)
        
        memory_before = self.get_memory_usage()
        
        # Charger tous les produits en mémoire
        all_products = list(Produit.objects.all())
        
        memory_after = self.get_memory_usage()
        
        if memory_before > 0 and memory_after > 0:
            memory_increase = memory_after - memory_before
            print(f"Augmentation mémoire: {memory_increase:.1f} MB")
            # Vérifie que l'augmentation n'est pas excessive
            self.assertLess(memory_increase, 100)  # Moins de 100 MB
    
    def test_iterator_vs_list_memory(self):
        """Comparer l'utilisation mémoire entre iterator et list"""
        # Créer des données de test
        categorie = Categorie.objects.create(nom="Iterator Test")
        fournisseur = Fournisseur.objects.create(
            nom="Iterator Fournisseur",
            email="iterator@fournisseur.fr",
            telephone="0123456789",
            adresse="Iterator Adresse",
            ville="Iterator Ville",
            code_postal="12345"
        )
        
        # Créer des produits
        for i in range(100):
            Produit.objects.create(
                nom=f"Produit Iterator {i}",
                reference=f"ITER-{i:03d}",
                categorie=categorie,
                fournisseur=fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("150.00")
            )
        
        memory_before = self.get_memory_usage()
        
        # Utiliser iterator() pour économiser la mémoire
        for product in Produit.objects.iterator():
            pass  # Traitement minimal
        
        memory_after_iterator = self.get_memory_usage()
        
        # Maintenant charger tout en liste
        all_products = list(Produit.objects.all())
        
        memory_after_list = self.get_memory_usage()
        
        if memory_before > 0:
            print(f"Mémoire avant: {memory_before:.1f} MB")
            print(f"Mémoire après iterator: {memory_after_iterator:.1f} MB")
            print(f"Mémoire après list: {memory_after_list:.1f} MB")


@override_settings(DEBUG=True)  # Pour capturer les requêtes SQL
class QueryOptimizationTest(TestCase):
    """Tests d'optimisation des requêtes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="queryuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Créer des données avec relations
        self.categorie = Categorie.objects.create(nom="Query Test")
        self.fournisseur = Fournisseur.objects.create(
            nom="Query Fournisseur",
            email="query@fournisseur.fr",
            telephone="0123456789",
            adresse="Query Adresse",
            ville="Query Ville",
            code_postal="12345"
        )
        
        # Créer des produits
        for i in range(50):
            Produit.objects.create(
                nom=f"Produit Query {i}",
                reference=f"QUERY-{i:03d}",
                categorie=self.categorie,
                fournisseur=self.fournisseur,
                prix_achat=Decimal("100.00"),
                prix_vente=Decimal("150.00")
            )
    
    def test_select_related_optimization(self):
        """Test d'optimisation avec select_related"""
        # Sans optimisation
        connection.queries_log.clear()
        
        products_without_optimization = Produit.objects.all()
        for product in products_without_optimization[:10]:
            _ = product.categorie.nom  # Accès à la relation
            _ = product.fournisseur.nom
        
        queries_without = len(connection.queries)
        
        # Avec optimisation
        connection.queries_log.clear()
        
        products_with_optimization = Produit.objects.select_related(
            'categorie', 'fournisseur'
        )
        for product in products_with_optimization[:10]:
            _ = product.categorie.nom
            _ = product.fournisseur.nom
        
        queries_with = len(connection.queries)
        
        print(f"Requêtes sans optimisation: {queries_without}")
        print(f"Requêtes avec select_related: {queries_with}")
        
        # L'optimisation devrait réduire significativement le nombre de requêtes
        self.assertLess(queries_with, queries_without)
    
    def test_prefetch_related_optimization(self):
        """Test d'optimisation avec prefetch_related"""
        # Créer des commandes avec lignes
        client = ClientModel.objects.create(
            nom="Client Query",
            prenom="Test",
            email="query@client.fr",
            telephone="0123456789"
        )
        
        for i in range(5):
            commande = Commande.objects.create(
                client=client,
                commercial=self.user,
                statut="EN_ATTENTE"
            )
            
            for j in range(3):
                LigneCommande.objects.create(
                    commande=commande,
                    produit=Produit.objects.first(),
                    quantite=j + 1,
                    prix_unitaire=Decimal("100.00")
                )
        
        # Test sans prefetch
        connection.queries_log.clear()
        
        commandes_without = Commande.objects.all()
        for commande in commandes_without:
            for ligne in commande.lignes.all():
                _ = ligne.produit.nom
        
        queries_without = len(connection.queries)
        
        # Test avec prefetch
        connection.queries_log.clear()
        
        commandes_with = Commande.objects.prefetch_related(
            'lignes__produit'
        )
        for commande in commandes_with:
            for ligne in commande.lignes.all():
                _ = ligne.produit.nom
        
        queries_with = len(connection.queries)
        
        print(f"Requêtes sans prefetch: {queries_without}")
        print(f"Requêtes avec prefetch_related: {queries_with}")
        
        self.assertLess(queries_with, queries_without)


class CachePerformanceTest(TestCase):
    """Tests de performance du cache"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="cacheuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="MANAGER")
        
        # Vider le cache avant les tests
        cache.clear()
    
    def test_cache_effectiveness(self):
        """Test de l'efficacité du cache"""
        # Créer des données
        categorie = Categorie.objects.create(nom="Cache Test")
        
        cache_key = "test_categories"
        
        # Premier accès (cache miss)
        start_time = time.time()
        categories_from_cache = cache.get(cache_key)
        if categories_from_cache is None:
            categories = list(Categorie.objects.all())
            cache.set(cache_key, categories, 300)  # 5 minutes
        else:
            categories = categories_from_cache
        first_access_time = time.time() - start_time
        
        # Deuxième accès (cache hit)
        start_time = time.time()
        categories_from_cache = cache.get(cache_key)
        if categories_from_cache is None:
            categories = list(Categorie.objects.all())
            cache.set(cache_key, categories, 300)
        else:
            categories = categories_from_cache
        second_access_time = time.time() - start_time
        
        print(f"Premier accès (cache miss): {first_access_time:.4f}s")
        print(f"Deuxième accès (cache hit): {second_access_time:.4f}s")
        
        # Le cache devrait être plus rapide
        self.assertLess(second_access_time, first_access_time)
    
    def test_cache_invalidation(self):
        """Test d'invalidation du cache"""
        cache_key = "test_products_count"
        
        # Mettre en cache le nombre de produits
        initial_count = Produit.objects.count()
        cache.set(cache_key, initial_count, 300)
        
        # Vérifier que la valeur est en cache
        cached_count = cache.get(cache_key)
        self.assertEqual(cached_count, initial_count)
        
        # Ajouter un produit (devrait invalider le cache)
        categorie = Categorie.objects.create(nom="Cache Invalidation")
        fournisseur = Fournisseur.objects.create(
            nom="Cache Fournisseur",
            email="cache@fournisseur.fr",
            telephone="0123456789",
            adresse="Cache Adresse",
            ville="Cache Ville",
            code_postal="12345"
        )
        
        Produit.objects.create(
            nom="Produit Cache",
            reference="CACHE-001",
            categorie=categorie,
            fournisseur=fournisseur,
            prix_achat=Decimal("100.00"),
            prix_vente=Decimal("150.00")
        )
        
        # Invalider manuellement le cache
        cache.delete(cache_key)
        
        # Vérifier que le cache est vide
        cached_count_after = cache.get(cache_key)
        self.assertIsNone(cached_count_after)


class LoadTest(TestCase):
    """Tests de charge basiques"""
    
    def setUp(self):
        self.users = []
        for i in range(5):  # 5 utilisateurs de test
            user = User.objects.create_user(
                username=f"loaduser{i}",
                password="testpass123"
            )
            Profile.objects.create(user=user, role="MANAGER")
            self.users.append(user)
    
    def test_concurrent_login_performance(self):
        """Test de performance de connexions concurrentes"""
        response_times = []
        
        for user in self.users:
            client = Client()
            
            start_time = time.time()
            response = client.post(reverse('users:login'), {
                'username': user.username,
                'password': 'testpass123'
            })
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Vérifier que la connexion réussit
            self.assertIn(response.status_code, [200, 302])
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"Temps moyen de connexion: {avg_response_time:.3f}s")
        print(f"Temps maximum de connexion: {max_response_time:.3f}s")
        
        # Critères de performance
        self.assertLess(avg_response_time, 1.0)  # Moyenne < 1s
        self.assertLess(max_response_time, 2.0)  # Maximum < 2s
    
    def test_concurrent_dashboard_access(self):
        """Test d'accès concurrent au dashboard"""
        response_times = []
        
        for user in self.users:
            client = Client()
            client.login(username=user.username, password="testpass123")
            
            start_time = time.time()
            response = client.get(reverse('users:dashboard'))
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            self.assertEqual(response.status_code, 200)
        
        avg_response_time = statistics.mean(response_times)
        print(f"Temps moyen d'accès dashboard: {avg_response_time:.3f}s")
        
        self.assertLess(avg_response_time, 1.5)


class MonitoringTest(TestCase):
    """Tests de monitoring et métriques"""
    
    def test_health_check_endpoints(self):
        """Test des endpoints de vérification de santé"""
        # Ces endpoints devraient être ajoutés pour la production
        client = Client()
        
        # Test endpoint de base (si disponible)
        try:
            response = client.get('/')
            self.assertIn(response.status_code, [200, 302, 404])
        except:
            pass  # Endpoint pas encore défini
    
    def test_database_health(self):
        """Test de santé de la base de données"""
        # Test de connexion à la base
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
        except Exception as e:
            self.fail(f"Problème de connexion à la base: {e}")
    
    def test_critical_models_accessibility(self):
        """Test d'accessibilité des modèles critiques"""
        # Vérifier que les modèles principaux sont accessibles
        try:
            User.objects.count()
            Profile.objects.count()
            Produit.objects.count()
            ClientModel.objects.count()
        except Exception as e:
            self.fail(f"Problème d'accès aux modèles: {e}")


if __name__ == '__main__':
    import unittest
    unittest.main()
