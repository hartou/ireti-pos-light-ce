"""
API Views for Ireti POS Light CE
Provides REST API endpoints with automatic documentation generation.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from cart.models import Cart
from inventory.models import product
from transaction.models import transaction


@extend_schema_view(
    get=extend_schema(
        operation_id='get_cart_contents',
        summary='Get Cart Contents',
        description='Retrieve current shopping cart contents including items, quantities, and total.',
        tags=['Cart'],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'price': {'type': 'number', 'format': 'decimal'},
                                'quantity': {'type': 'integer'},
                                'total': {'type': 'number', 'format': 'decimal'},
                            }
                        }
                    },
                    'total_items': {'type': 'integer'},
                    'total_amount': {'type': 'number', 'format': 'decimal'},
                }
            }
        }
    )
)
class CartAPIView(APIView):
    """
    Cart management API endpoint.
    
    Provides access to shopping cart contents and basic cart operations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current cart contents."""
        cart = Cart(request)
        
        cart_items = []
        total_amount = 0
        
        for item in cart:
            item_total = item['price'] * item['quantity']
            cart_items.append({
                'id': item['product_id'],
                'name': item['name'],
                'price': float(item['price']),
                'quantity': item['quantity'],
                'total': float(item_total)
            })
            total_amount += item_total
        
        return Response({
            'items': cart_items,
            'total_items': len(cart),
            'total_amount': float(total_amount)
        })


@extend_schema_view(
    get=extend_schema(
        operation_id='search_products',
        summary='Search Products',
        description='Search for products by name, barcode, or department.',
        tags=['Inventory'],
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query (product name, barcode, or department)',
                required=False,
                examples=[
                    OpenApiExample('Search by name', value='coffee'),
                    OpenApiExample('Search by barcode', value='1234567890'),
                ]
            ),
            OpenApiParameter(
                name='limit',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return',
                required=False,
                default=20
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'products': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'barcode': {'type': 'string'},
                                'price': {'type': 'number', 'format': 'decimal'},
                                'department': {'type': 'string'},
                                'quantity': {'type': 'integer'},
                            }
                        }
                    },
                    'count': {'type': 'integer'},
                }
            }
        }
    )
)
class ProductSearchAPIView(APIView):
    """
    Product search API endpoint.
    
    Allows searching for products by various criteria.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Search for products."""
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 20))
        
        products = product.objects.all()
        
        if query:
            products = products.filter(
                name__icontains=query
            ) | products.filter(
                barcode__icontains=query
            ) | products.filter(
                department__icontains=query
            )
        
        products = products[:limit]
        
        product_list = []
        for prod in products:
            product_list.append({
                'id': prod.id,
                'name': prod.name,
                'barcode': prod.barcode,
                'price': float(prod.price),
                'department': prod.department,
                'quantity': prod.qty,
            })
        
        return Response({
            'products': product_list,
            'count': len(product_list)
        })


@extend_schema_view(
    get=extend_schema(
        operation_id='get_dashboard_stats',
        summary='Get Dashboard Statistics',
        description='Retrieve dashboard statistics including sales, transactions, and inventory data.',
        tags=['Dashboard'],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'sales': {
                        'type': 'object',
                        'properties': {
                            'today': {'type': 'number', 'format': 'decimal'},
                            'week': {'type': 'number', 'format': 'decimal'},
                            'month': {'type': 'number', 'format': 'decimal'},
                        }
                    },
                    'transactions': {
                        'type': 'object',
                        'properties': {
                            'today': {'type': 'integer'},
                            'week': {'type': 'integer'},
                            'month': {'type': 'integer'},
                        }
                    },
                    'inventory': {
                        'type': 'object',
                        'properties': {
                            'total_products': {'type': 'integer'},
                            'low_stock_items': {'type': 'integer'},
                        }
                    }
                }
            }
        }
    )
)
class DashboardStatsAPIView(APIView):
    """
    Dashboard statistics API endpoint.
    
    Provides key metrics and statistics for the POS dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get dashboard statistics."""
        from datetime import datetime, timedelta
        from django.db.models import Sum, Count
        
        now = datetime.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Sales statistics
        sales_today = transaction.objects.filter(
            timestamp__date=today
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        
        sales_week = transaction.objects.filter(
            timestamp__date__gte=week_ago
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        
        sales_month = transaction.objects.filter(
            timestamp__date__gte=month_ago
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        
        # Transaction counts
        trans_today = transaction.objects.filter(timestamp__date=today).count()
        trans_week = transaction.objects.filter(timestamp__date__gte=week_ago).count()
        trans_month = transaction.objects.filter(timestamp__date__gte=month_ago).count()
        
        # Inventory statistics
        total_products = product.objects.count()
        low_stock_items = product.objects.filter(qty__lt=10).count()
        
        return Response({
            'sales': {
                'today': float(sales_today),
                'week': float(sales_week),
                'month': float(sales_month),
            },
            'transactions': {
                'today': trans_today,
                'week': trans_week,
                'month': trans_month,
            },
            'inventory': {
                'total_products': total_products,
                'low_stock_items': low_stock_items,
            }
        })


@extend_schema_view(
    post=extend_schema(
        operation_id='api_login',
        summary='API Authentication',
        description='Authenticate user and create session for API access.',
        tags=['Authentication'],
        request={
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
            },
            'required': ['username', 'password']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'email': {'type': 'string'},
                            'is_staff': {'type': 'boolean'},
                        }
                    }
                }
            },
            401: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                }
            }
        },
        examples=[
            OpenApiExample(
                'Login Example',
                value={
                    'username': 'admin',
                    'password': 'admin123'
                },
                request_only=True,
            ),
        ],
    )
)
@method_decorator(csrf_exempt, name='dispatch')
class AuthAPIView(APIView):
    """
    Authentication API endpoint.
    
    Provides login functionality for API access.
    """
    permission_classes = []  # No authentication required for login

    def post(self, request):
        """Authenticate user."""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)