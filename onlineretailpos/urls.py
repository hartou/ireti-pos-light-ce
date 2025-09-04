"""onlineretailpos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.static import serve
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from transaction import views as transaction_views
from cart import views as cart_views
from . import views as views
from . import admin_views  # Import integrated admin views
from django.contrib.auth import views as auth_views
from inventory import views as inventory_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


urlpatterns = [
        #Admin URL
        path('staff_portal/', admin.site.urls ),
    # Friendly alias: redirect /admin to /staff_portal/
    re_path(r'^admin/?$', RedirectView.as_view(url='/staff_portal/', permanent=False)),
    # i18n (language switching)
    path('i18n/', include('django.conf.urls.i18n')),

        # User URLs
        path("user/login/", views.user_login, name="user_login"),
        path("user/logout/", views.user_logout,name="user_logout"),
        path('user/change-password/', auth_views.PasswordChangeView.as_view(
            template_name='registration/change_password.html',
                success_url = '/' ),name='change_password'),


        # Dashboard URLs, Sales Dashboard is set Up as home Currently
        path('',views.dashboard_sales, name="home"),
        path('dashboard_sales/',views.dashboard_sales, name="dashboard_sales"),
        path('dashboard_department/',views.dashboard_department, name="dashboard_department"),
        path('dashboard_products/',views.dashboard_products, name="dashboard_products"),
        path("department_report/<start_date>/<end_date>/",views.report_regular),

        # Inventory add
        path('inventory/', inventory_views.inventoryAdd , name="inventory_add"),

        # Register URLs
        path('register/', views.register, name="register"),
        path('register/ProductNotFound/', views.register, name="ProductNotFound"),
        path('register/cart_clear/', cart_views.cart_clear, name='cart_clear'),
        path('register/returns_transaction/', transaction_views.returnsTransaction, name='returns_transaction'),
        path('register/suspend_transaction/', transaction_views.suspendTransaction, name='suspend_transaction'),
        path('register/recall_transaction/', transaction_views.recallTransaction, name='recall_transaction'),
        path('register/recall_transaction/<recallTransNo>/', transaction_views.recallTransaction, name='recall_transaction_no'),
        path('register/product_lookup/', inventory_views.product_lookup, name='product_lookup_default'),
        path('register/<manual_department>/<amount>/', inventory_views.manualAmount, name='manual_amount'),

        # Cart URLs
        path('cart/add/<id>/<qty>/', cart_views.cart_add, name='cart_add'),
        path('cart/item_clear/<id>/', cart_views.item_clear, name='item_clear'),
        # path('cart/item_increment/<id>/',cart_views.item_increment, name='item_increment'),
        # path('cart/item_decrement/<id>/',cart_views.item_decrement, name='item_decrement'),

        #Transactions Related URLs
        path('endTransaction/<type>/<value>/', transaction_views.endTransaction , name='endTransaction'),
        path('endTransaction/<transNo>/', transaction_views.endTransactionReceipt , name='endTransactionReceipt'),
        path('transaction/', transaction_views.transactionView , name='transactionView'),
        path('transaction/<transNo>/', transaction_views.transactionView , name='transactionView_id'),
        path('transaction_receipt/<transNo>/', transaction_views.transactionReceipt , name='transactionReceipt'),
        path('transaction_receipt/<transNo>/print/', transaction_views.transactionPrintReceipt , name='transactionPrintReceipt'),
        
        # Stripe Payment URLs
        path('start-stripe-payment/', transaction_views.start_stripe_payment, name='start_stripe_payment'),
        path('complete-stripe-payment/<transNo>/', transaction_views.complete_stripe_payment, name='complete_stripe_payment'),

        # Customer Screen URLs
        path("retail_display/",views.retail_display,name="retail_display"),
        path("retail_display/<values>/",views.retail_display),

        # Payment URLs
        path("payments/", include('payments.urls')),

        # Integrated Administration URLs (replace external admin)
        path('administration/', admin_views.admin_dashboard, name='admin_dashboard'),
        path('admin_products/', admin_views.admin_products, name='admin_products'),
        path('admin_inventory/', admin_views.admin_inventory, name='admin_inventory'),
        path('admin_users/', admin_views.admin_users, name='admin_users'),
        path('admin_transactions/', admin_views.admin_transactions, name='admin_transactions'),
        path('admin_system/', admin_views.admin_system, name='admin_system'),

        # Other URLs
        path("offline/", views.offline_page, name="offline_page"),
        re_path(r"^favicon.ico/*",RedirectView.as_view(url=staticfiles_storage.url("/img/cash-register-g87e120a86_640.png"))),

        # Static Files Serve WHEN Debug is False in DEV ENV
        re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    ] 
