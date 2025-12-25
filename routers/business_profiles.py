from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from models.business_profile import BusinessProfile
from schemas.business_profiles import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileOut,
)

router = APIRouter(prefix="/business-profiles", tags=["Business Profiles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}", response_model=BusinessProfileOut)
def get_business_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return profile


@router.post("/{user_id}", response_model=BusinessProfileOut)
def create_or_replace_business_profile(
    user_id: int, payload: BusinessProfileCreate, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
    if profile:
        # replace existing (id stays the same)
        profile.business_name = payload.business_name
        profile.phone = payload.phone
        profile.address = payload.address
    else:
        profile = BusinessProfile(
            user_id=user_id,
            business_name=payload.business_name,
            phone=payload.phone,
            address=payload.address,
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.put("/{user_id}", response_model=BusinessProfileOut)
def update_business_profile(
    user_id: int, payload: BusinessProfileUpdate, db: Session = Depends(get_db)
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")

    if payload.business_name is not None:
        profile.business_name = payload.business_name
    if payload.phone is not None:
        profile.phone = payload.phone
    if payload.address is not None:
        profile.address = payload.address

    db.commit()
    db.refresh(profile)
    return profile
