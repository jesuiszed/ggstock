# 🔍 DIAGNOSTIC - PRODUITS NE S'ENREGISTRENT PAS

**Date:** 13 novembre 2025  
**Problème:** Les produits ne s'enregistrent pas dans la base de données lors de la création de ventes

---

## 🚨 PROBLÈME IDENTIFIÉ

### Erreur dans les logs :
```
Form errors: Un objet Vente avec ce champ Numero vente existe déjà.
```

### Cause racine :
Le serveur Django utilisait **une version en cache** de l'ancien code au lieu du nouveau code corrigé.

---

## ✅ SOLUTION APPLIQUÉE

1. **Arrêt forcé du serveur Django**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **Redémarrage du serveur**
   ```bash
   .venv/bin/python manage.py runserver
   ```

3. **Vérification**
   - Serveur redémarré à 00:13:58
   - Code mis à jour chargé
   - Prêt pour les tests

---

## 🧪 TESTS À EFFECTUER MAINTENANT

### Test 1: Créer une nouvelle vente

1. Aller sur http://127.0.0.1:8000/inventory/ventes/nouvelle/
2. Remplir le formulaire:
   - Client: (sélectionner un client)
   - Mode de paiement: Espèces
   - Produit: (sélectionner un produit)
   - Quantité: 1
3. Cliquer sur "Créer la vente"

### ✅ Résultat attendu MAINTENANT :

Dans les logs du serveur, vous devriez voir:
```
=== DEBUG VENTE_CREATE ===
Lignes trouvées: ['0']
Traitement ligne 0: produit=XX, quantite=1, prix=XXXX
✓ Ligne 0 créée: [Nom Produit] x 1
✓ Total de lignes créées: 1
```

**PLUS de message "Recherche des clés" (ancien code)**

---

## 📊 VÉRIFICATION EN BASE DE DONNÉES

### Méthode 1: Django Shell
```bash
.venv/bin/python manage.py shell
```

```python
from inventory.models import Vente, LigneVente

# Voir la dernière vente
vente = Vente.objects.last()
print(f"Vente: {vente.numero_vente}")
print(f"Lignes: {vente.lignevente_set.count()}")

# Voir les lignes
for ligne in vente.lignevente_set.all():
    print(f"  - {ligne.produit.nom} x {ligne.quantite}")
```

### Méthode 2: Django Admin
1. Aller sur http://127.0.0.1:8000/admin/
2. Cliquer sur "Ventes"
3. Vérifier la dernière vente créée
4. Cliquer dessus et vérifier les "Ligne vente"

---

## 🐛 SI LE PROBLÈME PERSISTE

### Vérifier que le nouveau code est chargé

Dans le terminal du serveur Django, après avoir créé une vente, cherchez:

**✅ NOUVEAU CODE (bon):**
```
=== DEBUG VENTE_CREATE ===
Lignes trouvées: ['0']
Traitement ligne 0: ...
```

**❌ ANCIEN CODE (mauvais):**
```
Recherche des clés: ligne_0_produit, ...
Ligne 0: produit_id=...
```

Si vous voyez l'ANCIEN CODE:

1. **Vider le cache Python:**
   ```bash
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -name "*.pyc" -delete
   ```

2. **Redémarrer le serveur:**
   ```bash
   # Arrêter (Ctrl+C dans le terminal du serveur)
   # Ou forcer:
   lsof -ti:8000 | xargs kill -9
   
   # Relancer:
   .venv/bin/python manage.py runserver
   ```

---

## 🔧 AUTRES PROBLÈMES POSSIBLES

### Problème 1: "Numero vente existe déjà"

**Cause:** Le formulaire est soumis plusieurs fois ou le numéro est déjà utilisé

**Solution:**
1. Aller sur la liste des ventes
2. Supprimer les ventes incomplètes (sans lignes)
3. Créer une nouvelle vente (nouveau numéro sera généré)

### Problème 2: Stock insuffisant

**Cause:** Le produit n'a plus de stock

**Solution:**
1. Vérifier le stock du produit dans la liste des produits
2. Augmenter le stock si nécessaire
3. Ou choisir un autre produit avec stock > 0

### Problème 3: Formulaire invalide

**Cause:** Données manquantes ou invalides

**Solution:**
Vérifier dans les logs:
```
Form errors: ...
```

Et corriger les champs indiqués

---

## 📝 COMMANDES UTILES

### Voir les logs en temps réel
```bash
# Le serveur affiche déjà les logs
# Mais vous pouvez aussi filtrer:
tail -f /dev/stdout | grep "DEBUG VENTE"
```

### Compter les ventes
```bash
.venv/bin/python manage.py shell -c "from inventory.models import Vente; print(f'Total ventes: {Vente.objects.count()}')"
```

### Supprimer les ventes de test
```bash
.venv/bin/python manage.py shell
```
```python
from inventory.models import Vente

# Supprimer les ventes sans lignes
ventes_vides = Vente.objects.annotate(nb_lignes=Count('lignevente')).filter(nb_lignes=0)
print(f"Ventes vides: {ventes_vides.count()}")
ventes_vides.delete()
```

---

## ✅ CHECKLIST DE VÉRIFICATION

Après avoir créé une vente:

- [ ] Message de succès affiché dans l'interface
- [ ] Logs montrent "✓ Ligne X créée"
- [ ] Logs montrent "✓ Total de lignes créées: X"
- [ ] Vente visible dans la liste des ventes
- [ ] Vente a des lignes de produits (visible dans le détail)
- [ ] Stock du produit a diminué
- [ ] Mouvement de stock créé

---

## 🎯 STATUT ACTUEL

- ✅ Code corrigé installé
- ✅ Serveur Django redémarré (00:13:58)
- ✅ Prêt pour les tests
- ⏳ En attente de test de création de vente

**Prochaine étape:** Créer une vente et vérifier les logs pour confirmer que le nouveau code fonctionne.

---

## 📞 SI VOUS VOYEZ UNE ERREUR

Copiez-collez l'erreur complète des logs du serveur pour diagnostic approfondi.

Les erreurs typiques:
- `IntegrityError` → Contrainte de base de données violée
- `DoesNotExist` → Produit ou client introuvable
- `ValueError` → Quantité ou prix invalide
- `ValidationError` → Données du formulaire invalides
