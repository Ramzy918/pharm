from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from requests import HTTPError, RequestException
import json


from . import api_client


def _token(request):
    return request.session.get("access")


def _is_admin(request):
    """Vérifier si l'utilisateur est admin en utilisant le JWT role"""
    token = _token(request)
    if not token:
        return False
    try:
        import base64
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return False
        # Ajouter le padding si nécessaire
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        return data.get('role') == 'ADMIN'
    except:
        return False


def _require_admin(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    if not _is_admin(request):
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect("home")
    return None


def set_language(request):
    desired = request.GET.get("lang", "fr")
    if desired not in ("fr", "ar"):
        desired = "fr"
    request.session["lang"] = desired
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or reverse("home")
    return redirect(next_url)


def home(request):
    featured_products = []
    search_query = request.GET.get('q', '').strip()
    
    if _token(request):
        try:
            
            data = api_client.api_get("products/", _token(request))
            if isinstance(data, dict) and "results" in data:
                featured_products = data["results"][:8]  # Limiter à 8 produits
            elif isinstance(data, list):
                featured_products = data[:8]
        except RequestException:
            featured_products = []
    
    context = {
        "authenticated": bool(_token(request)),
        "featured_products": featured_products,
        "search_query": search_query,
    }
    
   
    if search_query:
        return redirect(f"{reverse('catalog')}?q={search_query}")
    
    return render(request, "shop/home.html", context)


def login_view(request):
    if _token(request):
        return redirect("catalog")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        try:
            data = api_client.auth_token(email=email, password=password)
        except HTTPError:
            messages.error(request, "E-mail ou mot de passe incorrect.")
            return render(request, "shop/login.html")
        except RequestException:
            messages.error(request, "Impossible de joindre le service d’authentification.")
            return render(request, "shop/login.html")
        request.session["access"] = data.get("access")
        request.session["refresh"] = data.get("refresh")
        messages.success(request, "Connexion réussie.")
       
        if _is_admin(request):
            next_url = request.GET.get("next") or reverse("admin_dashboard")
        else:
            next_url = request.GET.get("next") or reverse("catalog")
        return redirect(next_url)
    return render(request, "shop/login.html")


def logout_view(request):
    request.session.flush()
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("home")


def signup_view(request):
    if _token(request):
        return redirect("catalog")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("full_name", "").strip()
        
        if not email or not password:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, "shop/signup.html")
        
        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "shop/signup.html")
        
        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return render(request, "shop/signup.html")
        
        try:
            data = api_client.auth_register(
                email=email,
                password=password,
                first_name=first_name,
                role="PRO",
            )
        except HTTPError as e:
            try:
                err_detail = e.response.json()
                msg = str(err_detail)
            except:
                msg = "Erreur lors de l'enregistrement."
            messages.error(request, msg)
            return render(request, "shop/signup.html")
        except RequestException:
            messages.error(request, "Impossible de contacter le service d'authentification.")
            return render(request, "shop/signup.html")
        
        messages.success(request, "Inscription réussie! Vous pouvez vous connecter.")
        return redirect("login")
    
    return render(request, "shop/signup.html")


def _require_auth(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    return None


def catalog(request):
    redir = _require_auth(request)
    if redir:
        return redir

    params = {}
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    min_stock = request.GET.get("min_stock", "").strip()
    if q:
        params["search"] = q
    if category:
        params["category"] = category

    try:
        data = api_client.api_get("products/", _token(request), params=params if params else None)
    except RequestException:
        messages.error(request, "Catalogue indisponible.")
        return render(request, "shop/catalog.html", {"results": [], "categories": []})

    if isinstance(data, dict) and "results" in data:
        results = data["results"]
    elif isinstance(data, list):
        results = data
    else:
        results = []

    # Filtre stock minimum côté front si donné
    if min_stock:
        try:
            min_stock_int = int(min_stock)
            results = [p for p in results if int(p.get("stock", 0)) >= min_stock_int]
        except (TypeError, ValueError):
            pass

    # indicateur de date d'expiration proche (<30 jours)
    from datetime import datetime, timedelta

    now = datetime.now().date()
    for product in results:
        exp_date = product.get("expiration_date")
        if exp_date:
            try:
                exp_date_parsed = datetime.strptime(exp_date, "%Y-%m-%d").date()
                if exp_date_parsed < now:
                    product["expired"] = True
                    product["expiring_soon"] = False
                elif exp_date_parsed <= now + timedelta(days=30):
                    product["expired"] = False
                    product["expiring_soon"] = True
                else:
                    product["expired"] = False
                    product["expiring_soon"] = False
            except ValueError:
                product["expired"] = False
                product["expiring_soon"] = False
        else:
            product["expired"] = False
            product["expiring_soon"] = False

    # catégories pour le filtre client
    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = categories_data.get("results", categories_data) if isinstance(categories_data, dict) else categories_data
        if not isinstance(categories, list):
            categories = []
    except RequestException:
        categories = []

    return render(request, "shop/catalog.html", {"results": results, "categories": categories})


def _get_cart(request) -> dict[str, int]:
    cart = request.session.get("cart") or {}
    out = {}
    for k, v in cart.items():
        try:
            out[str(int(k))] = max(1, int(v))
        except (TypeError, ValueError):
            continue
    request.session["cart"] = out
    return out


def cart_add(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    messages.success(request, "Produit ajouté au panier.")
    return redirect("cart")


def cart_remove(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart")


def cart_update(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    if request.method == "POST":
        cart = _get_cart(request)
        quantity = request.POST.get("quantity", "0").strip()
        try:
            qty = int(quantity)
            if qty > 0:
                cart[str(product_id)] = qty
                messages.success(request, "Quantité mise à jour.")
            else:
                cart.pop(str(product_id), None)
                messages.info(request, "Produit retiré du panier.")
        except (ValueError, TypeError):
            messages.error(request, "Quantité invalide.")
        request.session["cart"] = cart
    return redirect("cart")


def cart_view(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    lines = []
    total = 0.0
    token = _token(request)
    for pid, qty in cart.items():
        try:
            p = api_client.api_get(f"products/{pid}/", token)
        except RequestException:
            continue
        price = float(p.get("price", 0))
        line_total = price * qty
        total += line_total
        lines.append({"product": p, "quantity": qty, "line_total": line_total})
    return render(
        request,
        "shop/cart.html",
        {"lines": lines, "cart_total": total},
    )


def checkout(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect("cart")
    payload_lines = [{"product_id": int(k), "quantity": int(v)} for k, v in cart.items()]
    try:
        api_client.api_post("orders/", _token(request), {"lines": payload_lines})
    except HTTPError as e:
        messages.error(request, str(e))
        return redirect("cart")
    except RequestException:
        messages.error(request, "Impossible de finaliser la commande.")
        return redirect("cart")
    request.session["cart"] = {}
    messages.success(request, "Commande enregistrée. Une notification a été envoyée via la file RabbitMQ.")
    return redirect("orders")


def orders(request):
    redir = _require_auth(request)
    if redir:
        return redir
    try:
        data = api_client.api_get("orders/", _token(request))
    except RequestException:
        messages.error(request, "Historique indisponible.")
        return render(request, "shop/orders.html", {"results": []})
    results = data.get("results", data) if isinstance(data, dict) else data
    if not isinstance(results, list):
        results = []
    return render(request, "shop/orders.html", {"results": results})


# ===== ADMIN VIEWS =====


def admin_dashboard(request):
    """Page d'accueil admin"""
    redir = _require_admin(request)
    if redir:
        return redir
    return render(request, "shop/admin/dashboard.html")


def admin_products_list(request):
    """Lister tous les produits (admin)"""
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        data = api_client.api_get("products/", _token(request))
        products = data.get("results", data) if isinstance(data, dict) else data
        if not isinstance(products, list):
            products = []
    except RequestException:
        messages.error(request, "Impossible de charger les produits.")
        products = []
    
    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = categories_data.get("results", categories_data) if isinstance(categories_data, dict) else categories_data
        if not isinstance(categories, list):
            categories = []
    except RequestException:
        categories = []
    
    return render(request, "shop/admin/products_list.html", {
        "products": products,
        "categories": categories
    })


def admin_product_create(request):
    """Créer un nouveau produit"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = categories_data.get("results", categories_data) if isinstance(categories_data, dict) else categories_data
        if not isinstance(categories, list):
            categories = []
    except RequestException:
        categories = []
    
    if request.method == "POST":
        payload = {
            "name": request.POST.get("name", "").strip(),
            "slug": request.POST.get("slug", "").strip().lower().replace(" ", "-"),
            "summary": request.POST.get("summary", "").strip(),
            "price": float(request.POST.get("price", 0)),
            "stock": int(request.POST.get("stock", 0)),
            "sku": request.POST.get("sku", "").strip().upper(),
            "category": int(request.POST.get("category", 0))
        }
        
        try:
            api_client.api_post("products/", _token(request), payload)
            messages.success(request, "Produit créé avec succès.")
            return redirect("admin_products_list")
        except HTTPError as e:
            messages.error(request, f"Erreur: {str(e)}")
        except RequestException:
            messages.error(request, "Erreur de communication avec le serveur.")
    
    return render(request, "shop/admin/product_form.html", {"categories": categories})


def admin_product_edit(request, product_id: int):
    """Modifier un produit existant"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        product = api_client.api_get(f"products/{product_id}/", _token(request))
    except RequestException:
        messages.error(request, "Produit non trouvé.")
        return redirect("admin_products_list")
    
    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = categories_data.get("results", categories_data) if isinstance(categories_data, dict) else categories_data
        if not isinstance(categories, list):
            categories = []
    except RequestException:
        categories = []
    
    if request.method == "POST":
        payload = {
            "name": request.POST.get("name", product.get("name", "")).strip(),
            "slug": request.POST.get("slug", product.get("slug", "")).strip().lower().replace(" ", "-"),
            "summary": request.POST.get("summary", product.get("summary", "")).strip(),
            "price": float(request.POST.get("price", product.get("price", 0))),
            "stock": int(request.POST.get("stock", product.get("stock", 0))),
            "sku": request.POST.get("sku", product.get("sku", "")).strip().upper(),
            "category": int(request.POST.get("category", product.get("category", 0)))
        }
        
        try:
            api_client.api_patch(f"products/{product_id}/", _token(request), payload)
            messages.success(request, "Produit mis à jour.")
            return redirect("admin_products_list")
        except HTTPError:
            messages.error(request, "Erreur lors de la mise à jour.")
        except RequestException:
            messages.error(request, "Erreur de communication.")
    
    return render(request, "shop/admin/product_form.html", {
        "product": product,
        "categories": categories
    })


def admin_product_delete(request, product_id: int):
    """Supprimer un produit"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        api_client.api_delete(f"products/{product_id}/", _token(request))
        messages.success(request, "Produit supprimé.")
    except RequestException:
        messages.error(request, "Erreur lors de la suppression.")
    
    return redirect("admin_products_list")


def admin_orders_list(request):
    """Lister toutes les commandes (admin)"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        data = api_client.api_get("orders/", _token(request))
        orders_list = data.get("results", data) if isinstance(data, dict) else data
        if not isinstance(orders_list, list):
            orders_list = []
    except RequestException:
        messages.error(request, "Impossible de charger les commandes.")
        orders_list = []
    
    return render(request, "shop/admin/orders_list.html", {"orders": orders_list})


def admin_order_detail(request, order_id: int):
    """Voir les détails d'une commande et modifier le statut"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        order = api_client.api_get(f"orders/{order_id}/", _token(request))
    except RequestException:
        messages.error(request, "Commande non trouvée.")
        return redirect("admin_orders_list")
    
    # Calculer le total par ligne
    if "lines" in order and isinstance(order.get("lines"), list):
        for line in order["lines"]:
            line["line_total"] = float(line.get("unit_price", 0)) * int(line.get("quantity", 1))
    
    if request.method == "POST":
        status = request.POST.get("status", "").strip()
        if status in ["PENDING", "CONFIRMED", "SHIPPED", "CANCELLED"]:
            try:
                api_client.api_patch(f"orders/{order_id}/", _token(request), {"status": status})
                messages.success(request, "Statut mis à jour.")
                return redirect("admin_order_detail", order_id=order_id)
            except RequestException:
                messages.error(request, "Erreur lors de la mise à jour du statut.")
    
    return render(request, "shop/admin/order_detail.html", {"order": order})  