# 🎯 UTILISATEURS CRÉÉS - SYSTÈME DE RÔLES

## ✅ **Utilisateurs Disponibles**

Voici les utilisateurs créés dans la base de données avec leurs identifiants de connexion :

### 👑 **Manager (Administrateur)**
- **Identifiant** : `manager`
- **Mot de passe** : `manager123`
- **Rôle** : Manager (Administrateur)
- **Permissions** : Accès complet à tout le système

### 🏪 **Commercial Showroom (Ventes)**
- **Identifiant** : `commercial1` 
- **Mot de passe** : `commercial123`
- **Rôle** : Commercial Showroom (Ventes)
- **Permissions** : Gestion des produits et des ventes

### 🚗 **Commercial Terrain (Commandes/Clients)**
- **Identifiant** : `commercial2`
- **Mot de passe** : `commercial123`
- **Rôle** : Commercial Terrain (Commandes/Clients)
- **Permissions** : Gestion des clients et des commandes

### 🔧 **Technicien (Stock/SAV)**
- **Identifiant** : `technicien`
- **Mot de passe** : `tech123`
- **Rôle** : Technicien (Stock/SAV)
- **Permissions** : Gestion du stock et service après-vente

---

## 🔗 **Comment tester**

1. **Page de connexion** : http://127.0.0.1:8000/users/login/
2. **Utiliser un des comptes ci-dessus**
3. **Tester les permissions** : http://127.0.0.1:8000/users/role-test/

## 📋 **Vérification des utilisateurs**

Pour vérifier les utilisateurs dans la base de données :
```bash
python check_users.py
```

---

🎉 **TOUS LES UTILISATEURS SONT MAINTENANT CRÉÉS ET CONFIGURÉS !**
