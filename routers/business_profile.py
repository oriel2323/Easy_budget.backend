from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from models.business_profile import BusinessProfile
from schemas.business_profile import BusinessProfileCreate, BusinessProfileUpdate, BusinessProfileOut

router = APIRouter(prefix="/business-profile", tags=["Business Profile"])


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
def create_or_update_business_profile(
    user_id: int,
    payload: BusinessProfileCreate,
    db: Session = Depends(get_db),
):
    # לוודא שהיוזר קיים
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()

    if not profile:
        profile = BusinessProfile(user_id=user_id)
        db.add(profile)

    # עדכון שדות (גם ב-create וגם ב-update)
    profile.business_name = payload.business_name
    profile.phone = payload.phone
    profile.address = payload.address

    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/{user_id}", response_model=BusinessProfileOut)
def patch_business_profile(
    user_id: int,
    payload: BusinessProfileUpdate,
    db: Session = Depends(get_db),
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    return profile
