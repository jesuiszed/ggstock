from django import forms
from django.forms import inlineformset_factory
from .models import Client, Produit, Commande, Vente, Fournisseur, Categorie, MouvementStock
from .models import Devis, LigneDevis, Prospect, NoteObservation, AppareilVendu, InterventionSAV, TransfertStock
from datetime import date, timedelta


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['client', 'date_validite', 'notes', 'conditions_particulieres']
        widgets = {
            'date_validite': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'conditions_particulieres': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'client': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Nouveau devis
            self.initial['date_validite'] = date.today() + timedelta(days=30)


class LigneDevisForm(forms.ModelForm):
    class Meta:
        model = LigneDevis
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise']
        widgets = {
            'produit': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'quantite': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'step': '0.01'}),
            'remise': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'step': '0.01', 'min': 0, 'max': 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'produit' in self.data and self.data['produit']:
            try:
                produit = Produit.objects.get(pk=self.data['produit'])
                self.initial['prix_unitaire'] = produit.prix_vente
            except Produit.DoesNotExist:
                pass


LigneDevisFormSet = inlineformset_factory(
    Devis, LigneDevis, form=LigneDevisForm,
    extra=1, can_delete=True
)


class ProspectForm(forms.ModelForm):
    class Meta:
        model = Prospect
        fields = ['nom', 'prenom', 'entreprise', 'email', 'telephone', 'adresse', 'ville', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'prenom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'entreprise': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'telephone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'ville': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'statut': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class NoteObservationForm(forms.ModelForm):
    class Meta:
        model = NoteObservation
        fields = ['type_note', 'titre', 'contenu', 'date_rappel']
        widgets = {
            'type_note': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'titre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'contenu': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_rappel': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class AppareilVenduForm(forms.ModelForm):
    class Meta:
        model = AppareilVendu
        fields = ['numero_serie', 'produit', 'client', 'date_installation', 'lieu_installation', 
                 'statut', 'prochaine_maintenance_preventive', 'intervalle_maintenance_jours',
                 'notes_installation', 'technicien_responsable']
        widgets = {
            'numero_serie': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'produit': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'client': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_installation': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'lieu_installation': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'statut': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'prochaine_maintenance_preventive': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'intervalle_maintenance_jours': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'notes_installation': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'technicien_responsable': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les techniciens seulement
        from users.models import Profile
        techniciens = Profile.objects.filter(role='TECHNICIEN').values_list('user', flat=True)
        self.fields['technicien_responsable'].queryset = self.fields['technicien_responsable'].queryset.filter(id__in=techniciens)


class InterventionSAVForm(forms.ModelForm):
    class Meta:
        model = InterventionSAV
        fields = ['type_intervention', 'appareil', 'technicien', 'date_prevue', 'duree_prevue', 
                 'description', 'statut']
        widgets = {
            'type_intervention': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'appareil': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'technicien': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_prevue': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'duree_prevue': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': 'Durée en minutes'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'statut': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les techniciens seulement
        from users.models import Profile
        techniciens = Profile.objects.filter(role='TECHNICIEN').values_list('user', flat=True)
        self.fields['technicien'].queryset = self.fields['technicien'].queryset.filter(id__in=techniciens)


class TransfertStockForm(forms.ModelForm):
    class Meta:
        model = TransfertStock
        fields = ['produit', 'quantite', 'origine', 'destination', 'notes']
        widgets = {
            'produit': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'quantite': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'min': 1}),
            'origine': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'destination': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class InterventionSAVCompletionForm(forms.ModelForm):
    """Formulaire pour compléter une intervention SAV"""
    class Meta:
        model = InterventionSAV
        fields = ['date_realisee', 'duree_reelle', 'travaux_realises', 'pieces_changees', 
                 'observations', 'statut']
        widgets = {
            'date_realisee': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'duree_reelle': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': 'Durée en minutes'}),
            'travaux_realises': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'pieces_changees': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'observations': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'statut': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter les statuts pour la complétion
        self.fields['statut'].choices = [
            ('TERMINEE', 'Terminée'),
            ('REPORTEE', 'Reportée'),
        ]
