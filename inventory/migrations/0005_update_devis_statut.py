# Generated migration for updating devis statut values

from django.db import migrations


def update_devis_statuts(apps, schema_editor):
    """Mettre à jour les statuts existants"""
    Devis = apps.get_model('inventory', 'Devis')
    
    # Remplacer ENVOYE par EN_COURS_VALIDATION
    Devis.objects.filter(statut='ENVOYE').update(statut='EN_COURS_VALIDATION')
    
    # Remplacer ACCEPTE par VALIDE
    Devis.objects.filter(statut='ACCEPTE').update(statut='VALIDE')


def reverse_devis_statuts(apps, schema_editor):
    """Annuler les changements si besoin"""
    Devis = apps.get_model('inventory', 'Devis')
    
    # Restaurer les anciens statuts
    Devis.objects.filter(statut='EN_COURS_VALIDATION').update(statut='ENVOYE')
    Devis.objects.filter(statut='VALIDE').update(statut='ACCEPTE')


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_interventionsav_client'),
    ]

    operations = [
        migrations.RunPython(update_devis_statuts, reverse_devis_statuts),
    ]
