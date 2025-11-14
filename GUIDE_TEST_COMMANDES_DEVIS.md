# 🧪 GUIDE DE TEST : Commandes & Devis

**Date** : 13 novembre 2025  
**Objectif** : Vérifier que les produits s'enregistrent correctement dans les commandes et devis

---

## ✅ CORRECTIONS APPLIQUÉES

### 1. **COMMANDES** (`inventory/views.py`)
- ✅ Ajout de `from django.db import transaction`
- ✅ Décorateur `@transaction.atomic` sur `commande_create_advanced()`
- ✅ Parsing manuel robuste avec dictionnaire `lines_data`
- ✅ Validation : quantité > 0, prix >= 0
- ✅ Warning si stock insuffisant (mais autorise quand même)
- ✅ Vérifie au moins 1 ligne de produit

### 2. **DEVIS** (`inventory/extended_views.py`)
- ✅ Ajout de `from django.db import transaction`
- ✅ Décorateur `@transaction.atomic` sur `devis_create()`
- ✅ **Remplacement du FormSet par parsing manuel** (même logique que commandes)
- ✅ Validation : quantité > 0, prix >= 0, remise 0-100%
- ✅ Vérifie au moins 1 ligne de produit
- ✅ Ajout de `produits` dans le contexte du template

### 3. **CACHE**
- ✅ Nettoyage de tous les fichiers `.pyc`
- ✅ Suppression des dossiers `__pycache__`
- ✅ Redémarrage propre du serveur (PID: 12399)

---

## 🧪 TEST 1 : Création de Commande

### Étapes
1. **Ouvrir** : http://127.0.0.1:8000/inventory/commandes/nouvelle/
2. **Remplir le formulaire** :
   - Fournisseur : Choisir un fournisseur
   - Adresse de livraison : Remplir une adresse
3. **Ajouter 2 produits** (clic sur "Ajouter un produit") :
   - Ligne 1 : Produit A, Quantité 2, Prix auto-rempli
   - Ligne 2 : Produit B, Quantité 1, Prix auto-rempli
4. **Vérifier le total** en bas (doit se mettre à jour automatiquement)
5. **Soumettre** : Clic sur "Confirmer la commande"

### Résultats attendus ✅
- ✅ Message de succès : "Commande CMD-XXXX créée et confirmée avec succès!"
- ✅ Redirection vers la page de détail de la commande
- ✅ **2 lignes de produits visibles** dans le tableau
- ✅ Quantités et prix corrects
- ✅ Total calculé = (Qté1 × Prix1) + (Qté2 × Prix2)

### Logs attendus (dans `django_server.log`)
```
=== DEBUG COMMANDE_CREATE ===
Lignes trouvées: ['0', '1']
Traitement ligne 0: produit=15, quantite=2, prix=5000.0
✓ Ligne 0 créée: LigneCommande object (1)
Traitement ligne 1: produit=18, quantite=1, prix=3000.0
✓ Ligne 1 créée: LigneCommande object (2)
✓ Total de lignes créées: 2
```

### Si ça ne marche pas ❌
- Vérifier les logs : `tail -f django_server.log`
- Si vous voyez "Recherche des clés:" → Relancer `./restart_clean.sh`
- Vérifier qu'il n'y a pas d'erreurs JavaScript (F12 dans le navigateur)

---

## 🧪 TEST 2 : Création de Devis

### Étapes
1. **Ouvrir** : http://127.0.0.1:8000/inventory/devis/nouveau/
2. **Remplir le formulaire** :
   - Client : Choisir un client
   - Date de validité : Sélectionner une date (par défaut : +30 jours)
   - Notes (optionnel)
3. **Ajouter 3 produits** (clic sur "Ajouter un produit") :
   - Ligne 1 : Produit A, Quantité 1, Remise 0%
   - Ligne 2 : Produit B, Quantité 2, Remise 10%
   - Ligne 3 : Produit C, Quantité 1, Remise 5%
4. **Vérifier le total** (doit inclure les remises et la TVA 18%)
5. **Soumettre** : Clic sur "Enregistrer le devis"

### Résultats attendus ✅
- ✅ Message de succès : "Devis DEV-XXXX créé avec succès (3 ligne(s))."
- ✅ Redirection vers la page de détail du devis
- ✅ **3 lignes de produits visibles** dans le tableau
- ✅ Quantités, prix et remises corrects
- ✅ Total calculé avec remises appliquées et TVA

### Logs attendus (dans `django_server.log`)
```
=== DEBUG DEVIS_CREATE ===
Lignes trouvées: ['0', '1', '2']
Traitement ligne 0: produit=15, qte=1, prix=5000.0, remise=0
✓ Ligne 0 créée: LigneDevis object (1)
Traitement ligne 1: produit=18, qte=2, prix=3000.0, remise=10.0
✓ Ligne 1 créée: LigneDevis object (2)
Traitement ligne 2: produit=22, qte=1, prix=2500.0, remise=5.0
✓ Ligne 2 créée: LigneDevis object (3)
✓ Total de lignes créées: 3
```

### Si ça ne marche pas ❌
- Vérifier les logs : `tail -f django_server.log`
- Vérifier que `produits` est bien passé au template (F12 → Console)
- Vérifier qu'il y a des produits actifs dans la base de données

---

## 🧪 TEST 3 : Validation des erreurs

### Test 3.1 : Commande sans produit
1. Créer une commande
2. Ne pas ajouter de produit
3. Soumettre
4. **Attendu** : ❌ Message d'erreur "Une commande doit contenir au moins un produit"

### Test 3.2 : Quantité invalide
1. Créer une commande
2. Ajouter un produit avec quantité = 0
3. Soumettre
4. **Attendu** : ❌ Message d'erreur "La quantité doit être positive"

### Test 3.3 : Remise invalide (devis)
1. Créer un devis
2. Ajouter un produit avec remise = 150%
3. Soumettre
4. **Attendu** : ❌ Message d'erreur "La remise doit être entre 0 et 100%"

---

## 🧪 TEST 4 : Vérification en base de données

### Via Django Admin
1. Aller sur : http://127.0.0.1:8000/admin/
2. Se connecter
3. **Inventory → Ligne Commandes** : Vérifier les lignes créées
4. **Inventory → Ligne Devis** : Vérifier les lignes créées

### Via le shell Django
```bash
cd /Users/flozed/Desktop/ZPRO/mystock/stock/ggstock
.venv/bin/python manage.py shell
```

```python
from inventory.models import Commande, LigneCommande, Devis, LigneDevis

# Dernière commande
commande = Commande.objects.last()
print(f"Commande: {commande.numero_commande}")
print(f"Lignes: {commande.lignecommande_set.count()}")
for ligne in commande.lignecommande_set.all():
    print(f"  - {ligne.produit.nom}: {ligne.quantite} × {ligne.prix_unitaire} F CFA")

# Dernier devis
devis = Devis.objects.last()
print(f"\nDevis: {devis.numero_devis}")
print(f"Lignes: {devis.lignedevis_set.count()}")
for ligne in devis.lignedevis_set.all():
    print(f"  - {ligne.produit.nom}: {ligne.quantite} × {ligne.prix_unitaire} F CFA (remise: {ligne.remise}%)")
```

**Résultat attendu** : Le nombre de lignes doit correspondre au nombre de produits ajoutés

---

## 📋 CHECKLIST DE VALIDATION

### Commandes
- [ ] Formulaire s'affiche correctement
- [ ] Bouton "Ajouter un produit" fonctionne
- [ ] Produits apparaissent dans la liste déroulante
- [ ] Prix se remplit automatiquement à la sélection
- [ ] Total se met à jour en temps réel
- [ ] Message de succès après soumission
- [ ] Lignes visibles dans le détail de la commande
- [ ] Logs montrent "Lignes trouvées" (pas "Recherche des clés")

### Devis
- [ ] Formulaire s'affiche correctement
- [ ] Bouton "Ajouter un produit" fonctionne
- [ ] Produits apparaissent dans la liste déroulante
- [ ] Prix se remplit automatiquement à la sélection
- [ ] Remise peut être saisie (0-100%)
- [ ] Total TTC inclut TVA 18%
- [ ] Message de succès après soumission
- [ ] Lignes visibles dans le détail du devis
- [ ] Logs montrent "DEBUG DEVIS_CREATE"

---

## 🚨 PROBLÈMES CONNUS & SOLUTIONS

### Problème 1 : "Ancien code" dans les logs
**Symptôme** : Logs montrent "Recherche des clés: ligne_0_produit"  
**Cause** : Cache Python (.pyc) pas nettoyé  
**Solution** :
```bash
./restart_clean.sh
```

### Problème 2 : Produits ne s'affichent pas dans la liste
**Symptôme** : Liste déroulante vide  
**Cause** : Pas de produits actifs en BDD  
**Solution** :
```bash
.venv/bin/python manage.py shell
```
```python
from inventory.models import Produit
print(Produit.objects.filter(actif=True).count())  # Doit être > 0
```

### Problème 3 : Erreur "produits not found in context"
**Symptôme** : Template crash avec KeyError  
**Cause** : Variable `produits` manquante dans le contexte  
**Solution** : Vérifier que les vues passent bien `'produits': Produit.objects.filter(actif=True)`

### Problème 4 : Total ne se calcule pas
**Symptôme** : JavaScript ne met pas à jour le total  
**Cause** : Erreur JavaScript (F12 → Console)  
**Solution** : Vérifier les logs navigateur, recharger la page (Ctrl+Shift+R)

---

## 📊 STATISTIQUES ATTENDUES

Après les tests, vous devriez avoir :
- ✅ 1+ commande(s) avec 2+ lignes chacune
- ✅ 1+ devis avec 3+ lignes chacun
- ✅ 0 erreur dans `django_server.log`
- ✅ 0 erreur JavaScript (F12)
- ✅ Messages de succès visibles dans l'interface

---

## 🎯 COMMANDES UTILES

### Surveiller les logs en temps réel
```bash
tail -f django_server.log
```

### Redémarrer le serveur proprement
```bash
./restart_clean.sh
```

### Compter les lignes en BDD
```bash
.venv/bin/python manage.py shell -c "
from inventory.models import LigneCommande, LigneDevis
print(f'Lignes Commande: {LigneCommande.objects.count()}')
print(f'Lignes Devis: {LigneDevis.objects.count()}')
"
```

### Arrêter le serveur
```bash
kill 12399  # Remplacer par le PID actuel
```

---

**Bonne chance avec les tests !** 🚀

Si les produits s'enregistrent correctement, le problème est résolu. Sinon, consultez les logs et ce guide.
