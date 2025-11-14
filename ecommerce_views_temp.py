
# ============ VUES PUBLIQUES E-COMMERCE ============

def ecommerce_home(request):
    """Landing page e-commerce avec produits populaires"""
    # Produits les plus populaires/récents
    produits_populaires = Produit.objects.filter(
        actif=True, 
        quantite_stock__gt=0
    ).order_by('-id')[:8]
    
    # Catégories principales
    categories = Categorie.objects.filter(actif=True)[:6]
    
    context = {
        'produits_populaires': produits_populaires,
        'categories': categories,
    }
    return render(request, 'inventory/ecommerce/home.html', context)


def ecommerce_catalogue(request):
    """Catalogue de produits e-commerce avec filtres"""
    produits = Produit.objects.filter(actif=True, quantite_stock__gt=0)
    
    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    # Recherche par nom/description
    search = request.GET.get('search')
    if search:
        produits = produits.filter(
            Q(nom__icontains=search) | Q(description__icontains=search)
        )
    
    # Tri
    sort_by = request.GET.get('sort', 'nom')
    if sort_by == 'prix_asc':
        produits = produits.order_by('prix_vente')
    elif sort_by == 'prix_desc':
        produits = produits.order_by('-prix_vente')
    elif sort_by == 'recent':
        produits = produits.order_by('-id')
    else:
        produits = produits.order_by('nom')
    
    # Pagination
    paginator = Paginator(produits, 12)  # 12 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Toutes les catégories pour le filtre
    categories = Categorie.objects.filter(actif=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_categorie': int(categorie_id) if categorie_id else None,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'inventory/ecommerce/catalogue.html', context)


def ecommerce_produit_detail(request, pk):
    """Page détail produit e-commerce"""
    produit = get_object_or_404(Produit, pk=pk, actif=True)
    
    # Produits similaires (même catégorie)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie,
        actif=True,
        quantite_stock__gt=0
    ).exclude(pk=pk)[:4]
    
    context = {
        'produit': produit,
        'produits_similaires': produits_similaires,
    }
    return render(request, 'inventory/ecommerce/produit_detail.html', context)


# ============ VUES D'AUTHENTIFICATION ============

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


def admin_login(request):
    """Page de connexion pour les administrateurs"""
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'inventory:dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    form = AuthenticationForm()
    return render(request, 'inventory/auth/login.html', {'form': form})


def admin_logout(request):
    """Déconnexion des administrateurs"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('inventory:ecommerce_home')
