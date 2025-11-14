from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from users.models import Profile
import getpass


class Command(BaseCommand):
    help = 'Créer un utilisateur avec un rôle spécifique'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nom d\'utilisateur')
        parser.add_argument('email', type=str, help='Adresse email')
        parser.add_argument('role', type=str, 
                          choices=['MANAGER', 'COMMERCIAL_SHOWROOM', 'COMMERCIAL_TERRAIN', 'TECHNICIEN'],
                          help='Rôle de l\'utilisateur')
        parser.add_argument('--first_name', type=str, help='Prénom', default='')
        parser.add_argument('--last_name', type=str, help='Nom de famille', default='')
        parser.add_argument('--telephone', type=str, help='Numéro de téléphone', default='')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        role = options['role']
        first_name = options['first_name']
        last_name = options['last_name']
        telephone = options['telephone']

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            raise CommandError(f'L\'utilisateur "{username}" existe déjà.')

        if User.objects.filter(email=email).exists():
            raise CommandError(f'L\'email "{email}" est déjà utilisé.')

        # Demander le mot de passe de manière sécurisée
        while True:
            password = getpass.getpass('Mot de passe : ')
            if len(password) < 6:
                self.stdout.write(
                    self.style.ERROR('Le mot de passe doit contenir au moins 6 caractères.')
                )
                continue
            
            confirm_password = getpass.getpass('Confirmer le mot de passe : ')
            if password != confirm_password:
                self.stdout.write(
                    self.style.ERROR('Les mots de passe ne correspondent pas.')
                )
                continue
            break

        try:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Créer le profil avec le rôle
            profile = Profile.objects.create(
                user=user,
                role=role,
                telephone=telephone
            )

            # Messages de succès avec style
            self.stdout.write(
                self.style.SUCCESS(f'✅ Utilisateur "{username}" créé avec succès!')
            )
            
            role_names = {
                'MANAGER': '👑 Manager',
                'COMMERCIAL_SHOWROOM': '🏪 Commercial Showroom', 
                'COMMERCIAL_TERRAIN': '🚀 Commercial Terrain',
                'TECHNICIEN': '🔧 Technicien'
            }
            
            self.stdout.write(
                self.style.SUCCESS(f'🎯 Rôle assigné : {role_names.get(role, role)}')
            )
            
            # Afficher les permissions
            self.stdout.write('\n📋 Permissions accordées :')
            if profile.can_manage_products():
                self.stdout.write('  ✅ Gestion des produits')
            if profile.can_manage_stock():
                self.stdout.write('  ✅ Gestion du stock')
            if profile.can_manage_sales():
                self.stdout.write('  ✅ Gestion des ventes')
            if profile.can_manage_orders():
                self.stdout.write('  ✅ Gestion des commandes')
            if profile.can_view_reports():
                self.stdout.write('  ✅ Consultation des rapports')
            if profile.can_manage_users():
                self.stdout.write('  ✅ Gestion des utilisateurs')
                
            self.stdout.write(
                self.style.SUCCESS(f'\n🔐 L\'utilisateur peut maintenant se connecter sur http://localhost:8000/accounts/login/')
            )

        except Exception as e:
            raise CommandError(f'Erreur lors de la création de l\'utilisateur : {str(e)}')
