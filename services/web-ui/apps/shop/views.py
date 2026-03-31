from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from requests import HTTPError, RequestException
import json


from . import api_client


def _token(request):
    return request.session.get("access")


def _get_role(request):
    token = _token(request)
    if not token:
        return None
    try:
        import base64
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        return data.get('role')
    except:
        return None


def _is_admin(request):
    """Vérifier si l'utilisateur est admin ou pharmacie pour accéder au dashboard"""
    return _get_role(request) in ('ADMIN', 'PHARMACY')


def _require_admin(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    if _get_role(request) != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect("home")
    return None

def _require_vendor(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    if not _is_admin(request):
        messages.error(request, "Accès réservé aux vendeurs.")
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
                role=request.POST.get("role", "PRO"),
                pharmacy_name=request.POST.get("pharmacy_name"),
                wilaya=request.POST.get("wilaya"),
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
    params = {}
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    min_stock = request.GET.get("min_stock", "").strip()
    selected_category_id = None

    if q:
        params["search"] = q

    # Charge les catégories d'abord pour pouvoir gérer slug et id interchangeables.
    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = categories_data.get("results", categories_data) if isinstance(categories_data, dict) else categories_data
        if not isinstance(categories, list):
            categories = []
    except RequestException:
        categories = []

    if category:
        if category.isdigit():
            params["category"] = category
            selected_category_id = int(category)
        else:
            category_slug = category.lower()
            if category_slug == "test":
                category_slug = "tests"
            params["category__slug"] = category_slug
            for cat in categories:
                if str(cat.get("slug", "")).lower() == category_slug:
                    selected_category_id = cat.get("id")
                    break
                if str(cat.get("name", "")).lower() == category_slug:
                    selected_category_id = cat.get("id")
                    params["category__slug"] = cat.get("slug")
                    break

    try:
        data = api_client.api_get("products/", _token(request), params=params if params else None)
    except RequestException:
        messages.error(request, "Catalogue indisponible.")
        return render(request, "shop/catalog.html", {"results": [], "categories": categories})

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

    return render(request, "shop/catalog.html", {
        "results": results,
        "categories": categories,
        "selected_category_id": selected_category_id,
    })


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
    
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect("cart")


def cart_remove(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
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
    token = _token(request)
    user_wilaya = None
    try:
        user_me = api_client.auth_get("users/me/", token)
        user_wilaya = user_me.get("wilaya")
    except:
        pass

    lines = []
    total = 0.0
    suggestions = []

    for pid, qty in cart.items():
        try:
            p = api_client.api_get(f"products/{pid}/", token)
            price = float(p.get("price", 0))
            line_total = price * qty
            total += line_total
            
            # Suggestion de proximité
            if user_wilaya and p.get("pharmacy_wilaya") != user_wilaya:
                # Chercher le même produit dans la wilaya de l'utilisateur
                alt_params = {"search": p.get("name"), "pharmacy_wilaya": user_wilaya}
                try:
                    alts_data = api_client.api_get("products/", token, params=alt_params)
                    alts_list = alts_data.get("results", alts_data) if isinstance(alts_data, dict) else alts_data
                    if isinstance(alts_list, list):
                        for better_alt in alts_list:
                            if better_alt.get("id") != int(pid) and better_alt.get("name") == p.get("name"):
                                suggestions.append({
                                    "original_id": pid,
                                    "original_name": p.get("name"),
                                    "alt_id": better_alt.get("id"),
                                    "pharmacy_name": better_alt.get("pharmacy_name"),
                                    "wilaya": better_alt.get("pharmacy_wilaya")
                                })
                                break # On en suggère un seul par produit
                except:
                    pass

            lines.append({"product": p, "quantity": qty, "line_total": line_total})
        except RequestException:
            continue
    return render(
        request,
        "shop/cart.html",
        {"lines": lines, "cart_total": total, "suggestions": suggestions, "user_wilaya": user_wilaya},
    )


def checkout(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect("cart")

    token = _token(request)
    
    if request.method == "POST":
        payload = {
            "lines": [{"product_id": int(k), "quantity": int(v)} for k, v in cart.items()],
            "phone": request.POST.get("phone", ""),
            "email": request.POST.get("email", ""),
            "city": request.POST.get("city", ""), # En réalité la Wilaya
            "commune": request.POST.get("commune", ""),
            "detailed_address": request.POST.get("detailed_address", ""),
            "postal_code": request.POST.get("postal_code", ""),
            "delivery_method": request.POST.get("delivery_method", "domicile")
        }
        try:
            api_client.api_post("orders/", token, payload)
            
            # AUTO-SAVE: Mettre à jour la Wilaya de l'utilisateur pour les prochaines suggestions
            new_wilaya = payload["city"]
            if token and new_wilaya:
                try:
                    api_client.auth_patch("users/me/", token, {"wilaya": new_wilaya})
                except: pass

            request.session["cart"] = {}
            messages.success(request, "Commande confirmée ! Votre localisation a été enregistrée pour vos prochaines visites.")
            return redirect("orders")
        except HTTPError as e:
            msg = str(e)
            if e.response is not None:
                try:
                    err_detail = e.response.json()
                    msg = f"Erreur de validation : {err_detail}"
                except: pass
            messages.error(request, msg)
        except RequestException:
            messages.error(request, "Impossible de finaliser la commande.")
        return redirect("cart")

    # Si GET : Préparer le récapitulatif
    cart_items = []
    total = 0.0
    suggestions = []
    for pid, qty in cart.items():
        try:
            p = api_client.api_get(f"products/{pid}/", token)
            p_total = float(p.get("price", 0)) * qty
            total += p_total
            cart_items.append({"product": p, "quantity": qty, "total_price": p_total})
            
            # Suggestion de proximité identique au panier
            if user_wilaya and p.get("pharmacy_wilaya") != user_wilaya:
                alt_params = {"search": p.get("name"), "pharmacy_wilaya": user_wilaya}
                try:
                    alts_data = api_client.api_get("products/", token, params=alt_params)
                    alts_list = alts_data.get("results", alts_data) if isinstance(alts_data, dict) else alts_data
                    if isinstance(alts_list, list):
                        for better_alt in alts_list:
                            if better_alt.get("id") != int(pid) and better_alt.get("name") == p.get("name"):
                                suggestions.append({
                                    "original_id": pid,
                                    "original_name": p.get("name"),
                                    "alt_id": better_alt.get("id"),
                                    "pharmacy_name": better_alt.get("pharmacy_name"),
                                    "wilaya": better_alt.get("pharmacy_wilaya")
                                })
                                break
                except: pass
        except: continue

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "cart_total": total,
        "original_suggestions": suggestions,
        "user_wilaya": user_wilaya
    })


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
    redir = _require_vendor(request)
    if redir:
        return redir
    return render(request, "shop/admin/dashboard.html")


def admin_products_list(request):
    """Lister tous les produits (admin)"""
    redir = _require_vendor(request)
    if redir:
        return redir
    try:
        params = None
        if _get_role(request) == 'PHARMACY':
            params = {"my_store": "true"}
        data = api_client.api_get("products/", _token(request), params=params)
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
    redir = _require_vendor(request)
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
        import uuid
        from django.utils.text import slugify
        
        name = request.POST.get("name", "").strip()
        slug = request.POST.get("slug", "").strip()
        sku = request.POST.get("sku", "").strip()
        
        if not slug and name:
            slug = slugify(name)
        if not sku:
            sku = f"AUTO-{uuid.uuid4().hex[:8].upper()}"
            
        payload = {
            "name": name,
            "slug": slug.lower().replace(" ", "-"),
            "summary": request.POST.get("summary", "").strip(),
            "price": float(request.POST.get("price", 0)),
            "stock": int(request.POST.get("stock", 0)),
            "sku": sku.upper(),
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
    redir = _require_vendor(request)
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
    redir = _require_vendor(request)
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


def admin_statistics(request):
    """Statistiques globales pour l'admin"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        # Fetch stats from catalog-api (if implemented) or calculate from available data
        orders_data = api_client.api_get("orders/", _token(request))
        orders = orders_data.get("results", orders_data) if isinstance(orders_data, dict) else orders_data
        
        products_data = api_client.api_get("products/", _token(request))
        # Handle cases where products_data might be a list or a dict with 'results'
        if isinstance(products_data, dict):
            products_count = products_data.get("count", len(products_data.get("results", [])))
        else:
            products_count = len(products_data)
        
        # Calculate revenue from orders
        total_revenue = 0
        if isinstance(orders, list):
            total_revenue = sum(float(o.get("total", 0)) for o in orders if o.get("status") != "CANCELLED")
            pending_orders = len([o for o in orders if o.get("status") == "PENDING"])
        else:
            orders = []
            pending_orders = 0
            
        stats = {
            "total_orders": len(orders),
            "total_revenue": total_revenue,
            "products_count": products_count,
            "pending_orders": pending_orders,
        }
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des statistiques: {str(e)}")
        stats = {
            "total_orders": 0,
            "total_revenue": 0,
            "products_count": 0,
            "pending_orders": 0,
        }
        
    return render(request, "shop/admin/statistics.html", {"stats": stats})


def admin_users_list(request):
    """Liste des utilisateurs (admin)"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        data = api_client.auth_get("users/", _token(request))
        users = data.get("results", data) if isinstance(data, dict) else data
        if not isinstance(users, list):
            users = []
    except Exception as e:
        messages.error(request, f"Impossible de charger la liste des utilisateurs: {str(e)}")
        users = []
        
    return render(request, "shop/admin/users_list.html", {"users": users})


def admin_user_toggle_active(request, user_id: int):
    """Activer ou désactiver un utilisateur (Approbation globale)"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        user_data = api_client.auth_get(f"users/{user_id}/", _token(request))
        current_status = user_data.get("is_active", True)
        new_status = not current_status
        api_client.auth_patch(f"users/{user_id}/", _token(request), {"is_active": new_status})
        
        if new_status:
            messages.success(request, "Le compte a été approuvé et activé avec succès.")
        else:
            messages.success(request, "Le compte a été désactivé / bloqué.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la modification du statut: {str(e)}")
        
    return redirect("admin_users_list")


def admin_user_delete(request, user_id: int):
    """Supprimer définitivement un utilisateur de la base de données"""
    redir = _require_admin(request)
    if redir:
        return redir
    
    try:
        api_client.auth_delete(f"users/{user_id}/", _token(request))
        messages.success(request, "Le profil a été supprimé avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de l'utilisateur: {str(e)}")
        
    return redirect("admin_users_list")


# ===== PROXY INTERACTION VIEWS =====

@csrf_exempt
def product_like(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method != "POST":
        return json_response({"error": "Method not allowed"}, status=405)
    try:
        data = api_client.api_post(f"products/{product_id}/like/", _token(request))
        return json_response(data)
    except RequestException as e:
        return json_response({"error": str(e)}, status=500)


@csrf_exempt
def product_recommend(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method != "POST":
        return json_response({"error": "Method not allowed"}, status=405)
    try:
        data = api_client.api_post(f"products/{product_id}/recommend/", _token(request))
        return json_response(data)
    except RequestException as e:
        return json_response({"error": str(e)}, status=500)


@csrf_exempt
def product_rate(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            data = api_client.api_post(f"products/{product_id}/rate/", _token(request), body)
            return json_response(data)
        except RequestException as e:
            return json_response({"error": str(e)}, status=500)
    return json_response({"error": "Method not allowed"}, status=405)


@csrf_exempt
def product_unrate(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method != "POST":
        return json_response({"error": "Method not allowed"}, status=405)
    try:
        data = api_client.api_post(f"products/{product_id}/unrate/", _token(request))
        return json_response(data)
    except RequestException as e:
        return json_response({"error": str(e)}, status=500)


def profile_view(request):
    """Gérer le profil de l'utilisateur (nom, wilaya)"""
    redir = _require_auth(request)
    if redir:
        return redir
    
    token = _token(request)
    if request.method == "POST":
        payload = {
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "wilaya": request.POST.get("wilaya", "")
        }
        if _get_role(request) == 'PHARMACY':
            payload["pharmacy_name"] = request.POST.get("pharmacy_name", "")

        try:
            api_client.auth_patch("users/me/", token, payload)
            messages.success(request, "Profil mis à jour avec succès.")
        except RequestException as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")

    try:
        user_data = api_client.auth_get("users/me/", token)
    except RequestException:
        messages.error(request, "Impossible de charger le profil.")
        return redirect("home")

    return render(request, "shop/profile.html", {"user_profile": user_data})


def profile_view(request):
    """Gérer le profil de l'utilisateur (nom, wilaya)"""
    redir = _require_auth(request)
    if redir:
        return redir
    
    token = _token(request)
    if request.method == "POST":
        payload = {
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "wilaya": request.POST.get("wilaya", "")
        }
        if _get_role(request) == 'PHARMACY':
            payload["pharmacy_name"] = request.POST.get("pharmacy_name", "")

        try:
            api_client.auth_patch("users/me/", token, payload)
            messages.success(request, "Profil mis à jour avec succès.")
        except RequestException as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")

    try:
        user_data = api_client.auth_get("users/me/", token)
    except RequestException:
        messages.error(request, "Impossible de charger le profil.")
        return redirect("home")

    return render(request, "shop/profile.html", {"user_profile": user_data})


def json_response(data, status=200):
    from django.http import JsonResponse
    return JsonResponse(data, status=status)