from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def role_required(allowed_roles):
    """
    Décorateur pour vérifier si l'utilisateur a l'un des rôles autorisés.
    
    Usage:
    @role_required(['MANAGER', 'COMMERCIAL_SHOWROOM', 'COMMERCIAL_TERRAIN','TECHNICIAN'])
    def ma_vue(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, "Aucun profil trouvé pour cet utilisateur.")
                return redirect('users:login')
            
            user_role = request.user.profile.role
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                return HttpResponseForbidden("Accès refusé : permissions insuffisantes")
        
        return _wrapped_view
    return decorator

def permission_required(permissions):
    """
    Décorateur pour vérifier les permissions spécifiques.
    
    Usage:
    @permission_required(['can_manage_products', 'can_manage_stock'])
    def ma_vue(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, "Aucun profil trouvé pour cet utilisateur.")
                return redirect('users:login')
            
            profile = request.user.profile
            
            # Vérifier si l'utilisateur a au moins une des permissions requises
            has_permission = False
            for permission in permissions:
                if hasattr(profile, permission) and getattr(profile, permission)():
                    has_permission = True
                    break
            
            if has_permission:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                return HttpResponseForbidden("Accès refusé : permissions insuffisantes")
        
        return _wrapped_view
    return decorator

def manager_required(view_func):
    """
    Décorateur pour les vues réservées aux managers seulement.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "Aucun profil trouvé pour cet utilisateur.")
            return redirect('users:login')
        
        if request.user.profile.is_manager():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Accès réservé aux managers uniquement.")
            return HttpResponseForbidden("Accès refusé : vous devez être manager")
    
    return _wrapped_view

def permission_required(permission_method):
    """Décorateur utilisant les méthodes de permission du modèle Profile"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Vous devez vous connecter pour accéder à cette page.")
                return redirect('inventory:admin_login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, "Votre compte n'a pas de profil assigné. Contactez l'administrateur.")
                return redirect('inventory:ecommerce_home')
            
            # Vérifier la permission spécifique
            if not getattr(request.user.profile, permission_method)():
                messages.error(request, "Vous n'avez pas les permissions nécessaires pour cette action.")
                return redirect('inventory:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
