# Utilities for recommendation and forecasting
import os, pandas as pd, numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import Part, InvoiceItem, Invoice
from django.conf import settings
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO
import joblib

# Recommendation: item-item based on co-occurrence matrix from InvoiceItem
def build_item_matrix():
    # rows: invoices, cols: parts; value: qty (or 1)
    invoices = Invoice.objects.all().order_by('id')
    parts = Part.objects.all().order_by('id')
    if not invoices.exists() or not parts.exists():
        return None, None, None
    inv_ids = [i.id for i in invoices]
    part_ids = [p.id for p in parts]
    data = []
    for inv in invoices:
        row = { 'invoice_id': inv.id }
        items = InvoiceItem.objects.filter(invoice=inv)
        for it in items:
            row[str(it.part.id)] = it.qty
        data.append(row)
    df = pd.DataFrame(data).fillna(0).set_index('invoice_id')
    # ensure all parts columns exist
    for pid in part_ids:
        if str(pid) not in df.columns:
            df[str(pid)] = 0
    df = df[[str(pid) for pid in part_ids]]
    return df, part_ids, parts

def get_item_recommendations(part_id, topn=6):
    df, part_ids, parts = build_item_matrix()
    if df is None:
        return []
    # item vectors: transpose df -> items x invoices
    item_matrix = df.T.values  # shape (n_items, n_invoices)
    if item_matrix.shape[0] == 0:
        return []
    # cosine similarity between items
    sim = cosine_similarity(item_matrix)
    # map part id to index
    id_to_index = {pid: idx for idx, pid in enumerate(part_ids)}
    if part_id not in id_to_index:
        return []
    idx = id_to_index[part_id]
    scores = list(enumerate(sim[idx]))
    # sort by score desc, skip self (score==1)
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    recs = []
    for i, score in scores:
        pid = part_ids[i]
        if pid == part_id: continue
        try:
            p = Part.objects.get(id=pid)
            recs.append({'part':p, 'score':float(score)})
        except Part.DoesNotExist:
            continue
        if len(recs) >= topn-1:
            break
    return recs

# Forecasting: aggregate monthly sales quantity for a part and run ARIMA
def aggregate_monthly_sales(part_id):
    items = InvoiceItem.objects.filter(part_id=part_id).select_related('invoice').order_by('invoice__date')
    if not items.exists():
        return None
    records = []
    for it in items:
        records.append({'date': it.invoice.date, 'qty': it.qty})
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').resample('M').sum().fillna(0)
    df.index = pd.DatetimeIndex(df.index).to_period('M').to_timestamp()
    return df['qty']

def generate_forecast_plot(part_id, periods=3):
    series = aggregate_monthly_sales(part_id)
    part = Part.objects.filter(id=part_id).first()
    if series is None or len(series) < 3:
        # Not enough data to forecast; create simple plot of existing series
        fig, ax = plt.subplots(figsize=(8,4))
        if series is None:
            ax.text(0.5,0.5,'No sales data available', ha='center', va='center')
        else:
            series.plot(ax=ax, marker='o')
            ax.set_title(f'Sales for {part.name}')
            ax.set_ylabel('Quantity')
        img_dir = os.path.join(settings.MEDIA_ROOT, 'ai')
        os.makedirs(img_dir, exist_ok=True)
        path = os.path.join(img_dir, f'forecast_{part_id}.png')
        fig.tight_layout(); fig.savefig(path); plt.close(fig)
        return path
    # Fit simple ARIMA(1,0,0) or auto if possible
    try:
        model = ARIMA(series, order=(1,0,0))
        model_fit = model.fit()
        forecast = model_fit.get_forecast(steps=periods)
        fc_series = forecast.predicted_mean
        conf = forecast.conf_int()
    except Exception as e:
        # fallback: use last value repeated
        fc_series = pd.Series([series.iloc[-1]]*periods, index=pd.date_range(series.index[-1]+pd.offsets.MonthBegin(), periods=periods, freq='M'))
        conf = None
    # Plot
    fig, ax = plt.subplots(figsize=(9,4))
    series.plot(ax=ax, label='Historic', marker='o')
    fc_series.index = pd.date_range(series.index[-1]+pd.offsets.MonthBegin(), periods=len(fc_series), freq='M')
    fc_series.plot(ax=ax, label='Forecast', marker='o')
    if conf is not None:
        try:
            lower = conf.iloc[:,0].values
            upper = conf.iloc[:,1].values
            ax.fill_between(fc_series.index, lower, upper, alpha=0.2)
        except Exception:
            pass
    ax.set_title(f'Forecast for {part.name} (next {periods} months)')
    ax.set_ylabel('Quantity')
    ax.legend()
    img_dir = os.path.join(settings.MEDIA_ROOT, 'ai')
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, f'forecast_{part_id}.png')
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return path
