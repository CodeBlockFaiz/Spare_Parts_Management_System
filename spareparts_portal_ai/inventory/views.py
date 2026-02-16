from django.shortcuts import render, redirect, get_object_or_404
from .models import Part, Invoice, InvoiceItem, Payment
from .forms import PartForm, InvoiceForm, PaymentForm
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum
from . import ai_utils
import os
from django.conf import settings

def dashboard(request):
    total_invoices = Invoice.objects.count()
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    recent = Invoice.objects.order_by('-date')[:6]
    months = {}
    for inv in Invoice.objects.order_by('-date'):
        months.setdefault(inv.month_key(), []).append(inv)
    return render(request,'inventory/dashboard.html', {'total_invoices':total_invoices,'total_payments':total_payments,'recent':recent,'months':months})

def part_list(request):
    if request.method=='POST':
        form=PartForm(request.POST)
        if form.is_valid():
            form.save(); messages.success(request,'Part added')
            return redirect('inventory:part_list')
    else:
        form=PartForm()
    parts=Part.objects.all()
    return render(request,'inventory/parts.html',{'parts':parts,'form':form})

def part_recommendations(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    recs = ai_utils.get_item_recommendations(part_id, topn=6)
    return render(request,'inventory/part_recommendations.html', {'part':part, 'recs':recs})

@transaction.atomic
def create_invoice(request):
    if request.method=='POST':
        inv_form = InvoiceForm(request.POST)
        if inv_form.is_valid():
            inv = inv_form.save(commit=False)
            inv.total = 0
            inv.save()
            i = 0
            while True:
                p = request.POST.get(f'part_{i}')
                q = request.POST.get(f'qty_{i}')
                if not p: break
                try:
                    part = Part.objects.get(id=int(p))
                    qty = int(q or 1)
                    InvoiceItem.objects.create(invoice=inv, part=part, qty=qty, unit_price=part.price)
                    inv.total += part.price * qty
                    # reduce inventory qty optionally
                    # part.quantity = max(0, part.quantity - qty)
                    # part.save()
                except Exception:
                    pass
                i += 1
            inv.save()
            messages.success(request,'Invoice created')
            return redirect('inventory:invoice_list')
    else:
        inv_form=InvoiceForm()
    parts=Part.objects.all()
    return render(request,'inventory/create_invoice.html',{'form':inv_form,'parts':parts})

def invoice_list(request):
    invoices = Invoice.objects.order_by('-date')[:200]
    from collections import OrderedDict
    months = OrderedDict()
    for inv in invoices:
        k=inv.month_key()
        months.setdefault(k,[]).append(inv)
    return render(request,'inventory/invoices.html',{'months':months})

def payment_list(request):
    if request.method=='POST':
        form=PaymentForm(request.POST)
        if form.is_valid():
            form.save(); messages.success(request,'Payment recorded'); return redirect('inventory:payment_list')
    else:
        form=PaymentForm()
    payments = Payment.objects.order_by('-date')[:200]
    return render(request,'inventory/payments.html',{'payments':payments,'form':form})

def forecast_part_sales(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    # generate forecast plot using ai_utils
    img_path = ai_utils.generate_forecast_plot(part_id)
    img_url = None
    if img_path and os.path.exists(img_path):
        # make relative to MEDIA_URL
        img_url = os.path.relpath(img_path, settings.MEDIA_ROOT).replace('\\','/')
        img_url = settings.MEDIA_URL + img_url
    return render(request, 'inventory/forecast.html', {'part':part, 'img_url':img_url})
