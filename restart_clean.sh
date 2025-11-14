#!/bin/bash

echo "🧹 NETTOYAGE COMPLET ET REDÉMARRAGE DU SERVEUR DJANGO"
echo "======================================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Arrêter tous les serveurs Django
echo "1️⃣ Arrêt de tous les processus Django..."
pkill -9 -f "manage.py runserver" 2>/dev/null
sleep 2

# Vérifier qu'ils sont bien arrêtés
if ps aux | grep -v grep | grep "manage.py runserver" > /dev/null; then
    echo -e "${RED}❌ Impossible d'arrêter les processus Django${NC}"
    echo "   Processus restants:"
    ps aux | grep -v grep | grep "manage.py runserver"
    exit 1
else
    echo -e "${GREEN}✅ Tous les processus Django arrêtés${NC}"
fi

# 2. Nettoyer les fichiers .pyc et __pycache__
echo ""
echo "2️⃣ Nettoyage des fichiers Python compilés..."
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✅ Fichiers .pyc nettoyés${NC}"

# 3. Vérifier que le code corrigé est bien présent
echo ""
echo "3️⃣ Vérification du code corrigé..."

# Vérifier la présence du nouveau code
if grep -q "# Parser toutes les clés POST pour trouver TOUTES les lignes de produit" inventory/views.py; then
    echo -e "${GREEN}✅ Nouveau code détecté dans vente_create${NC}"
else
    echo -e "${RED}❌ ERREUR: Le nouveau code n'est pas présent dans vente_create!${NC}"
    exit 1
fi

if grep -q "Lignes trouvées:" inventory/views.py; then
    echo -e "${GREEN}✅ Nouveau code détecté dans commande_create_advanced${NC}"
else
    echo -e "${RED}❌ ERREUR: Le nouveau code n'est pas présent dans commande_create_advanced!${NC}"
    exit 1
fi

# Vérifier que l'ancien code n'est plus là
if grep -q "Recherche des clés:" inventory/views.py; then
    echo -e "${RED}❌ ATTENTION: L'ancien code est toujours présent!${NC}"
    echo "   Ligne trouvée:"
    grep -n "Recherche des clés:" inventory/views.py
    exit 1
else
    echo -e "${GREEN}✅ Ancien code bien supprimé${NC}"
fi

# 4. Redémarrer le serveur Django
echo ""
echo "4️⃣ Redémarrage du serveur Django..."
echo -e "${YELLOW}⏳ Démarrage en cours...${NC}"

# Lancer le serveur en arrière-plan
nohup .venv/bin/python manage.py runserver > django_server.log 2>&1 &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 3

# Vérifier que le serveur est bien démarré
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✅ Serveur Django démarré (PID: $SERVER_PID)${NC}"
    echo ""
    echo "📊 Logs du serveur (dernières lignes):"
    echo "----------------------------------------"
    tail -20 django_server.log
    echo "----------------------------------------"
else
    echo -e "${RED}❌ Échec du démarrage du serveur${NC}"
    echo "   Logs:"
    cat django_server.log
    exit 1
fi

# 5. Tester la connexion
echo ""
echo "5️⃣ Test de connexion au serveur..."
sleep 2

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/inventory/ 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Serveur accessible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠️  Serveur peut-être en démarrage (HTTP $HTTP_CODE)${NC}"
    echo "   Vérifiez manuellement: http://127.0.0.1:8000/"
fi

# 6. Instructions finales
echo ""
echo "🎉 NETTOYAGE ET REDÉMARRAGE TERMINÉS"
echo "===================================="
echo ""
echo "✅ Prochaines étapes:"
echo "   1. Aller sur: http://127.0.0.1:8000/inventory/commandes/nouvelle/"
echo "   2. Créer une nouvelle commande avec 1+ produits"
echo "   3. Vérifier les logs: tail -f django_server.log"
echo ""
echo "📋 Logs attendus (NOUVEAU CODE):"
echo "   ==> DEBUG COMMANDE_CREATE ==="
echo "   Lignes trouvées: ['0']"
echo "   Traitement ligne 0: produit=XX, quantite=1, prix=XXXX"
echo "   ✓ Ligne 0 créée: [Nom Produit] x 1"
echo "   ✓ Total de lignes créées: 1"
echo ""
echo "❌ Si vous voyez encore (ANCIEN CODE):"
echo "   Recherche des clés: ligne_0_produit..."
echo "   → Exécutez à nouveau ce script!"
echo ""
echo "📁 Logs du serveur sauvegardés dans: django_server.log"
echo "   Voir en temps réel: tail -f django_server.log"
echo ""
echo "🛑 Pour arrêter le serveur: kill $SERVER_PID"
echo ""
