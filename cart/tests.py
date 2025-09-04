from django.test import TestCase, RequestFactory
from django.utils.translation import activate
from cart.models import Cart
from inventory.models import product, department, tax, deposit
from decimal import Decimal


class CartLocalizedNameTestCase(TestCase):
    def setUp(self):
        """Set up test data and mock request"""
        self.factory = RequestFactory()
        
        # Create tax and deposit categories
        self.tax_category = tax.objects.create(
            tax_category="Standard Tax",
            tax_percentage=Decimal("13.000")
        )
        self.deposit_category = deposit.objects.create(
            deposit_category="No Deposit",
            deposit_value=Decimal("0.00")
        )
        
        # Create department
        self.department = department.objects.create(
            department_name="Electronics",
            department_name_fr="Électronique",
            department_name_es="Electrónicos"
        )
        
        # Create product with localized names
        self.product = product.objects.create(
            barcode="123456789",
            name="Laptop",
            name_fr="Ordinateur portable",
            name_es="Computadora portátil",
            sales_price=Decimal("999.99"),
            department=self.department,
            tax_category=self.tax_category,
            deposit_category=self.deposit_category
        )

    def _create_cart_request(self):
        """Create a mock request with session"""
        request = self.factory.get('/')
        request.session = {}
        return request

    def test_cart_add_uses_localized_name_french(self):
        """Test that Cart.add uses French localized name"""
        activate('fr')
        request = self._create_cart_request()
        cart = Cart(request)
        
        cart.add(self.product, 1)
        
        # Check that the cart item uses the French name
        cart_item = cart.cart[self.product.barcode]
        self.assertEqual(cart_item['name'], "Ordinateur portable")

    def test_cart_add_uses_localized_name_spanish(self):
        """Test that Cart.add uses Spanish localized name"""
        activate('es')
        request = self._create_cart_request()
        cart = Cart(request)
        
        cart.add(self.product, 1)
        
        # Check that the cart item uses the Spanish name
        cart_item = cart.cart[self.product.barcode]
        self.assertEqual(cart_item['name'], "Computadora portátil")

    def test_cart_add_uses_english_fallback(self):
        """Test that Cart.add falls back to English name"""
        activate('en')
        request = self._create_cart_request()
        cart = Cart(request)
        
        cart.add(self.product, 1)
        
        # Check that the cart item uses the English name
        cart_item = cart.cart[self.product.barcode]
        self.assertEqual(cart_item['name'], "Laptop")

    def test_cart_add_product_without_localized_names(self):
        """Test Cart.add with product that has no localized names"""
        # Create product without localized names
        product_no_localized = product.objects.create(
            barcode="987654321",
            name="Mouse",
            sales_price=Decimal("29.99"),
            department=self.department,
            tax_category=self.tax_category,
            deposit_category=self.deposit_category
        )
        
        activate('fr')
        request = self._create_cart_request()
        cart = Cart(request)
        
        cart.add(product_no_localized, 1)
        
        # Should fall back to base name
        cart_item = cart.cart[product_no_localized.barcode]
        self.assertEqual(cart_item['name'], "Mouse")
