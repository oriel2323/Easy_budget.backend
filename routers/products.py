from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.product import Product
from models.user import User
from schemas.products import ProductCreate, ProductUpdate, ProductOut

router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}", response_model=list[ProductOut])
def list_products(user_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.user_id == user_id).all()


@router.post("/{user_id}", response_model=ProductOut)
def create_product(user_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    product = Product(user_id=user_id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{user_id}/{product_id}", response_model=ProductOut)
def update_product(user_id: int, product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == user_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(product, k, v)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{user_id}/{product_id}")
def delete_product(user_id: int, product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == user_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"success": True}
