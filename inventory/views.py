from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import (
    Produit, Categorie, Fournisseur, Client, Commande, 
    Vente, MouvementStock, LigneVente, LigneCommande
)
from .forms import (
    ProduitForm, ClientForm, CommandeForm, VenteForm, 
    MouvementStockForm, FournisseurForm, CategorieForm
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO

# Imports pour la gestion des rôles
from users.decorators import role_required, permission_required
from users.models import Profile

# Page d'accueil client (catalogue public)
def client_homepage(request):
    # Produits actifs par catégorie
    categories = Categorie.objects.all()
    produits_nouveaux = Produit.objects.filter(
        actif=True, 
        quantite_stock__gt=0
    ).order_by('-date_creation')[:8]
    
    # Recherche
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    
    produits = Produit.objects.filter(actif=True, quantite_stock__gt=0)
    
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query) |
            Q(reference__icontains=query)
        )
    
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    # Pagination
    paginator = Paginator(produits, 12)
    page_number = request.GET.get('page')
    produits_page = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'produits_nouveaux': produits_nouveaux,
        'produits': produits_page,
        'query': query,
        'categorie_id': int(categorie_id) if categorie_id else None,
    }
    
    return render(request, 'inventory/client_homepage.html', context)


# Gestion des produits
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import (
    Produit, Categorie, Fournisseur, Client, Commande, 
    Vente, MouvementStock, LigneVente, LigneCommande
)
from .forms import (
    ProduitForm, ClientForm, CommandeForm, VenteForm, 
    MouvementStockForm, FournisseurForm, CategorieForm
)


# Vue d'accueil générale (Dashboard)
@login_required
def dashboard(request):
    # Obtenir le rôle de l'utilisateur
    try:
        user_role = request.user.profile.role
    except:
        # Si pas de profil, rediriger vers la création
        return redirect('admin:index')
    
    # Statistiques de base communes
    total_produits = Produit.objects.filter(actif=True).count()
    total_clients = Client.objects.filter(actif=True).count()
    total_fournisseurs = Fournisseur.objects.filter(actif=True).count()
    
    # Produits en stock bas
    produits_stock_bas = Produit.objects.filter(
        actif=True, 
        quantite_stock__lte=F('seuil_alerte')
    ).count()
    
    # Ventes du mois
    debut_mois = datetime.now().replace(day=1)
    ventes_mois = Vente.objects.filter(
        date_vente__gte=debut_mois
    ).aggregate(
        total=Sum('total'),
        count=Count('id')
    )
    
    # Commandes en attente
    commandes_attente = Commande.objects.filter(
        statut__in=['EN_ATTENTE', 'CONFIRMEE']
    ).count()
    
    # Derniers mouvements de stock
    derniers_mouvements = MouvementStock.objects.select_related(
        'produit', 'utilisateur'
    ).order_by('-date_mouvement')[:10]
    
    # Produits les plus vendus (30 derniers jours)
    fin_periode = datetime.now()
    debut_periode = fin_periode - timedelta(days=30)
    
    produits_populaires = Produit.objects.filter(
        lignevente__vente__date_vente__range=[debut_periode, fin_periode]
    ).annotate(
        total_vendu=Sum('lignevente__quantite')
    ).order_by('-total_vendu')[:5]
    
    # Context de base
    context = {
        'total_produits': total_produits,
        'total_clients': total_clients,
        'total_fournisseurs': total_fournisseurs,
        'produits_stock_bas': produits_stock_bas,
        'ventes_mois': ventes_mois,
        'commandes_attente': commandes_attente,
        'derniers_mouvements': derniers_mouvements,
        'produits_populaires': produits_populaires,
        'user_role': user_role,
    }

    # Dernières ventes (pour tous les rôles)
    dernieres_ventes = Vente.objects.select_related('client').order_by('-date_vente')[:5]
    context['dernieres_ventes'] = dernieres_ventes

    # Dernières commandes (pour tous les rôles)
    dernieres_commandes = Commande.objects.select_related('client', 'utilisateur').order_by('-date_commande')[:5]
    context['dernieres_commandes'] = dernieres_commandes

    
    # Choisir le template selon le rôle
    if user_role == 'MANAGER':
        # Statistiques complètes pour le manager
        context.update({
            'total_utilisateurs': Profile.objects.count(),
            'revenus_mois': ventes_mois.get('total', 0) or 0,
        })
        template = 'inventory/dashboard_manager.html'
        
    elif user_role == 'COMMERCIAL_SHOWROOM':
        # Statistiques pour commercial 1 (clients/ventes/commandes)
        mes_ventes = Vente.objects.filter(
            utilisateur=request.user,
            date_vente__gte=debut_mois
        ).aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        mes_commandes = Commande.objects.filter(
            utilisateur=request.user,
            date_commande__gte=debut_mois
        ).aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        commandes_en_cours = Commande.objects.filter(
            utilisateur=request.user,
            statut__in=['EN_ATTENTE', 'CONFIRMEE']
        ).count()
        
        context.update({
            'mes_ventes': mes_ventes,
            'mes_commandes': mes_commandes,
            'commandes_en_cours': commandes_en_cours,
            'stats': {
                'ventes_total': mes_ventes.get('total', 0) or 0,
                'ventes_count': mes_ventes.get('count', 0) or 0,
                'commandes_total': mes_commandes.get('total', 0) or 0,
                'commandes_count': mes_commandes.get('count', 0) or 0,
            },
        })
        template = 'inventory/dashboard_commercial_showroom.html'
        
    elif user_role == 'COMMERCIAL_TERRAIN':
        # Statistiques pour commercial 2 (clients/devis/prospects + rapports)
        try:
            from .models import Devis, Prospect
            mes_devis = Devis.objects.filter(commercial=request.user).aggregate(
                total=Count('id'),
                brouillon=Count('id', filter=Q(statut='BROUILLON')),
                envoyes=Count('id', filter=Q(statut='ENVOYE')),
                acceptes=Count('id', filter=Q(statut='ACCEPTE'))
            )
            
            mes_prospects = Prospect.objects.filter(commercial=request.user).aggregate(
                total=Count('id'),
                nouveaux=Count('id', filter=Q(statut='NOUVEAU')),
                qualifies=Count('id', filter=Q(statut='QUALIFIE')),
                convertis=Count('id', filter=Q(statut='CONVERTI'))
            )
        except:
            mes_devis = {'total': 0, 'brouillon': 0, 'envoyes': 0, 'acceptes': 0}
            mes_prospects = {'total': 0, 'nouveaux': 0, 'qualifies': 0, 'convertis': 0}
        
        context.update({
            'mes_devis': mes_devis,
            'mes_prospects': mes_prospects,
            'stats': {
                'devis_brouillon': mes_devis['brouillon'] or 0,
                'devis_envoyes': mes_devis['envoyes'] or 0,
                'devis_acceptes': mes_devis['acceptes'] or 0,
                'prospects_nouveaux': mes_prospects['nouveaux'] or 0,
            }
        })
        template = 'inventory/dashboard_commercial_terrain.html'
        
    elif user_role == 'TECHNICIEN':
        # Statistiques de stock pour technicien
        mouvements_recents = MouvementStock.objects.filter(
            utilisateur=request.user
        ).order_by('-date_mouvement')[:5]

        # Mouvements du jour
        today = datetime.now().date()
        mouvements_jour = MouvementStock.objects.filter(date_mouvement__date=today).count()
        entrees_jour = MouvementStock.objects.filter(date_mouvement__date=today, type_mouvement='ENTREE').aggregate(total=Sum('quantite'))['total'] or 0
        sorties_jour = MouvementStock.objects.filter(date_mouvement__date=today, type_mouvement='SORTIE').aggregate(total=Sum('quantite'))['total'] or 0

        # Valeur totale du stock
        valeur_stock = Produit.objects.filter(actif=True).aggregate(valeur=Sum(F('prix_vente') * F('quantite_stock')))['valeur'] or 0
        produits_actifs = Produit.objects.filter(actif=True).count()
        total_categories = Categorie.objects.count()

        # Fournisseurs principaux (par nombre de produits actifs)
        fournisseurs_principaux = Fournisseur.objects.annotate(
            produits_count=Count('produit', filter=Q(produit__actif=True))
        ).order_by('-produits_count')[:5]

        # Produits critiques (stock <= seuil)
        produits_critiques = Produit.objects.filter(actif=True, quantite_stock__lte=F('seuil_alerte'))

        # Nouvelles statistiques biomédicales pour Technicien
        try:
            from .models import AppareilVendu, InterventionSAV, TransfertStock
            from datetime import date
            
            # Appareils vendus sous ma responsabilité
            mes_appareils = AppareilVendu.objects.filter(technicien_responsable=request.user).aggregate(
                total=Count('id'),
                maintenance_due=Count('id', filter=Q(prochaine_maintenance_preventive__lte=date.today())),
                en_service=Count('id', filter=Q(statut='EN_SERVICE'))
            )
            
            # Interventions SAV
            mes_interventions = InterventionSAV.objects.filter(technicien=request.user).aggregate(
                total=Count('id'),
                planifiees=Count('id', filter=Q(statut='PLANIFIEE')),
                maintenance_preventive=Count('id', filter=Q(type_intervention='PREVENTIVE'))
            )
            
            # Transferts de stock
            mes_transferts = TransfertStock.objects.filter(
                Q(demandeur=request.user) | Q(expediteur=request.user) | Q(recepteur=request.user)
            ).aggregate(
                total=Count('id'),
                en_attente=Count('id', filter=Q(statut='EN_ATTENTE')),
                expedies=Count('id', filter=Q(statut='EXPEDIE'))
            )
        except:
            mes_appareils = {'maintenance_due': 0, 'en_service': 0}
            mes_interventions = {'planifiees': 0, 'maintenance_preventive': 0}
            mes_transferts = {'en_attente': 0, 'expedies': 0}

        context.update({
            'mes_mouvements': mouvements_recents,
            'produits_critique': produits_critiques.count(),
            'mouvements_jour': mouvements_jour,
            'entrees_jour': entrees_jour,
            'sorties_jour': sorties_jour,
            'valeur_stock': valeur_stock,
            'produits_actifs': produits_actifs,
            'total_categories': total_categories,
            'fournisseurs_principaux': fournisseurs_principaux,
            'produits_critiques': produits_critiques,
            'stats': {
                'maintenance_due': mes_appareils['maintenance_due'] or 0,
                'appareils_service': mes_appareils['en_service'] or 0,
                'interventions_planifiees': mes_interventions['planifiees'] or 0,
                'maintenance_preventive': mes_interventions['maintenance_preventive'] or 0,
                'transferts_attente': mes_transferts['en_attente'] or 0,
                'transferts_expedies': mes_transferts['expedies'] or 0,
            }
        })
        template = 'inventory/dashboard_technicien.html'
        
    else:
        # Par défaut, template manager
        template = 'inventory/dashboard_manager.html'
    
    return render(request, template, context)


# Page d'accueil client (catalogue public)
def client_homepage(request):
    # Produits actifs par catégorie
    categories = Categorie.objects.all()
    produits_nouveaux = Produit.objects.filter(
        actif=True, 
        quantite_stock__gt=0
    ).order_by('-date_creation')[:8]
    
    # Recherche
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    
    produits = Produit.objects.filter(actif=True, quantite_stock__gt=0)
    
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query) |
            Q(reference__icontains=query)
        )
    
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    # Pagination
    paginator = Paginator(produits, 12)
    page_number = request.GET.get('page')
    produits_page = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'produits_nouveaux': produits_nouveaux,
        'produits': produits_page,
        'query': query,
        'categorie_id': int(categorie_id) if categorie_id else None,
    }
    
    return render(request, 'inventory/client_homepage.html', context)


# ================== GESTION DES PRODUITS ==================

@login_required
@permission_required('can_manage_products')
def produits_list(request):
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    fournisseur_id = request.GET.get('fournisseur', '')
    stock_bas = request.GET.get('stock_bas', '')
    
    produits = Produit.objects.select_related('categorie', 'fournisseur')
    
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | 
            Q(reference__icontains=query) |
            Q(code_barre__icontains=query)
        )
    
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    if fournisseur_id:
        produits = produits.filter(fournisseur_id=fournisseur_id)
    
    if stock_bas:
        produits = produits.filter(quantite_stock__lte=F('seuil_alerte'))
    
    # Pagination
    paginator = Paginator(produits, 20)
    page_number = request.GET.get('page')
    produits_page = paginator.get_page(page_number)
    
    categories = Categorie.objects.all()
    fournisseurs = Fournisseur.objects.filter(actif=True)
    
    context = {
        'produits': produits_page,
        'categories': categories,
        'fournisseurs': fournisseurs,
        'query': query,
        'categorie_id': int(categorie_id) if categorie_id else None,
        'fournisseur_id': int(fournisseur_id) if fournisseur_id else None,
        'stock_bas': stock_bas,
    }
    
    return render(request, 'inventory/produits_list.html', context)


@login_required
def produit_detail(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    mouvements = MouvementStock.objects.filter(
        produit=produit
    ).select_related('utilisateur').order_by('-date_mouvement')[:20]
    
    context = {
        'produit': produit,
        'mouvements': mouvements,
    }
    
    return render(request, 'inventory/produit_detail.html', context)


@login_required
@permission_required('can_manage_products')
def produit_create(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save()
            # Créer un mouvement d'entrée initial si nécessaire
            if produit.quantite_stock > 0:
                MouvementStock.objects.create(
                    produit=produit,
                    type_mouvement='ENTREE',
                    quantite=produit.quantite_stock,
                    quantite_avant=0,
                    quantite_apres=produit.quantite_stock,
                    motif='Stock initial',
                    utilisateur=request.user
                )
            messages.success(request, f'Le produit {produit.nom} a été créé avec succès.')
            return redirect('inventory:produit_detail', pk=produit.pk)
    else:
        form = ProduitForm()
    
    return render(request, 'inventory/produit_form.html', {
        'form': form,
        'title': 'Nouveau Produit'
    })


@login_required
def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    ancien_stock = produit.quantite_stock
    
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            produit = form.save()
            
            # Si le stock a changé, créer un mouvement
            nouveau_stock = produit.quantite_stock
            if nouveau_stock != ancien_stock:
                if nouveau_stock > ancien_stock:
                    type_mouvement = 'ENTREE'
                    quantite = nouveau_stock - ancien_stock
                else:
                    type_mouvement = 'SORTIE'
                    quantite = ancien_stock - nouveau_stock
                
                MouvementStock.objects.create(
                    produit=produit,
                    type_mouvement=type_mouvement,
                    quantite=quantite,
                    quantite_avant=ancien_stock,
                    quantite_apres=nouveau_stock,
                    motif='Ajustement manuel',
                    utilisateur=request.user
                )
            
            messages.success(request, f'Le produit {produit.nom} a été modifié avec succès.')
            return redirect('inventory:produit_detail', pk=produit.pk)
    else:
        form = ProduitForm(instance=produit)
    
    return render(request, 'inventory/produit_form.html', {
        'form': form,
        'produit': produit,
        'title': f'Modifier {produit.nom}'
    })


@login_required
def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    
    if request.method == 'POST':
        nom_produit = produit.nom
        produit.delete()
        messages.success(request, f'Le produit {nom_produit} a été supprimé avec succès.')
        return redirect('inventory:produits_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': produit,
        'object_name': 'produit'
    })


# ================== GESTION DES CLIENTS ==================

@login_required
def clients_list(request):
    query = request.GET.get('q', '')
    ville = request.GET.get('ville', '')
    
    clients = Client.objects.all()
    
    if query:
        clients = clients.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(telephone__icontains=query)
        )
    
    if ville:
        clients = clients.filter(ville__icontains=ville)
    
    # Pagination
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)
    
    # Villes pour le filtre
    villes = Client.objects.values_list('ville', flat=True).distinct().order_by('ville')
    
    context = {
        'clients': clients_page,
        'villes': villes,
        'query': query,
        'ville': ville,
    }
    
    return render(request, 'inventory/clients_list.html', context)


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    # Dernières commandes
    commandes = Commande.objects.filter(client=client).order_by('-date_commande')[:10]
    
    # Dernières ventes
    ventes = Vente.objects.filter(client=client).order_by('-date_vente')[:10]
    
    # Statistiques
    total_commandes = Commande.objects.filter(client=client).aggregate(
        total=Sum('total'),
        count=Count('id')
    )
    
    total_ventes = Vente.objects.filter(client=client).aggregate(
        total=Sum('total'),
        count=Count('id')
    )
    
    context = {
        'client': client,
        'commandes': commandes,
        'ventes': ventes,
        'total_commandes': total_commandes,
        'total_ventes': total_ventes,
    }
    
    return render(request, 'inventory/client_detail.html', context)


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Le client {client.nom_complet} a été créé avec succès.')
            return redirect('inventory:client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    return render(request, 'inventory/client_form.html', {
        'form': form,
        'title': 'Nouveau Client'
    })


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Le client {client.nom_complet} a été modifié avec succès.')
            return redirect('inventory:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'inventory/client_form.html', {
        'form': form,
        'client': client,
        'title': f'Modifier {client.nom_complet}'
    })


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        nom_client = client.nom_complet
        client.delete()
        messages.success(request, f'Le client {nom_client} a été supprimé avec succès.')
        return redirect('inventory:clients_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': client,
        'object_name': 'client'
    })


# ================== GESTION DES FOURNISSEURS ==================

@login_required
def fournisseurs_list(request):
    query = request.GET.get('q', '')
    ville = request.GET.get('ville', '')
    
    fournisseurs = Fournisseur.objects.all()
    
    if query:
        fournisseurs = fournisseurs.filter(
            Q(nom__icontains=query) |
            Q(email__icontains=query)
        )
    
    if ville:
        fournisseurs = fournisseurs.filter(ville__icontains=ville)
    
    # Pagination
    paginator = Paginator(fournisseurs, 20)
    page_number = request.GET.get('page')
    fournisseurs_page = paginator.get_page(page_number)
    
    # Villes pour le filtre
    villes = Fournisseur.objects.values_list('ville', flat=True).distinct().order_by('ville')
    
    context = {
        'fournisseurs': fournisseurs_page,
        'villes': villes,
        'query': query,
        'ville': ville,
    }
    
    return render(request, 'inventory/fournisseurs_list.html', context)


@login_required
def fournisseur_detail(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    # Produits de ce fournisseur
    produits = Produit.objects.filter(fournisseur=fournisseur).order_by('nom')
    
    # Statistiques
    stats = {
        'total_produits': produits.count(),
        'produits_actifs': produits.filter(actif=True).count(),
        'valeur_stock': sum([p.quantite_stock * p.prix_achat for p in produits]),
    }
    
    context = {
        'fournisseur': fournisseur,
        'produits': produits[:10],  # Limiter l'affichage
        'stats': stats,
    }
    
    return render(request, 'inventory/fournisseur_detail.html', context)


@login_required
def fournisseur_create(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Le fournisseur {fournisseur.nom} a été créé avec succès.')
            return redirect('inventory:fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm()
    
    return render(request, 'inventory/fournisseur_form.html', {
        'form': form,
        'title': 'Nouveau Fournisseur'
    })


@login_required
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Le fournisseur {fournisseur.nom} a été modifié avec succès.')
            return redirect('inventory:fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm(instance=fournisseur)
    
    return render(request, 'inventory/fournisseur_form.html', {
        'form': form,
        'fournisseur': fournisseur,
        'title': f'Modifier {fournisseur.nom}'
    })


@login_required
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        nom_fournisseur = fournisseur.nom
        fournisseur.delete()
        messages.success(request, f'Le fournisseur {nom_fournisseur} a été supprimé avec succès.')
        return redirect('inventory:fournisseurs_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': fournisseur,
        'object_name': 'fournisseur'
    })


# ================== GESTION DES COMMANDES ==================

@login_required
def commandes_list(request):
    statut = request.GET.get('statut', '')
    query = request.GET.get('q', '')
    
    commandes = Commande.objects.select_related('client', 'utilisateur')
    
    if statut:
        commandes = commandes.filter(statut=statut)
    
    if query:
        commandes = commandes.filter(
            Q(numero_commande__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(client__prenom__icontains=query)
        )
    
    commandes = commandes.order_by('-date_commande')
    
    # Statistiques pour les badges
    stats = {
        'en_attente': Commande.objects.filter(statut='EN_ATTENTE').count(),
        'confirmees': Commande.objects.filter(statut='CONFIRMEE').count(),
        'expediees': Commande.objects.filter(statut='EXPEDIEE').count(),
        'total_mois': Commande.objects.filter(
            date_commande__gte=datetime.now().replace(day=1)
        ).aggregate(total=Sum('total'))['total'] or 0,
    }
    
    # Pagination
    paginator = Paginator(commandes, 20)
    page_number = request.GET.get('page')
    commandes_page = paginator.get_page(page_number)
    
    context = {
        'commandes': commandes_page,
        'statut_choices': Commande.STATUT_CHOICES,
        'statut': statut,
        'query': query,
        'stats': stats,
    }
    
    return render(request, 'inventory/commandes_list.html', context)


@login_required
def commandes_guide(request):
    """Guide d'utilisation des commandes"""
    return render(request, 'inventory/commandes_guide.html')


@login_required
def commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    lignes = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    context = {
        'commande': commande,
        'lignes': lignes,
    }
    
    return render(request, 'inventory/commande_detail.html', context)


@login_required
def commande_create(request):
    """Créer une nouvelle commande avec parsing manuel des lignes"""
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    commande = form.save(commit=False)
                    commande.utilisateur = request.user
                    commande.save()
                    
                    # Traitement des lignes de produit - LOGIQUE ROBUSTE
                    lines_created = 0
                    has_error = False
                    
                    # Parser toutes les clés POST pour trouver TOUTES les lignes de produit
                    lines_data = {}
                    for key in request.POST:
                        if key.startswith('ligne_') and '_' in key:
                            parts = key.split('_', 2)
                            if len(parts) == 3:
                                line_idx = parts[1]
                                field_name = parts[2]
                                
                                if line_idx not in lines_data:
                                    lines_data[line_idx] = {}
                                lines_data[line_idx][field_name] = request.POST[key]
                    
                    print(f"=== DEBUG COMMANDE_CREATE ===")
                    print(f"POST data: {request.POST}")
                    print(f"Lignes trouvées: {sorted(lines_data.keys())}")
                    
                    # Traiter chaque ligne trouvée (triée par index)
                    for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                        data = lines_data[line_idx]
                        produit_id = data.get('produit')
                        quantite = data.get('quantite')
                        prix_unitaire = data.get('prix_unitaire')
                        
                        print(f"Traitement ligne {line_idx}: produit={produit_id}, quantite={quantite}, prix={prix_unitaire}")
                        
                        # Ignorer les lignes vides
                        if not produit_id:
                            print(f"Ligne {line_idx} ignorée (pas de produit)")
                            continue
                        
                        # Vérifier que tous les champs requis sont présents
                        if not quantite or not prix_unitaire:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Quantité et prix requis')
                            has_error = True
                            continue
                        
                        try:
                            produit = Produit.objects.get(id=produit_id)
                            quantite = int(quantite)
                            prix_unitaire = float(prix_unitaire)
                            
                            # Validation
                            if quantite <= 0:
                                messages.error(request, f'{produit.nom}: La quantité doit être positive')
                                has_error = True
                                continue
                            
                            if prix_unitaire < 0:
                                messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                                has_error = True
                                continue
                            
                            # Vérifier le stock disponible (warning, pas bloquant)
                            if quantite > produit.quantite_stock:
                                messages.warning(request, f'{produit.nom}: Stock insuffisant ({produit.quantite_stock} disponibles)')
                            
                            # Créer la ligne de commande
                            ligne = LigneCommande.objects.create(
                                commande=commande,
                                produit=produit,
                                quantite=quantite,
                                prix_unitaire=prix_unitaire
                            )
                            lines_created += 1
                            print(f"✓ Ligne {line_idx} créée: {ligne}")
                            
                        except Produit.DoesNotExist:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Produit introuvable')
                            has_error = True
                            continue
                        except (ValueError, TypeError) as e:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Erreur de conversion - {str(e)}')
                            has_error = True
                            continue
                    
                    print(f"✓ Total de lignes créées: {lines_created}")
                    
                    # Si erreur détectée, annuler la transaction
                    if has_error:
                        raise ValueError('Erreurs détectées dans les lignes')
                    
                    # Vérifier qu'au moins une ligne a été créée
                    if lines_created == 0:
                        messages.error(request, 'Une commande doit contenir au moins un produit')
                        raise ValueError('Aucune ligne de produit')
                    
                    # Calculer le total
                    commande.calculer_total()
                    
                    messages.success(request, f'Commande {commande.numero_commande} créée avec succès ({lines_created} ligne(s)).')
                    return redirect('inventory:commande_detail', pk=commande.pk)
                    
            except ValueError as e:
                # Erreur de validation, le formulaire sera réaffiché avec les erreurs
                print(f"Erreur de validation: {e}")
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CommandeForm()
    
    # Récupérer tous les produits actifs pour le formulaire
    produits = Produit.objects.filter(actif=True).order_by('nom')
    clients = Client.objects.filter(actif=True).order_by('nom', 'prenom')

    context = {
        'form': form,
        'title': 'Nouvelle Commande',
        'produits': produits,
        'clients': clients
    }
    
    return render(request, 'inventory/commande_form.html', context)


# Company information for all documents - Style DIMAT MEDICAL
COMPANY_INFO = {
    'name': 'DIMAT MEDICAL',
    'subtitle': 'CHIRURGIE GENERALE - RADIOLOGIE - IMAGERIE MÉDICALE',
    'address': '123 Rue Médicale, 75000 Paris, France',
    'phone': '+33 1 23 45 67 89',
    'fax': '+33 1 23 45 67 90',
    'email': 'contact@dimatmedical.com',
    'website': 'www.dimatmedical.com',
    'siret': 'SIRET: 123 456 789 00012',
    'vat': 'TVA: FR12123456789',
    'logo_path': 'static/images/logo.png'  # Placeholder for logo
}

# Common styles for all documents
def get_document_styles():
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#1e3a8a')
        ),
        'subtitle': ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#1e3a8a')
        ),
        'normal': ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8
        ),
        'footer': ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    }

# Common header for all documents
def build_header(story, title_text, styles):
    # Logo placeholder (replace with actual logo path)
    try:
        logo = Image(COMPANY_INFO['logo_path'], width=1.5*inch, height=0.75*inch)
        story.append(logo)
    except:
        story.append(Paragraph("Logo Placeholder", styles['normal']))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 10))
    
    # Company information
    company_data = [
        [COMPANY_INFO['name']],
        [COMPANY_INFO['address']],
        [f"Tél: {COMPANY_INFO['phone']} | Email: {COMPANY_INFO['email']}"],
        [f"{COMPANY_INFO['siret']} | {COMPANY_INFO['vat']}"]
    ]
    company_table = Table(company_data, colWidths=[6*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(company_table)
    story.append(Spacer(1, 20))

# Common footer for all documents
def build_footer(canvas, doc):
    canvas.saveState()
    footer_text = f"{COMPANY_INFO['name']} | {COMPANY_INFO['address']} | Tél: {COMPANY_INFO['phone']} | Email: {COMPANY_INFO['email']} | {COMPANY_INFO['siret']} | {COMPANY_INFO['vat']}"
    footer = Paragraph(footer_text, get_document_styles()['footer'])
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin, doc.bottomMargin - 10)
    canvas.restoreState()

@login_required
def commande_print_bon(request, pk):
    """Générer le bon de commande en PDF professionnel avec WeasyPrint"""
    from django.template.loader import render_to_string
    from weasyprint import HTML
    from django.http import HttpResponse
    from decimal import Decimal
    from datetime import datetime
    
    commande = get_object_or_404(Commande, pk=pk)
    lignes_commande = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    # Calculer TVA et Total TTC
    tva = commande.total * Decimal('0.18')
    total_ttc = commande.total + tva
    
    # Calculer quantité totale
    total_quantity = sum(ligne.quantite for ligne in lignes_commande)
    
    # Informations entreprise
    company_info = {
        'company_address': 'Dakar, Sénégal',
        'company_phone': '+221 XX XXX XX XX',
        'company_email': 'contact@dimatmedical.sn',
    }
    
    # Préparer le contexte
    context = {
        'commande': commande,
        'lignes_commande': lignes_commande,
        'tva': tva,
        'total_ttc': total_ttc,
        'total_quantity': total_quantity,
        'now': datetime.now(),
        **company_info
    }
    
    # Rendre le template HTML
    html_string = render_to_string('inventory/bon_commande_pdf.html', context)
    
    # Générer le PDF avec WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    
    # Créer la réponse HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bon_Commande_{commande.numero_commande}.pdf"'
    
    return response

@login_required
def commande_print_livraison(request, pk):
    """Générer le bon de livraison en PDF selon le modèle DIMAT MEDICAL"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from io import BytesIO
    
    commande = get_object_or_404(Commande, pk=pk)
    lignes = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=2*cm)
    story = []
    
    # Styles personnalisés
    styles = getSampleStyleSheet()
    
    # En-tête entreprise style DIMAT MEDICAL
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # En-tête avec logo et infos entreprise
    header_data = [
        [Paragraph("DIMAT MEDICAL", company_style), "", Paragraph("CODE CLIENT:", styles['Normal']), commande.client.id if commande.client else ""],
        [Paragraph("CHIRURGIE GENERALE - RADIOLOGIE - IMAGERIE MÉDICALE", subtitle_style), "", "", ""],
        [Paragraph(f"Tél: {COMPANY_INFO['phone']} Fax: {COMPANY_INFO['fax']}", styles['Normal']), "", Paragraph("DIVERS CLIENT", styles['Normal']), ""],
        [Paragraph(f"RC: 123456 - Email: {COMPANY_INFO['email']}", styles['Normal']), "", "", ""]
    ]
    
    header_table = Table(header_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (2, 0), (3, 2), 1, colors.black),
        ('GRID', (2, 0), (3, 2), 0.5, colors.black),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Titre du document
    story.append(Paragraph("BON DE LIVRAISON", title_style))
    story.append(Spacer(1, 15))
    
    # Informations de la livraison
    info_data = [
        ["NUMERO", "DATE", "REFERENCE", "CLIENT SUIVI PAR:", "AFFAIRE/OBJECTIF"],
        [commande.numero_commande, 
         commande.date_commande.strftime('%d/%m/%y'), 
         commande.numero_commande,
         commande.utilisateur.get_full_name() or commande.utilisateur.username,
         commande.client.nom_complet if commande.client else "Client comptoir"]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.8*inch, 1.7*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # Tableau des produits pour bon de livraison (simplifié)
    if lignes:
        # En-tête du tableau simplifié
        data = [['Référence', 'Désignation', 'Qte', 'Observation']]
        
        # Lignes de produits
        for ligne in lignes:
            data.append([
                ligne.produit.reference or 'N/A',
                ligne.produit.nom[:50] + '...' if len(ligne.produit.nom) > 50 else ligne.produit.nom,
                str(ligne.quantite),
                ""  # Observation vide par défaut
            ])
        
        # Créer le tableau principal
        main_table = Table(data, colWidths=[1.5*inch, 3.5*inch, 1*inch, 2*inch])
        main_table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Corps du tableau
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Référence à gauche
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Désignation à gauche
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Qte et observation centrées
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 30))
        
        # Section cachet et visa client
        visa_data = [
            ["Cachet et Visa Client"],
            [""],
            [""],
            [""],
            [""]
        ]
        
        visa_table = Table(visa_data, colWidths=[4*inch], rowHeights=[0.4*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch])
        visa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(visa_table)
    
    # Conditions générales en bas
    story.append(Spacer(1, 30))
    conditions_text = """Conditions de ventes - La marchandise est sous la responsabilité du client dès la signature et le cachet du bon de livraison. Toutes les réclamations formulées après cette décharge ne seront pas prises en compte. Conformément à l'article 314 de l'Acte Uniforme du Droit Commercial Général, le transfert de propriété de la marchandise ne s'effectue qu'au jour du paiement complet et de toute satisfaction et notre propriété."""
    
    story.append(Paragraph(conditions_text, ParagraphStyle(
        'Conditions',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_JUSTIFY
    )))
    
    # Construire le PDF
    doc.build(story)
    
    # Retourner la réponse
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bon_livraison_{commande.numero_commande}.pdf"'
    return response  # Générer le bon de livraison en PDF
    commande = get_object_or_404(Commande, pk=pk)
    lignes = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    if commande.statut not in ['EXPEDIEE', 'LIVREE']:
        messages.error(request, 'Le bon de livraison ne peut être généré que pour les commandes expédiées ou livrées.')
        return redirect('inventory:commande_detail', pk=pk)
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.75*inch)
    story = []
    styles = get_document_styles()
    
    # Header
    build_header(story, "BON DE LIVRAISON", styles)
    
    # Commande information
    info_data = [
        ['Numéro de commande:', commande.numero_commande],
        ['Date de commande:', commande.date_commande.strftime('%d/%m/%Y')],
        ['Date de livraison:', commande.date_livraison_prevue.strftime('%d/%m/%Y') if commande.date_livraison_prevue else 'Non définie'],
        ['Client:', commande.client.nom_complet],
        ['Adresse de livraison:', commande.adresse_livraison],
        ['Statut:', commande.get_statut_display()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Tableau des produits
    if lignes:
        story.append(Paragraph("PRODUITS LIVRÉS", styles['subtitle']))
        story.append(Spacer(1, 10))
        
        data = [['Produit', 'Référence', 'Quantité livrée', 'État']]
        for ligne in lignes:
            data.append([
                ligne.produit.nom,
                ligne.produit.reference or 'N/A',
                str(ligne.quantite),
                'Livré'
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
    
    # Signature section
    story.append(Spacer(1, 30))
    story.append(Paragraph("VÉRIFICATION DE LA LIVRAISON", styles['subtitle']))
    signature_data = [
        ['Signature du livreur:', 'Signature du client:'],
        ['', ''],
        ['Date: _______________', 'Date: _______________']
    ]
    
    signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 40),
        ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(signature_table)
    
    # Notes
    if commande.notes:
        story.append(Spacer(1, 20))
        story.append(Paragraph("NOTES:", styles['subtitle']))
        story.append(Paragraph(commande.notes, styles['normal']))
    
    # Build PDF with footer
    doc.build(story, onFirstPage=build_footer, onLaterPages=build_footer)
    
    # Return response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bon_livraison_{commande.numero_commande}.pdf"'
    return response

@login_required
def commande_print_facture(request, pk):
    """Générer la facture en PDF"""
    commande = get_object_or_404(Commande, pk=pk)
    lignes = LigneCommande.objects.filter(commande=commande).select_related('produit')
    total = commande.total
    
    if commande.statut != 'LIVREE':
        messages.error(request, 'La facture ne peut être générée que pour les commandes livrées.')
        return redirect('inventory:commande_detail', pk=pk)
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.75*inch)
    story = []
    styles = get_document_styles()
    
    # Header
    build_header(story, "FACTURE", styles)
    
    # Billing information
    billing_data = [
        ['FACTURÉ À:'],
        [commande.client.nom_complet],
        [commande.client.email],
        [commande.client.telephone or 'Non renseigné'],
        [commande.adresse_livraison]
    ]
    
    billing_table = Table(billing_data, colWidths=[6*inch])
    billing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 20))
    
    # Invoice information
    invoice_data = [
        ['Numéro de facture:', f"FACT-{commande.numero_commande}"],
        ['Date de facture:', commande.date_commande.strftime('%d/%m/%Y')],
        ['Numéro de commande:', commande.numero_commande],
        ['Date de livraison:', commande.date_livraison_prevue.strftime('%d/%m/%Y') if commande.date_livraison_prevue else 'Non définie'],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Tableau des produits
    if lignes:
        story.append(Paragraph("DÉTAIL DE LA FACTURE", styles['subtitle']))
        story.append(Spacer(1, 10))
        
        data = [['Description', 'Qté', 'Prix unitaire HT', 'Total HT']]
        subtotal = 0
        for ligne in lignes:
            total_ligne = ligne.sous_total()
            subtotal += total_ligne
            data.append([
                ligne.produit.nom,
                str(ligne.quantite),
                f"{ligne.prix_unitaire:.2f}F CFA",
                f"{total_ligne:.2f}F CFA"
            ])
        
        from decimal import Decimal
        tva_rate = Decimal('0.20')
        tva_amount = subtotal * tva_rate
        total_ttc = subtotal + tva_amount
        
        data.append(['', '', 'Sous-total HT:', f"{subtotal:.2f}F CFA"])
        data.append(['', '', f'TVA ({tva_rate*100:.0f}%):', f"{tva_amount:.2f}F CFA"])
        data.append(['', '', 'TOTAL TTC:', f"{total_ttc:.2f}F CFA"])
        
        table = Table(data, colWidths=[3*inch, 0.8*inch, 1.6*inch, 1.6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -4), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
    
    # Conditions de paiement
    story.append(Spacer(1, 20))
    story.append(Paragraph("CONDITIONS DE PAIEMENT", styles['subtitle']))
    conditions = [
        "• Paiement à 30 jours fin de mois",
        "• Escompte de 2% pour paiement à 8 jours",
        "• Pénalités de retard : 3 fois le taux légal",
        "• Indemnité forfaitaire de recouvrement : 40F CFA"
    ]
    for condition in conditions:
        story.append(Paragraph(condition, styles['normal']))
    
    # Notes
    if commande.notes:
        story.append(Spacer(1, 20))
        story.append(Paragraph("NOTES:", styles['subtitle']))
        story.append(Paragraph(commande.notes, styles['normal']))
    
    # Build PDF with footer
    doc.build(story, onFirstPage=build_footer, onLaterPages=build_footer)
    
    # Return response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{commande.numero_commande}.pdf"'
    return response
    
@login_required
def commande_update(request, pk):
    """Modifier une commande avec parsing manuel des lignes"""
    commande = get_object_or_404(Commande, pk=pk)
    
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    commande = form.save()
                    
                    # Supprimer les anciennes lignes
                    commande.lignecommande_set.all().delete()
                    
                    # Traitement des lignes de produit - LOGIQUE ROBUSTE
                    lines_created = 0
                    has_error = False
                    
                    # Parser toutes les clés POST pour trouver TOUTES les lignes de produit
                    lines_data = {}
                    for key in request.POST:
                        if key.startswith('ligne_') and '_' in key:
                            parts = key.split('_', 2)
                            if len(parts) == 3:
                                line_idx = parts[1]
                                field_name = parts[2]
                                
                                if line_idx not in lines_data:
                                    lines_data[line_idx] = {}
                                lines_data[line_idx][field_name] = request.POST[key]
                    
                    print(f"=== DEBUG COMMANDE_UPDATE ===")
                    print(f"POST data: {request.POST}")
                    print(f"Lignes trouvées: {sorted(lines_data.keys())}")
                    
                    # Traiter chaque ligne trouvée (triée par index)
                    for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                        data = lines_data[line_idx]
                        produit_id = data.get('produit')
                        quantite = data.get('quantite')
                        prix_unitaire = data.get('prix_unitaire')
                        
                        print(f"Traitement ligne {line_idx}: produit={produit_id}, quantite={quantite}, prix={prix_unitaire}")
                        
                        # Ignorer les lignes vides
                        if not produit_id:
                            print(f"Ligne {line_idx} ignorée (pas de produit)")
                            continue
                        
                        # Vérifier que tous les champs requis sont présents
                        if not quantite or not prix_unitaire:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Quantité et prix requis')
                            has_error = True
                            continue
                        
                        try:
                            produit = Produit.objects.get(id=produit_id)
                            quantite = int(quantite)
                            prix_unitaire = float(prix_unitaire)
                            
                            # Validation
                            if quantite <= 0:
                                messages.error(request, f'{produit.nom}: La quantité doit être positive')
                                has_error = True
                                continue
                            
                            if prix_unitaire < 0:
                                messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                                has_error = True
                                continue
                            
                            # Créer la ligne de commande
                            ligne = LigneCommande.objects.create(
                                commande=commande,
                                produit=produit,
                                quantite=quantite,
                                prix_unitaire=prix_unitaire
                            )
                            lines_created += 1
                            print(f"✓ Ligne {line_idx} créée: {ligne}")
                            
                        except Produit.DoesNotExist:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Produit introuvable')
                            has_error = True
                            continue
                        except (ValueError, TypeError) as e:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Erreur de conversion - {str(e)}')
                            has_error = True
                            continue
                    
                    print(f"✓ Total de lignes créées: {lines_created}")
                    
                    # Si erreur détectée, annuler la transaction
                    if has_error:
                        raise ValueError('Erreurs détectées dans les lignes')
                    
                    # Vérifier qu'au moins une ligne a été créée
                    if lines_created == 0:
                        messages.error(request, 'Une commande doit contenir au moins un produit')
                        raise ValueError('Aucune ligne de produit')
                    
                    # Calculer le total
                    commande.calculer_total()
                    
                    messages.success(request, f'Commande {commande.numero_commande} modifiée avec succès ({lines_created} ligne(s)).')
                    return redirect('inventory:commande_detail', pk=commande.pk)
                    
            except ValueError as e:
                # Erreur de validation, le formulaire sera réaffiché avec les erreurs
                print(f"Erreur de validation: {e}")
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CommandeForm(instance=commande)

    # Récupérer les lignes existantes avec les produits
    lignes_existantes = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    context = {
        'form': form,
        'commande': commande,
        'lignes_existantes': lignes_existantes,  # Pour pré-remplir le formulaire
        'title': f'Modifier la commande {commande.numero_commande}',
        'produits': Produit.objects.filter(actif=True).order_by('nom'),
        'clients': Client.objects.filter(actif=True).order_by('nom', 'prenom')
    }
    
    return render(request, 'inventory/commande_form.html', context)


@login_required
def commande_delete(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    
    if request.method == 'POST':
        numero_commande = commande.numero_commande
        commande.delete()
        messages.success(request, f'La commande {numero_commande} a été supprimée avec succès.')
        return redirect('inventory:commandes_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': commande,
        'object_name': 'commande'
    })


@login_required
def commande_print_proforma(request, pk):
    """Générer un proforma en PDF selon le modèle DIMAT MEDICAL"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from io import BytesIO
    from decimal import Decimal
    import datetime
    
    commande = get_object_or_404(Commande, pk=pk)
    lignes = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=2*cm)
    story = []
    
    # Styles personnalisés
    styles = getSampleStyleSheet()
    
    # En-tête entreprise style DIMAT MEDICAL
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    # En-tête avec logo et infos entreprise
    story.append(Paragraph("DIMAT MEDICAL", company_style))
    story.append(Paragraph("CHIRURGIE GENERALE - RADIOLOGIE - IMAGERIE MÉDICALE", subtitle_style))
    story.append(Spacer(1, 30))
    
    # Numéro de proforma centré
    proforma_style = ParagraphStyle(
        'ProformaStyle',
        parent=styles['Heading1'],
        fontSize=18,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    story.append(Paragraph(f"Proforma n° {commande.numero_commande}", proforma_style))
    story.append(Spacer(1, 20))
    
    # Informations client et date
    client_info = f"Client: {commande.client.nom_complet if commande.client else 'Client comptoir'}"
    date_info = f"DATE: {commande.date_commande.strftime('%d/%m/%Y')}"
    
    info_data = [[client_info, date_info]]
    info_table = Table(info_data, colWidths=[4*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Tableau des produits style proforma
    if lignes:
        # En-tête du tableau
        data = [['Description', 'Quantité', 'Prix unitaire', 'Prix Total']]
        
        total_general = Decimal('0.00')
        
        # Lignes de produits
        for ligne in lignes:
            total_ligne = ligne.prix_unitaire * ligne.quantite
            total_general += total_ligne
            
            data.append([
                ligne.produit.nom,
                str(ligne.quantite),
                f"{ligne.prix_unitaire:.0f} 000",  # Style des prix dans l'image
                f"{total_ligne:.0f} 000"
            ])
        
        # Ligne de total
        data.append(['', 'TOTAL', '', f"{total_general:.0f} 000"])
        
        # Créer le tableau
        main_table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        main_table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Description à gauche
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Corps du tableau
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Ligne de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 30))
    
    # Informations de garantie et SAV (selon le modèle)
    garantie_data = [
        ["Garantie 12 Mois"],
        ["SAV Assuré"],
        ["Validité de l'offre: 2 mois"]
    ]
    
    garantie_table = Table(garantie_data, colWidths=[3*inch])
    garantie_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(garantie_table)
    story.append(Spacer(1, 30))
    
    # Pied de page avec coordonnées
    footer_text = f"Route nationale en face EDK technologie Dakar - Tél : +221 33 833 03 17 - Email : info@dimatmedical.com"
    footer_text2 = f"Numéro compte CBAO : sn 01307 03816162A001 34/PC, SN DKR 2018-B-1833 - NINEA : 006890892 200"
    
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer1',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=5
    )))
    
    story.append(Paragraph(footer_text2, ParagraphStyle(
        'Footer2',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666')
    )))
    
    # Construire le PDF
    doc.build(story)
    
    # Retourner la réponse
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proforma_{commande.numero_commande}.pdf"'
    return response


# ================== GESTION DES VENTES ==================

@login_required
def ventes_list(request):
    mode_paiement = request.GET.get('mode_paiement', '')
    query = request.GET.get('q', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    ventes = Vente.objects.select_related('client', 'utilisateur')
    
    if mode_paiement:
        ventes = ventes.filter(mode_paiement=mode_paiement)
    
    if query:
        ventes = ventes.filter(
            Q(numero_vente__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(client__prenom__icontains=query)
        )
    
    if date_debut:
        ventes = ventes.filter(date_vente__gte=date_debut)
    
    if date_fin:
        ventes = ventes.filter(date_vente__lte=date_fin)
    
    ventes = ventes.order_by('-date_vente')
    
    # Statistiques
    total_ventes = ventes.aggregate(
        total=Sum('total'),
        count=Count('id')
    )
    
    # Calcul de la vente moyenne
    vente_moyenne = 0
    if total_ventes['count'] and total_ventes['total']:
        vente_moyenne = total_ventes['total'] / total_ventes['count']
    
    # Ventes aujourd'hui
    aujourd_hui = datetime.now().date()
    ventes_aujourdhui = Vente.objects.filter(
        date_vente__date=aujourd_hui
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Pagination
    paginator = Paginator(ventes, 20)
    page_number = request.GET.get('page')
    ventes_page = paginator.get_page(page_number)
    
    context = {
        'ventes': ventes_page,
        'mode_paiement_choices': Vente.MODE_PAIEMENT_CHOICES,
        'mode_paiement': mode_paiement,
        'query': query,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total_ventes': total_ventes,
        'ventes_aujourdhui': ventes_aujourdhui,
        'vente_moyenne': vente_moyenne,
    }
    
    return render(request, 'inventory/ventes_list.html', context)


@login_required
def vente_detail(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    lignes = LigneVente.objects.filter(vente=vente).select_related('produit')
    
    # Calculer les statistiques
    total_quantity = sum(ligne.quantite for ligne in lignes)
    
    context = {
        'vente': vente,
        'lignes': lignes,
        'total_quantity': total_quantity,
        'nb_articles': lignes.count(),
    }
    
    return render(request, 'inventory/vente_detail.html', context)


@login_required
@transaction.atomic
def vente_create(request):
    """Création de vente avec gestion des lignes de produit en une seule étape"""
    if request.method == 'POST':
        # Debug: afficher les données POST reçues
        print("=== DEBUG VENTE_CREATE ===")
        print("POST data:", dict(request.POST))
        
        form = VenteForm(request.POST)
        
        if form.is_valid():
            vente = form.save(commit=False)
            vente.utilisateur = request.user
            vente.save()
            
            # Traitement des lignes de produit - NOUVELLE LOGIQUE ROBUSTE
            lines_created = 0
            
            # Parser toutes les clés POST pour trouver TOUTES les lignes de produit
            lines_data = {}
            for key in request.POST:
                if key.startswith('ligne_') and '_' in key:
                    parts = key.split('_', 2)  # ligne_0_produit → ['ligne', '0', 'produit']
                    if len(parts) == 3:
                        line_idx = parts[1]
                        field_name = parts[2]
                        
                        if line_idx not in lines_data:
                            lines_data[line_idx] = {}
                        lines_data[line_idx][field_name] = request.POST[key]
            
            print(f"=== DEBUG VENTE_CREATE ===")
            print(f"Lignes trouvées: {sorted(lines_data.keys())}")
            
            # Traiter chaque ligne trouvée (triée par index)
            for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                data = lines_data[line_idx]
                produit_id = data.get('produit')
                quantite = data.get('quantite')
                prix_unitaire = data.get('prix_unitaire')
                
                print(f"Traitement ligne {line_idx}: produit={produit_id}, quantite={quantite}, prix={prix_unitaire}")
                
                # Ignorer les lignes vides (pas de produit sélectionné)
                if not produit_id:
                    print(f"Ligne {line_idx} ignorée (pas de produit)")
                    continue
                
                # Vérifier que tous les champs requis sont présents
                if not (quantite and prix_unitaire):
                    messages.error(request, f'Ligne {int(line_idx) + 1}: Quantité et prix requis')
                    raise ValueError(f'Données incomplètes pour la ligne {line_idx}')
                
                try:
                    # Verrouiller le produit pour éviter les race conditions
                    produit = Produit.objects.select_for_update().get(id=produit_id)
                    quantite = int(quantite)
                    prix_unitaire = float(prix_unitaire)
                    
                    # Validation
                    if quantite <= 0:
                        messages.error(request, f'{produit.nom}: La quantité doit être positive')
                        raise ValueError('Quantité invalide')
                    
                    if prix_unitaire < 0:
                        messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                        raise ValueError('Prix invalide')
                    
                    # Vérifier le stock disponible
                    if quantite > produit.quantite_stock:
                        messages.error(
                            request, 
                            f'Stock insuffisant pour {produit.nom}. '
                            f'Stock disponible: {produit.quantite_stock}, Demandé: {quantite}'
                        )
                        raise ValueError('Stock insuffisant')
                    
                    # Créer la ligne de vente
                    ligne = LigneVente.objects.create(
                        vente=vente,
                        produit=produit,
                        quantite=quantite,
                        prix_unitaire=prix_unitaire
                    )
                    lines_created += 1
                    print(f"✓ Ligne {line_idx} créée: {ligne}")
                    
                    # Mettre à jour le stock
                    quantite_avant = produit.quantite_stock
                    produit.quantite_stock -= quantite
                    produit.save()
                    
                    # Enregistrer le mouvement de stock
                    MouvementStock.objects.create(
                        produit=produit,
                        type_mouvement='SORTIE',
                        quantite=quantite,
                        quantite_avant=quantite_avant,
                        quantite_apres=produit.quantite_stock,
                        motif=f'Vente {vente.numero_vente}',
                        utilisateur=request.user
                    )
                    
                except Produit.DoesNotExist:
                    messages.error(request, f'Ligne {int(line_idx) + 1}: Produit introuvable')
                    raise
                except (ValueError, TypeError) as e:
                    messages.error(request, f'Ligne {int(line_idx) + 1}: {str(e)}')
                    raise
            
            print(f"✓ Total de lignes créées: {lines_created}")
            
            # Vérifier qu'au moins une ligne a été créée
            if lines_created == 0:
                messages.error(request, 'Une vente doit contenir au moins un produit')
                raise ValueError('Aucune ligne de produit')
            
            # Calculer le total avec remise
            vente.calculer_total()
            
            action = request.POST.get('action', 'finalize')
            if action == 'finalize':
                messages.success(request, f'Vente {vente.numero_vente} créée avec succès! ({lines_created} lignes)')
                return redirect('inventory:vente_detail', pk=vente.id)
            else:
                messages.success(request, f'Vente {vente.numero_vente} enregistrée en brouillon. ({lines_created} lignes)')
                return redirect('inventory:vente_detail', pk=vente.id)
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = VenteForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle Vente',
        'produits': Produit.objects.filter(actif=True, quantite_stock__gt=0),
        'clients': Client.objects.filter(actif=True)
    }
    
    return render(request, 'inventory/vente_form.html', context)


@login_required
def vente_update(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    
    if request.method == 'POST':
        form = VenteForm(request.POST, instance=vente)
        if form.is_valid():
            vente = form.save()
            messages.success(request, f'La vente {vente.numero_vente} a été modifiée avec succès.')
            return redirect('inventory:vente_detail', pk=vente.pk)
    else:
        form = VenteForm(instance=vente)
    
    return render(request, 'inventory/vente_form.html', {
        'form': form,
        'vente': vente,
        'title': f'Modifier la vente {vente.numero_vente}'
    })


@login_required
def vente_print(request, pk):
    """Générer le reçu de vente en PDF avec tous les éléments d'une facture"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from io import BytesIO
    from decimal import Decimal
    import datetime
    
    vente = get_object_or_404(Vente, pk=pk)
    lignes = LigneVente.objects.filter(vente=vente).select_related('produit')
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=2*cm)
    story = []
    
    # Styles personnalisés
    styles = getSampleStyleSheet()
    
    # Style pour le titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        textColor=colors.HexColor('#059669'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style pour l'en-tête de l'entreprise
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#059669'),
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    # Style pour les informations de contact
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # En-tête de l'entreprise
    story.append(Paragraph("GGStock", company_style))
    story.append(Paragraph("Système de Gestion d'Inventaire Médical", contact_style))
    story.append(Paragraph("Email: contact@ggstock.com | Tél: +33 1 23 45 67 89", contact_style))
    story.append(Spacer(1, 20))
    
    # Titre de la facture
    story.append(Paragraph("FACTURE DE VENTE", title_style))
    story.append(Spacer(1, 15))
    
    # Section informations client et vente
    info_client_vente = []
    
    # Colonne gauche - Informations client
    if vente.client:
        client_info = f"""
        <b>FACTURER À:</b><br/>
        {vente.client.nom_complet}<br/>
        {vente.client.adresse if vente.client.adresse else 'Adresse non renseignée'}<br/>
        {vente.client.code_postal or ''} {vente.client.ville or ''}<br/>
        Email: {vente.client.email}<br/>
        Tél: {vente.client.telephone or 'Non renseigné'}
        """
        if hasattr(vente.client, 'entreprise') and vente.client.entreprise:
            client_info = f"""
            <b>FACTURER À:</b><br/>
            {vente.client.entreprise}<br/>
            {vente.client.nom_complet}<br/>
            {vente.client.adresse if vente.client.adresse else 'Adresse non renseignée'}<br/>
            {vente.client.code_postal or ''} {vente.client.ville or ''}<br/>
            Email: {vente.client.email}<br/>
            Tél: {vente.client.telephone or 'Non renseigné'}
            """
    else:
        client_info = """
        <b>FACTURER À:</b><br/>
        Client au comptoir<br/>
        Vente directe
        """
    
    # Colonne droite - Informations de la vente
    vente_info = f"""
    <b>NUMÉRO:</b> {vente.numero_vente}<br/>
    <b>DATE:</b> {vente.date_vente.strftime('%d/%m/%Y')}<br/>
    <b>HEURE:</b> {vente.date_vente.strftime('%H:%M')}<br/>
    <b>VENDEUR:</b> {vente.utilisateur.get_full_name() or vente.utilisateur.username}<br/>
    <b>MODE DE PAIEMENT:</b> {vente.get_mode_paiement_display()}
    """
    
    # Tableau pour disposer les informations côte à côte
    info_data = [[Paragraph(client_info, styles['Normal']), Paragraph(vente_info, styles['Normal'])]]
    info_table = Table(info_data, colWidths=[4*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Tableau des produits détaillé
    if lignes:
        story.append(Paragraph("DÉTAIL DE LA VENTE", ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=15
        )))
        
        # En-tête du tableau avec plus de colonnes
        data = [['Article', 'Réf.', 'Qté', 'Prix unit. HT', 'TVA', 'Prix unit. TTC', 'Total HT', 'Total TTC']]
        
        total_ht = Decimal('0.00')
        total_tva = Decimal('0.00')
        total_ttc = Decimal('0.00')
        
        # Lignes de produits avec calculs détaillés
        for ligne in lignes:
            # Calculs TVA (assumons 20% par défaut)
            taux_tva = Decimal('0.20')  # 20%
            prix_ht = ligne.prix_unitaire / (1 + taux_tva)
            montant_tva = ligne.prix_unitaire - prix_ht
            total_ligne_ht = prix_ht * ligne.quantite
            total_ligne_ttc = ligne.prix_unitaire * ligne.quantite
            
            total_ht += total_ligne_ht
            total_tva += montant_tva * ligne.quantite
            total_ttc += total_ligne_ttc
            
            data.append([
                ligne.produit.nom[:25] + '...' if len(ligne.produit.nom) > 25 else ligne.produit.nom,
                ligne.produit.reference or 'N/A',
                str(ligne.quantite),
                f"{prix_ht:.2f}F CFA",
                f"{taux_tva*100:.0f}%",
                f"{ligne.prix_unitaire:.2f}F CFA",
                f"{total_ligne_ht:.2f}F CFA",
                f"{total_ligne_ttc:.2f}F CFA"
            ])
        
        # Lignes de totaux
        data.append(['', '', '', '', '', '', '', ''])  # Ligne vide
        data.append(['', '', '', '', '', 'TOTAL HT:', f"{total_ht:.2f}F CFA", ''])
        data.append(['', '', '', '', '', 'TOTAL TVA:', f"{total_tva:.2f}F CFA", ''])
        data.append(['', '', '', '', '', 'TOTAL TTC:', '', f"{total_ttc:.2f}F CFA"])
        
        # Création du tableau avec largeurs adaptées
        table = Table(data, colWidths=[2.2*inch, 0.7*inch, 0.5*inch, 0.8*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        
        # Style du tableau
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Corps du tableau
            ('FONTSIZE', (0, 1), (-1, -5), 8),
            ('ALIGN', (1, 1), (-1, -5), 'CENTER'),  # Centrer sauf première colonne
            ('ALIGN', (0, 1), (0, -5), 'LEFT'),    # Première colonne à gauche
            ('GRID', (0, 0), (-1, -5), 0.5, colors.HexColor('#d1d5db')),
            
            # Ligne vide avant totaux
            ('LINEBELOW', (0, -5), (-1, -5), 1, colors.HexColor('#059669')),
            
            # Section totaux
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, -4), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, -4), (-1, -1), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#059669')),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
    
    # Informations de paiement
    story.append(Paragraph("INFORMATIONS DE PAIEMENT", ParagraphStyle(
        'PaymentTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10
    )))
    
    payment_info = f"""
    <b>Mode de paiement:</b> {vente.get_mode_paiement_display()}<br/>
    <b>Date de paiement:</b> {vente.date_vente.strftime('%d/%m/%Y')}<br/>
    <b>Statut:</b> Payé
    """
    
    if vente.notes:
        payment_info += f"<br/><b>Notes:</b> {vente.notes}"
    
    story.append(Paragraph(payment_info, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Conditions générales
    story.append(Paragraph("CONDITIONS GÉNÉRALES", ParagraphStyle(
        'TermsTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10
    )))
    
    conditions = """
    • Les produits médicaux sont vendus conformément aux réglementations en vigueur.<br/>
    • Garantie selon les conditions du fabricant.<br/>
    • Retour possible sous 14 jours pour les produits non ouverts.<br/>
    • Facturation TTC, TVA non applicable selon l'article 293 B du CGI.<br/>
    • Paiement comptant à la livraison.
    """
    
    story.append(Paragraph(conditions, ParagraphStyle(
        'Conditions',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280')
    )))
    
    # Pied de page avec remerciements
    story.append(Spacer(1, 40))
    story.append(Paragraph("Merci de votre confiance !", ParagraphStyle(
        'Thanks',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#059669'),
        alignment=TA_CENTER
    )))
    
    story.append(Paragraph(f"Document généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                          ParagraphStyle(
                              'Generated',
                              parent=styles['Normal'],
                              fontSize=8,
                              textColor=colors.HexColor('#9ca3af'),
                              alignment=TA_CENTER
                          )))
    
    # Construire le PDF
    doc.build(story)
    
    # Retourner la réponse
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_vente_{vente.numero_vente}.pdf"'
    
    return response


@login_required
def vente_print_proforma(request, pk):
    """Générer un proforma de vente en PDF selon le modèle DIMAT MEDICAL"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from io import BytesIO
    from decimal import Decimal
    import datetime
    
    vente = get_object_or_404(Vente, pk=pk)
    lignes = LigneVente.objects.filter(vente=vente).select_related('produit')
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=2*cm)
    story = []
    
    # Styles personnalisés
    styles = getSampleStyleSheet()
    
    # En-tête entreprise style DIMAT MEDICAL
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    # En-tête avec logo et infos entreprise
    story.append(Paragraph("DIMAT MEDICAL", company_style))
    story.append(Paragraph("CHIRURGIE GENERALE - RADIOLOGIE - IMAGERIE MÉDICALE", subtitle_style))
    story.append(Spacer(1, 30))
    
    # Numéro de proforma centré
    proforma_style = ParagraphStyle(
        'ProformaStyle',
        parent=styles['Heading1'],
        fontSize=18,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    story.append(Paragraph(f"Proforma n° {vente.numero_vente}", proforma_style))
    story.append(Spacer(1, 20))
    
    # Informations client et date
    client_info = f"Client: {vente.client.nom_complet if vente.client else 'Client comptoir'}"
    date_info = f"DATE: {vente.date_vente.strftime('%d/%m/%Y')}"
    
    info_data = [[client_info, date_info]]
    info_table = Table(info_data, colWidths=[4*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Tableau des produits style proforma
    if lignes:
        # En-tête du tableau
        data = [['Description', 'Quantité', 'Prix unitaire', 'Prix Total']]
        
        total_general = Decimal('0.00')
        
        # Lignes de produits
        for ligne in lignes:
            total_ligne = ligne.prix_unitaire * ligne.quantite
            total_general += total_ligne
            
            data.append([
                ligne.produit.nom,
                str(ligne.quantite),
                f"{ligne.prix_unitaire:.0f} 000",  # Style des prix dans l'image
                f"{total_ligne:.0f} 000"
            ])
        
        # Ligne de total
        data.append(['', 'TOTAL', '', f"{total_general:.0f} 000"])
        
        # Créer le tableau
        main_table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        main_table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Description à gauche
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Corps du tableau
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Ligne de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 30))
    
    # Informations de garantie et SAV (selon le modèle)
    garantie_data = [
        ["Garantie 12 Mois"],
        ["SAV Assuré"],
        ["Validité de l'offre: 2 mois"]
    ]
    
    garantie_table = Table(garantie_data, colWidths=[3*inch])
    garantie_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(garantie_table)
    story.append(Spacer(1, 30))
    
    # Pied de page avec coordonnées
    footer_text = f"Route nationale en face EDK technologie Dakar - Tél : +221 33 833 03 17 - Email : info@dimatmedical.com"
    footer_text2 = f"Numéro compte CBAO : sn 01307 03816162A001 34/PC, SN DKR 2018-B-1833 - NINEA : 006890892 200"
    
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer1',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=5
    )))
    
    story.append(Paragraph(footer_text2, ParagraphStyle(
        'Footer2',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666')
    )))
    
    # Construire le PDF
    doc.build(story)
    
    # Retourner la réponse
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proforma_vente_{vente.numero_vente}.pdf"'
    return response


# ================== GESTION DU STOCK ==================

@login_required
def stock_list(request):
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    stock_bas = request.GET.get('stock_bas', '')
    
    produits = Produit.objects.select_related('categorie', 'fournisseur').filter(actif=True)
    
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) |
            Q(reference__icontains=query)
        )
    
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    if stock_bas:
        produits = produits.filter(quantite_stock__lte=F('seuil_alerte'))
    
    # Pagination
    paginator = Paginator(produits, 20)
    page_number = request.GET.get('page')
    produits_page = paginator.get_page(page_number)
    
    categories = Categorie.objects.all()
    
    # Statistiques
    stats = {
        'total_produits': produits.count(),
        'produits_stock_bas': produits.filter(quantite_stock__lte=F('seuil_alerte')).count(),
        'valeur_stock': sum([p.quantite_stock * p.prix_achat for p in produits]),
    }
    
    context = {
        'produits': produits_page,
        'categories': categories,
        'query': query,
        'categorie_id': int(categorie_id) if categorie_id else None,
        'stock_bas': stock_bas,
        'stats': stats,
    }
    
    return render(request, 'inventory/stock_list.html', context)


@login_required
@role_required(['MANAGER', 'TECHNICIEN'])
def mouvement_create(request):
    """Créer un mouvement de stock (entrée/sortie)"""
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.utilisateur = request.user
            # Calcul des quantités avant/après
            produit = mouvement.produit
            mouvement.quantite_avant = produit.quantite_stock
            if mouvement.type_mouvement == 'ENTREE':
                produit.quantite_stock += mouvement.quantite
            else:
                produit.quantite_stock -= mouvement.quantite
            produit.save()
            mouvement.quantite_apres = produit.quantite_stock
            mouvement.save()
            messages.success(request, "Mouvement de stock enregistré avec succès.")
            return redirect('inventory:stock_list')
    else:
        form = MouvementStockForm()
    return render(request, 'inventory/mouvement_form.html', {'form': form, 'title': 'Nouveau Mouvement de Stock'})


# ================== API POUR RECHERCHES AJAX ==================

@login_required
def api_produit_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    produits = Produit.objects.filter(
        Q(nom__icontains=query) | Q(reference__icontains=query),
        actif=True
    )[:10]
    
    results = [{
        'id': p.id,
        'text': f"{p.nom} - {p.reference}",
        'prix': str(p.prix_vente),
        'stock': p.quantite_stock
    } for p in produits]
    
    return JsonResponse({'results': results})


@login_required
def api_client_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    clients = Client.objects.filter(
        Q(nom__icontains=query) | Q(prenom__icontains=query) | Q(email__icontains=query),
        actif=True
    )[:10]
    
    results = [{
        'id': c.id,
        'text': f"{c.nom_complet} - {c.email}",
        'email': c.email,
        'telephone': c.telephone
    } for c in clients]
    
    return JsonResponse({'results': results})


# ============ VUES PUBLIQUES E-COMMERCE ============

def ecommerce_home(request):
    """Landing page e-commerce avec produits populaires"""
    # Produits les plus populaires/récents
    produits_populaires = Produit.objects.filter(
        actif=True, 
        quantite_stock__gt=0
    ).order_by('-id')[:8]
    
    # Catégories principales
    categories = Categorie.objects.all()[:6]
    
    context = {
        'produits_populaires': produits_populaires,
        'categories': categories,
    }
    return render(request, 'inventory/ecommerce/home.html', context)


def ecommerce_catalogue(request):
    """Catalogue de produits e-commerce avec filtres"""
    produits = Produit.objects.filter(actif=True, quantite_stock__gt=0)
    
    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    # Recherche par nom/description
    search = request.GET.get('search')
    if search:
        produits = produits.filter(
            Q(nom__icontains=search) | Q(description__icontains=search)
        )
    
    # Tri
    sort_by = request.GET.get('sort', 'nom')
    if sort_by == 'prix_asc':
        produits = produits.order_by('prix_vente')
    elif sort_by == 'prix_desc':
        produits = produits.order_by('-prix_vente')
    elif sort_by == 'recent':
        produits = produits.order_by('-id')
    else:
        produits = produits.order_by('nom')
    
    # Pagination
    paginator = Paginator(produits, 12)  # 12 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Toutes les catégories pour le filtre
    categories = Categorie.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_categorie': int(categorie_id) if categorie_id else None,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'inventory/ecommerce/catalogue.html', context)


def ecommerce_produit_detail(request, pk):
    """Page détail produit e-commerce"""
    produit = get_object_or_404(Produit, pk=pk, actif=True)
    
    # Produits similaires (même catégorie)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie,
        actif=True,
        quantite_stock__gt=0
    ).exclude(pk=pk)[:4]
    
    context = {
        'produit': produit,
        'produits_similaires': produits_similaires,
    }
    return render(request, 'inventory/ecommerce/produit_detail.html', context)


# ============ VUES D'AUTHENTIFICATION ============

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


def admin_login(request):
    """Page de connexion pour les administrateurs"""
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'inventory:dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    form = AuthenticationForm()
    return render(request, 'inventory/auth/login.html', {'form': form})


def admin_logout(request):
    """Déconnexion des administrateurs"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('inventory:ecommerce_home')


def contact(request):
    """Page de contact statique"""
    return render(request, 'inventory/ecommerce/contact.html')


# ========== NOUVELLES VUES POUR FORMULAIRES AVANCÉS ==========


@login_required
def commande_create_advanced(request):
    """Création de commande avec gestion des lignes de produit en une seule étape"""
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    commande = form.save(commit=False)
                    commande.utilisateur = request.user
                    commande.save()
                    
                    # Traitement des lignes de produit - LOGIQUE ROBUSTE
                    lines_created = 0
                    has_error = False
                    
                    # Parser toutes les clés POST pour trouver TOUTES les lignes de produit
                    lines_data = {}
                    for key in request.POST:
                        if key.startswith('ligne_') and '_' in key:
                            parts = key.split('_', 2)  # ligne_0_produit → ['ligne', '0', 'produit']
                            if len(parts) == 3:
                                line_idx = parts[1]
                                field_name = parts[2]
                                
                                if line_idx not in lines_data:
                                    lines_data[line_idx] = {}
                                lines_data[line_idx][field_name] = request.POST[key]
                    
                    print(f"=== DEBUG COMMANDE_CREATE ===")
                    print(f"POST data: {request.POST}")
                    print(f"Lignes trouvées: {sorted(lines_data.keys())}")
                    
                    # Traiter chaque ligne trouvée (triée par index)
                    for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                        data = lines_data[line_idx]
                        produit_id = data.get('produit')
                        quantite = data.get('quantite')
                        prix_unitaire = data.get('prix_unitaire')
                        
                        print(f"Traitement ligne {line_idx}: produit={produit_id}, quantite={quantite}, prix={prix_unitaire}")
                        
                        # Ignorer les lignes vides (pas de produit sélectionné)
                        if not produit_id:
                            print(f"Ligne {line_idx} ignorée (pas de produit)")
                            continue
                        
                        # Vérifier que tous les champs requis sont présents
                        if not quantite or not prix_unitaire:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Quantité et prix requis')
                            has_error = True
                            continue
                        
                        try:
                            produit = Produit.objects.get(id=produit_id)
                            quantite = int(quantite)
                            prix_unitaire = float(prix_unitaire)
                            
                            # Validation
                            if quantite <= 0:
                                messages.error(request, f'{produit.nom}: La quantité doit être positive')
                                has_error = True
                                continue
                            
                            if prix_unitaire < 0:
                                messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                                has_error = True
                                continue
                            
                            # ✅ VÉRIFICATION DE STOCK (avec warning, pas d'erreur)
                            if quantite > produit.quantite_stock:
                                messages.warning(
                                    request,
                                    f'⚠️ Stock insuffisant pour {produit.nom}: '
                                    f'Stock disponible={produit.quantite_stock}, Commandé={quantite}. '
                                    f'La commande sera créée, mais vérifiez le stock avant livraison.'
                                )
                                # On continue quand même (c'est une commande fournisseur)
                            
                            # Créer la ligne de commande
                            ligne = LigneCommande.objects.create(
                                commande=commande,
                                produit=produit,
                                quantite=quantite,
                                prix_unitaire=prix_unitaire
                            )
                            lines_created += 1
                            print(f"✓ Ligne {line_idx} créée: {ligne}")
                            
                        except Produit.DoesNotExist:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Produit introuvable')
                            has_error = True
                            continue
                        except (ValueError, TypeError) as e:
                            messages.error(request, f'Ligne {int(line_idx) + 1}: Erreur de conversion - {str(e)}')
                            has_error = True
                            continue
                    
                    print(f"✓ Total de lignes créées: {lines_created}")
                    
                    # Si erreur détectée, annuler la transaction
                    if has_error:
                        raise ValueError('Erreurs détectées dans les lignes')
                    
                    # Vérifier qu'au moins une ligne a été créée
                    if lines_created == 0:
                        messages.error(request, 'Une commande doit contenir au moins un produit')
                        raise ValueError('Aucune ligne de produit')
                    
                    # Calculer le total
                    commande.calculer_total()
                    
                    action = request.POST.get('action', 'confirm')
                    if action == 'confirm':
                        commande.statut = 'CONFIRMEE'
                        commande.save()
                        messages.success(request, f'Commande {commande.numero_commande} créée et confirmée avec succès ({lines_created} ligne(s))!')
                        return redirect('inventory:commande_detail', pk=commande.id)
                    else:
                        # Brouillon - statut reste EN_ATTENTE
                        messages.success(request, f'Commande {commande.numero_commande} enregistrée en brouillon ({lines_created} ligne(s)).')
                        return redirect('inventory:commande_detail', pk=commande.id)
                        
            except ValueError as e:
                # Erreur de validation, le formulaire sera réaffiché avec les erreurs
                print(f"Erreur de validation: {e}")
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CommandeForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle Commande Complète',
        'produits': Produit.objects.filter(actif=True),
        'clients': Client.objects.filter(actif=True)
    }
    
    return render(request, 'inventory/commande_form.html', context)


@login_required
@role_required(['MANAGER', 'COMMERCIAL_SHOWROOM'])
def vente_generate_pdf(request, vente_id):
    """Génération de PDF pour une vente avec ReportLab"""
    vente = get_object_or_404(Vente, id=vente_id)
    
    # Vérification des permissions
    if not request.user.profile.role in ['MANAGER', 'COMMERCIAL_SHOWROOM']:
        messages.error(request, "Vous n'avez pas les permissions pour générer ce document.")
        return redirect('inventory:vente_detail', vente_id=vente_id)
    
    try:
        # Création du PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="facture_{vente.numero_vente}.pdf"'
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#007bff')
        )
        
        # En-tête
        story.append(Paragraph("GGSTOCK ENTERPRISE", title_style))
        story.append(Paragraph("FACTURE", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Informations de base
        info_data = [
            ['Numéro:', vente.numero_vente],
            ['Date:', vente.date_vente.strftime('%d/%m/%Y %H:%M')],
            ['Vendeur:', vente.utilisateur.get_full_name() or vente.utilisateur.username],
            ['Client:', vente.client.nom_complet if vente.client else 'VENTE COMPTOIR'],
            ['Mode de paiement:', vente.get_mode_paiement_display()],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Tableau des produits
        lignes = vente.lignevente_set.all()
        if lignes:
            # En-têtes du tableau
            data = [['Produit', 'Référence', 'Qté', 'Prix unitaire', 'Total']]
            
            # Lignes de produits
            for ligne in lignes:
                data.append([
                    ligne.produit.nom,
                    ligne.produit.reference,
                    str(ligne.quantite),
                    f"{ligne.prix_unitaire:.2f} F CFA",
                    f"{ligne.sous_total():.2f} F CFA"
                ])
            
            # Total
            subtotal = sum(ligne.sous_total() for ligne in lignes)
            remise_amount = subtotal * vente.remise / 100
            total = subtotal - remise_amount
            
            data.append(['', '', '', 'Sous-total:', f"{subtotal:.2f} F CFA"])
            if vente.remise > 0:
                data.append(['', '', '', f'Remise ({vente.remise}%):', f"-{remise_amount:.2f} F CFA"])
            data.append(['', '', '', 'TOTAL TTC:', f"{total:.2f} F CFA"])
            
            table = Table(data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
            table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                # Corps
                ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -4), 9),
                ('GRID', (0, 0), (-1, -4), 1, colors.black),
                # Totaux
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("Aucun produit dans cette vente", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Notes
        if vente.notes:
            story.append(Paragraph("Notes:", styles['Heading3']))
            story.append(Paragraph(vente.notes, styles['Normal']))
        
        # Pied de page
        story.append(Spacer(1, 50))
        story.append(Paragraph("Merci pour votre confiance !", styles['Normal']))
        story.append(Paragraph("GGSTOCK Enterprise - contact@ggstock.com", styles['Normal']))
        
        # Construction du PDF
        doc.build(story)
        
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('inventory:vente_detail', vente_id=vente_id)


@login_required
@role_required(['MANAGER', 'COMMERCIAL_SHOWROOM', 'COMMERCIAL_TERRAIN'])  
def commande_generate_pdf(request, commande_id):
    """Génération de PDF pour une commande avec ReportLab"""
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Vérification des permissions
    if not request.user.profile.role in ['MANAGER', 'COMMERCIAL_SHOWROOM', 'COMMERCIAL_TERRAIN']:
        messages.error(request, "Vous n'avez pas les permissions pour générer ce document.")
        return redirect('inventory:commande_detail', commande_id=commande_id)
    
    try:
        # Création du PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="bon_commande_{commande.numero_commande}.pdf"'
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#007bff')
        )
        
        # En-tête
        story.append(Paragraph("GGSTOCK ENTERPRISE", title_style))
        story.append(Paragraph("BON DE COMMANDE", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Informations de base
        info_data = [
            ['Numéro:', commande.numero_commande],
            ['Date:', commande.date_commande.strftime('%d/%m/%Y %H:%M')],
            ['Commercial:', commande.utilisateur.get_full_name() or commande.utilisateur.username],
            ['Client:', commande.client.nom_complet],
            ['Statut:', commande.get_statut_display()],
        ]
        
        if commande.date_livraison_prevue:
            info_data.append(['Livraison prévue:', commande.date_livraison_prevue.strftime('%d/%m/%Y')])
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Adresse de livraison
        if commande.adresse_livraison:
            story.append(Paragraph("Adresse de livraison:", styles['Heading3']))
            story.append(Paragraph(commande.adresse_livraison.replace('\n', '<br/>'), styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Tableau des produits
        lignes = commande.lignecommande_set.all()
        if lignes:
            # En-têtes du tableau
            data = [['Produit', 'Référence', 'Qté', 'Prix unitaire', 'Total']]
            
            # Lignes de produits
            for ligne in lignes:
                data.append([
                    ligne.produit.nom,
                    ligne.produit.reference,
                    str(ligne.quantite),
                    f"{ligne.prix_unitaire:.2f} F CFA",
                    f"{ligne.sous_total():.2f} F CFA"
                ])
            
            # Total
            total = sum(ligne.sous_total() for ligne in lignes)
            data.append(['', '', '', 'TOTAL TTC:', f"{total:.2f} F CFA"])
            
            table = Table(data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
            table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                # Corps
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                # Total
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("Aucun produit dans cette commande", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Notes
        if commande.notes:
            story.append(Paragraph("Notes et instructions:", styles['Heading3']))
            story.append(Paragraph(commande.notes, styles['Normal']))
        
        # Conditions
        story.append(Spacer(1, 30))
        story.append(Paragraph("Conditions:", styles['Heading3']))
        conditions = """
        • Les délais de livraison sont donnés à titre indicatif<br/>
        • Les prix sont valables au moment de la commande<br/>
        • Toute modification doit être confirmée par écrit<br/>
        • Signature requise à la livraison
        """
        story.append(Paragraph(conditions, styles['Normal']))
        
        # Pied de page
        story.append(Spacer(1, 50))
        story.append(Paragraph("GGSTOCK Enterprise - Votre partenaire de confiance", styles['Normal']))
        story.append(Paragraph("contact@ggstock.com | +33 1 23 45 67 89", styles['Normal']))
        
        # Construction du PDF
        doc.build(story)
        
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('inventory:commande_detail', commande_id=commande_id)
