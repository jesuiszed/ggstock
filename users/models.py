from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    class Role(models.TextChoices):
        MANAGER = 'MANAGER', 'Manager (Administrateur)'
        COMMERCIAL_SHOWROOM = 'COMMERCIAL_SHOWROOM', 'Commercial 1 (Clients/Ventes/Commandes)'
        COMMERCIAL_TERRAIN = 'COMMERCIAL_TERRAIN', 'Commercial 2 (Clients/Devis/Prospects)'
        TECHNICIEN = 'TECHNICIEN', 'Technicien (Stock/SAV)'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=25, choices=Role.choices, default=Role.TECHNICIEN)
    date_creation = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=30, blank=True)
    
    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
    
    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'
    
    def can_manage_products(self):
        """Vérifie si l'utilisateur peut gérer les produits"""
        return self.role in [self.Role.MANAGER, self.Role.TECHNICIEN]
    
    def can_manage_clients(self):
        """Vérifie si l'utilisateur peut gérer les clients"""
        return self.role in [self.Role.MANAGER, self.Role.COMMERCIAL_SHOWROOM, self.Role.COMMERCIAL_TERRAIN]
    
    def can_manage_orders(self):
        """Vérifie si l'utilisateur peut gérer les commandes"""
        return self.role in [self.Role.MANAGER, self.Role.COMMERCIAL_SHOWROOM]
    
    def can_manage_sales(self):
        """Vérifie si l'utilisateur peut gérer les ventes"""
        return self.role in [self.Role.MANAGER, self.Role.COMMERCIAL_SHOWROOM]
    
    def can_manage_quotes(self):
        """Vérifie si l'utilisateur peut gérer les devis"""
        return self.role in [self.Role.MANAGER, self.Role.COMMERCIAL_TERRAIN]
    
    def can_manage_prospects(self):
        """Vérifie si l'utilisateur peut gérer les prospects"""
        return self.role in [self.Role.MANAGER, self.Role.COMMERCIAL_TERRAIN]
    
    def can_view_reports(self):
        """Vérifie si l'utilisateur peut voir les rapports"""
        return self.role in [self.Role.MANAGER, self.Role.COMMERCIAL_TERRAIN]
    
    def can_manage_stock(self):
        """Vérifie si l'utilisateur peut gérer le stock"""
        return self.role in [self.Role.MANAGER, self.Role.TECHNICIEN]
    
    def can_manage_suppliers(self):
        """Vérifie si l'utilisateur peut gérer les fournisseurs"""
        return self.role in [self.Role.MANAGER, self.Role.TECHNICIEN]
    
    def can_view_analytics(self):
        """Vérifie si l'utilisateur peut voir les analyses/statistiques"""
        return self.role == self.Role.MANAGER
    
    def can_manage_users(self):
        """Vérifie si l'utilisateur peut gérer les autres utilisateurs"""
        return self.role == self.Role.MANAGER
    
    def is_manager(self):
        """Vérifie si l'utilisateur est un manager"""
        return self.role == self.Role.MANAGER

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # S'assurer que le profil existe
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
