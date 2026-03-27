from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.signup_view, name="signup"),
    path("connexion/", views.login_view, name="login"),
    path("deconnexion/", views.logout_view, name="logout"),
    path("catalogue/", views.catalog, name="catalog"),
    path("panier/", views.cart_view, name="cart"),
    path("panier/ajouter/<int:product_id>/", views.cart_add, name="cart_add"),
    path("panier/modifier/<int:product_id>/", views.cart_update, name="cart_update"),
    path("panier/retirer/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("commander/", views.checkout, name="checkout"),
    path("commandes/", views.orders, name="orders"),
    
    # Admin routes
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/produits/", views.admin_products_list, name="admin_products_list"),
    path("admin/produits/creer/", views.admin_product_create, name="admin_product_create"),
    path("admin/produits/<int:product_id>/modifier/", views.admin_product_edit, name="admin_product_edit"),
    path("admin/produits/<int:product_id>/supprimer/", views.admin_product_delete, name="admin_product_delete"),
    path("admin/commandes/", views.admin_orders_list, name="admin_orders_list"),
    path("admin/commandes/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin/statistiques/", views.admin_statistics, name="admin_statistics"),
    path("admin/utilisateurs/", views.admin_users_list, name="admin_users_list"),
    path("lang/", views.set_language, name="set_language"),
    
    # Interactions
    path("api/products/<int:product_id>/like/", views.product_like, name="product_like"),
    path("api/products/<int:product_id>/recommend/", views.product_recommend, name="product_recommend"),
    path("api/products/<int:product_id>/rate/", views.product_rate, name="product_rate"),
    path("api/products/<int:product_id>/unrate/", views.product_unrate, name="product_unrate"),
]
