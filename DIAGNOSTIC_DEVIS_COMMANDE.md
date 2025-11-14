# 🔍 DIAGNOSTIC : Produits ne s'enregistrent pas (Commandes & Devis)

**Date**: 13 novembre 2025
**Problème**: Les produits ne s'affichent pas car ils ne s'enregistrent pas dans la base de données

---

## 🎯 RÉSUMÉ DU PROBLÈME

### **COMMANDES** : ✅ Code corrigé mais serveur en cache
- ✅ Template `commande_create_advanced.html` génère correctement : `ligne_0_produit`, `ligne_0_quantite`, etc.
- ✅ Vue `commande_create_advanced()` parse correctement ces champs avec dictionnaire
- ❌ **Serveur Django utilise l'ancien code en cache** (bytecode .pyc)
- 🔧 **Solution** : Nettoyer cache avec `restart_clean.sh` ✅ FAIT

### **DEVIS** : ❌ Incompatibilité Template ↔ Vue
- ❌ Template `devis_form.html` génère : `ligne_0_produit`, `ligne_0_quantite`
- ❌ Vue `devis_create()` utilise **Django FormSet** qui attend : `form-0-produit`, `form-TOTAL_FORMS`
- ❌ **Les données POST ne sont jamais traitées !**
- 🔧 **Solution** : Remplacer FormSet par parsing manuel (comme commandes)

---

## 📋 ANALYSE DÉTAILLÉE

### 1. **COMMANDE** - État actuel

#### Template `commande_create_advanced.html`
```javascript
// Ligne 251 : Nommage des champs
input.name = `ligne_${lineCount}_${name}`;

// Génère :
// ligne_0_produit = 15
// ligne_0_quantite = 2
// ligne_0_prix_unitaire = 5000
```

#### Vue `commande_create_advanced()` (inventory/views.py ligne 2726)
```python
# Parser toutes les clés POST
lines_data = {}
for key in request.POST:
    if key.startswith('ligne_') and '_' in key:
        parts = key.split('_', 2)  # ligne_0_produit → ['ligne', '0', 'produit']
        if len(parts) == 3:
            line_idx = parts[1]
            field_name = parts[2]
            lines_data[line_idx][field_name] = request.POST[key]

# Résultat :
# lines_data = {
#     '0': {'produit': '15', 'quantite': '2', 'prix_unitaire': '5000'},
#     '1': {'produit': '18', 'quantite': '1', 'prix_unitaire': '3000'}
# }
```

✅ **COMPATIBLE** : Template et Vue utilisent le même format !

---

### 2. **DEVIS** - Incompatibilité

#### Template `devis_form.html`
```javascript
// Ligne 246 : Nommage des champs
input.name = `ligne_${lineCount}_${originalName}`;

// Génère :
// ligne_0_produit = 15
// ligne_0_quantite = 2
// ligne_0_prix_unitaire = 5000
// ligne_0_remise = 10
```

#### Vue `devis_create()` (inventory/extended_views.py ligne 94)
```python
# PROBLÈME : Utilise FormSet qui attend un format différent !
formset = LigneDevisFormSet(request.POST)

# FormSet attend :
# form-TOTAL_FORMS = 2
# form-INITIAL_FORMS = 0
# form-0-produit = 15
# form-0-quantite = 2
# form-1-produit = 18
# ...

# Mais reçoit :
# ligne_0_produit = 15
# ligne_0_quantite = 2
# ligne_1_produit = 18
# ...

# ❌ formset.is_valid() → False (données non reconnues)
# ❌ Aucune ligne LigneDevis n'est créée !
```

❌ **INCOMPATIBLE** : Template envoie `ligne_X_champ` mais FormSet attend `form-X-champ` !

---

## 🔧 SOLUTIONS

### Solution 1 : **Adapter le template au FormSet** (❌ Non recommandé)
- Réécrire tout le JavaScript de `devis_form.html`
- Ajouter les champs cachés `form-TOTAL_FORMS`, `form-INITIAL_FORMS`
- Changer tous les noms : `ligne_X` → `form-X`
- ⚠️ Complexe et fragile

### Solution 2 : **Adapter la vue au template** (✅ Recommandé)
- Remplacer FormSet par parsing manuel (comme `commande_create_advanced`)
- Copier la logique robuste qui fonctionne
- Ajouter `@transaction.atomic` pour sécurité
- ✅ Simple, cohérent, testé

---

## 📝 CODE À APPLIQUER

### Nouvelle vue `devis_create()` (extended_views.py)

```python
from django.db import transaction

@login_required
@role_required(['COMMERCIAL_TERRAIN', 'MANAGER'])
@transaction.atomic
def devis_create(request):
    """Créer un nouveau devis avec parsing manuel des lignes"""
    if request.method == 'POST':
        form = DevisForm(request.POST)
        
        if form.is_valid():
            devis = form.save(commit=False)
            devis.commercial = request.user
            devis.save()
            
            # ✅ PARSING MANUEL (comme commande_create_advanced)
            lines_created = 0
            lines_data = {}
            
            # Parser toutes les clés POST
            for key in request.POST:
                if key.startswith('ligne_') and '_' in key:
                    parts = key.split('_', 2)
                    if len(parts) == 3:
                        line_idx = parts[1]
                        field_name = parts[2]
                        
                        if line_idx not in lines_data:
                            lines_data[line_idx] = {}
                        lines_data[line_idx][field_name] = request.POST[key]
            
            print(f"=== DEBUG DEVIS_CREATE ===")
            print(f"Lignes trouvées: {sorted(lines_data.keys())}")
            
            # Traiter chaque ligne
            for line_idx in sorted(lines_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                data = lines_data[line_idx]
                produit_id = data.get('produit')
                quantite = data.get('quantite')
                prix_unitaire = data.get('prix_unitaire')
                remise = data.get('remise', 0)  # Remise optionnelle
                
                print(f"Traitement ligne {line_idx}: produit={produit_id}, qte={quantite}, prix={prix_unitaire}, remise={remise}")
                
                # Ignorer lignes vides
                if not produit_id:
                    print(f"Ligne {line_idx} ignorée (pas de produit)")
                    continue
                
                # Vérifier champs requis
                if not (quantite and prix_unitaire):
                    messages.error(request, f'Ligne {int(line_idx) + 1}: Quantité et prix requis')
                    raise ValueError(f'Données incomplètes pour la ligne {line_idx}')
                
                try:
                    produit = Produit.objects.get(id=produit_id)
                    quantite = int(quantite)
                    prix_unitaire = float(prix_unitaire)
                    remise = float(remise) if remise else 0
                    
                    # Validations
                    if quantite <= 0:
                        messages.error(request, f'{produit.nom}: La quantité doit être positive')
                        raise ValueError('Quantité invalide')
                    
                    if prix_unitaire < 0:
                        messages.error(request, f'{produit.nom}: Le prix ne peut pas être négatif')
                        raise ValueError('Prix invalide')
                    
                    if remise < 0 or remise > 100:
                        messages.error(request, f'{produit.nom}: La remise doit être entre 0 et 100%')
                        raise ValueError('Remise invalide')
                    
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
                    raise
                except (ValueError, TypeError) as e:
                    messages.error(request, f'Ligne {int(line_idx) + 1}: {str(e)}')
                    raise
            
            print(f"✓ Total de lignes créées: {lines_created}")
            
            # Vérifier au moins une ligne
            if lines_created == 0:
                messages.error(request, 'Un devis doit contenir au moins un produit')
                raise ValueError('Aucune ligne de produit')
            
            # Calculer le total
            devis.calculer_total()
            
            messages.success(request, f"Devis {devis.numero_devis} créé avec succès ({lines_created} ligne(s)).")
            return redirect('inventory:devis_detail', pk=devis.pk)
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
```

---

## ✅ AVANTAGES DE CETTE SOLUTION

1. **Cohérence** : Même logique pour Commandes et Devis
2. **Robustesse** : Gère les lignes supprimées, indices non consécutifs
3. **Transactions** : `@transaction.atomic` garantit l'intégrité
4. **Validation** : Vérifie quantité, prix, remise
5. **Debug** : Logs clairs pour diagnostiquer
6. **Simplicité** : Pas besoin de FormSet complexe

---

## 🧪 TESTS À EFFECTUER

### Test Devis
1. Aller sur : http://127.0.0.1:8000/inventory/devis/nouveau/
2. Remplir client, date validité
3. Ajouter 2-3 produits avec quantités et remises
4. Soumettre
5. **Résultat attendu** :
   - ✅ Devis créé avec numéro
   - ✅ Lignes visibles dans le détail
   - ✅ Total calculé correctement

### Test Commande
1. Aller sur : http://127.0.0.1:8000/inventory/commandes/nouvelle/
2. Remplir fournisseur, adresse
3. Ajouter 2-3 produits avec quantités
4. Soumettre
5. **Résultat attendu** :
   - ✅ Commande créée avec numéro
   - ✅ Lignes visibles dans le détail
   - ✅ Total calculé correctement

---

## 📊 ÉTAT ACTUEL

- ✅ **Commandes** : Code corrigé, serveur redémarré proprement
- ❌ **Devis** : Vue incompatible avec template (à corriger)
- ✅ **Cache** : Nettoyé avec `restart_clean.sh`
- ✅ **Serveur** : Redémarré proprement (PID: 11918)

---

## 🚀 PROCHAINES ÉTAPES

1. ✅ Appliquer la correction à `devis_create()` dans `extended_views.py`
2. ✅ Redémarrer le serveur Django
3. ✅ Tester création de devis
4. ✅ Tester création de commande
5. ✅ Vérifier que les lignes s'enregistrent dans la BDD

---

**Correction générée le** : 13 novembre 2025  
**Auteur** : GitHub Copilot  
**Statut** : Prêt à appliquer
