"""
Configuration et utilitaires pour les tests
Enterprise Inventory Management System
"""

import os
import django
from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line
import sys
import subprocess
import time
from decimal import Decimal


class TestRunner:
    """Runner personnalisé pour les tests"""
    
    def __init__(self):
        self.setup_django()
    
    def setup_django(self):
        """Configuration Django pour les tests"""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_inventory.settings')
        django.setup()
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 Démarrage de la suite complète de tests...")
        print("=" * 60)
        
        # Tests unitaires standards
        print("\n📋 Tests unitaires (inventory)...")
        self.run_test_module('inventory.tests')
        
        print("\n👤 Tests unitaires (users)...")
        self.run_test_module('users.tests')
        
        # Tests d'intégration
        print("\n🔗 Tests d'intégration...")
        self.run_test_module('tests_integration')
        
        # Tests de performance
        print("\n⚡ Tests de performance...")
        self.run_test_module('tests_performance')
        
        print("\n" + "=" * 60)
        print("✅ Suite de tests terminée!")
    
    def run_test_module(self, module_name):
        """Exécuter un module de tests spécifique"""
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', module_name, '-v', '2'
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ {module_name} - Réussi ({duration:.2f}s)")
            else:
                print(f"❌ {module_name} - Échec ({duration:.2f}s)")
                print("Erreurs:")
                print(result.stdout)
                print(result.stderr)
            
        except subprocess.TimeoutExpired:
            print(f"⏱️ {module_name} - Timeout (>300s)")
        except Exception as e:
            print(f"💥 {module_name} - Erreur: {e}")
    
    def run_coverage_analysis(self):
        """Analyser la couverture de code"""
        print("\n📊 Analyse de couverture de code...")
        
        try:
            # Installer coverage si pas disponible
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                          capture_output=True)
            
            # Exécuter les tests avec coverage
            subprocess.run([
                'coverage', 'run', '--source', '.', 'manage.py', 'test'
            ], check=True)
            
            # Générer le rapport
            result = subprocess.run(['coverage', 'report'], 
                                  capture_output=True, text=True)
            print(result.stdout)
            
            # Générer le rapport HTML
            subprocess.run(['coverage', 'html'], capture_output=True)
            print("📄 Rapport HTML généré dans htmlcov/")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'analyse de couverture: {e}")
        except FileNotFoundError:
            print("⚠️ Coverage non installé. Utilisez: pip install coverage")
    
    def run_security_tests(self):
        """Exécuter les tests de sécurité"""
        print("\n🔒 Tests de sécurité...")
        
        security_checks = [
            self.check_debug_mode,
            self.check_secret_key,
            self.check_allowed_hosts,
            self.check_database_security,
            self.check_static_files_security
        ]
        
        for check in security_checks:
            try:
                check()
            except Exception as e:
                print(f"❌ Erreur dans {check.__name__}: {e}")
    
    def check_debug_mode(self):
        """Vérifier que DEBUG est False en production"""
        if settings.DEBUG:
            print("⚠️ DEBUG=True détecté (OK pour développement)")
        else:
            print("✅ DEBUG=False (Prêt pour production)")
    
    def check_secret_key(self):
        """Vérifier la clé secrète"""
        secret_key = getattr(settings, 'SECRET_KEY', '')
        if len(secret_key) < 50:
            print("⚠️ SECRET_KEY trop courte")
        else:
            print("✅ SECRET_KEY de longueur appropriée")
        
        if 'django-insecure' in secret_key:
            print("⚠️ SECRET_KEY de développement détectée")
    
    def check_allowed_hosts(self):
        """Vérifier ALLOWED_HOSTS"""
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        if not allowed_hosts or '*' in allowed_hosts:
            print("⚠️ ALLOWED_HOSTS non configuré ou trop permissif")
        else:
            print("✅ ALLOWED_HOSTS correctement configuré")
    
    def check_database_security(self):
        """Vérifier la sécurité de la base de données"""
        db_config = settings.DATABASES.get('default', {})
        engine = db_config.get('ENGINE', '')
        
        if 'sqlite' in engine.lower():
            print("⚠️ SQLite détecté (OK pour développement)")
        else:
            print(f"✅ Base de données: {engine}")
        
        # Vérifier les mots de passe
        password = db_config.get('PASSWORD', '')
        if not password and 'sqlite' not in engine.lower():
            print("⚠️ Mot de passe de base de données vide")
    
    def check_static_files_security(self):
        """Vérifier la configuration des fichiers statiques"""
        static_url = getattr(settings, 'STATIC_URL', '')
        static_root = getattr(settings, 'STATIC_ROOT', '')
        
        if static_url and static_root:
            print("✅ Configuration des fichiers statiques correcte")
        else:
            print("⚠️ Configuration des fichiers statiques incomplète")


class TestDataFactory:
    """Factory pour créer des données de test"""
    
    @staticmethod
    def create_test_user(username="testuser", role="MANAGER"):
        """Créer un utilisateur de test"""
        from django.contrib.auth.models import User
        from users.models import Profile
        
        user = User.objects.create_user(
            username=username,
            email=f"{username}@test.com",
            password="testpass123"
        )
        Profile.objects.create(user=user, role=role)
        return user
    
    @staticmethod
    def create_test_category(name="Test Category"):
        """Créer une catégorie de test"""
        from inventory.models import Categorie
        return Categorie.objects.create(nom=name)
    
    @staticmethod
    def create_test_supplier(name="Test Supplier"):
        """Créer un fournisseur de test"""
        from inventory.models import Fournisseur
        return Fournisseur.objects.create(
            nom=name,
            email=f"{name.lower().replace(' ', '')}@test.com",
            telephone="0123456789",
            adresse="123 Test Street",
            ville="Test City",
            code_postal="12345"
        )
    
    @staticmethod
    def create_test_product(name="Test Product", category=None, supplier=None):
        """Créer un produit de test"""
        from inventory.models import Produit
        
        if not category:
            category = TestDataFactory.create_test_category()
        if not supplier:
            supplier = TestDataFactory.create_test_supplier()
        
        return Produit.objects.create(
            nom=name,
            reference=f"TEST-{name[:3].upper()}",
            categorie=category,
            fournisseur=supplier,
            prix_achat=Decimal("100.00"),
            prix_vente=Decimal("150.00"),
            quantite_stock=10,
            seuil_alerte=5
        )
    
    @staticmethod
    def create_test_client(name="Test Client"):
        """Créer un client de test"""
        from inventory.models import Client
        return Client.objects.create(
            nom=name.split()[1] if len(name.split()) > 1 else "Client",
            prenom=name.split()[0],
            email=f"{name.lower().replace(' ', '')}@test.com",
            telephone="0987654321",
            entreprise=f"{name} Enterprise"
        )
    
    @staticmethod
    def create_complete_test_environment():
        """Créer un environnement de test complet"""
        from inventory.models import Commande, LigneCommande, Devis, LigneDevis
        
        # Utilisateurs
        manager = TestDataFactory.create_test_user("manager", "MANAGER")
        commercial = TestDataFactory.create_test_user("commercial", "COMMERCIAL_TERRAIN")
        
        # Données de base
        category = TestDataFactory.create_test_category("Équipement Médical")
        supplier = TestDataFactory.create_test_supplier("MedTech Supplier")
        product = TestDataFactory.create_test_product("Stéthoscope", category, supplier)
        client = TestDataFactory.create_test_client("Jean Dupont")
        
        # Commande
        commande = Commande.objects.create(
            client=client,
            commercial=commercial,
            statut="EN_ATTENTE"
        )
        
        LigneCommande.objects.create(
            commande=commande,
            produit=product,
            quantite=2,
            prix_unitaire=product.prix_vente
        )
        
        # Devis
        devis = Devis.objects.create(
            client=client,
            commercial=commercial,
            objet="Équipement médical",
            conditions_paiement="30 jours"
        )
        
        LigneDevis.objects.create(
            devis=devis,
            produit=product,
            quantite=1,
            prix_unitaire=product.prix_vente
        )
        
        return {
            'users': {'manager': manager, 'commercial': commercial},
            'category': category,
            'supplier': supplier,
            'product': product,
            'client': client,
            'commande': commande,
            'devis': devis
        }


class PerformanceProfiler:
    """Profiler de performance pour les tests"""
    
    def __init__(self):
        self.start_time = None
        self.checkpoints = []
    
    def start(self):
        """Démarrer le profiling"""
        self.start_time = time.time()
        self.checkpoints = []
    
    def checkpoint(self, name):
        """Ajouter un point de contrôle"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.checkpoints.append((name, elapsed))
    
    def report(self):
        """Générer un rapport de performance"""
        if not self.start_time:
            return "Profiler non démarré"
        
        total_time = time.time() - self.start_time
        report = [f"📊 Rapport de performance (Total: {total_time:.3f}s)"]
        report.append("-" * 50)
        
        for name, elapsed in self.checkpoints:
            percentage = (elapsed / total_time) * 100 if total_time > 0 else 0
            report.append(f"{name}: {elapsed:.3f}s ({percentage:.1f}%)")
        
        return "\n".join(report)


# Script principal pour lancer les tests
if __name__ == "__main__":
    import sys
    
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            runner.run_all_tests()
        elif command == "coverage":
            runner.run_coverage_analysis()
        elif command == "security":
            runner.run_security_tests()
        elif command == "create-data":
            TestDataFactory.create_complete_test_environment()
            print("✅ Environnement de test créé")
        else:
            print("Commandes disponibles:")
            print("  all      - Exécuter tous les tests")
            print("  coverage - Analyser la couverture de code")
            print("  security - Vérifier la sécurité")
            print("  create-data - Créer des données de test")
    else:
        print("🧪 Test Runner - Enterprise Inventory Management")
        print("=" * 50)
        print("Usage: python test_config.py [command]")
        print()
        print("Commandes disponibles:")
        print("  all      - Exécuter tous les tests")
        print("  coverage - Analyser la couverture de code")
        print("  security - Vérifier la sécurité")
        print("  create-data - Créer des données de test")
        print()
        print("Ou utilisez directement:")
        print("  python manage.py test")
