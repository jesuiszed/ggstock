# 📋 CAHIER DES CHARGES COMPLET
## SYSTÈME DE GESTION D'INVENTAIRE D'ENTREPRISE BIOMÉDICALE

---

### 📊 **INFORMATIONS GÉNÉRALES DU PROJET**

**Nom du projet :** Enterprise Inventory Management System (EIMS)  
**Domaine d'activité :** Équipements biomédicaux et matériel médical  
**Type :** Application web de gestion intégrée  
**Framework :** Django 5.2.4 avec interface Tailwind CSS  
**Date de rédaction :** 27 août 2025  
**Version :** 1.0 - Production Ready  

---

## 🎯 **OBJECTIFS ET CONTEXTE**

### **Objectif principal**
Développer un système de gestion d'inventaire complet et intégré pour une entreprise spécialisée dans les équipements biomédicaux, permettant la gestion efficace des produits, clients, ventes, commandes, et du service après-vente.

### **Contexte métier**
L'entreprise évolue dans le secteur biomédical et nécessite :
- Une gestion rigoureuse des équipements médicaux
- Un suivi précis de la maintenance préventive et corrective
- Une traçabilité complète des appareils vendus
- Un système de prospection et de fidélisation client
- Une gestion multi-rôles adaptée aux différents métiers

---

## 👥 **SYSTÈME DE GESTION DES RÔLES**

### **1. 👑 MANAGER (Administrateur Général)**
**Périmètre :** Supervision générale et administration système

#### **Fonctionnalités autorisées :**
- ✅ **Gestion des utilisateurs** : Création, modification, suppression de comptes
- ✅ **Administration système** : Accès à Django Admin, configuration
- ✅ **Supervision complète** : Vue d'ensemble de toutes les activités
- ✅ **Gestion des produits** : CRUD complet, catégories, fournisseurs
- ✅ **Gestion du stock** : Mouvements, transferts, ajustements
- ✅ **Gestion des clients** : Base de données complète
- ✅ **Gestion des commandes** : Workflow complet
- ✅ **Gestion des ventes** : Point de vente, facturation
- ✅ **Analytics et rapports** : Tableaux de bord, statistiques
- ✅ **Service biomédical** : Supervision des interventions SAV
- ✅ **Gestion des devis** : Validation et supervision

#### **Interface spécifique :**
- Dashboard manager avec KPI globaux
- Accès à tous les modules
- Outils d'administration avancés

---

### **2. 🏪 COMMERCIAL SHOWROOM (Type 1)**
**Périmètre :** Ventes directes et gestion des commandes

#### **Fonctionnalités autorisées :**
- ✅ **Gestion des produits** : Consultation, mise à jour des prix
- ✅ **Gestion des ventes** : 
  - Création et gestion des bons de vente
  - Émission de factures
  - Gestion des modes de paiement
  - Impression des documents de vente
- ✅ **Gestion des commandes** :
  - Création et gestion des bons de commande
  - Création et gestion des bons de livraison
  - Suivi du workflow commande → livraison → facturation
  - Impression des documents de commande
- ✅ **Consultation du stock** : Vérification des disponibilités
- ✅ **Gestion clientèle basique** : Consultation des clients existants
- ✅ **Catalogue e-commerce** : Mise à jour des informations produits

#### **Fonctionnalités interdites :**
- ❌ Gestion des fournisseurs
- ❌ Modifications du stock (sauf ventes et commandes)
- ❌ Administration des utilisateurs
- ❌ Gestion des prospects et devis

#### **Interface spécifique :**
- Dashboard orienté ventes et commandes avec statistiques de performance
- Interface de point de vente optimisée
- Module de gestion des commandes intégré
- Accès direct aux outils de facturation et impression

---

### **3. 🚗 COMMERCIAL TERRAIN (Type 2)**
**Périmètre :** Relations clients, développement commercial et reporting

#### **Fonctionnalités autorisées :**
- ✅ **Gestion complète des clients** :
  - Création et mise à jour des fiches clients
  - Historique des interactions
  - Gestion des entreprises clientes
- ✅ **Système de devis/proforma** :
  - Création de devis personnalisés
  - Génération PDF avec logo entreprise
  - Suivi des devis (accepté, refusé, en attente)
  - Conversion devis → commande (transmission au showroom)
- ✅ **Gestion des prospects** :
  - Base de données prospects avec statuts
  - Pipeline commercial (nouveau, contacté, intéressé, etc.)
  - Notes d'observation et suivi des interactions
  - Planification des relances
- ✅ **Système de rapports** :
  - **Rapports clients** : Analyse de la clientèle par secteur, chiffre d'affaires, fréquence d'achat
  - **Rapports prospects** : Pipeline commercial, taux de conversion, prospects par statut
  - **Rapports d'activité** : Visites terrain, devis envoyés, négociations en cours
  - **Rapports de performance** : Objectifs vs réalisé, évolution mensuelle/trimestrielle
  - Export Excel/PDF des rapports personnalisés
- ✅ **Outils de prospection** :
  - Identification des prospects prioritaires
  - Historique des contacts
  - Notes d'observations détaillées
- ✅ **Analyse territoriale** :
  - Mapping des clients par zone géographique
  - Potentiel de développement par secteur
  - Planification des tournées terrain

#### **Fonctionnalités interdites :**
- ❌ Gestion directe du stock
- ❌ Ventes en showroom
- ❌ Administration technique
- ❌ Gestion des commandes (transférées au showroom)

#### **Interface spécifique :**
- Dashboard commercial avec pipeline et objectifs
- CRM intégré pour le suivi client/prospect
- Module de génération de rapports personnalisés
- Outils de génération de devis automatisés
- Interface de cartographie et analyse territoriale

---

### **4. 🔧 TECHNICIEN (Service Biomédical)**
**Périmètre :** Gestion technique, stock et service après-vente

#### **Fonctionnalités autorisées :**

#### **a) Gestion des Stocks et Logistique :**
- ✅ **Gestion du stock dépôt** :
  - Réception de marchandises
  - Contrôle qualité des équipements
  - Gestion des emplacements de stockage
  - Inventaires et ajustements
- ✅ **Transferts inter-magasins** :
  - Transfert dépôt → showroom
  - Transfert entre sites
  - Suivi des mouvements avec traçabilité
  - Gestion des transporteurs
- ✅ **Gestion des fournisseurs** :
  - Mise à jour des informations fournisseurs
  - Suivi des livraisons
  - Gestion des retours fournisseurs

#### **b) Service Après-Vente (SAV) :**
- ✅ **Répertoire des appareils vendus** :
  - Base de données complète des équipements installés
  - Localisation précise dans les structures sanitaires
  - Historique complet par appareil
- ✅ **Maintenance préventive** :
  - Planification automatique des maintenances
  - Calendrier des interventions
  - Rappels et alertes de maintenance
- ✅ **Maintenance corrective** :
  - Gestion des pannes et incidents
  - Planification des interventions urgentes
  - Suivi des réparations
- ✅ **Gestion des interventions** :
  - Création et planning des interventions
  - Rapports d'intervention détaillés
  - Gestion des pièces de rechange
  - Satisfaction client et notes

#### **Fonctionnalités interdites :**
- ❌ Gestion des ventes directes
- ❌ Gestion des devis commerciaux
- ❌ Administration des utilisateurs

#### **Interface spécifique :**
- Dashboard technique avec alertes de maintenance
- Planning des interventions SAV
- Outils de gestion des stocks avancés

---

## 🗂️ **MODULES FONCTIONNELS DÉTAILLÉS**

### **MODULE 1 : GESTION DES PRODUITS**

#### **Fonctionnalités :**
- **Catalogue produits** avec catégorisation
- **Gestion des références** et codes-barres
- **Prix d'achat et prix de vente** avec calcul de marge
- **Images produits** avec upload et gestion
- **Descriptions techniques** détaillées
- **Seuils d'alerte** pour stock bas
- **Statut actif/inactif** pour archivage

#### **Rôles autorisés :** Manager, Commercial Showroom, Technicien

---

### **MODULE 2 : GESTION DU STOCK**

#### **Fonctionnalités :**
- **Suivi en temps réel** des quantités
- **Mouvements de stock** tracés (entrées, sorties, ajustements)
- **Alertes de stock bas** automatiques
- **Valorisation du stock** par produit
- **Transferts inter-magasins** avec workflow d'approbation
- **Inventaires** et ajustements
- **Historique complet** des mouvements

#### **Rôles autorisés :** Manager, Technicien

---

### **MODULE 3 : GESTION DES CLIENTS**

#### **Fonctionnalités :**
- **Base de données clients** complète
- **Informations entreprise** et contacts
- **Historique des achats** et commandes
- **Statut client** (actif, prospect, etc.)
- **Notes et observations** personnalisées
- **Géolocalisation** et secteurs

#### **Rôles autorisés :** Manager, Commercial Terrain

---

### **MODULE 4 : SYSTÈME DE DEVIS/PROFORMA**

#### **Fonctionnalités :**
- **Création de devis** personnalisés
- **Lignes de devis** avec produits et quantités
- **Calculs automatiques** (HT, TVA, TTC)
- **Génération PDF** avec mise en forme professionnelle
- **Statuts de suivi** (brouillon, envoyé, accepté, refusé)
- **Conversion automatique** devis → commande
- **Historique et versions**

#### **Rôles autorisés :** Manager, Commercial Terrain

---

### **MODULE 5 : GESTION DES PROSPECTS**

#### **Fonctionnalités :**
- **Pipeline commercial** avec étapes définies
- **Statuts prospects** (nouveau, contacté, intéressé, négociation, gagné, perdu)
- **Notes d'observation** horodatées
- **Planification des relances**
- **Conversion prospect → client**
- **Statistiques de conversion**

#### **Rôles autorisés :** Manager, Commercial Terrain

---

### **MODULE 6 : GESTION DES COMMANDES**

#### **Fonctionnalités :**
- **Workflow complet** commande → livraison → facturation
- **Statuts de commande** (en attente, confirmée, expédiée, livrée)
- **Bon de commande** et bon de livraison
- **Suivi des délais** de livraison
- **Facturation automatique** post-livraison
- **Gestion des retours**

#### **Rôles autorisés :** Manager, Commercial Terrain

---

### **MODULE 7 : GESTION DES VENTES**

#### **Fonctionnalités :**
- **Point de vente** intégré
- **Gestion des modes de paiement**
- **Facturation instantanée**
- **Impression tickets** et factures
- **Statistiques de vente** par période
- **Gestion des remises** et promotions

#### **Rôles autorisées :** Manager, Commercial Showroom

---

### **MODULE 8 : SERVICE BIOMÉDICAL**

#### **Fonctionnalités appareils vendus :**
- **Répertoire complet** des équipements installés
- **Fiche technique** par appareil (modèle, série, configuration)
- **Localisation précise** dans les structures sanitaires
- **Date d'installation** et mise en service
- **Garantie** et fin de garantie
- **Historique des interventions**

#### **Fonctionnalités maintenance :**
- **Planning de maintenance préventive**
- **Alertes automatiques** de maintenance due
- **Types d'intervention** (préventive, corrective, installation, formation)
- **Planification des techniciens**
- **Rapports d'intervention** détaillés
- **Gestion des pièces** de rechange
- **Satisfaction client** et évaluations

#### **Rôles autorisés :** Manager, Technicien

---

### **MODULE 9 : TRANSFERTS DE STOCK**

#### **Fonctionnalités :**
- **Workflow d'approbation** des transferts
- **Types de transfert** (inter-magasin, retour fournisseur, livraison client, maintenance, rebut)
- **Suivi des statuts** (en attente, approuvé, expédié, livré)
- **Gestion des transporteurs**
- **Numéros de suivi** et tracking
- **Priorités** (normal, haute, urgent)

#### **Rôles autorisés :** Manager, Technicien

---

### **MODULE 10 : E-COMMERCE PUBLIC**

#### **Fonctionnalités :**
- **Catalogue public** sans prix
- **Recherche et filtres** avancés
- **Fiches produits** détaillées avec images
- **Interface responsive** mobile/desktop
- **Formulaire de contact** intégré

#### **Accès :** Public (sans authentification)

---

## 💻 **SPÉCIFICATIONS TECHNIQUES**

### **Architecture Système**
- **Framework :** Django 5.2.4 (Python)
- **Base de données :** SQLite (développement) / PostgreSQL (production)
- **Frontend :** HTML5, CSS3, JavaScript, Tailwind CSS
- **Authentification :** Django Auth avec système de rôles personnalisé
- **Gestion des fichiers :** Django FileField avec stockage local/cloud

### **Structure de la Base de Données**
- **13 modèles principaux** avec relations optimisées
- **Contraintes d'intégrité** référentielle
- **Index** sur les champs de recherche fréquents
- **Soft delete** pour la traçabilité

### **Sécurité**
- **Authentification obligatoire** pour toutes les fonctions métier
- **Système de permissions** granulaire par rôle
- **Protection CSRF** activée
- **Validation** côté serveur et client
- **Logs d'audit** des actions sensibles

### **Performance**
- **Pagination** automatique des listes
- **Requêtes optimisées** avec select_related/prefetch_related
- **Mise en cache** des données statiques
- **Compression** des images uploadées

---

## 📱 **INTERFACE UTILISATEUR**

### **Design et Ergonomie**
- **Design moderne** avec Tailwind CSS
- **Interface responsive** (mobile, tablet, desktop)
- **Navigation contextuelle** selon le rôle utilisateur
- **Sidebar dynamique** avec icônes Font Awesome
- **Messages de feedback** utilisateur
- **Thème cohérent** aux couleurs de l'entreprise

### **Dashboards Personnalisés**
- **Dashboard Manager :** Vue d'ensemble avec KPI globaux
- **Dashboard Commercial Showroom :** Focus ventes et stock
- **Dashboard Commercial Terrain :** CRM et pipeline commercial
- **Dashboard Technicien :** Planning SAV et alertes de stock

### **Fonctionnalités UX**
- **Recherche instantanée** avec autocomplétion
- **Filtres avancés** sur toutes les listes
- **Formulaires avec validation** temps réel
- **Confirmations** pour les actions critiques
- **Breadcrumb** de navigation
- **États de chargement** et progression

---

## 📊 **RAPPORTS ET ANALYSES**

### **Rapports Standards**
- **Rapport de stock** avec valorisation
- **Rapport de ventes** par période/commercial
- **Rapport de commandes** en cours et historique
- **Rapport SAV** avec statistiques d'intervention
- **Rapport prospects** avec taux de conversion

### **Exports**
- **PDF** pour devis, factures, rapports
- **Excel/CSV** pour les données analytiques
- **Impression** optimisée pour tous les documents

---

## 🔧 **WORKFLOW MÉTIER**

### **Cycle de Vie Prospect → Client**
1. **Prospection** → Création du prospect
2. **Qualification** → Notes d'observation, statut
3. **Négociation** → Création de devis
4. **Conversion** → Transformation en client + commande
5. **Fidélisation** → Suivi post-vente et SAV

### **Cycle de Vie Commande**
1. **Création** → Saisie par commercial terrain
2. **Validation** → Vérification stock et prix
3. **Préparation** → Picking en stock dépôt
4. **Expédition** → Transfert vers lieu de livraison
5. **Livraison** → Installation et mise en service
6. **Facturation** → Génération facture finale

### **Cycle de Vie SAV**
1. **Installation** → Création fiche appareil
2. **Planning** → Planification maintenance préventive
3. **Intervention** → Exécution et rapport
4. **Suivi** → Mise à jour planning suivant
5. **Évaluation** → Satisfaction client

---

## 📈 **INDICATEURS DE PERFORMANCE**

### **KPI Commerciaux**
- Chiffre d'affaires par commercial et période
- Taux de conversion prospects → clients
- Nombre de devis envoyés/acceptés
- Panier moyen par client
- Top 10 des produits vendus

### **KPI Stock et Logistique**
- Valeur du stock par catégorie
- Nombre d'alertes de stock bas
- Taux de rotation des stocks
- Efficacité des transferts inter-magasins

### **KPI Service Biomédical**
- Nombre d'appareils sous maintenance
- Temps moyen d'intervention
- Taux de satisfaction client SAV
- Nombre d'interventions préventives vs correctives

---

## 🚀 **DÉPLOIEMENT ET MAINTENANCE**

### **Environnements**
- **Développement :** Local avec SQLite
- **Test :** Serveur de staging
- **Production :** Serveur dédié avec PostgreSQL

### **Sauvegarde et Sécurité**
- **Sauvegarde quotidienne** automatique de la base
- **Versioning** des fichiers media
- **Monitoring** des performances
- **Logs** d'erreurs et d'audit

### **Formation Utilisateurs**
- **Documentation** utilisateur par rôle
- **Guides** d'utilisation intégrés
- **Formation** sur site pour les équipes
- **Support** technique post-déploiement

---

## ✅ **CRITÈRES D'ACCEPTATION**

### **Fonctionnels**
- ✅ Tous les rôles utilisateur opérationnels
- ✅ Workflow complet prospect → client → commande → livraison
- ✅ Système de devis avec génération PDF
- ✅ Planning SAV avec alertes automatiques
- ✅ Transferts de stock avec traçabilité
- ✅ E-commerce public fonctionnel

### **Techniques**
- ✅ Performance : pages < 2s de chargement
- ✅ Sécurité : authentification et permissions
- ✅ Compatibilité : Chrome, Firefox, Safari, Edge
- ✅ Responsive : mobile, tablet, desktop
- ✅ Stabilité : 99.9% de disponibilité

### **Organisationnels**
- ✅ Formation équipes réalisée
- ✅ Documentation livrée
- ✅ Migration données existantes
- ✅ Support technique mis en place

---

## 📋 **LIVRABLES ATTENDUS**

1. **Application web complète** déployée en production
2. **Code source** documenté et versionné
3. **Base de données** structurée avec données de test
4. **Documentation technique** complète
5. **Guides utilisateur** par rôle
6. **Formation** des équipes opérationnelles
7. **Support** technique 3 mois post-déploiement

---

---

## 📱 **SPÉCIFICATIONS DÉTAILLÉES DES INTERFACES**

### **🏠 Dashboard Principal**
- **Vue d'ensemble** : Métriques clés, alertes stock, ventes récentes
- **Graphiques interactifs** : Évolution du CA, top produits, performances par commercial
- **Notifications** : Stock bas, commandes en attente, interventions SAV urgentes
- **Widgets personnalisables** par rôle utilisateur
- **Responsive design** : Optimisé mobile/tablette/desktop

### **🛒 Interface E-commerce Client (site vitrine - sans authentification client)**
- **Catalogue produits** : Navigation par catégories avec filtres avancés
- **Fiche produit détaillée** : Images, caractéristiques techniques, disponibilité
- **Moteur de recherche** : Recherche multicritères (nom, référence, marque)
- **Système de devis** : Demande de devis en ligne avec formulaire détaillé

### **📊 Interface de Gestion du Stock**
- **Vue d'ensemble stock** : Tableau avec alertes visuelles (rouge: rupture, orange: stock bas)
- **Mouvements de stock** : Historique complet avec filtres par période/produit
- **Transferts entre sites** : Interface de création et suivi des transferts
- **Inventaire** : Module de comptage avec import/export Excel
- **Prédictions** : Analyses tendances et recommandations réapprovisionnement

### **👥 CRM Commercial**
- **Base clients** : Fiche complète avec historique achats et interactions
- **Pipeline prospects** : Vue Kanban avec étapes personnalisables
- **Calendrier commercial** : Planification RDV et relances
- **Génération devis** : Interface drag-drop avec bibliothèque de modèles
- **Reporting commercial** : Tableaux de bord avec graphiques évolution

### **🔧 Interface SAV Technique**
- **Planning interventions** : Calendrier avec affectation techniciens
- **Fiche d'intervention** : Checklist maintenance, photos, signatures électroniques
- **Historique appareil** : Traçabilité complète interventions par série
- **Pièces détachées** : Gestion stock SAV avec liens fournisseurs
- **Certification qualité** : Génération certificats maintenance réglementaires

### **💰 Module Financier**
- **Facturation** : Génération automatique avec modèles personnalisables
- **Suivi paiements** : Échéancier avec relances automatiques
- **Comptabilité** : Interface de saisie avec export comptable
- **Analyse rentabilité** : Marges par produit/client/commercial
- **Prévisionnel** : Projections CA basées sur pipeline

### **⚙️ Administration Système**
- **Gestion utilisateurs** : Création comptes avec gestion rôles/permissions
- **Configuration** : Paramétrage tarifs, remises, conditions commerciales
- **Sauvegarde** : Interface backup automatique avec historique
- **Monitoring** : Supervision performances et utilisation système
- **Sécurité** : Logs d'audit et contrôle d'accès

---


**Date de validation :** 27 août 2025  
**Statut :** ✅ CAHIER DES CHARGES VALIDÉ ET IMPLÉMENTÉ  
**Version système :** 1.0 Production Ready

```
