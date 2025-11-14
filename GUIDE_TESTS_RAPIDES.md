# 🧪 GUIDE DE TEST RAPIDE - CORRECTIONS APPLIQUÉES

**Date:** 12 novembre 2025  
**Durée estimée:** 15-20 minutes  
**Objectif:** Valider les 5 corrections critiques

---

## 🎯 PRÉREQUIS

- [ ] Serveur Django en cours d'exécution (`python manage.py runserver`)
- [ ] Base de données avec au moins:
  - 3 produits avec stock > 0
  - 2 clients actifs
  - 1 utilisateur connecté avec permissions

---

## ✅ TEST 1: JavaScript Non Dupliqué (2 min)

### Objectif
Vérifier que le JavaScript ne s'exécute qu'une fois

### Étapes
1. Ouvrir la console du navigateur (F12)
2. Aller sur `/inventory/commandes/create/advanced/`
3. Cliquer sur "Ajouter un produit"
4. Vérifier dans la console qu'il n'y a pas d'erreurs JavaScript

### ✅ Résultat attendu
- Une ligne de produit est ajoutée
- Pas d'erreurs dans la console
- Pas de messages dupliqués

### ❌ En cas d'échec
- Vérifier que le second bloc JavaScript a bien été supprimé dans `commande_create_advanced.html`

---

## ✅ TEST 2: Transaction Atomique - Rollback (3 min)

### Objectif
Vérifier qu'une erreur ne laisse pas de données orphelines

### Étapes - Vente
1. Aller sur `/inventory/ventes/create/`
2. Ajouter 2 produits:
   - Produit 1: quantité = 1, prix = 100
   - Produit 2: quantité = **-5** (négatif), prix = 50
3. Soumettre le formulaire

### ✅ Résultat attendu
- Message d'erreur affiché: "La quantité doit être positive"
- **AUCUNE vente créée en base** (vérifier dans Django Admin)
- **Stock des produits inchangé**

### Vérification en base
```bash
# Dans le terminal Django
python manage.py shell
>>> from inventory.models import Vente
>>> Vente.objects.count()  # Noter le nombre
# Après le test, le nombre doit être identique
```

### ❌ En cas d'échec
- Si une vente partielle existe → Le `@transaction.atomic` n'est pas appliqué
- Vérifier que le décorateur est bien présent dans `views.py`

---

## ✅ TEST 3: Parsing de Toutes les Lignes (4 min)

### Objectif
Vérifier que toutes les lignes sont traitées même si on en supprime au milieu

### Étapes - Commande
1. Aller sur `/inventory/commandes/create/advanced/`
2. Ajouter 5 lignes de produits:
   - Ligne 1: Produit A, qté 1
   - Ligne 2: Produit B, qté 2
   - Ligne 3: Produit C, qté 3
   - Ligne 4: Produit D, qté 4
   - Ligne 5: Produit E, qté 5
3. **SUPPRIMER les lignes 2 et 4** (cliquer sur l'icône poubelle)
4. Remplir les infos de commande (client, date livraison, adresse)
5. Soumettre

### ✅ Résultat attendu
- Commande créée avec **3 lignes** (1, 3, 5)
- Message de succès affiché
- Dans le détail de la commande:
  - Produit A: quantité 1 ✓
  - Produit C: quantité 3 ✓
  - Produit E: quantité 5 ✓

### Vérification
1. Cliquer sur la commande créée
2. Compter le nombre de lignes affichées
3. Vérifier que les quantités correspondent

### ❌ En cas d'échec
- Si seulement la ligne 1 est créée → Ancienne logique encore active
- Vérifier que le nouveau code de parsing est bien présent

---

## ✅ TEST 4: Vérification de Stock - Commande (3 min)

### Objectif
Vérifier qu'un warning est affiché si stock insuffisant (mais commande créée)

### Préparation
1. Trouver un produit avec stock faible (ex: stock = 5)

### Étapes
1. Aller sur `/inventory/commandes/create/advanced/`
2. Ajouter ce produit avec quantité = **20** (> stock de 5)
3. Soumettre

### ✅ Résultat attendu
- **Warning affiché** (bannière orange): 
  ```
  ⚠️ Stock insuffisant pour [Nom Produit]: 
  Stock disponible=5, Commandé=20. 
  La commande sera créée, mais vérifiez le stock avant livraison.
  ```
- **Commande CRÉÉE quand même** (c'est normal)
- Ligne de commande avec quantité = 20

### ❌ En cas d'échec
- Si erreur au lieu de warning → Code de commande utilise le mauvais type de message
- Si pas de message → Vérification de stock non ajoutée

---

## ✅ TEST 5: Vérification de Stock - Vente (3 min)

### Objectif
Vérifier qu'une erreur bloque la vente si stock insuffisant

### Préparation
1. Utiliser le même produit (stock = 5)

### Étapes
1. Aller sur `/inventory/ventes/create/`
2. Ajouter ce produit avec quantité = **20** (> stock de 5)
3. Soumettre

### ✅ Résultat attendu
- **Erreur affichée** (bannière rouge):
  ```
  Stock insuffisant pour [Nom Produit]. 
  Stock disponible: 5, Demandé: 20
  ```
- **Vente NON créée**
- Stock du produit **inchangé** = 5

### Vérification du stock
1. Aller dans la liste des produits
2. Vérifier que le stock est toujours 5

### ❌ En cas d'échec
- Si vente créée → Vérification de stock non fonctionnelle
- Si stock négatif → select_for_update() non appliqué

---

## ✅ TEST 6: Validation Minimum 1 Ligne (2 min)

### Objectif
Vérifier qu'on ne peut pas créer de vente/commande vide

### Étapes - Vente
1. Aller sur `/inventory/ventes/create/`
2. La première ligne s'ajoute automatiquement
3. **Supprimer cette ligne** (cliquer sur poubelle)
4. Soumettre directement

### ✅ Résultat attendu
- **Erreur affichée**: "Une vente doit contenir au moins un produit"
- **Aucune vente créée**

### Étapes - Commande
1. Aller sur `/inventory/commandes/create/advanced/`
2. La première ligne s'ajoute automatiquement
3. **Supprimer cette ligne**
4. Soumettre

### ✅ Résultat attendu
- **Erreur affichée**: "Une commande doit contenir au moins un produit"
- **Aucune commande créée**

### ❌ En cas d'échec
- Si vente/commande créée avec total = 0 → Validation non appliquée

---

## ✅ TEST 7: Validation des Valeurs Négatives (2 min)

### Objectif
Vérifier que prix et quantités négatifs sont rejetés

### Test 7a: Quantité négative
1. Créer une vente avec quantité = **-5**
2. **Résultat attendu:** Erreur "La quantité doit être positive"

### Test 7b: Prix négatif
1. Créer une vente avec prix unitaire = **-100**
2. **Résultat attendu:** Erreur "Le prix ne peut pas être négatif"

### ❌ En cas d'échec
- Vérifier que les validations sont bien présentes dans le code

---

## 📊 RÉCAPITULATIF DES TESTS

| # | Test | Durée | Statut |
|---|------|-------|--------|
| 1 | JavaScript non dupliqué | 2 min | ⬜ |
| 2 | Transaction atomique | 3 min | ⬜ |
| 3 | Parsing de toutes les lignes | 4 min | ⬜ |
| 4 | Stock commande (warning) | 3 min | ⬜ |
| 5 | Stock vente (erreur) | 3 min | ⬜ |
| 6 | Minimum 1 ligne | 2 min | ⬜ |
| 7 | Valeurs négatives | 2 min | ⬜ |
| **TOTAL** | | **19 min** | **0/7** |

---

## 🐛 DEBUGGING

### Si un test échoue

1. **Vérifier les logs console:**
   ```bash
   # Dans le terminal où tourne le serveur Django
   # Chercher les messages DEBUG
   === DEBUG VENTE_CREATE ===
   Lignes trouvées: ['0', '1', '2']
   ```

2. **Vérifier la base de données:**
   ```bash
   python manage.py shell
   >>> from inventory.models import Vente, LigneVente
   >>> vente = Vente.objects.last()
   >>> vente.lignevente_set.count()  # Nombre de lignes
   ```

3. **Vérifier les messages Django:**
   - Regarder en haut de la page après soumission
   - Types de messages:
     - 🔴 Rouge = Error
     - 🟠 Orange = Warning
     - 🟢 Vert = Success

4. **Console JavaScript (F12):**
   - Onglet "Console" pour les erreurs JS
   - Onglet "Network" pour les requêtes POST

---

## ✅ VALIDATION FINALE

Une fois tous les tests passés:

- [ ] 7/7 tests réussis
- [ ] Aucune erreur JavaScript
- [ ] Aucune donnée orpheline en base
- [ ] Messages d'erreur clairs et informatifs
- [ ] Comportement cohérent vente vs commande

### Actions post-validation

1. **Documenter les tests:**
   ```bash
   # Créer un fichier de résultats
   echo "Tests effectués le $(date)" > test_results.txt
   echo "Tous les tests passés ✅" >> test_results.txt
   ```

2. **Informer l'équipe:**
   - Les corrections sont validées
   - Le système est prêt pour la production

3. **Planifier les tests avancés:**
   - Tests de charge
   - Tests de sécurité
   - Tests automatisés

---

## 📞 SUPPORT

En cas de problème:

1. Consulter les fichiers d'analyse:
   - `ANALYSE_VENTE_FORM.md`
   - `ANALYSE_COMMANDE_FORM.md`
   - `CORRECTIONS_APPLIQUEES.md`

2. Vérifier les modifications dans Git:
   ```bash
   git diff inventory/views.py
   git diff templates/inventory/commande_create_advanced.html
   ```

3. Revenir en arrière si nécessaire:
   ```bash
   git checkout -- inventory/views.py
   git checkout -- templates/inventory/commande_create_advanced.html
   ```

---

**Bon tests ! 🚀**
