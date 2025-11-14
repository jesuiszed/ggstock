from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile

class Command(BaseCommand):
    help = 'Créer des profils pour tous les utilisateurs qui n\'en ont pas'

    def handle(self, *args, **options):
        users_without_profile = []
        
        for user in User.objects.all():
            try:
                # Essayer d'accéder au profil
                user.profile
            except Profile.DoesNotExist:
                # Créer le profil s'il n'existe pas
                Profile.objects.create(user=user)
                users_without_profile.append(user.username)
        
        if users_without_profile:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Profils créés pour {len(users_without_profile)} utilisateurs: {", ".join(users_without_profile)}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Tous les utilisateurs ont déjà un profil.')
            )
