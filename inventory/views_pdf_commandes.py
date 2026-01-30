"""
Vues de génération de PDF pour les commandes avec WeasyPrint
Bon de Commande, Facture Proforma, Bon de Livraison
"""

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
from decimal import Decimal
from datetime import datetime
import os

from .models import Commande, LigneCommande


def commande_print_bon_weasyprint(request, pk):
    """Générer le bon de commande en PDF professionnel avec WeasyPrint"""
    commande = get_object_or_404(Commande, pk=pk)
    lignes_commande = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    # Calculer TVA et Total TTC
    tva = commande.total * Decimal('0.18')
    total_ttc = commande.total + tva
    
    # Calculer quantité totale
    total_quantity = sum(ligne.quantite for ligne in lignes_commande)
    
    # Chemin absolu vers le logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    
    # Préparer le contexte
    context = {
        'commande': commande,
        'lignes_commande': lignes_commande,
        'tva': tva,
        'total_ttc': total_ttc,
        'total_quantite': total_quantity,
        'now': datetime.now(),
        'logo_path': logo_path,
        'STATIC_ROOT': os.path.join(settings.BASE_DIR, 'static'),
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


def commande_print_proforma_weasyprint(request, pk):
    """Générer la facture proforma en PDF professionnel avec WeasyPrint"""
    commande = get_object_or_404(Commande, pk=pk)
    lignes_commande = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    # Calculer TVA et Total TTC
    tva = commande.total * Decimal('0.18')
    total_ttc = commande.total + tva
    
    # Chemin absolu vers le logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    
    # Préparer le contexte
    context = {
        'commande': commande,
        'lignes_commande': lignes_commande,
        'tva': tva,
        'total_ttc': total_ttc,
        'now': datetime.now(),
        'logo_path': logo_path,
        'STATIC_ROOT': os.path.join(settings.BASE_DIR, 'static'),
    }
    
    # Rendre le template HTML
    html_string = render_to_string('inventory/facture_proforma_pdf.html', context)
    
    # Générer le PDF avec WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    
    # Créer la réponse HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_Proforma_{commande.numero_commande}.pdf"'
    
    return response


def commande_print_livraison_weasyprint(request, pk):
    """Générer le bon de livraison en PDF professionnel avec WeasyPrint"""
    commande = get_object_or_404(Commande, pk=pk)
    lignes_commande = LigneCommande.objects.filter(commande=commande).select_related('produit')
    
    # Calculer quantité totale et quantité livrée
    total_quantite = sum(ligne.quantite for ligne in lignes_commande)
    total_quantite_livree = sum(ligne.quantite_recue if ligne.quantite_recue else ligne.quantite for ligne in lignes_commande)
    
    # Chemin absolu vers le logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    
    # Préparer le contexte
    context = {
        'commande': commande,
        'lignes_commande': lignes_commande,
        'total_quantite': total_quantite,
        'total_quantite_livree': total_quantite_livree,
        'now': datetime.now(),
        'logo_path': logo_path,
        'STATIC_ROOT': os.path.join(settings.BASE_DIR, 'static'),
    }
    
    # Rendre le template HTML
    html_string = render_to_string('inventory/bon_livraison_pdf.html', context)
    
    # Générer le PDF avec WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    
    # Créer la réponse HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bon_Livraison_{commande.numero_commande}.pdf"'
    
    return response
