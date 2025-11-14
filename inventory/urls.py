from django.urls import path
from . import views
from . import extended_views

app_name = 'inventory'

urlpatterns = [
    # Dashboard et accueil
    path('', views.dashboard, name='dashboard'),
    path('client/', views.client_homepage, name='client_homepage'),
    
    # Gestion des produits
    path('produits/', views.produits_list, name='produits_list'),
    path('produits/<int:pk>/', views.produit_detail, name='produit_detail'),
    path('produits/nouveau/', views.produit_create, name='produit_create'),
    path('produits/<int:pk>/modifier/', views.produit_update, name='produit_update'),
    path('produits/<int:pk>/supprimer/', views.produit_delete, name='produit_delete'),
    
    # Gestion des clients
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/nouveau/', views.client_create, name='client_create'),
    path('clients/<int:pk>/modifier/', views.client_update, name='client_update'),
    path('clients/<int:pk>/supprimer/', views.client_delete, name='client_delete'),
    
    # Gestion des fournisseurs
    path('fournisseurs/', views.fournisseurs_list, name='fournisseurs_list'),
    path('fournisseurs/<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),
    path('fournisseurs/nouveau/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),
    
    # Gestion des commandes
    path('commandes/', views.commandes_list, name='commandes_list'),
    path('commandes/guide/', views.commandes_guide, name='commandes_guide'),
    path('commandes/<int:pk>/', views.commande_detail, name='commande_detail'),
    path('commandes/nouvelle/', views.commande_create, name='commande_create'),
    path('commandes/avancee/', views.commande_create_advanced, name='commande_create_advanced'),
    path('commandes/<int:pk>/modifier/', views.commande_update, name='commande_update'),
    path('commandes/<int:pk>/supprimer/', views.commande_delete, name='commande_delete'),
    path('commandes/<int:pk>/bon-commande/', views.commande_print_bon, name='commande_print_bon'),
    path('commandes/<int:pk>/bon-livraison/', views.commande_print_livraison, name='commande_print_livraison'),
    path('commandes/<int:pk>/proforma/', views.commande_print_proforma, name='commande_print_proforma'),
    path('commandes/<int:commande_id>/pdf/', views.commande_generate_pdf, name='commande_generate_pdf'),
    
    # Gestion des ventes
    path('ventes/', views.ventes_list, name='ventes_list'),
    path('ventes/<int:pk>/', views.vente_detail, name='vente_detail'),
    path('ventes/nouvelle/', views.vente_create, name='vente_create'),
    path('ventes/<int:pk>/modifier/', views.vente_update, name='vente_update'),
    path('ventes/<int:pk>/proforma/', views.vente_print_proforma, name='vente_print_proforma'),
    path('ventes/<int:pk>/imprimer/', views.vente_print, name='vente_print'),
    path('ventes/<int:vente_id>/pdf/', views.vente_generate_pdf, name='vente_generate_pdf'),
    
    # Gestion du stock
    path('stock/', views.stock_list, name='stock_list'),
    
    # E-commerce public
    path('ecommerce/', views.ecommerce_home, name='ecommerce_home'),
    path('ecommerce/catalogue/', views.ecommerce_catalogue, name='ecommerce_catalogue'),
    path('ecommerce/produit/<int:pk>/', views.ecommerce_produit_detail, name='ecommerce_produit_detail'),
    
    # Authentification
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # API endpoints
    path('api/produit-search/', views.api_produit_search, name='api_produit_search'),
    path('api/client-search/', views.api_client_search, name='api_client_search'),
    
    # Gestion des mouvements de stock
    path('mouvements/nouveau/', views.mouvement_create, name='mouvement_create'),
    
    # ========== NOUVELLES FONCTIONNALITÉS BIOMÉDICALES ==========
    
    # Devis (Commercial Terrain)
    path('devis/', extended_views.devis_list, name='devis_list'),
    path('devis/<int:pk>/', extended_views.devis_detail, name='devis_detail'),
    path('devis/nouveau/', extended_views.devis_create, name='devis_create'),
    path('devis/<int:pk>/modifier/', extended_views.devis_edit, name='devis_edit'),
    path('devis/<int:pk>/pdf/', extended_views.devis_pdf, name='devis_pdf'),
    
    # Prospects (Commercial Terrain)
    path('prospects/', extended_views.prospect_list, name='prospect_list'),
    path('prospects/<int:pk>/', extended_views.prospect_detail, name='prospect_detail'),
    path('prospects/nouveau/', extended_views.prospect_create, name='prospect_create'),
    path('prospects/<int:pk>/modifier/', extended_views.prospect_edit, name='prospect_edit'),
    
    # Notes d'observation
    path('notes/nouvelle/', extended_views.note_create, name='note_create'),
    
    # Appareils vendus (Service Biomédical)
    path('appareils/', extended_views.appareil_list, name='appareil_list'),
    path('appareils/<int:pk>/', extended_views.appareil_detail, name='appareil_detail'),
    
    # Interventions SAV (Service Biomédical)
    path('interventions/', extended_views.intervention_list, name='intervention_list'),
    path('interventions/<int:pk>/', extended_views.intervention_detail, name='intervention_detail'),
    path('interventions/nouvelle/', extended_views.intervention_create, name='intervention_create'),
    path('interventions/<int:pk>/modifier/', extended_views.intervention_edit, name='intervention_edit'),
    
    # Transferts de stock (Technicien -> Showroom)
    path('transferts/', extended_views.transfert_list, name='transfert_list'),
    path('transferts/<int:pk>/', extended_views.transfert_detail, name='transfert_detail'),
    path('transferts/nouveau/', extended_views.transfert_create, name='transfert_create'),
    path('transferts/<int:pk>/modifier/', extended_views.transfert_edit, name='transfert_edit'),
]
