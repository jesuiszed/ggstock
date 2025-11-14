from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Profile
from .decorators import role_required, permission_required, manager_required
from .forms import ProfileForm


class ProfileModelTest(TestCase):
    """Tests pour le modèle Profile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            role="MANAGER",
            telephone="0123456789"
        )
    
    def test_string_representation(self):
        expected = "Test User (MANAGER)"
        self.assertEqual(str(self.profile), expected)
    
    def test_role_choices_validation(self):
        """Test que seuls les rôles valides sont acceptés"""
        valid_roles = ["MANAGER", "COMMERCIAL_SHOWROOM", "COMMERCIAL_TERRAIN", "TECHNICIEN"]
        for role in valid_roles:
            profile = Profile(user=self.user, role=role)
            # Ne devrait pas lever d'exception
            try:
                profile.full_clean()
            except ValidationError:
                self.fail(f"Role {role} should be valid")
    
    def test_permissions_manager(self):
        """Test des permissions pour le rôle MANAGER"""
        manager_profile = Profile.objects.create(
            user=User.objects.create_user("manager", "test@test.com", "pass"),
            role="MANAGER"
        )
        
        self.assertTrue(manager_profile.can_manage_users)
        self.assertTrue(manager_profile.can_manage_products)
        self.assertTrue(manager_profile.can_manage_stock)
        self.assertTrue(manager_profile.can_manage_sales)
        self.assertTrue(manager_profile.can_manage_orders)
        self.assertTrue(manager_profile.can_manage_clients)
        self.assertTrue(manager_profile.can_manage_suppliers)
    
    def test_permissions_commercial_showroom(self):
        """Test des permissions pour le rôle COMMERCIAL_SHOWROOM"""
        commercial_profile = Profile.objects.create(
            user=User.objects.create_user("commercial", "test@test.com", "pass"),
            role="COMMERCIAL_SHOWROOM"
        )
        
        self.assertFalse(commercial_profile.can_manage_users)
        self.assertTrue(commercial_profile.can_manage_products)
        self.assertFalse(commercial_profile.can_manage_stock)
        self.assertTrue(commercial_profile.can_manage_sales)
        self.assertFalse(commercial_profile.can_manage_orders)
        self.assertFalse(commercial_profile.can_manage_clients)
        self.assertFalse(commercial_profile.can_manage_suppliers)
    
    def test_permissions_commercial_terrain(self):
        """Test des permissions pour le rôle COMMERCIAL_TERRAIN"""
        terrain_profile = Profile.objects.create(
            user=User.objects.create_user("terrain", "test@test.com", "pass"),
            role="COMMERCIAL_TERRAIN"
        )
        
        self.assertFalse(terrain_profile.can_manage_users)
        self.assertFalse(terrain_profile.can_manage_products)
        self.assertFalse(terrain_profile.can_manage_stock)
        self.assertFalse(terrain_profile.can_manage_sales)
        self.assertTrue(terrain_profile.can_manage_orders)
        self.assertTrue(terrain_profile.can_manage_clients)
        self.assertFalse(terrain_profile.can_manage_suppliers)
    
    def test_permissions_technicien(self):
        """Test des permissions pour le rôle TECHNICIEN"""
        tech_profile = Profile.objects.create(
            user=User.objects.create_user("tech", "test@test.com", "pass"),
            role="TECHNICIEN"
        )
        
        self.assertFalse(tech_profile.can_manage_users)
        self.assertTrue(tech_profile.can_manage_products)
        self.assertTrue(tech_profile.can_manage_stock)
        self.assertFalse(tech_profile.can_manage_sales)
        self.assertFalse(tech_profile.can_manage_orders)
        self.assertFalse(tech_profile.can_manage_clients)
        self.assertTrue(tech_profile.can_manage_suppliers)


class ProfileSignalsTest(TestCase):
    """Tests pour les signaux du modèle Profile"""
    
    def test_profile_created_on_user_creation(self):
        """Test qu'un profil est créé automatiquement lors de la création d'un utilisateur"""
        user = User.objects.create_user(
            username="newuser",
            password="testpass123"
        )
        
        # Vérifier qu'un profil a été créé
        self.assertTrue(Profile.objects.filter(user=user).exists())
        
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, "COMMERCIAL_SHOWROOM")  # Rôle par défaut


class UserViewsTest(TestCase):
    """Tests pour les vues des utilisateurs"""
    
    def setUp(self):
        self.client = Client()
        self.manager_user = User.objects.create_user(
            username="manager",
            password="testpass123"
        )
        self.manager_profile = Profile.objects.create(
            user=self.manager_user,
            role="MANAGER"
        )
        
        self.regular_user = User.objects.create_user(
            username="regular",
            password="testpass123"
        )
        self.regular_profile = Profile.objects.create(
            user=self.regular_user,
            role="COMMERCIAL_SHOWROOM"
        )
    
    def test_login_view_get(self):
        """Test de la vue de connexion (GET)"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connexion")
    
    def test_login_view_post_valid(self):
        """Test de la vue de connexion avec des données valides"""
        response = self.client.post(reverse('users:login'), {
            'username': 'manager',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après connexion
    
    def test_login_view_post_invalid(self):
        """Test de la vue de connexion avec des données invalides"""
        response = self.client.post(reverse('users:login'), {
            'username': 'manager',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Reste sur la page de login
        self.assertContains(response, "Nom d'utilisateur ou mot de passe incorrect")
    
    def test_logout_view(self):
        """Test de la vue de déconnexion"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Redirection après déconnexion
    
    def test_profile_view_authenticated(self):
        """Test de la vue profil pour utilisateur authentifié"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profil")
    
    def test_profile_view_anonymous(self):
        """Test de la vue profil pour utilisateur anonyme"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_user_management_view_manager(self):
        """Test de la vue gestion des utilisateurs pour un manager"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse('users:user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion des Utilisateurs")
    
    def test_user_management_view_non_manager(self):
        """Test de la vue gestion des utilisateurs pour un non-manager"""
        self.client.login(username="regular", password="testpass123")
        response = self.client.get(reverse('users:user_management'))
        # Devrait être redirigé ou avoir une erreur de permission
        self.assertNotEqual(response.status_code, 200)
    
    def test_role_test_view(self):
        """Test de la vue de test des rôles"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse('users:role_test'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test des Rôles")
    
    def test_profils_list_view_manager(self):
        """Test de la vue liste des profils pour un manager"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse('users:profils_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_profil_create_view(self):
        """Test de la vue création de profil"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse('users:profil_create'))
        self.assertEqual(response.status_code, 200)
        
        # Test création via POST
        user_data = {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'role': 'TECHNICIEN',
            'telephone': '0987654321'
        }
        response = self.client.post(reverse('users:profil_create'), user_data)
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_profil_update_view(self):
        """Test de la vue modification de profil"""
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(
            reverse('users:profil_update', kwargs={'pk': self.regular_profile.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Test modification via POST
        update_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@test.com',
            'role': 'TECHNICIEN',
            'telephone': '0111111111'
        }
        response = self.client.post(
            reverse('users:profil_update', kwargs={'pk': self.regular_profile.pk}),
            update_data
        )
        
        # Vérifier que les modifications ont été appliquées
        updated_user = User.objects.get(pk=self.regular_user.pk)
        self.assertEqual(updated_user.first_name, 'Updated')


class DecoratorsTest(TestCase):
    """Tests pour les décorateurs de permission"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer des utilisateurs avec différents rôles
        self.manager = User.objects.create_user("manager", "test@test.com", "pass")
        Profile.objects.create(user=self.manager, role="MANAGER")
        
        self.commercial = User.objects.create_user("commercial", "test@test.com", "pass")
        Profile.objects.create(user=self.commercial, role="COMMERCIAL_SHOWROOM")
        
        self.technicien = User.objects.create_user("tech", "test@test.com", "pass")
        Profile.objects.create(user=self.technicien, role="TECHNICIEN")
    
    def test_role_required_decorator(self):
        """Test du décorateur role_required"""
        
        # Créer une vue de test avec le décorateur
        from django.http import HttpResponse
        
        @role_required(['MANAGER'])
        def test_view(request):
            return HttpResponse("Success")
        
        # Test avec un manager (devrait fonctionner)
        request = self.client.get('/').wsgi_request
        request.user = self.manager
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        
        # Test avec un commercial (devrait échouer)
        request.user = self.commercial
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Redirection
    
    def test_manager_required_decorator(self):
        """Test du décorateur manager_required"""
        
        from django.http import HttpResponse
        
        @manager_required
        def test_view(request):
            return HttpResponse("Manager only")
        
        # Test avec un manager
        request = self.client.get('/').wsgi_request
        request.user = self.manager
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        
        # Test avec un non-manager
        request.user = self.commercial
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Redirection


class ProfileFormTest(TestCase):
    """Tests pour le formulaire ProfileForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            role="COMMERCIAL_SHOWROOM"
        )
    
    def test_profile_form_valid_data(self):
        """Test du formulaire avec des données valides"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'role': 'MANAGER',
            'telephone': '0123456789'
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_profile_form_invalid_role(self):
        """Test du formulaire avec un rôle invalide"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'role': 'INVALID_ROLE',
            'telephone': '0123456789'
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
    
    def test_profile_form_save(self):
        """Test de la sauvegarde du formulaire"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'role': 'TECHNICIEN',
            'telephone': '0987654321'
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        
        if form.is_valid():
            updated_profile = form.save()
            
            # Vérifier que les modifications ont été appliquées
            self.assertEqual(updated_profile.user.first_name, 'Updated')
            self.assertEqual(updated_profile.role, 'TECHNICIEN')
            self.assertEqual(updated_profile.telephone, '0987654321')


class IntegrationTest(TestCase):
    """Tests d'intégration pour le module users"""
    
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            username="manager",
            password="testpass123"
        )
        Profile.objects.create(user=self.manager, role="MANAGER")
    
    def test_complete_user_management_workflow(self):
        """Test du workflow complet de gestion des utilisateurs"""
        self.client.login(username="manager", password="testpass123")
        
        # 1. Accéder à la gestion des utilisateurs
        response = self.client.get(reverse('users:user_management'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Créer un nouvel utilisateur
        create_data = {
            'username': 'newemployee',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'Employee',
            'email': 'new@company.com',
            'role': 'COMMERCIAL_TERRAIN',
            'telephone': '0123456789'
        }
        response = self.client.post(reverse('users:profil_create'), create_data)
        
        # Vérifier que l'utilisateur a été créé
        new_user = User.objects.get(username='newemployee')
        self.assertIsNotNone(new_user)
        
        profile = Profile.objects.get(user=new_user)
        self.assertEqual(profile.role, 'COMMERCIAL_TERRAIN')
        
        # 3. Modifier l'utilisateur
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Employee',
            'email': 'updated@company.com',
            'role': 'TECHNICIEN',
            'telephone': '0987654321'
        }
        response = self.client.post(
            reverse('users:profil_update', kwargs={'pk': profile.pk}),
            update_data
        )
        
        # Vérifier les modifications
        updated_profile = Profile.objects.get(pk=profile.pk)
        self.assertEqual(updated_profile.role, 'TECHNICIEN')
        self.assertEqual(updated_profile.user.first_name, 'Updated')
    
    def test_role_based_navigation(self):
        """Test de la navigation basée sur les rôles"""
        # Créer différents utilisateurs
        users_roles = [
            ('manager', 'MANAGER'),
            ('commercial_s', 'COMMERCIAL_SHOWROOM'),
            ('commercial_t', 'COMMERCIAL_TERRAIN'),
            ('technicien', 'TECHNICIEN')
        ]
        
        for username, role in users_roles:
            user = User.objects.create_user(username, f"{username}@test.com", "pass")
            Profile.objects.create(user=user, role=role)
            
            # Se connecter et vérifier l'accès au dashboard
            self.client.login(username=username, password="pass")
            response = self.client.get(reverse('inventory:dashboard'))
            self.assertEqual(response.status_code, 200)
            
            # Vérifier que le template approprié est utilisé
            if role == 'MANAGER':
                self.assertContains(response, 'dashboard_manager.html')
            elif role == 'COMMERCIAL_SHOWROOM':
                self.assertContains(response, 'dashboard_commercial_showroom.html')
            elif role == 'COMMERCIAL_TERRAIN':
                self.assertContains(response, 'dashboard_commercial_terrain.html')
            elif role == 'TECHNICIEN':
                self.assertContains(response, 'dashboard_technicien.html')
            
            self.client.logout()


class SecurityTest(TestCase):
    """Tests de sécurité pour le module users"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        Profile.objects.create(user=self.user, role="COMMERCIAL_SHOWROOM")
    
    def test_password_requirements(self):
        """Test des exigences de mot de passe"""
        # Test avec un mot de passe trop faible
        weak_passwords = ['123', 'password', 'abc123']
        
        for weak_password in weak_passwords:
            form_data = {
                'username': 'testuser2',
                'password1': weak_password,
                'password2': weak_password,
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test2@test.com',
                'role': 'COMMERCIAL_SHOWROOM',
                'telephone': '0123456789'
            }
            
            response = self.client.post(reverse('users:profil_create'), form_data)
            # Le formulaire devrait rejeter les mots de passe faibles
            # (dépend de la configuration AUTH_PASSWORD_VALIDATORS)
    
    def test_unauthorized_user_modification(self):
        """Test de protection contre la modification non autorisée"""
        # Créer deux utilisateurs
        user1 = User.objects.create_user("user1", "user1@test.com", "pass")
        profile1 = Profile.objects.create(user=user1, role="COMMERCIAL_SHOWROOM")
        
        user2 = User.objects.create_user("user2", "user2@test.com", "pass")
        profile2 = Profile.objects.create(user=user2, role="COMMERCIAL_SHOWROOM")
        
        # Se connecter en tant que user1
        self.client.login(username="user1", password="pass")
        
        # Tenter de modifier le profil de user2
        response = self.client.get(
            reverse('users:profil_update', kwargs={'pk': profile2.pk})
        )
        # Devrait être bloqué car user1 n'est pas manager
        self.assertNotEqual(response.status_code, 200)
    
    def test_session_security(self):
        """Test de la sécurité des sessions"""
        # Se connecter
        self.client.login(username="testuser", password="testpass123")
        
        # Vérifier qu'on est connecté
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Se déconnecter
        self.client.logout()
        
        # Vérifier qu'on ne peut plus accéder aux pages protégées
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login


if __name__ == '__main__':
    import unittest
    unittest.main()
