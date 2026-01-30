from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    ville = models.CharField(max_length=50)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50, default="France")
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=200)
    reference = models.CharField(max_length=50, unique=True)
    code_barre = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantite_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    seuil_alerte = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return f"{self.nom} - {self.reference}"

    def is_stock_bas(self):
        return self.quantite_stock <= self.seuil_alerte

    def marge_beneficiaire(self):
        return ((self.prix_vente - self.prix_achat) / self.prix_achat) * 100 if self.prix_achat > 0 else 0

    @property
    def valeur_stock(self):
        return self.quantite_stock * self.prix_achat


class MouvementStock(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
        ('AJUSTEMENT', 'Ajustement'),
        ('RETOUR', 'Retour'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    type_mouvement = models.CharField(max_length=20, choices=TYPE_MOUVEMENT_CHOICES)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    quantite_avant = models.IntegerField()
    quantite_apres = models.IntegerField()
    motif = models.CharField(max_length=200)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    numero_lot = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Mouvement de Stock"
        verbose_name_plural = "Mouvements de Stock"
        ordering = ['-date_mouvement']

    def __str__(self):
        return f"{self.produit.nom} - {self.type_mouvement} - {self.quantite}"


class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    entreprise = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    ville = models.CharField(max_length=50)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50, default="France")
    date_naissance = models.DateField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Commande(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmée'),
        ('EXPEDIEE', 'Expédiée'),
        ('LIVREE', 'Livrée'),
        ('ANNULEE', 'Annulée'),
    ]

    numero_commande = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_commande = models.DateTimeField(auto_now_add=True)
    date_livraison_prevue = models.DateField(blank=True, null=True)
    adresse_livraison = models.TextField()
    notes = models.TextField(blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande {self.numero_commande} - {self.client.nom_complet}"

    def calculer_total(self):
        total = sum([ligne.sous_total() for ligne in self.lignecommande_set.all()])
        self.total = total
        self.save()
        return total


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ligne de Commande"
        verbose_name_plural = "Lignes de Commande"

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"

    def sous_total(self):
        return self.quantite * self.prix_unitaire


class Vente(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ('ESPECES', 'Espèces'),
        ('CARTE', 'Carte bancaire'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement'),
        ('CREDIT', 'Crédit'),
    ]

    numero_vente = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES)
    date_vente = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-date_vente']

    def __str__(self):
        client_info = f" - {self.client.nom_complet}" if self.client else " - Vente comptoir"
        return f"Vente {self.numero_vente}{client_info}"

    def calculer_total(self):
        sous_total = sum([ligne.sous_total() for ligne in self.lignevente_set.all()])
        self.total = sous_total - (sous_total * self.remise / 100)
        self.save()
        return self.total


class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ligne de Vente"
        verbose_name_plural = "Lignes de Vente"

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"

    def sous_total(self):
        return self.quantite * self.prix_unitaire


# ========== NOUVEAUX MODÈLES POUR EXTENSION BIOMÉDICALE ==========

class Devis(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('ENVOYE', 'Envoyé'),
        ('ACCEPTE', 'Accepté'),
        ('REFUSE', 'Refusé'),
        ('EXPIRE', 'Expiré'),
    ]

    numero_devis = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devis')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validite = models.DateField()
    commercial = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devis_commerciaux')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    conditions_particulieres = models.TextField(blank=True)

    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Devis {self.numero_devis} - {self.client.nom_complet}"

    def calculer_total(self):
        total = sum([ligne.sous_total() for ligne in self.lignedevis_set.all()])
        self.total = total
        self.save()
        return total

    def save(self, *args, **kwargs):
        if not self.numero_devis:
            # Générer automatiquement le numéro de devis
            from datetime import datetime
            année = datetime.now().year
            dernier_devis = Devis.objects.filter(numero_devis__startswith=f'DEV{année}').order_by('numero_devis').last()
            if dernier_devis:
                numero = int(dernier_devis.numero_devis[-4:]) + 1
            else:
                numero = 1
            self.numero_devis = f'DEV{année}{numero:04d}'
        super().save(*args, **kwargs)


class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Ligne de Devis"
        verbose_name_plural = "Lignes de Devis"

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"

    def sous_total(self):
        montant_brut = self.quantite * self.prix_unitaire
        return montant_brut - (montant_brut * self.remise / 100)


class Prospect(models.Model):
    STATUT_CHOICES = [
        ('NOUVEAU', 'Nouveau'),
        ('CONTACTE', 'Contacté'),
        ('INTERESSE', 'Intéressé'),
        ('QUALIFIE', 'Qualifié'),
        ('PROPOSE', 'Proposition envoyée'),
        ('NEGOCIE', 'En négociation'),
        ('CONVERTI', 'Converti en client'),
        ('PERDU', 'Perdu'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    entreprise = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=50, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    commercial = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prospects')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_interaction = models.DateTimeField(auto_now=True)
    client_converti = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Prospect"
        verbose_name_plural = "Prospects"
        ordering = ['-date_derniere_interaction']

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.entreprise}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class NoteObservation(models.Model):
    TYPE_CHOICES = [
        ('CLIENT', 'Note Client'),
        ('PROSPECT', 'Note Prospect'),
        ('INTERACTION', 'Interaction'),
        ('RELANCE', 'Relance'),
        ('REUNION', 'Réunion'),
        ('APPEL', 'Appel téléphonique'),
    ]

    type_note = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Relations optionnelles
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    
    # Suivi
    date_rappel = models.DateTimeField(null=True, blank=True)
    terminee = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Note d'Observation"
        verbose_name_plural = "Notes d'Observation"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.get_type_note_display()}"


class AppareilVendu(models.Model):
    STATUT_CHOICES = [
        ('INSTALLE', 'Installé'),
        ('EN_SERVICE', 'En service'),
        ('MAINTENANCE', 'En maintenance'),
        ('PANNE', 'En panne'),
        ('HORS_SERVICE', 'Hors service'),
    ]

    numero_serie = models.CharField(max_length=100, unique=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vente = models.ForeignKey('Vente', on_delete=models.CASCADE, related_name='appareils')
    date_installation = models.DateField()
    lieu_installation = models.CharField(max_length=200)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='INSTALLE')
    
    # Maintenance
    prochaine_maintenance_preventive = models.DateField()
    derniere_maintenance = models.DateField(null=True, blank=True)
    intervalle_maintenance_jours = models.IntegerField(default=365)  # 1 an par défaut
    
    # Notes techniques
    notes_installation = models.TextField(blank=True)
    technicien_responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='appareils_responsable')

    class Meta:
        verbose_name = "Appareil Vendu"
        verbose_name_plural = "Appareils Vendus"
        ordering = ['prochaine_maintenance_preventive']

    def __str__(self):
        return f"{self.produit.nom} ({self.numero_serie}) - {self.client.nom_complet}"

    def est_maintenance_due(self):
        return self.prochaine_maintenance_preventive <= date.today()


class InterventionSAV(models.Model):
    TYPE_CHOICES = [
        ('PREVENTIVE', 'Maintenance préventive'),
        ('CORRECTIVE', 'Maintenance corrective'),
        ('INSTALLATION', 'Installation'),
        ('FORMATION', 'Formation'),
        ('DIAGNOSTIC', 'Diagnostic'),
    ]

    STATUT_CHOICES = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('REPORTEE', 'Reportée'),
        ('ANNULEE', 'Annulée'),
    ]

    numero_intervention = models.CharField(max_length=50, unique=True)
    type_intervention = models.CharField(max_length=20, choices=TYPE_CHOICES)
    appareil = models.ForeignKey(AppareilVendu, on_delete=models.CASCADE, related_name='interventions')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    technicien = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interventions_technicien')
    
    date_prevue = models.DateTimeField()
    date_realisee = models.DateTimeField(null=True, blank=True)
    duree_prevue = models.IntegerField(help_text="Durée en minutes")
    duree_reelle = models.IntegerField(null=True, blank=True, help_text="Durée en minutes")
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PLANIFIEE')
    description = models.TextField()
    travaux_realises = models.TextField(blank=True)
    pieces_changees = models.TextField(blank=True)
    observations = models.TextField(blank=True)
    
    # Satisfaction client
    note_satisfaction = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    commentaire_client = models.TextField(blank=True)

    class Meta:
        verbose_name = "Intervention SAV"
        verbose_name_plural = "Interventions SAV"
        ordering = ['date_prevue']

    def __str__(self):
        return f"{self.numero_intervention} - {self.appareil} - {self.get_type_intervention_display()}"

    def save(self, *args, **kwargs):
        if not self.numero_intervention:
            # Générer automatiquement le numéro d'intervention
            from datetime import datetime
            année = datetime.now().year
            derniere_intervention = InterventionSAV.objects.filter(numero_intervention__startswith=f'INT{année}').order_by('numero_intervention').last()
            if derniere_intervention:
                numero = int(derniere_intervention.numero_intervention[-4:]) + 1
            else:
                numero = 1
            self.numero_intervention = f'INT{année}{numero:04d}'
        
        # Assigner automatiquement le client depuis l'appareil si pas déjà défini
        if self.appareil and not self.client:
            self.client = self.appareil.client
            
        super().save(*args, **kwargs)


class TransfertStock(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EXPEDIE', 'Expédié'),
        ('RECU', 'Reçu'),
        ('ANNULE', 'Annulé'),
    ]

    numero_transfert = models.CharField(max_length=50, unique=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    origine = models.CharField(max_length=100, default='Dépôt')
    destination = models.CharField(max_length=100, default='Showroom')
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expedition = models.DateTimeField(null=True, blank=True)
    date_reception = models.DateTimeField(null=True, blank=True)
    
    demandeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transferts_demandes')
    expediteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferts_expedies')
    recepteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferts_recus')
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Transfert de Stock"
        verbose_name_plural = "Transferts de Stock"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Transfert {self.numero_transfert} - {self.produit.nom} x{self.quantite}"

    def save(self, *args, **kwargs):
        if not self.numero_transfert:
            # Générer automatiquement le numéro de transfert
            from datetime import datetime
            année = datetime.now().year
            dernier_transfert = TransfertStock.objects.filter(numero_transfert__startswith=f'TRA{année}').order_by('numero_transfert').last()
            if dernier_transfert:
                numero = int(dernier_transfert.numero_transfert[-4:]) + 1
            else:
                numero = 1
            self.numero_transfert = f'TRA{année}{numero:04d}'
        super().save(*args, **kwargs)


class ProspectionTelephonique(models.Model):
    """Modèle pour la gestion de la prospection téléphonique"""
    TYPE_APPEL_CHOICES = [
        ('SORTANT', 'Appel sortant'),
        ('ENTRANT', 'Appel entrant'),
    ]
    
    STATUT_CHOICES = [
        ('RDV', 'RDV'),
        ('BV', 'BV'),
        ('CLIENT_ACQUIS', 'Client acquis'),
        ('A_RELANCER', 'À relancer'),
    ]
    
    SOURCE_PROSPECT_CHOICES = [
        ('CONTACT_EMAIL', 'Contact email'),
        ('APPEL_DIRECT', 'Appel direct'),
        ('SITE_WEB', 'Site web'),
        ('RESEAUX_SOCIAUX', 'Réseaux sociaux'),
        ('FLYER', 'Flyer'),
        ('VISIOCONFERENCE', 'Visioconférence'),
        ('BOUCHE_OREILLE', 'Bouche à oreille'),
    ]
    
    # Champs communs
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    numero_telephone = models.CharField(max_length=20, verbose_name="Numéro téléphonique")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='A_RELANCER', verbose_name="Statut")
    date_rdv = models.DateField(blank=True, null=True, verbose_name="Date de RDV")
    description = models.TextField(verbose_name="Description")
    type_appel = models.CharField(max_length=20, choices=TYPE_APPEL_CHOICES, verbose_name="Type d'appel")
    
    # Champ spécifique appel sortant
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Champ spécifique appel entrant
    source_prospect = models.CharField(
        max_length=50, 
        choices=SOURCE_PROSPECT_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Source de prospect"
    )
    
    # Métadonnées
    commercial = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Commercial")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Prospection Téléphonique"
        verbose_name_plural = "Prospections Téléphoniques"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom_complet} - {self.get_statut_display()} ({self.get_type_appel_display()})"
    
    def get_couleur_statut(self):
        """Retourne la couleur CSS selon le statut"""
        couleurs = {
            'RDV': 'bg-yellow-100 text-yellow-800 border-yellow-300',
            'BV': 'bg-red-100 text-red-800 border-red-300',
            'CLIENT_ACQUIS': 'bg-green-100 text-green-800 border-green-300',
            'A_RELANCER': 'bg-gray-100 text-gray-800 border-gray-300',
        }
        return couleurs.get(self.statut, 'bg-gray-100 text-gray-800 border-gray-300')
    
    def get_badge_statut(self):
        """Retourne le badge HTML complet pour le statut"""
        couleur = self.get_couleur_statut()
        return f'<span class="px-2 py-1 rounded-full text-xs font-semibold {couleur}">{self.get_statut_display()}</span>'
