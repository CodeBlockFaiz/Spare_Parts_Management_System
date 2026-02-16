from django.contrib import admin
from .models import Part, Invoice, InvoiceItem, Payment
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem; extra = 1
class PaymentInline(admin.TabularInline):
    model = Payment; extra = 0
@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('sku','name','price','quantity')
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number','date','total')
    inlines = [InvoiceItemInline, PaymentInline]
