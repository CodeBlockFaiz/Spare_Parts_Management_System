from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.models import Part, Invoice, InvoiceItem, Payment
from decimal import Decimal
import random
import datetime

class Command(BaseCommand):
    help = "Safely seed sample Parts, Invoices, and Payments into the database."

    def handle(self, *args, **kwargs):
        self.stdout.write("🚗 Starting safe database seeding...")

        # --- PARTS SEEDING ---
        parts_list = [
            ("Brake Pad", "High quality ceramic brake pad", 1200.50),
            ("Oil Filter", "Engine oil filter for all models", 450.00),
            ("Air Filter", "Performance air filter", 800.00),
            ("Headlight Bulb", "LED headlight bulb set", 1500.00),
            ("Spark Plug", "Copper spark plug pack of 4", 950.00),
            ("Radiator", "Car radiator assembly", 5400.00),
            ("Alternator", "12V alternator", 7800.00),
            ("Fuel Pump", "Electric fuel pump", 3600.00),
            ("Battery", "12V 60Ah battery", 5400.00),
            ("Clutch Plate", "Heavy duty clutch plate", 4200.00),
        ]

        for idx, (name, desc, price) in enumerate(parts_list, start=1):
            sku = f"SKU{idx:04d}"
            Part.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "description": desc,
                    "price": Decimal(price),
                    "quantity": random.randint(10, 100),
                },
            )
        self.stdout.write("✅ Parts seeded successfully (no duplicates).")

        # --- INVOICES SEEDING ---
        invoices = []
        for i in range(1, 21):
            invoice_number = f"INV{1000 + i}"
            invoice, created = Invoice.objects.get_or_create(
                invoice_number=invoice_number,
                defaults={
                    "date": timezone.now().date() - datetime.timedelta(days=random.randint(0, 180)),
                    "total": 0,
                    "notes": f"Sample invoice {i}",
                },
            )
            invoices.append(invoice)
        self.stdout.write("✅ 20 invoices created with unique invoice numbers.")

        # --- INVOICE ITEMS SEEDING ---
        parts = list(Part.objects.all())
        for invoice in invoices:
            item_count = random.randint(1, 5)
            total = Decimal(0)
            for _ in range(item_count):
                part = random.choice(parts)
                qty = random.randint(1, 5)
                unit_price = part.price
                InvoiceItem.objects.create(
                    invoice=invoice,
                    part=part,
                    qty=qty,
                    unit_price=unit_price,
                )
                total += qty * unit_price
            invoice.total = total
            invoice.save()
        self.stdout.write("✅ Invoice items added and totals updated.")

        # --- PAYMENTS SEEDING ---
        for invoice in invoices:
            if random.choice([True, False]):  # half of invoices paid
                Payment.objects.create(
                    invoice=invoice,
                    date=invoice.date + datetime.timedelta(days=random.randint(0, 5)),
                    amount=invoice.total,
                    method=random.choice(["Cash", "Card", "UPI", "Bank Transfer"]),
                    reference=f"TXN{random.randint(100000,999999)}",
                )
        self.stdout.write("✅ Payments created successfully.")

        self.stdout.write(self.style.SUCCESS("🎉 Sample data seeding complete!"))
