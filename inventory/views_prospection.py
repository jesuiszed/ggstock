from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import datetime
import csv
from .models import ProspectionTelephonique
from .forms import ProspectionTelephoniqueForm
from users.decorators import role_required


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_list(request):
    """Liste des prospections téléphoniques avec filtres et recherche"""
    
    # Récupération de tous les prospects
    prospections = ProspectionTelephonique.objects.select_related('commercial').all()
    
    # Filtres commerciaux uniquement voient leurs prospects
    if hasattr(request.user, 'profile') and request.user.profile.role == 'COMMERCIAL_TERRAIN':
        prospections = prospections.filter(commercial=request.user)
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        prospections = prospections.filter(
            Q(nom_complet__icontains=search_query) |
            Q(numero_telephone__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filtre par statut
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        prospections = prospections.filter(statut=statut_filter)
    
    # Filtre par type d'appel
    type_appel_filter = request.GET.get('type_appel', '')
    if type_appel_filter:
        prospections = prospections.filter(type_appel=type_appel_filter)
    
    # Filtre par source (appel entrant uniquement)
    source_filter = request.GET.get('source', '')
    if source_filter:
        prospections = prospections.filter(source_prospect=source_filter)
    
    # Tri
    sort_by = request.GET.get('sort', '-date_creation')
    prospections = prospections.order_by(sort_by)
    
    # Statistiques
    stats = {
        'total': ProspectionTelephonique.objects.filter(
            commercial=request.user if request.user.profile.role == 'commercial_terrain' else None
        ).count() if request.user.profile.role == 'commercial_terrain' else ProspectionTelephonique.objects.count(),
        'rdv': prospections.filter(statut='RDV').count(),
        'bv': prospections.filter(statut='BV').count(),
        'client_acquis': prospections.filter(statut='CLIENT_ACQUIS').count(),
        'a_relancer': prospections.filter(statut='A_RELANCER').count(),
        'appel_sortant': prospections.filter(type_appel='SORTANT').count(),
        'appel_entrant': prospections.filter(type_appel='ENTRANT').count(),
    }
    
    # Pagination
    paginator = Paginator(prospections, 20)  # 20 prospects par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'search_query': search_query,
        'statut_filter': statut_filter,
        'type_appel_filter': type_appel_filter,
        'source_filter': source_filter,
        'sort_by': sort_by,
        'statut_choices': ProspectionTelephonique.STATUT_CHOICES,
        'type_appel_choices': ProspectionTelephonique.TYPE_APPEL_CHOICES,
        'source_choices': ProspectionTelephonique.SOURCE_PROSPECT_CHOICES,
    }
    
    return render(request, 'inventory/prospection_list.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_create(request):
    """Créer une nouvelle fiche de prospection"""
    
    if request.method == 'POST':
        form = ProspectionTelephoniqueForm(request.POST)
        if form.is_valid():
            prospection = form.save(commit=False)
            prospection.commercial = request.user
            prospection.save()
            messages.success(request, '✅ Fiche de prospection créée avec succès!')
            return redirect('inventory:prospection_detail', pk=prospection.pk)
        else:
            messages.error(request, '❌ Erreur lors de la création. Veuillez vérifier les champs.')
    else:
        form = ProspectionTelephoniqueForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle Prospection Téléphonique',
        'action': 'create'
    }
    
    return render(request, 'inventory/prospection_form.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_detail(request, pk):
    """Afficher les détails d'une prospection"""
    
    prospection = get_object_or_404(ProspectionTelephonique, pk=pk)
    
    # Vérifier les permissions
    if hasattr(request.user, 'profile') and request.user.profile.role == 'COMMERCIAL_TERRAIN' and prospection.commercial != request.user:
        messages.error(request, '❌ Vous n\'avez pas accès à cette prospection.')
        return redirect('inventory:prospection_list')
    
    context = {
        'prospection': prospection,
    }
    
    return render(request, 'inventory/prospection_detail.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_edit(request, pk):
    """Modifier une fiche de prospection"""
    
    prospection = get_object_or_404(ProspectionTelephonique, pk=pk)
    
    # Vérifier les permissions
    if hasattr(request.user, 'profile') and request.user.profile.role == 'COMMERCIAL_TERRAIN' and prospection.commercial != request.user:
        messages.error(request, '❌ Vous ne pouvez pas modifier cette prospection.')
        return redirect('inventory:prospection_list')
    
    if request.method == 'POST':
        form = ProspectionTelephoniqueForm(request.POST, instance=prospection)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Fiche de prospection mise à jour avec succès!')
            return redirect('inventory:prospection_detail', pk=prospection.pk)
        else:
            messages.error(request, '❌ Erreur lors de la modification. Veuillez vérifier les champs.')
    else:
        form = ProspectionTelephoniqueForm(instance=prospection)
    
    context = {
        'form': form,
        'prospection': prospection,
        'title': 'Modifier Prospection Téléphonique',
        'action': 'edit'
    }
    
    return render(request, 'inventory/prospection_form.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_delete(request, pk):
    """Supprimer une fiche de prospection"""
    
    prospection = get_object_or_404(ProspectionTelephonique, pk=pk)
    
    # Vérifier les permissions
    if hasattr(request.user, 'profile') and request.user.profile.role == 'COMMERCIAL_TERRAIN' and prospection.commercial != request.user:
        messages.error(request, '❌ Vous ne pouvez pas supprimer cette prospection.')
        return redirect('inventory:prospection_list')
    
    if request.method == 'POST':
        nom_complet = prospection.nom_complet
        prospection.delete()
        messages.success(request, f'✅ La prospection de "{nom_complet}" a été supprimée avec succès!')
        return redirect('inventory:prospection_list')
    
    context = {
        'prospection': prospection,
        'title': 'Supprimer Prospection'
    }
    
    return render(request, 'inventory/prospection_confirm_delete.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_export_excel(request):
    """Exporter les prospections en CSV (compatible Excel)"""
    
    # Récupération des prospects selon les filtres
    prospections = ProspectionTelephonique.objects.select_related('commercial').all()
    
    # Filtres commerciaux uniquement voient leurs prospects
    if hasattr(request.user, 'profile') and request.user.profile.role == 'COMMERCIAL_TERRAIN':
        prospections = prospections.filter(commercial=request.user)
    
    # Appliquer les mêmes filtres que la liste
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        prospections = prospections.filter(statut=statut_filter)
    
    type_appel_filter = request.GET.get('type_appel', '')
    if type_appel_filter:
        prospections = prospections.filter(type_appel=type_appel_filter)
    
    # Créer la réponse HTTP
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="prospections_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff'.encode('utf-8'))  # BOM pour Excel
    
    writer = csv.writer(response, delimiter=';')
    
    # En-têtes
    writer.writerow([
        'Nom Complet', 
        'Numéro Téléphone', 
        'Email', 
        'Type Appel', 
        'Statut', 
        'Date RDV', 
        'Source Prospect', 
        'Description', 
        'Commercial',
        'Date Création',
        'Date Modification'
    ])
    
    # Données
    for prospection in prospections:
        writer.writerow([
            prospection.nom_complet,
            prospection.numero_telephone,
            prospection.email or '',
            prospection.get_type_appel_display(),
            prospection.get_statut_display(),
            prospection.date_rdv.strftime('%d/%m/%Y') if prospection.date_rdv else '',
            prospection.get_source_prospect_display() if prospection.source_prospect else '',
            prospection.description,
            f"{prospection.commercial.first_name} {prospection.commercial.last_name}",
            prospection.date_creation.strftime('%d/%m/%Y %H:%M'),
            prospection.date_modification.strftime('%d/%m/%Y %H:%M'),
        ])
    
    return response


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospection_stats_api(request):
    """API JSON pour les statistiques (pour graphiques futurs)"""
    from django.http import JsonResponse
    
    prospections = ProspectionTelephonique.objects.all()
    
    if hasattr(request.user, 'profile') and request.user.profile.role == 'COMMERCIAL_TERRAIN':
        prospections = prospections.filter(commercial=request.user)
    
    stats = {
        'par_statut': {
            'RDV': prospections.filter(statut='RDV').count(),
            'BV': prospections.filter(statut='BV').count(),
            'CLIENT_ACQUIS': prospections.filter(statut='CLIENT_ACQUIS').count(),
            'A_RELANCER': prospections.filter(statut='A_RELANCER').count(),
        },
        'par_type': {
            'SORTANT': prospections.filter(type_appel='SORTANT').count(),
            'ENTRANT': prospections.filter(type_appel='ENTRANT').count(),
        },
        'total': prospections.count(),
    }
    
    return JsonResponse(stats)
