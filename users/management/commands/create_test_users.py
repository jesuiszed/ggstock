from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile

class Command(BaseCommand):
    help = 'Créer des utilisateurs de test avec différents rôles'

    def handle(self, *args, **options):
        # Définir les utilisateurs à créer
        users_data = [
            {
                'username': 'manager',
                'password': 'manager123',
                'role': Profile.Role.MANAGER,
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'email': 'manager@ggstock.com',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'commercial1',
                'password': 'commercial123',
                'role': Profile.Role.COMMERCIAL_SHOWROOM,
                'first_name': 'Marie',
                'last_name': 'Martin',
                'email': 'commercial1@ggstock.com'
            },
            {
                'username': 'commercial2',
                'password': 'commercial123',
                'role': Profile.Role.COMMERCIAL_TERRAIN,
                'first_name': 'Pierre',
                'last_name': 'Durand',
                'email': 'commercial2@ggstock.com'
            },
            {
                'username': 'technicien',
                'password': 'tech123',
                'role': Profile.Role.TECHNICIEN,
                'first_name': 'Sophie',
                'last_name': 'Leroy',
                'email': 'technicien@ggstock.com'
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(
                    self.style.WARNING(f'L\'utilisateur {user_data["username"]} existe déjà.')
                )
                continue
            
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email']
            )
            
            # Définir les permissions admin si nécessaire
            if user_data.get('is_staff'):
                user.is_staff = True
            if user_data.get('is_superuser'):
                user.is_superuser = True
            user.save()
            
            # Le profil est créé automatiquement par le signal
            # Mettre à jour le rôle
            profile = user.profile
            profile.role = user_data['role']
            profile.save()
            
            created_users.append({
                'username': user.username,
                'role': profile.get_role_display()
            })
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Utilisateur créé: {user.username} ({profile.get_role_display()})'
                )
            )
        
        if created_users:
            self.stdout.write(
                self.style.SUCCESS(f'\n{len(created_users)} utilisateurs créés avec succès!')
            )
            self.stdout.write('\nInformations de connexion:')
            for user_data in users_data:
                if any(u['username'] == user_data['username'] for u in created_users):
                    self.stdout.write(f"- {user_data['username']} / {user_data['password']}")
        else:
            self.stdout.write(
                self.style.WARNING('Aucun nouvel utilisateur créé.')
            )
