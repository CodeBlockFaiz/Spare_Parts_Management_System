# SpareParts Portal (Django) - with AI modules
This project is the SpareParts Portal with added AI features:
- Item-item recommendations based on co-occurrence in invoices (scikit-learn cosine similarity)
- Simple sales forecasting per part using ARIMA (statsmodels) and plotted as an image

## Quick start
1. Install Python 3.10+ and create a virtualenv
```
python -m venv venv
source venv/bin/activate     # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```
2. Run migrations and create superuser
```
python manage.py migrate
python manage.py createsuperuser
```
3. Run the server
```
python manage.py runserver
```
4. Add Parts and create Invoices via admin (/admin/) or the UI. Then visit Parts list to see 'Recommendations' and 'Forecast' links for each part.

Notes:
- Forecasting requires some historic invoice data (monthly) to produce useful predictions.
- This is a starter implementation — you can later add background tasks, caching of similarity matrices, and improved ARIMA hyperparameter selection.
