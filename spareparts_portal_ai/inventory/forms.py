from django import forms
from .models import Part, Invoice, InvoiceItem, Payment
class PartForm(forms.ModelForm):
    class Meta: model = Part; fields = '__all__'
class InvoiceForm(forms.ModelForm):
    class Meta: model = Invoice; fields = ['invoice_number','date','notes']
class PaymentForm(forms.ModelForm):
    class Meta: model = Payment; fields = ['invoice','date','amount','method','reference']
