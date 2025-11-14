#!/usr/bin/env python
"""
Script pour afficher les utilisateurs et leurs rôles
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_inventory.settings')
sys.path.append('/Users/flozed/Desktop/ZPRO/mystock/stock/ggstock')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile

print("=== UTILISATEURS AVEC LEURS RÔLES ===")
print()

users_info = [
    {'username': 'manager', 'password': 'manager123', 'role': 'Manager'},
    {'username': 'commercial1', 'password': 'commercial123', 'role': 'Commercial Showroom'},
    {'username': 'commercial2', 'password': 'commercial123', 'role': 'Commercial Terrain'},
    {'username': 'technicien', 'password': 'tech123', 'role': 'Technicien'},
]

for info in users_info:
    try:
        user = User.objects.get(username=info['username'])
        role_actual = user.profile.get_role_display() if hasattr(user, 'profile') else "Pas de profil"
        status = "✅" if hasattr(user, 'profile') else "❌"
        print(f"{status} {info['username']} / {info['password']} → {role_actual}")
    except User.DoesNotExist:
        print(f"❌ {info['username']} → N'existe pas")

print(f"\nTotal utilisateurs: {User.objects.count()}")

# Corriger les rôles si nécessaire
print("\n=== CORRECTION DES RÔLES ===")

# Corriger commercial2
try:
    commercial2 = User.objects.get(username='commercial2')
    if commercial2.profile.role != Profile.Role.COMMERCIAL_TERRAIN:
        commercial2.profile.role = Profile.Role.COMMERCIAL_TERRAIN
        commercial2.profile.save()
        print("✅ commercial2 rôle corrigé → Commercial Terrain")
    else:
        print("✅ commercial2 rôle déjà correct")
except User.DoesNotExist:
    print("❌ commercial2 n'existe pas")

print("\n=== ÉTAT FINAL ===")
for user in User.objects.all():
    role = user.profile.get_role_display() if hasattr(user, 'profile') else "Pas de profil"
    print(f"{user.username} → {role}")
