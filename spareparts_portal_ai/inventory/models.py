from django.db import models
from django.utils import timezone
class Part(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    def __str__(self): return f"{self.sku} - {self.name}"

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True)
    date = models.DateField(default=timezone.now)
    parts = models.ManyToManyField(Part, through='InvoiceItem')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    def month_key(self):
        return self.date.strftime('%Y-%m')
    def __str__(self): return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    def line_total(self): return self.qty * self.unit_price

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=100, choices=(('Cash','Cash'),('Card','Card'),('UPI','UPI'),('Bank Transfer','Bank Transfer')))
    reference = models.CharField(max_length=200, blank=True)
    def __str__(self): return f"Payment {self.amount} on {self.date} for {self.invoice}"
