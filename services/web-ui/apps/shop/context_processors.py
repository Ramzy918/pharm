from django.conf import settings

from .views import _is_admin


def public_endpoints(request):
    lang = request.session.get("lang", "fr")
    texts = {
        "fr": {
            "brand": "MarketPharm",
            "tagline": "Pharmacie & parapharmacie pour professionnels",
            "catalog": "Catalogue",
            "cart": "Panier",
            "orders": "Mes commandes",
            "login": "Connexion",
            "logout": "Déconnexion",
            "search_placeholder": "Recherche produit...",
            "min_stock": "Stock min",
            "all_categories": "Toutes catégories",
            "filter": "Filtrer",
            "empty_cart": "Panier vide",
            "checkout": "Commander",
            "no_orders": "Aucune commande pour le moment.",
        },
        "ar": {
            "brand": "ماركت فارم",
            "tagline": "صيدلية وبارافارما للمحترفين",
            "catalog": "الكتالوج",
            "cart": "سلة التسوق",
            "orders": "طلباتي",
            "login": "تسجيل الدخول",
            "logout": "تسجيل الخروج",
            "search_placeholder": "بحث عن منتج...",
            "min_stock": "الحد الأدنى للمخزون",
            "all_categories": "جميع الفئات",
            "filter": "تصفية",
            "empty_cart": "السلة فارغة",
            "checkout": "إنهاء الطلب",
            "no_orders": "لا توجد طلبات حتى الآن.",
        },
    }
    active_text = texts.get(lang, texts["fr"])
    return {
        "PUBLIC_AUTH_URL": settings.PUBLIC_AUTH_URL,
        "PUBLIC_API_URL": settings.PUBLIC_API_URL,
        "LANG": lang,
         "DIR": "rtl" if lang == "ar" else "ltr",
        "T": active_text,
        "user_is_admin": _is_admin(request),
    }
