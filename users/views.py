from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from .decorators import permission_required, manager_required
from .forms import ProfileForm

class UserProfileCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(max_length=30, required=False, label="Prénom")
    last_name = forms.CharField(max_length=30, required=False, label="Nom")

    class Meta:
        model = Profile
        fields = ['role', 'telephone']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return profile

def login_view(request):
    """Vue de connexion personnalisée"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Rediriger selon le rôle de l'utilisateur
            if hasattr(user, 'profile'):
                if user.profile.role == 'MANAGER':
                    return redirect('inventory:dashboard')
                elif user.profile.role == 'COMMERCIAL_SHOWROOM':
                    return redirect('inventory:dashboard')  # Dashboard showroom
                elif user.profile.role == 'COMMERCIAL_TERRAIN':
                    return redirect('inventory:dashboard')  # Dashboard terrain
                elif user.profile.role == 'TECHNICIEN':
                    return redirect('inventory:dashboard')  # Dashboard technicien
            
            # Redirection par défaut
            return redirect('inventory:dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'users/login.html')

def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('users:login')

@login_required
def profile_view(request):
    """Vue du profil utilisateur"""
    return render(request, 'users/profile.html', {
        'user': request.user,
        'profile': request.user.profile
    })

@permission_required('can_manage_users')
def user_management(request):
    """Gestion des utilisateurs (réservée aux managers)"""
    users = User.objects.all().select_related('profile')
    return render(request, 'users/user_management.html', {
        'users': users
    })

@login_required
def role_test(request):
    """Vue de test pour vérifier les permissions des rôles"""
    if not hasattr(request.user, 'profile'):
        context = {
            'error': 'Aucun profil trouvé pour cet utilisateur'
        }
    else:
        profile = request.user.profile
        context = {
            'user': request.user,
            'role': profile.get_role_display(),
            'can_manage_products': profile.can_manage_products(),
            'can_manage_clients': profile.can_manage_clients(),
            'can_manage_orders': profile.can_manage_orders(),
            'can_manage_sales': profile.can_manage_sales(),
            'can_manage_quotes': profile.can_manage_quotes(),
            'can_manage_prospects': profile.can_manage_prospects(),
            'can_view_reports': profile.can_view_reports(),
            'can_manage_stock': profile.can_manage_stock(),
            'can_manage_suppliers': profile.can_manage_suppliers(),
            'can_view_analytics': profile.can_view_analytics(),
        }
    
    return render(request, 'users/role_test.html', context)

@manager_required
def profils_list(request):
    """Liste et gestion des profils utilisateurs (réservé au manager)"""
    profils = Profile.objects.select_related('user').all()
    return render(request, 'users/profils_list.html', {'profils': profils})

@manager_required
def profil_update(request, pk):
    """Modification d'un profil utilisateur (réservé au manager)"""
    profil = get_object_or_404(Profile, pk=pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('users:profils_list')
    else:
        form = ProfileForm(instance=profil)
    return render(request, 'users/profil_form.html', {'form': form, 'profil': profil})

@manager_required
def profil_create(request):
    """Création d'un nouvel utilisateur (réservé au manager)"""
    if request.method == 'POST':
        form = UserProfileCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nouvel utilisateur créé avec succès.")
            return redirect('users:profils_list')
    else:
        form = UserProfileCreateForm()
    return render(request, 'users/profil_create.html', {'form': form})
