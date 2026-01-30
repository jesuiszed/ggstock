from django.contrib import admin
from .models import (
    Categorie, Fournisseur, Produit, MouvementStock, 
    Client, Commande, LigneCommande, Vente, LigneVente,
    Devis, LigneDevis, Prospect, NoteObservation, 
    AppareilVendu, InterventionSAV, TransfertStock,
    ProspectionTelephonique
)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'date_creation']
    search_fields = ['nom']
    list_filter = ['date_creation']


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'telephone', 'ville', 'actif', 'date_creation']
    search_fields = ['nom', 'email', 'ville']
    list_filter = ['ville', 'actif', 'date_creation']
    list_editable = ['actif']


class MouvementStockInline(admin.TabularInline):
    model = MouvementStock
    extra = 0
    readonly_fields = ['quantite_avant', 'quantite_apres', 'date_mouvement', 'utilisateur']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'reference', 'categorie', 'fournisseur', 
        'quantite_stock', 'prix_vente', 'is_stock_bas', 'actif'
    ]
    list_filter = ['categorie', 'fournisseur', 'actif', 'date_creation']
    search_fields = ['nom', 'reference', 'code_barre']
    list_editable = ['quantite_stock', 'prix_vente', 'actif']
    inlines = [MouvementStockInline]
    readonly_fields = ['date_creation', 'date_modification']
    
    def is_stock_bas(self, obj):
        return obj.is_stock_bas()
    is_stock_bas.boolean = True
    is_stock_bas.short_description = 'Stock bas'

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'reference', 'code_barre', 'description', 'image')
        }),
        ('Classification', {
            'fields': ('categorie', 'fournisseur')
        }),
        ('Prix et Stock', {
            'fields': ('prix_achat', 'prix_vente', 'quantite_stock', 'seuil_alerte')
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = [
        'produit', 'type_mouvement', 'quantite', 'quantite_avant', 
        'quantite_apres', 'utilisateur', 'date_mouvement'
    ]
    list_filter = ['type_mouvement', 'date_mouvement', 'utilisateur']
    search_fields = ['produit__nom', 'motif']
    readonly_fields = ['date_mouvement']
    date_hierarchy = 'date_mouvement'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'nom_complet', 'email', 'telephone', 'ville', 'actif', 'date_creation'
    ]
    search_fields = ['nom', 'prenom', 'email', 'telephone']
    list_filter = ['ville', 'actif', 'date_creation']
    list_editable = ['actif']
    
    def nom_complet(self, obj):
        return obj.nom_complet
    nom_complet.short_description = 'Nom complet'

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'email', 'telephone', 'date_naissance')
        }),
        ('Adresse', {
            'fields': ('adresse', 'ville', 'code_postal', 'pays')
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
    )


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1
    autocomplete_fields = ['produit']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'numero_commande', 'client', 'statut', 'total', 
        'date_commande', 'utilisateur'
    ]
    list_filter = ['statut', 'date_commande', 'utilisateur']
    search_fields = ['numero_commande', 'client__nom', 'client__prenom']
    inlines = [LigneCommandeInline]
    readonly_fields = ['date_commande', 'total']
    autocomplete_fields = ['client']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_commande', 'client', 'statut')
        }),
        ('Livraison', {
            'fields': ('date_livraison_prevue', 'adresse_livraison')
        }),
        ('Détails', {
            'fields': ('notes', 'total', 'date_commande')
        }),
    )


class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1
    autocomplete_fields = ['produit']


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = [
        'numero_vente', 'client', 'mode_paiement', 'total', 
        'date_vente', 'utilisateur'
    ]
    list_filter = ['mode_paiement', 'date_vente', 'utilisateur']
    search_fields = ['numero_vente', 'client__nom', 'client__prenom']
    inlines = [LigneVenteInline]
    readonly_fields = ['date_vente', 'total']
    autocomplete_fields = ['client']
    date_hierarchy = 'date_vente'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_vente', 'client', 'mode_paiement')
        }),
        ('Montants', {
            'fields': ('remise', 'total')
        }),
        ('Détails', {
            'fields': ('notes', 'date_vente')
        }),
    )


# ========== ADMINISTRATION DES NOUVEAUX MODÈLES BIOMÉDICAUX ==========

class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 1
    fields = ['produit', 'quantite', 'prix_unitaire', 'remise']


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ['numero_devis', 'client', 'statut', 'total', 'commercial', 'date_creation', 'date_validite']
    list_filter = ['statut', 'commercial', 'date_creation']
    search_fields = ['numero_devis', 'client__nom', 'client__prenom', 'client__entreprise']
    readonly_fields = ['numero_devis', 'total', 'date_creation']
    inlines = [LigneDevisInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_devis', 'client', 'commercial', 'statut')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_validite')
        }),
        ('Montant', {
            'fields': ('total',)
        }),
        ('Notes', {
            'fields': ('notes', 'conditions_particulieres'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'entreprise', 'email', 'telephone', 'statut', 'commercial', 'date_derniere_interaction']
    list_filter = ['statut', 'commercial', 'ville', 'date_creation']
    search_fields = ['nom', 'prenom', 'entreprise', 'email']
    list_editable = ['statut']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'email', 'telephone')
        }),
        ('Informations entreprise', {
            'fields': ('entreprise', 'adresse', 'ville')
        }),
        ('Suivi commercial', {
            'fields': ('statut', 'commercial', 'client_converti')
        }),
    )


@admin.register(NoteObservation)
class NoteObservationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_note', 'auteur', 'client', 'prospect', 'date_creation', 'terminee']
    list_filter = ['type_note', 'auteur', 'terminee', 'date_creation']
    search_fields = ['titre', 'contenu', 'client__nom', 'prospect__nom']
    list_editable = ['terminee']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('type_note', 'titre', 'contenu', 'auteur')
        }),
        ('Relations', {
            'fields': ('client', 'prospect')
        }),
        ('Suivi', {
            'fields': ('date_rappel', 'terminee')
        }),
    )


@admin.register(AppareilVendu)
class AppareilVenduAdmin(admin.ModelAdmin):
    list_display = ['numero_serie', 'produit', 'client', 'statut', 'prochaine_maintenance_preventive', 'est_maintenance_due', 'technicien_responsable']
    list_filter = ['statut', 'technicien_responsable', 'date_installation', 'prochaine_maintenance_preventive']
    search_fields = ['numero_serie', 'produit__nom', 'client__nom', 'lieu_installation']
    list_editable = ['statut']
    
    def est_maintenance_due(self, obj):
        return obj.est_maintenance_due()
    est_maintenance_due.boolean = True
    est_maintenance_due.short_description = 'Maintenance due'
    
    fieldsets = (
        ('Identification', {
            'fields': ('numero_serie', 'produit', 'client', 'vente')
        }),
        ('Installation', {
            'fields': ('date_installation', 'lieu_installation', 'statut', 'notes_installation')
        }),
        ('Maintenance', {
            'fields': ('prochaine_maintenance_preventive', 'derniere_maintenance', 'intervalle_maintenance_jours', 'technicien_responsable')
        }),
    )


@admin.register(InterventionSAV)
class InterventionSAVAdmin(admin.ModelAdmin):
    list_display = ['numero_intervention', 'type_intervention', 'appareil', 'client', 'technicien', 'date_prevue', 'statut']
    list_filter = ['type_intervention', 'statut', 'technicien', 'date_prevue']
    search_fields = ['numero_intervention', 'appareil__numero_serie', 'client__nom', 'description']
    readonly_fields = ['numero_intervention']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_intervention', 'type_intervention', 'appareil', 'client', 'technicien')
        }),
        ('Planification', {
            'fields': ('date_prevue', 'duree_prevue', 'statut', 'description')
        }),
        ('Réalisation', {
            'fields': ('date_realisee', 'duree_reelle', 'travaux_realises', 'pieces_changees', 'observations'),
            'classes': ('collapse',)
        }),
        ('Satisfaction client', {
            'fields': ('note_satisfaction', 'commentaire_client'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TransfertStock)
class TransfertStockAdmin(admin.ModelAdmin):
    list_display = ['numero_transfert', 'produit', 'quantite', 'origine', 'destination', 'statut', 'demandeur', 'date_creation']
    list_filter = ['statut', 'origine', 'destination', 'demandeur', 'date_creation']
    search_fields = ['numero_transfert', 'produit__nom', 'notes']
    readonly_fields = ['numero_transfert', 'date_creation']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_transfert', 'produit', 'quantite', 'notes')
        }),
        ('Transfert', {
            'fields': ('origine', 'destination', 'statut')
        }),
        ('Suivi', {
            'fields': ('demandeur', 'expediteur', 'recepteur', 'date_creation', 'date_expedition', 'date_reception')
        }),
    )


@admin.register(ProspectionTelephonique)
class ProspectionTelephoniqueAdmin(admin.ModelAdmin):
    list_display = [
        'nom_complet', 'numero_telephone', 'type_appel', 'statut', 
        'date_rdv', 'commercial', 'date_creation'
    ]
    list_filter = ['statut', 'type_appel', 'source_prospect', 'commercial', 'date_creation']
    search_fields = ['nom_complet', 'numero_telephone', 'email', 'description']
    readonly_fields = ['date_creation', 'date_modification']
    list_editable = ['statut']
    date_hierarchy = 'date_creation'
    
    fieldsets = (
        ('Informations de Contact', {
            'fields': ('nom_complet', 'numero_telephone', 'email')
        }),
        ('Type d\'Appel', {
            'fields': ('type_appel', 'source_prospect')
        }),
        ('Suivi Commercial', {
            'fields': ('statut', 'date_rdv', 'description', 'commercial')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtrer par commercial si l'utilisateur n'est pas admin
        return qs.filter(commercial=request.user)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si création
            obj.commercial = request.user
        super().save_model(request, obj, form, change)


# Configuration générale de l'admin
admin.site.site_header = "Enterprise Inventory - Administration"
admin.site.site_title = "Enterprise Inventory"
admin.site.index_title = "Gestion d'Inventaire d'Entreprise"

# Amélioration des autocomplete
Produit.search_fields = ['nom', 'reference']
Client.search_fields = ['nom', 'prenom', 'email']
