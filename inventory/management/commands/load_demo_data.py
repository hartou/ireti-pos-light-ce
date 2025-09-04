from django.core.management.base import BaseCommand
from django.db import transaction
from inventory.models import department, tax, deposit, product
from cart.models import displayed_items

DEPTS = [
    ("Grocery", "Everyday items"),
    ("Beverages", "Drinks and refreshments"),
    ("Snacks", "Chips and confectionery"),
]

TAXES = [
    ("Taxable", "Standard sales tax", 8.875),
    ("Non-Tax", "No tax", 0.0),
]

DEPOSITS = [
    ("BottleDeposit", "Applicable to bottles", 0.05),
    ("NoDeposit", "No deposit", 0.0),
]

PRODUCTS = [
    ("0001110001110", "Milk 1L", 3.49, "Grocery", "Taxable", "NoDeposit", 50),
    ("0002220002220", "Bread Loaf", 2.69, "Grocery", "Non-Tax", "NoDeposit", 40),
    ("0003330003330", "Cola 330ml", 1.25, "Beverages", "Taxable", "BottleDeposit", 100),
    ("0004440004440", "Orange Juice 1L", 3.99, "Beverages", "Taxable", "BottleDeposit", 60),
    ("0005550005550", "Potato Chips 150g", 2.49, "Snacks", "Taxable", "NoDeposit", 80),
]

DISPLAYED = [
    ("0001110001110", "Milk 1L", "Popular"),
    ("0003330003330", "Cola 330ml", "Chilled"),
    ("0005550005550", "Chips", "Promo"),
]

class Command(BaseCommand):
    help = "Load demo data for development."

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Only load if no products exist")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts.get("if_empty") and product.objects.exists():
            self.stdout.write(self.style.WARNING("Skipping: products exist."))
            return

        # Create departments
        dept_map = {}
        for name, desc in DEPTS:
            obj, _ = department.objects.get_or_create(department_name=name, defaults={"department_desc": desc})
            dept_map[name] = obj
        
        # Create taxes
        tax_map = {}
        for name, desc, percent in TAXES:
            obj, _ = tax.objects.get_or_create(tax_category=name, defaults={"tax_desc": desc, "tax_percentage": percent})
            tax_map[name] = obj

        # Create deposits
        dep_map = {}
        for name, desc, val in DEPOSITS:
            obj, _ = deposit.objects.get_or_create(deposit_category=name, defaults={"deposit_desc": desc, "deposit_value": val})
            dep_map[name] = obj

        # Create products
        for code, name, price, dept_name, tax_name, dep_name, qty in PRODUCTS:
            product.objects.update_or_create(
                barcode=code,
                defaults={
                    "name": name,
                    "sales_price": price,
                    "qty": qty,
                    "cost_price": round(float(price) * 0.7, 2),
                    "department": dept_map[dept_name],
                    "tax_category": tax_map[tax_name],
                    "deposit_category": dep_map[dep_name],
                },
            )

        # Displayed items
        for code, dname, info in DISPLAYED:
            displayed_items.objects.get_or_create(barcode=code, defaults={
                "display_name": dname,
                "display_info": info,
                "variable_price": False,
            })

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
