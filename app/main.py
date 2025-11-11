from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import datetime
from app import deps, crud, auth, reports
from typing import Optional

app = FastAPI(title="StockWise API")


@app.on_event("startup")
def startup():
    deps.init_db()


@app.post("/users/", status_code=201)
def register(username: str, password: str, db: Session = Depends
             (deps.get_session)):
    existing = crud.get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = crud.create_user(db, username=username, password=password)
    return {"id": user.id, "username": user.username}


@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session =
          Depends(deps.get_session)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid\
                  credentials")
    access_token = auth.create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/products/", status_code=201)
def create_product(name: str, price: float, quantity: int, category: Optional
                   [str] = None, db: Session = Depends(deps.get_session),
                   user=Depends(deps.get_current_user)):
    product = crud.create_product(db, name, price, quantity, category)
    return product


@app.get("/products/")
def get_products(db: Session = Depends(deps.get_session), user=Depends
                 (deps.get_current_user)):
    return crud.list_products(db)


@app.post("/sales/", status_code=201)
def create_sale(product_id: int, quantity: int, db: Session = Depends
                (deps.get_session), user=Depends(deps.get_current_user)):
    try:
        sale = crud.create_sale(db, product_id=product_id, quantity=quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return sale


@app.get("/sales/")
def get_sales(product_id: Optional[int] = None, db: Session = Depends
              (deps.get_session), user=Depends(deps.get_current_user)):
    return crud.list_sales(db, product_id=product_id)


@app.get("/reports/sales/csv")
def report_sales_csv(start: Optional[str] = None, end: Optional[str] = None,
                     db: Session = Depends(deps.get_session), user=Depends
                     (deps.get_current_user)):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    sales = crud.get_all_sales_for_period(db, start_dt, end_dt)
    filename = reports.sales_to_csv(sales, filename="sales_report.csv")
    return {"filename": filename, "rows": len(sales)}


@app.get("/reports/sales/pdf")
def report_sales_pdf(start: Optional[str] = None, end: Optional[str] = None,
                     db: Session = Depends(deps.get_session), user=Depends
                     (deps.get_current_user)):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    sales = crud.get_all_sales_for_period(db, start_dt, end_dt)
    filename = reports.sales_to_pdf(sales, db=db, filename="sales_report.pdf")
    return {"filename": filename, "rows": len(sales)}
