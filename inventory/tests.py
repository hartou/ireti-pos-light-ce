from django.test import TestCase
from django.utils.translation import activate
from inventory.models import product, department, tax, deposit
from decimal import Decimal


class ProductLocalizedNameTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
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
        
        # Create product without localized names
        self.product_no_localized = product.objects.create(
            barcode="987654321",
            name="Mouse",
            sales_price=Decimal("29.99"),
            department=self.department,
            tax_category=self.tax_category,
            deposit_category=self.deposit_category
        )

    def test_get_localized_name_french(self):
        """Test getting French localized name"""
        activate('fr')
        self.assertEqual(self.product.get_localized_name(), "Ordinateur portable")
        
    def test_get_localized_name_spanish(self):
        """Test getting Spanish localized name"""
        activate('es')
        self.assertEqual(self.product.get_localized_name(), "Computadora portátil")
        
    def test_get_localized_name_english_fallback(self):
        """Test fallback to English when no localized name exists"""
        activate('en')
        self.assertEqual(self.product.get_localized_name(), "Laptop")
        
    def test_get_localized_name_fallback_when_empty(self):
        """Test fallback to base name when localized fields are empty"""
        activate('fr')
        self.assertEqual(self.product_no_localized.get_localized_name(), "Mouse")
        
    def test_get_localized_name_explicit_lang(self):
        """Test explicit language parameter"""
        self.assertEqual(self.product.get_localized_name('fr'), "Ordinateur portable")
        self.assertEqual(self.product.get_localized_name('es'), "Computadora portátil")
        self.assertEqual(self.product.get_localized_name('en'), "Laptop")
        
    def test_get_localized_name_with_hyphenated_lang(self):
        """Test language codes with region (e.g., fr-CA)"""
        self.assertEqual(self.product.get_localized_name('fr-CA'), "Ordinateur portable")
        self.assertEqual(self.product.get_localized_name('es-MX'), "Computadora portátil")


class DepartmentLocalizedNameTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.department = department.objects.create(
            department_name="Electronics",
            department_name_fr="Électronique",
            department_name_es="Electrónicos"
        )
        
        self.department_no_localized = department.objects.create(
            department_name="Books"
        )

    def test_get_localized_name_french(self):
        """Test getting French localized department name"""
        activate('fr')
        self.assertEqual(self.department.get_localized_name(), "Électronique")
        
    def test_get_localized_name_spanish(self):
        """Test getting Spanish localized department name"""
        activate('es')
        self.assertEqual(self.department.get_localized_name(), "Electrónicos")
        
    def test_get_localized_name_english_fallback(self):
        """Test fallback to English when no localized name exists"""
        activate('en')
        self.assertEqual(self.department.get_localized_name(), "Electronics")
        
    def test_get_localized_name_fallback_when_empty(self):
        """Test fallback to base name when localized fields are empty"""
        activate('fr')
        self.assertEqual(self.department_no_localized.get_localized_name(), "Books")
        
    def test_get_localized_name_explicit_lang(self):
        """Test explicit language parameter"""
        self.assertEqual(self.department.get_localized_name('fr'), "Électronique")
        self.assertEqual(self.department.get_localized_name('es'), "Electrónicos")
        self.assertEqual(self.department.get_localized_name('en'), "Electronics")
