# Module de Prospection Téléphonique

## Vue d'ensemble

Module complet de gestion de prospection téléphonique pour les commerciaux avec support des appels entrants et sortants.

## Fonctionnalités

### 1. Types d'Appels
- **Appel Sortant** : Appels initiés par le commercial
  - Champ email obligatoire
- **Appel Entrant** : Appels reçus de prospects
  - Champ source obligatoire (Contact email, Appel direct, Site web, Réseaux sociaux, Flyer, Visioconférence, Bouche à oreille)

### 2. Champs Disponibles
- **Nom complet** (obligatoire)
- **Numéro téléphonique** (obligatoire)
- **Statut** (obligatoire) : RDV, BV, Client acquis, À relancer
- **Date de RDV** (facultatif)
- **Description** (obligatoire) : Notes de la conversation
- **Email** (conditionnel) : Obligatoire pour appel sortant
- **Source de prospect** (conditionnel) : Obligatoire pour appel entrant
- **Type d'appel** (obligatoire) : Sortant ou Entrant

### 3. Code Couleur par Statut
- 🟡 **Jaune** : RDV (Rendez-vous fixé)
- 🔴 **Rouge** : BV (Bon de visite)
- 🟢 **Vert** : Client acquis (Conversion réussie)
- ⚪ **Gris** : À relancer (Suivi nécessaire)

### 4. Fonctionnalités CRUD Complètes
- ✅ **Créer** une fiche de prospection
- 📖 **Lire** la liste avec filtres avancés
- ✏️ **Modifier** une fiche existante
- 🗑️ **Supprimer** une fiche (avec confirmation)

### 5. Filtres et Recherche
- Recherche rapide : nom, téléphone, email, description
- Filtre par statut
- Filtre par type d'appel
- Filtre par source (appels entrants)
- Tri : plus récent, plus ancien, alphabétique, par statut

### 6. Statistiques
- Nombre total de prospections
- Nombre par statut (RDV, BV, Client acquis, À relancer)
- Nombre par type (Sortant, Entrant)
- Affichage en temps réel

### 7. Export
- **Export Excel/CSV** : Export de toutes les prospections avec les filtres actifs
- Format compatible Excel avec encodage UTF-8
- Séparateur point-virgule (;)

### 8. Permissions
- **Commercial Terrain** : Accès uniquement à ses propres prospections
- **Manager** : Accès à toutes les prospections
- **Admin** : Accès complet

## URLs

```python
# Liste et CRUD
/inventory/prospection/                        # Liste des prospections
/inventory/prospection/<id>/                   # Détails d'une prospection
/inventory/prospection/nouvelle/               # Créer une prospection
/inventory/prospection/<id>/modifier/          # Modifier une prospection
/inventory/prospection/<id>/supprimer/         # Supprimer une prospection

# Export et API
/inventory/prospection/export/excel/           # Export Excel/CSV
/inventory/prospection/stats/api/              # Statistiques JSON
```

## Modèle de Données

```python
class ProspectionTelephonique:
    # Champs principaux
    nom_complet: str
    numero_telephone: str
    statut: str  # RDV, BV, CLIENT_ACQUIS, A_RELANCER
    date_rdv: date (nullable)
    description: text
    type_appel: str  # SORTANT, ENTRANT
    
    # Champs conditionnels
    email: str (nullable)  # Obligatoire si SORTANT
    source_prospect: str (nullable)  # Obligatoire si ENTRANT
    
    # Métadonnées
    commercial: ForeignKey(User)
    date_creation: datetime
    date_modification: datetime
```

## Interface Utilisateur

### Page de Liste
- Tableau responsive avec pagination (20 résultats par page)
- Statistiques en haut de page (7 KPIs)
- Barre de filtres et recherche
- Code couleur pour statuts
- Icônes Font Awesome
- Actions rapides (Voir, Modifier, Supprimer)

### Formulaire de Création/Modification
- Formulaire dynamique qui s'adapte au type d'appel
- Validation côté client et serveur
- Messages d'erreur clairs
- Guide des statuts intégré
- Design responsive

### Page de Détails
- Affichage complet des informations
- Badge statut avec code couleur
- Métadonnées (dates création/modification)
- Actions rapides (Modifier, Supprimer, Email)

### Confirmation de Suppression
- Page de confirmation sécurisée
- Récapitulatif des informations
- Avertissement visible

## Utilisation

### Créer une Prospection
1. Cliquer sur "Nouvelle Prospection"
2. Sélectionner le type d'appel (Sortant ou Entrant)
3. Remplir les champs obligatoires
4. Ajouter une description détaillée
5. Enregistrer

### Filtrer les Prospections
1. Utiliser la barre de recherche pour chercher par nom, téléphone ou email
2. Utiliser les filtres déroulants pour affiner par statut, type ou source
3. Choisir l'ordre de tri
4. Cliquer sur "Filtrer"

### Exporter les Données
1. Appliquer les filtres souhaités
2. Cliquer sur "Exporter Excel"
3. Le fichier CSV sera téléchargé automatiquement
4. Ouvrir avec Excel, LibreOffice ou Google Sheets

## Développement

### Fichiers Créés
```
inventory/
├── models.py                              # Modèle ProspectionTelephonique
├── forms.py                               # ProspectionTelephoniqueForm
├── views_prospection.py                   # Toutes les vues
├── urls.py                                # URLs ajoutées
├── admin.py                               # Admin Django
└── migrations/
    └── 0007_prospectiontelephonique.py

templates/inventory/
├── prospection_list.html                  # Liste avec filtres
├── prospection_form.html                  # Formulaire CRUD
├── prospection_detail.html                # Page de détails
└── prospection_confirm_delete.html        # Confirmation suppression
```

### Technologies Utilisées
- **Backend** : Django 5.2.4
- **Frontend** : Tailwind CSS, Font Awesome
- **JavaScript** : Vanilla JS (pas de framework)
- **Base de données** : SQLite (compatible PostgreSQL, MySQL)

## API JSON

### Endpoint Statistiques
```
GET /inventory/prospection/stats/api/
```

Retourne:
```json
{
    "par_statut": {
        "RDV": 15,
        "BV": 8,
        "CLIENT_ACQUIS": 22,
        "A_RELANCER": 10
    },
    "par_type": {
        "SORTANT": 35,
        "ENTRANT": 20
    },
    "total": 55
}
```

## Migration

Pour appliquer la migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Tests Recommandés

1. ✅ Créer un appel sortant avec email
2. ✅ Créer un appel entrant avec source
3. ✅ Tenter de créer un appel sortant sans email (doit échouer)
4. ✅ Tenter de créer un appel entrant sans source (doit échouer)
5. ✅ Filtrer par statut
6. ✅ Rechercher par nom
7. ✅ Exporter en Excel
8. ✅ Modifier une prospection
9. ✅ Supprimer une prospection
10. ✅ Vérifier les permissions (commercial vs manager)

## Support

Pour toute question ou amélioration, contactez l'équipe de développement.

---

**Date de création** : 17 novembre 2025
**Version** : 1.0.0
**Auteur** : GitHub Copilot
