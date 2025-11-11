# StockWise - API (no frontend)

## Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Rodar
uvicorn app.main:app --reload

## Endpoints principais
POST /users/?username=...&password=...     # register
POST /token (form data username+password)   # get JWT
POST /products/?name=...&price=...&quantity=...  (Bearer token)
GET  /products/                              (Bearer token)
POST /sales/?product_id=...&quantity=...     (Bearer token)
GET /reports/sales/csv                       (Bearer token) -> creates sales_report.csv
GET /reports/sales/pdf                       (Bearer token) -> creates sales_report.pdf

## Tests
pytest
