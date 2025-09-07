"""
Integrated Admin Views
Replaces external Django admin with integrated POS system administration
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm
from inventory.models import product, department  # Fixed: lowercase model names
from transaction.models import transaction  # Use existing transaction model
import json
from datetime import datetime, timedelta


@staff_member_required
def admin_dashboard(request):
    """Integrated admin dashboard within main UI"""
    # Get system statistics
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Product statistics
    total_products = product.objects.count()
    active_products = product.objects.count()  # Note: No 'active' field in model
    
    # Inventory statistics (using product qty field)
    total_inventory = product.objects.count()
    low_stock_items = product.objects.filter(qty__lt=10).count()
    
    # Transaction statistics
    total_transactions = transaction.objects.count()
    week_transactions = transaction.objects.filter(date_time__gte=week_ago).count()
    month_revenue = transaction.objects.filter(
        date_time__gte=month_ago
    ).aggregate(total=Sum('total_sale'))['total'] or 0
    
    # User statistics
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Recent activity
    recent_transactions = transaction.objects.order_by('-date_time')[:5]
    recent_products = product.objects.order_by('-id')[:5]
    
    context = {
        'page_title': _('Data Administration Dashboard'),
        'page_icon': 'fas fa-tachometer-alt',
        'stats': {
            'products': {
                'total': total_products,
                'active': active_products,
                'inactive': 0  # No active field in model
            },
            'inventory': {
                'total': total_inventory,
                'low_stock': low_stock_items,
                'ok_stock': total_inventory - low_stock_items
            },
            'transactions': {
                'total': total_transactions,
                'week': week_transactions,
                'month_revenue': month_revenue
            },
            'users': {
                'total': total_users,
                'staff': staff_users,
                'regular': total_users - staff_users
            }
        },
        'recent_activity': {
            'transactions': recent_transactions,
            'products': recent_products
        },
        'breadcrumbs': [
            {'url': '/', 'label': _('Home'), 'icon': 'fas fa-home'},
            {'url': '/administration/', 'label': _('Administration'), 'icon': 'fas fa-laptop-house', 'active': True}
        ]
    }
    return render(request, 'admin/dashboard.html', context)


@staff_member_required  
def admin_products(request):
    """Product management within integrated UI"""
    products_list = product.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(barcode__icontains=search_query) |
            Q(product_desc__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products_list, 25)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Statistics
    total_products = product.objects.count()
    active_products = product.objects.count()  # All products considered active
    
    context = {
        'page_title': _('Product Management'),
        'page_icon': 'fas fa-box',
        'products': products,
        'search_query': search_query,
        'stats': {
            'total': total_products,
            'active': active_products,
            'inactive': 0  # No active field in current model
        },
        'breadcrumbs': [
            {'url': '/', 'label': _('Home'), 'icon': 'fas fa-home'},
            {'url': '/administration/', 'label': _('Administration'), 'icon': 'fas fa-laptop-house'},
            {'url': '/admin_products/', 'label': _('Products'), 'icon': 'fas fa-box', 'active': True}
        ]
    }
    return render(request, 'admin/products.html', context)


@staff_member_required
def admin_inventory(request):
    """Inventory management within integrated UI"""
    # Use product model since there's no separate Inventory model
    inventory_list = product.objects.all().order_by('name')
    
    # Filter by stock level (using qty field from product)
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        inventory_list = inventory_list.filter(qty__lt=10)
    elif stock_filter == 'out':
        inventory_list = inventory_list.filter(qty=0)
    elif stock_filter == 'good':
        inventory_list = inventory_list.filter(qty__gte=10)
    
    # Pagination
    paginator = Paginator(inventory_list, 25)
    page_number = request.GET.get('page')
    inventory = paginator.get_page(page_number)
    
    # Statistics
    total_items = product.objects.count()
    low_stock = product.objects.filter(qty__lt=10).count()
    out_of_stock = product.objects.filter(qty=0).count()
    
    context = {
        'page_title': _('Inventory Management'),
        'page_icon': 'fas fa-warehouse',
        'inventory': inventory,
        'stock_filter': stock_filter,
        'stats': {
            'total': total_items,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'good_stock': total_items - low_stock - out_of_stock
        },
        'breadcrumbs': [
            {'url': '/', 'label': _('Home'), 'icon': 'fas fa-home'},
            {'url': '/administration/', 'label': _('Administration'), 'icon': 'fas fa-laptop-house'},
            {'url': '/admin_inventory/', 'label': _('Inventory'), 'icon': 'fas fa-warehouse', 'active': True}
        ]
    }
    return render(request, 'admin/inventory.html', context)


@staff_member_required
def admin_users(request):
    """User management within integrated UI"""
    users_list = User.objects.all().order_by('username')
    
    # Filter by user type
    user_filter = request.GET.get('type', '')
    if user_filter == 'staff':
        users_list = users_list.filter(is_staff=True)
    elif user_filter == 'active':
        users_list = users_list.filter(is_active=True)
    elif user_filter == 'inactive':
        users_list = users_list.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users_list, 25)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    # Statistics
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    context = {
        'page_title': _('User Management'),
        'page_icon': 'fas fa-users',
        'users': users,
        'user_filter': user_filter,
        'stats': {
            'total': total_users,
            'staff': staff_users,
            'active': active_users,
            'inactive': total_users - active_users
        },
        'breadcrumbs': [
            {'url': '/', 'label': _('Home'), 'icon': 'fas fa-home'},
            {'url': '/administration/', 'label': _('Administration'), 'icon': 'fas fa-laptop-house'},
            {'url': '/admin_users/', 'label': _('Users'), 'icon': 'fas fa-users', 'active': True}
        ]
    }
    return render(request, 'admin/users.html', context)


@staff_member_required
def admin_transactions(request):
    """Transaction management within integrated UI"""
    transactions_list = transaction.objects.all().order_by('-date_time')
    
    # Filter by transaction type (if field exists)
    trans_filter = request.GET.get('type', '')
    if trans_filter:
        # Note: Check if transactionType field exists in transaction model
        pass  # Skip filtering for now
    
    # Filter by date range
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        today = datetime.now().date()
        transactions_list = transactions_list.filter(date_time__date=today)
    elif date_filter == 'week':
        week_ago = datetime.now().date() - timedelta(days=7)
        transactions_list = transactions_list.filter(date_time__date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = datetime.now().date() - timedelta(days=30)
        transactions_list = transactions_list.filter(date_time__date__gte=month_ago)
    
    # Pagination
    paginator = Paginator(transactions_list, 25)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
    # Statistics
    total_transactions = transaction.objects.count()
    today_transactions = transaction.objects.filter(
        date_time__date=datetime.now().date()
    ).count()
    total_revenue = transaction.objects.aggregate(
        total=Sum('total_sale')
    )['total'] or 0
    
    context = {
        'page_title': _('Transaction Management'),
        'page_icon': 'fas fa-receipt',
        'transactions': transactions,
        'trans_filter': trans_filter,
        'date_filter': date_filter,
        'stats': {
            'total': total_transactions,
            'today': today_transactions,
            'revenue': total_revenue
        },
        'breadcrumbs': [
            {'url': '/', 'label': _('Home'), 'icon': 'fas fa-home'},
            {'url': '/administration/', 'label': _('Administration'), 'icon': 'fas fa-laptop-house'},
            {'url': '/admin_transactions/', 'label': _('Transactions'), 'icon': 'fas fa-receipt', 'active': True}
        ]
    }
    return render(request, 'admin/transactions.html', context)


@staff_member_required
def admin_system(request):
    """System settings and maintenance within integrated UI"""
    import os
    import django
    from django.conf import settings
    
    # System information
    system_info = {
        'django_version': django.get_version(),
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'debug_mode': settings.DEBUG,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'static_url': settings.STATIC_URL,
        'media_url': settings.MEDIA_URL,
        'installed_apps_count': len(settings.INSTALLED_APPS)
    }
    
    # Database statistics
    db_stats = {
        'products': product.objects.count(),
        'inventory': product.objects.count(),  # Same as products since no separate inventory
        'transactions': transaction.objects.count(),
        'users': User.objects.count()
    }
    
    # Log file information (if available)
    log_info = []
    try:
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if os.path.exists(log_dir):
            for log_file in os.listdir(log_dir):
                if log_file.endswith('.log'):
                    file_path = os.path.join(log_dir, log_file)
                    file_size = os.path.getsize(file_path)
                    modified_time = os.path.getmtime(file_path)
                    log_info.append({
                        'name': log_file,
                        'size': f"{file_size / 1024:.1f} KB",
                        'modified': datetime.fromtimestamp(modified_time)
                    })
    except Exception:
        pass
    
    context = {
        'page_title': _('System Settings'),
        'page_icon': 'fas fa-server',
        'system_info': system_info,
        'db_stats': db_stats,
        'log_info': log_info,
        'breadcrumbs': [
            {'url': '/', 'label': _('Home'), 'icon': 'fas fa-home'},
            {'url': '/administration/', 'label': _('Administration'), 'icon': 'fas fa-laptop-house'},
            {'url': '/admin_system/', 'label': _('System'), 'icon': 'fas fa-server', 'active': True}
        ]
    }
    return render(request, 'admin/system.html', context)
