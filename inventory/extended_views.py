from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
from users.decorators import role_required
from .models import *
from .extended_forms import *
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


# ========== VUES DEVIS ==========

@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def devis_list(request):
    """Liste des devis pour commercial terrain"""
    devis_list = Devis.objects.all()
    
    # Filtrage par statut
    statut = request.GET.get('statut')
    if statut:
        devis_list = devis_list.filter(statut=statut)
    
    # Filtrage par commercial (si pas manager)
    if request.user.profile.role == 'COMMERCIAL_TERRAIN':
        devis_list = devis_list.filter(commercial=request.user)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        devis_list = devis_list.filter(
            Q(numero_devis__icontains=search) |
            Q(client__nom__icontains=search) |
            Q(client__prenom__icontains=search) |
            Q(client__entreprise__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(devis_list, 20)
    page_number = request.GET.get('page')
    devis = paginator.get_page(page_number)
    
    # Statistiques pour le dashboard
    stats = {
        'total_devis': devis_list.count(),
        'devis_brouillon': devis_list.filter(statut='BROUILLON').count(),
        'devis_envoyes': devis_list.filter(statut='ENVOYE').count(),
        'devis_acceptes': devis_list.filter(statut='ACCEPTE').count(),
        'total_montant': devis_list.aggregate(total=Sum('total'))['total'] or 0,
    }
    
    context = {
        'devis': devis,
        'stats': stats,
        'statut_choices': Devis.STATUT_CHOICES,
        'current_statut': statut,
        'search': search,
    }
    return render(request, 'inventory/devis_list.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def devis_detail(request, pk):
    """Détail d'un devis"""
    devis = get_object_or_404(Devis, pk=pk)
    
    # Vérifier les permissions
    if request.user.profile.role == 'COMMERCIAL_TERRAIN' and devis.commercial != request.user:
        messages.error(request, "Vous n'avez pas accès à ce devis.")
        return redirect('inventory:devis_list')
    
    lignes_devis = devis.lignedevis_set.all()
    
    context = {
        'devis': devis,
        'lignes_devis': lignes_devis,
    }
    return render(request, 'inventory/devis_detail.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def devis_create(request):
    """Créer un nouveau devis avec parsing manuel des lignes"""
    if request.method == 'POST':
        form = DevisForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    devis = form.save(commit=False)
                    devis.commercial = request.user
                    devis.save()
                    
                    # ✅ PARSING MANUEL (comme commande_create_advanced)
                    lines_created = 0
                    lines_data = {}
                    has_error = False
                    
                    # Parser toutes les clés POST pour trouver TOUTES les lignes de produit
                    for key in request.POST:
                        if key.startswith('ligne_') and '_' in key:
                            parts = key.split('_', 2)  # ligne_0_produit → ['ligne', '0', 'produit']
                            if len(parts) == 3:
                                line_idx = parts[1]
                                field_name = parts[2]
                                
                                if line_idx not in lines_data:
                                    lines_data[line_idx] = {}
                                lines_data[line_idx][field_name] = request.POST[key]
                    
                    print(f"=== DEBUG DEVIS_CREATE ===")
                    print(f"POST data: {request.POST}")
                    print(f"Lignes trouvées: {sorted(lines_data.keys())}")
                    
                    # Traiter chaque ligne trouvée (triée par index)
                    for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                        data = lines_data[line_idx]
                        produit_id = data.get('produit')
                        quantite = data.get('quantite')
                        prix_unitaire = data.get('prix_unitaire')
                        remise = data.get('remise', '0')  # Remise optionnelle
                        
                        print(f"Traitement ligne {line_idx}: produit={produit_id}, qte={quantite}, prix={prix_unitaire}, remise={remise}")
                        
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
                            remise = float(remise) if remise else 0
                            
                            # Validations
                            if quantite <= 0:
                                messages.error(request, f'{produit.nom}: La quantité doit être positive')
                                has_error = True
                                continue
                            
                            if prix_unitaire < 0:
                                messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                                has_error = True
                                continue
                            
                            if remise < 0 or remise > 100:
                                messages.error(request, f'{produit.nom}: La remise doit être entre 0 et 100%')
                                has_error = True
                                continue
                            
                            # Créer la ligne de devis
                            ligne = LigneDevis.objects.create(
                                devis=devis,
                                produit=produit,
                                quantite=quantite,
                                prix_unitaire=prix_unitaire,
                                remise=remise
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
                        messages.error(request, 'Un devis doit contenir au moins un produit')
                        raise ValueError('Aucune ligne de produit')
                    
                    # Calculer le total
                    devis.calculer_total()
                    
                    messages.success(request, f"Devis {devis.numero_devis} créé avec succès ({lines_created} ligne(s)).")
                    return redirect('inventory:devis_detail', pk=devis.pk)
                    
            except ValueError as e:
                # Erreur de validation, le formulaire sera réaffiché avec les erreurs
                print(f"Erreur de validation: {e}")
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = DevisForm()
    
    context = {
        'form': form,
        'title': 'Créer un Devis',
        'produits': Produit.objects.filter(actif=True),
    }
    return render(request, 'inventory/devis_form.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def devis_edit(request, pk):
    """Modifier un devis avec parsing manuel des lignes"""
    devis = get_object_or_404(Devis, pk=pk)
    
    # Vérifier les permissions
    if request.user.profile.role == 'COMMERCIAL_TERRAIN' and devis.commercial != request.user:
        messages.error(request, "Vous n'avez pas accès à ce devis.")
        return redirect('inventory:devis_list')
    
    if request.method == 'POST':
        form = DevisForm(request.POST, instance=devis)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    devis = form.save()
                    
                    # Supprimer les anciennes lignes
                    devis.lignedevis_set.all().delete()
                    
                    # ✅ PARSING MANUEL (comme devis_create)
                    lines_created = 0
                    lines_data = {}
                    has_error = False
                    
                    # Parser toutes les clés POST pour trouver TOUTES les lignes de produit
                    for key in request.POST:
                        if key.startswith('ligne_') and '_' in key:
                            parts = key.split('_', 2)
                            if len(parts) == 3:
                                line_idx = parts[1]
                                field_name = parts[2]
                                
                                if line_idx not in lines_data:
                                    lines_data[line_idx] = {}
                                lines_data[line_idx][field_name] = request.POST[key]
                    
                    print(f"=== DEBUG DEVIS_EDIT ===")
                    print(f"POST data: {request.POST}")
                    print(f"Lignes trouvées: {sorted(lines_data.keys())}")
                    
                    # Traiter chaque ligne trouvée (triée par index)
                    for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                        data = lines_data[line_idx]
                        produit_id = data.get('produit')
                        quantite = data.get('quantite')
                        prix_unitaire = data.get('prix_unitaire')
                        remise = data.get('remise', '0')
                        
                        print(f"Traitement ligne {line_idx}: produit={produit_id}, qte={quantite}, prix={prix_unitaire}, remise={remise}")
                        
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
                            remise = float(remise) if remise else 0
                            
                            # Validations
                            if quantite <= 0:
                                messages.error(request, f'{produit.nom}: La quantité doit être positive')
                                has_error = True
                                continue
                            
                            if prix_unitaire < 0:
                                messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                                has_error = True
                                continue
                            
                            if remise < 0 or remise > 100:
                                messages.error(request, f'{produit.nom}: La remise doit être entre 0 et 100%')
                                has_error = True
                                continue
                            
                            # Créer la ligne de devis
                            ligne = LigneDevis.objects.create(
                                devis=devis,
                                produit=produit,
                                quantite=quantite,
                                prix_unitaire=prix_unitaire,
                                remise=remise
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
                        messages.error(request, 'Un devis doit contenir au moins un produit')
                        raise ValueError('Aucune ligne de produit')
                    
                    # Calculer le total
                    devis.calculer_total()
                    
                    messages.success(request, f"Devis {devis.numero_devis} modifié avec succès ({lines_created} ligne(s)).")
                    return redirect('inventory:devis_detail', pk=devis.pk)
                    
            except ValueError as e:
                # Erreur de validation, le formulaire sera réaffiché avec les erreurs
                print(f"Erreur de validation: {e}")
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = DevisForm(instance=devis)
    
    context = {
        'form': form,
        'devis': devis,
        'lignes_existantes': list(devis.lignedevis_set.all()),  # Pour pré-remplir le formulaire
        'title': f'Modifier le Devis {devis.numero_devis}',
        'produits': Produit.objects.filter(actif=True),
    }
    return render(request, 'inventory/devis_form.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def devis_pdf(request, pk):
    """Générer un PDF pour un devis"""
    devis = get_object_or_404(Devis, pk=pk)
    
    # Vérifier les permissions
    if request.user.profile.role == 'COMMERCIAL_TERRAIN' and devis.commercial != request.user:
        messages.error(request, "Vous n'avez pas accès à ce devis.")
        return redirect('inventory:devis_list')
    
    # Créer le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="devis_{devis.numero_devis}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Styles
    styles = getSampleStyleSheet()
    elements = []
    
    # En-tête
    elements.append(Paragraph(f"DEVIS N° {devis.numero_devis}", styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Informations client
    client_info = f"""
    <b>Client:</b> {devis.client.nom_complet}<br/>
    <b>Entreprise:</b> {devis.client.entreprise}<br/>
    <b>Email:</b> {devis.client.email}<br/>
    <b>Téléphone:</b> {devis.client.telephone}<br/>
    """
    elements.append(Paragraph(client_info, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Informations devis
    devis_info = f"""
    <b>Date de création:</b> {devis.date_creation.strftime('%d/%m/%Y')}<br/>
    <b>Valide jusqu'au:</b> {devis.date_validite.strftime('%d/%m/%Y')}<br/>
    <b>Commercial:</b> {devis.commercial.get_full_name()}<br/>
    <b>Statut:</b> {devis.get_statut_display()}
    """
    elements.append(Paragraph(devis_info, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tableau des lignes
    data = [['Produit', 'Quantité', 'Prix unitaire', 'Remise', 'Sous-total']]
    
    for ligne in devis.lignedevis_set.all():
        data.append([
            ligne.produit.nom,
            str(ligne.quantite),
            f"{ligne.prix_unitaire:.2f} F CFA",
            f"{ligne.remise:.2f}%",
            f"{ligne.sous_total():.2f} F CFA"
        ])
    
    # Total
    data.append(['', '', '', 'TOTAL', f"{devis.total:.2f} F CFA"])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Notes
    if devis.notes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Notes:</b> {devis.notes}", styles['Normal']))
    
    # Conditions particulières
    if devis.conditions_particulieres:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Conditions particulières:</b> {devis.conditions_particulieres}", styles['Normal']))
    
    # Construire le PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


# ========== VUES PROSPECTS ==========

@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospect_list(request):
    """Liste des prospects"""
    prospects_list = Prospect.objects.all()
    
    # Filtrage par commercial (si pas manager)
    if request.user.profile.role == 'COMMERCIAL_TERRAIN':
        prospects_list = prospects_list.filter(commercial=request.user)
    
    # Filtrage par statut
    statut = request.GET.get('statut')
    if statut:
        prospects_list = prospects_list.filter(statut=statut)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        prospects_list = prospects_list.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(entreprise__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(prospects_list, 20)
    page_number = request.GET.get('page')
    prospects = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total_prospects': prospects_list.count(),
        'nouveaux': prospects_list.filter(statut='NOUVEAU').count(),
        'qualifies': prospects_list.filter(statut='QUALIFIE').count(),
        'convertis': prospects_list.filter(statut='CONVERTI').count(),
    }
    
    context = {
        'prospects': prospects,
        'stats': stats,
        'statut_choices': Prospect.STATUT_CHOICES,
        'current_statut': statut,
        'search': search,
    }
    return render(request, 'inventory/prospect_list.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospect_create(request):
    """Créer un nouveau prospect"""
    if request.method == 'POST':
        form = ProspectForm(request.POST)
        if form.is_valid():
            prospect = form.save(commit=False)
            prospect.commercial = request.user
            prospect.save()
            
            messages.success(request, f"Prospect {prospect.nom_complet} créé avec succès.")
            return redirect('inventory:prospect_detail', pk=prospect.pk)
    else:
        form = ProspectForm()
    
    context = {
        'form': form,
        'title': 'Nouveau Prospect',
    }
    return render(request, 'inventory/prospect_form.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospect_detail(request, pk):
    """Détail d'un prospect avec ses notes"""
    prospect = get_object_or_404(Prospect, pk=pk)
    
    # Vérifier les permissions
    if request.user.profile.role == 'COMMERCIAL_TERRAIN' and prospect.commercial != request.user:
        messages.error(request, "Vous n'avez pas accès à ce prospect.")
        return redirect('inventory:prospect_list')
    
    notes = prospect.notes.all()[:10]  # 10 dernières notes
    
    context = {
        'prospect': prospect,
        'notes': notes,
    }
    return render(request, 'inventory/prospect_detail.html', context)


@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
def prospect_edit(request, pk):
    """Modifier un prospect"""
    prospect = get_object_or_404(Prospect, pk=pk)
    
    # Vérifier les permissions
    if request.user.profile.role == 'COMMERCIAL_TERRAIN' and prospect.commercial != request.user:
        messages.error(request, "Vous n'avez pas accès à ce prospect.")
        return redirect('inventory:prospect_list')
    
    if request.method == 'POST':
        form = ProspectForm(request.POST, instance=prospect)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prospect modifié avec succès.')
            return redirect('inventory:prospect_detail', pk=prospect.pk)
    else:
        form = ProspectForm(instance=prospect)
    
    context = {
        'form': form,
        'object': prospect,
    }
    return render(request, 'inventory/prospect_form.html', context)


# ========== VUES NOTES D'OBSERVATION ==========

@login_required
@role_required(['COMMERCIAL_TERRAIN', 'COMMERCIAL_SHOWROOM', 'MANAGER'])
def note_create(request):
    """Créer une nouvelle note d'observation"""
    if request.method == 'POST':
        form = NoteObservationForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.auteur = request.user
            note.save()
            
            messages.success(request, "Note créée avec succès.")
            
            # Rediriger vers le détail du client ou prospect
            if note.client:
                return redirect('inventory:client_detail', pk=note.client.pk)
            elif note.prospect:
                return redirect('inventory:prospect_detail', pk=note.prospect.pk)
            else:
                return redirect('inventory:notes_list')
    else:
        form = NoteObservationForm()
        
        # Pré-remplir si client ou prospect spécifié
        client_id = request.GET.get('client')
        prospect_id = request.GET.get('prospect')
        
        if client_id:
            form.initial['client'] = client_id
        elif prospect_id:
            form.initial['prospect'] = prospect_id
    
    context = {
        'form': form,
        'title': 'Nouvelle Note',
    }
    return render(request, 'inventory/note_form.html', context)


# ========== VUES APPAREILS VENDUS ==========

@login_required
@role_required(['TECHNICIEN', 'MANAGER'])
def appareil_list(request):
    """Liste des appareils vendus"""
    appareils_list = AppareilVendu.objects.select_related('produit', 'client', 'technicien_responsable')
    
    # Filtrage par technicien (si pas manager)
    if request.user.profile.role == 'TECHNICIEN':
        appareils_list = appareils_list.filter(technicien_responsable=request.user)
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        appareils_list = appareils_list.filter(statut=statut)
    
    maintenance_due = request.GET.get('maintenance_due')
    if maintenance_due == 'true':
        appareils_list = appareils_list.filter(prochaine_maintenance_preventive__lte=date.today())
    
    # Recherche
    search = request.GET.get('search')
    if search:
        appareils_list = appareils_list.filter(
            Q(numero_serie__icontains=search) |
            Q(produit__nom__icontains=search) |
            Q(client__nom__icontains=search) |
            Q(lieu_installation__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(appareils_list, 20)
    page_number = request.GET.get('page')
    appareils = paginator.get_page(page_number)
    
    # Statistiques
    maintenance_due_count = AppareilVendu.objects.filter(prochaine_maintenance_preventive__lte=date.today()).count()
    
    context = {
        'appareils': appareils,
        'maintenance_due_count': maintenance_due_count,
        'statut_choices': AppareilVendu.STATUT_CHOICES,
        'current_statut': statut,
        'search': search,
    }
    return render(request, 'inventory/appareil_list.html', context)


@login_required
@role_required(['TECHNICIEN', 'MANAGER'])
def appareil_detail(request, pk):
    """Détail d'un appareil avec historique des interventions"""
    appareil = get_object_or_404(AppareilVendu, pk=pk)
    
    interventions = appareil.interventions.all()[:10]  # 10 dernières interventions
    
    context = {
        'appareil': appareil,
        'interventions': interventions,
    }
    return render(request, 'inventory/appareil_detail.html', context)


# ========== VUES INTERVENTIONS SAV ==========

@login_required
@role_required(['TECHNICIEN', 'MANAGER'])
def intervention_list(request):
    """Liste des interventions SAV"""
    interventions_list = InterventionSAV.objects.select_related('appareil', 'client', 'technicien')
    
    # Filtrage par technicien (si pas manager)
    if request.user.profile.role == 'TECHNICIEN':
        interventions_list = interventions_list.filter(technicien=request.user)
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        interventions_list = interventions_list.filter(statut=statut)
    
    type_intervention = request.GET.get('type')
    if type_intervention:
        interventions_list = interventions_list.filter(type_intervention=type_intervention)
    
    # Pagination
    paginator = Paginator(interventions_list, 20)
    page_number = request.GET.get('page')
    interventions = paginator.get_page(page_number)
    
    context = {
        'interventions': interventions,
        'statut_choices': InterventionSAV.STATUT_CHOICES,
        'type_choices': InterventionSAV.TYPE_CHOICES,
        'current_statut': statut,
        'current_type': type_intervention,
    }
    return render(request, 'inventory/intervention_list.html', context)


@login_required
@role_required(['TECHNICIEN', 'MANAGER'])
def intervention_create(request):
    """Créer une nouvelle intervention SAV"""
    if request.method == 'POST':
        form = InterventionSAVForm(request.POST)
        if form.is_valid():
            intervention = form.save(commit=False)
            # Le technicien par défaut est l'utilisateur connecté si c'est un technicien
            if request.user.profile.role == 'TECHNICIEN':
                intervention.technicien = request.user
            intervention.save()
            
            messages.success(request, f"Intervention {intervention.numero_intervention} planifiée avec succès.")
            return redirect('inventory:intervention_detail', pk=intervention.pk)
    else:
        form = InterventionSAVForm()
        
        # Pré-remplir l'appareil si spécifié
        appareil_id = request.GET.get('appareil')
        if appareil_id:
            appareil = get_object_or_404(AppareilVendu, pk=appareil_id)
            form.initial['appareil'] = appareil
            form.initial['client'] = appareil.client
    
    context = {
        'form': form,
        'title': 'Planifier une Intervention',
    }
    return render(request, 'inventory/intervention_form.html', context)


@login_required
@role_required(['TECHNICIEN', 'MANAGER'])
def intervention_detail(request, pk):
    """Détail d'une intervention SAV"""
    intervention = get_object_or_404(InterventionSAV, pk=pk)
    
    context = {
        'intervention': intervention,
    }
    return render(request, 'inventory/intervention_detail.html', context)


@login_required
@role_required(['TECHNICIEN', 'MANAGER'])
def intervention_edit(request, pk):
    """Modifier une intervention SAV"""
    intervention = get_object_or_404(InterventionSAV, pk=pk)
    
    if request.method == 'POST':
        form = InterventionSAVForm(request.POST, instance=intervention)
        if form.is_valid():
            # Gérer les actions spéciales depuis l'URL
            action = request.GET.get('action')
            if action == 'start':
                form.instance.statut = 'EN_COURS'
                form.instance.date_realisee = timezone.now()
            elif action == 'complete':
                form.instance.statut = 'TERMINEE'
                if not form.instance.date_realisee:
                    form.instance.date_realisee = timezone.now()
            
            form.save()
            messages.success(request, 'Intervention modifiée avec succès.')
            return redirect('inventory:intervention_detail', pk=intervention.pk)
    else:
        form = InterventionSAVForm(instance=intervention)
        
        # Pré-remplir selon l'action
        action = request.GET.get('action')
        if action == 'start':
            form.initial['statut'] = 'EN_COURS'
            form.initial['date_realisee'] = timezone.now()
        elif action == 'complete':
            form.initial['statut'] = 'TERMINEE'
            if not intervention.date_realisee:
                form.initial['date_realisee'] = timezone.now()
    
    context = {
        'form': form,
        'object': intervention,
    }
    return render(request, 'inventory/intervention_form.html', context)


# ========== VUES TRANSFERTS DE STOCK ==========

@login_required
@role_required(['TECHNICIEN', 'COMMERCIAL_SHOWROOM', 'MANAGER'])
def transfert_list(request):
    """Liste des transferts de stock"""
    transferts_list = TransfertStock.objects.select_related('produit', 'demandeur')
    
    # Filtrage par utilisateur
    if request.user.profile.role in ['TECHNICIEN', 'COMMERCIAL_SHOWROOM']:
        transferts_list = transferts_list.filter(
            Q(demandeur=request.user) | 
            Q(expediteur=request.user) | 
            Q(recepteur=request.user)
        )
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        transferts_list = transferts_list.filter(statut=statut)
    
    # Pagination
    paginator = Paginator(transferts_list, 20)
    page_number = request.GET.get('page')
    transferts = paginator.get_page(page_number)
    
    context = {
        'transferts': transferts,
        'statut_choices': TransfertStock.STATUT_CHOICES,
        'current_statut': statut,
    }
    return render(request, 'inventory/transfert_list.html', context)


@login_required
@role_required(['TECHNICIEN', 'COMMERCIAL_SHOWROOM', 'MANAGER'])
def transfert_create(request):
    """Créer un nouveau transfert de stock"""
    if request.method == 'POST':
        form = TransfertStockForm(request.POST)
        if form.is_valid():
            transfert = form.save(commit=False)
            transfert.demandeur = request.user
            transfert.save()
            
            messages.success(request, f"Transfert {transfert.numero_transfert} créé avec succès.")
            return redirect('inventory:transfert_detail', pk=transfert.pk)
    else:
        form = TransfertStockForm()
    
    context = {
        'form': form,
        'title': 'Nouveau Transfert de Stock',
    }
    return render(request, 'inventory/transfert_form.html', context)


@login_required
@role_required(['TECHNICIEN', 'COMMERCIAL_SHOWROOM', 'MANAGER'])
def transfert_detail(request, pk):
    """Détail d'un transfert de stock"""
    transfert = get_object_or_404(TransfertStock, pk=pk)
    
    context = {
        'transfert': transfert,
    }
    return render(request, 'inventory/transfert_detail.html', context)


@login_required
@role_required(['TECHNICIEN', 'COMMERCIAL_SHOWROOM', 'MANAGER'])
def transfert_edit(request, pk):
    """Modifier un transfert de stock"""
    transfert = get_object_or_404(TransfertStock, pk=pk)
    
    if request.method == 'POST':
        form = TransfertStockForm(request.POST, instance=transfert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transfert modifié avec succès.')
            return redirect('inventory:transfert_detail', pk=transfert.pk)
    else:
        form = TransfertStockForm(instance=transfert)
    
    context = {
        'form': form,
        'object': transfert,
    }
    return render(request, 'inventory/transfert_form.html', context)
