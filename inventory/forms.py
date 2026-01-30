from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date
from .models import (
    Produit, Client, Commande, Vente, MouvementStock, 
    Fournisseur, Categorie, LigneCommande, LigneVente,
    ProspectionTelephonique
)


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'nom', 'reference', 'code_barre', 'description', 'categorie', 
            'fournisseur', 'prix_achat', 'prix_vente', 'quantite_stock', 
            'seuil_alerte', 'image', 'actif'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'code_barre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'seuil_alerte': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'nom', 'prenom', 'email', 'telephone', 'adresse', 
            'ville', 'code_postal', 'pays', 'date_naissance', 'actif'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = [
            'nom', 'email', 'telephone', 'adresse', 'ville', 
            'code_postal', 'pays', 'actif'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = [
            'numero_commande', 'client', 'statut', 'date_livraison_prevue',
            'adresse_livraison', 'notes'
        ]
        widgets = {
            'numero_commande': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'readonly': 'readonly'
            }),
            'client': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'onchange': 'updateClientAddress(this)'
            }),
            'statut': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
            }),
            'date_livraison_prevue': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'adresse_livraison': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'rows': 3,
                'placeholder': 'Adresse de livraison complète...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'rows': 3,
                'placeholder': 'Instructions spéciales, commentaires...'
            }),
        }
        labels = {
            'numero_commande': 'Numéro de commande',
            'client': 'Client',
            'statut': 'Statut',
            'date_livraison_prevue': 'Date de livraison prévue',
            'adresse_livraison': 'Adresse de livraison',
            'notes': 'Notes et instructions',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Générer automatiquement un numéro de commande
            from datetime import datetime
            self.fields['numero_commande'].initial = f"CMD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self.fields['date_livraison_prevue'].help_text = "Date prévue pour la livraison"
        self.fields['adresse_livraison'].help_text = "L'adresse du client sera automatiquement renseignée"
        
    def clean_date_livraison_prevue(self):
        date_livraison = self.cleaned_data.get('date_livraison_prevue')
        if date_livraison and date_livraison < date.today():
            raise forms.ValidationError("La date de livraison ne peut pas être dans le passé")
        return date_livraison


class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'produit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'onchange': 'updatePrice(this)'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'min': '1',
                'oninput': 'calculateSubtotal(this)'
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'step': '0.01',
                'min': '0.01',
                'oninput': 'calculateSubtotal(this)'
            }),
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
            'prix_unitaire': 'Prix unitaire (F CFA)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit'].queryset = Produit.objects.filter(actif=True)
        self.fields['prix_unitaire'].help_text = "Prix sera automatiquement rempli lors de la sélection du produit"


class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = [
            'numero_vente', 'client', 'mode_paiement', 'remise', 'notes'
        ]
        widgets = {
            'numero_vente': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'readonly': 'readonly'
            }),
            'client': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
            }),
            'mode_paiement': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
            }),
            'remise': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'rows': 3,
                'placeholder': 'Notes additionnelles...'
            }),
        }
        labels = {
            'numero_vente': 'Numéro de vente',
            'client': 'Client',
            'mode_paiement': 'Mode de paiement',
            'remise': 'Remise (%)',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Générer automatiquement un numéro de vente
            from datetime import datetime
            self.fields['numero_vente'].initial = f"VTE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Permettre les ventes sans client (vente comptoir)
        self.fields['client'].required = False
        self.fields['client'].empty_label = "--- Vente comptoir ---"
        
        # Améliorer les choix de mode de paiement
        self.fields['mode_paiement'].help_text = "Sélectionnez le mode de paiement utilisé"
        self.fields['remise'].help_text = "Remise en pourcentage (0-100)"


class LigneVenteForm(forms.ModelForm):
    class Meta:
        model = LigneVente
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'produit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'onchange': 'updatePrice(this)'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'min': '1',
                'oninput': 'calculateSubtotal(this)'
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'step': '0.01',
                'min': '0.01',
                'oninput': 'calculateSubtotal(this)'
            }),
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
            'prix_unitaire': 'Prix unitaire (F CFA)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter aux produits actifs avec stock
        self.fields['produit'].queryset = Produit.objects.filter(
            actif=True, 
            quantite_stock__gt=0
        )
        self.fields['prix_unitaire'].help_text = "Prix sera automatiquement rempli lors de la sélection du produit"
        
    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        quantite = cleaned_data.get('quantite')
        
        if produit and quantite:
            if quantite > produit.quantite_stock:
                raise forms.ValidationError(
                    f"Quantité insuffisante en stock. Stock disponible: {produit.quantite_stock}"
                )
        
        return cleaned_data


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = [
            'produit', 'type_mouvement', 'quantite', 'motif', 'numero_lot'
        ]
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_lot': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit'].queryset = Produit.objects.filter(actif=True)


class RechercheForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Rechercher...'
            }
        )
    )


class FiltreStockForm(forms.Form):
    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.filter(actif=True),
        required=False,
        empty_label="Tous les fournisseurs",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    stock_bas = forms.BooleanField(
        required=False,
        label="Stock bas uniquement",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class FiltreDateForm(forms.Form):
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProspectionTelephoniqueForm(forms.ModelForm):
    """Formulaire pour la prospection téléphonique"""
    class Meta:
        model = ProspectionTelephonique
        fields = [
            'nom_complet', 'numero_telephone', 'statut', 'date_rdv', 
            'description', 'type_appel', 'email', 'source_prospect'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: Jean Dupont'
            }),
            'numero_telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: +221 77 123 45 67'
            }),
            'statut': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'date_rdv': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Détails de la conversation, besoins identifiés, remarques...'
            }),
            'type_appel': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_type_appel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'exemple@email.com',
                'id': 'id_email'
            }),
            'source_prospect': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_source_prospect'
            }),
        }
        labels = {
            'nom_complet': 'Nom complet',
            'numero_telephone': 'Numéro téléphonique',
            'statut': 'Statut',
            'date_rdv': 'Date de RDV (facultatif)',
            'description': 'Description',
            'type_appel': "Type d'appel",
            'email': 'Email (pour appel sortant uniquement)',
            'source_prospect': 'Source de prospect (pour appel entrant uniquement)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        type_appel = cleaned_data.get('type_appel')
        email = cleaned_data.get('email')
        source_prospect = cleaned_data.get('source_prospect')
        
        # Validation: Email obligatoire pour appel sortant
        if type_appel == 'SORTANT' and not email:
            self.add_error('email', 'L\'email est obligatoire pour un appel sortant.')
        
        # Validation: Source obligatoire pour appel entrant
        if type_appel == 'ENTRANT' and not source_prospect:
            self.add_error('source_prospect', 'La source de prospect est obligatoire pour un appel entrant.')
        
        # Nettoyage: Vider email si appel entrant
        if type_appel == 'ENTRANT':
            cleaned_data['email'] = None
        
        # Nettoyage: Vider source si appel sortant
        if type_appel == 'SORTANT':
            cleaned_data['source_prospect'] = None
        
        return cleaned_data
